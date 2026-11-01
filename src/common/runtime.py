import json
from pathlib import Path

from . import ast
from .errors import LanguageError, RuntimeLangError


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Env:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise RuntimeLangError(f"Undefined name '{name}'")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            raise RuntimeLangError(f"Undefined name '{name}'")


class Function:
    def __init__(self, declaration, closure, interpreter):
        self.declaration = declaration
        self.closure = closure
        self.interpreter = interpreter

    def __call__(self, args):
        expected = len(self.declaration.params)
        if len(args) != expected:
            raise RuntimeLangError(
                f"{self.declaration.name} expected {expected} args, got {len(args)}"
            )
        env = Env(self.closure)
        for name, value in zip(self.declaration.params, args):
            env.define(name, value)
        try:
            self.interpreter.block(self.declaration.body, env)
        except ReturnSignal as signal:
            return signal.value
        except (BreakSignal, ContinueSignal) as error:
            raise RuntimeLangError("loop control used outside a function-local loop") from error
        return None


class Builtin:
    def __init__(self, name, function, arity=None):
        self.name = name
        self.function = function
        self.arity = arity

    def __call__(self, args):
        if self.arity is not None and len(args) != self.arity:
            raise RuntimeLangError(
                f"{self.name} expected {self.arity} args, got {len(args)}"
            )
        try:
            return self.function(*args)
        except LanguageError:
            raise
        except Exception as error:
            raise RuntimeLangError(f"{self.name} failed: {error}") from error


def json_stringify(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


class Interpreter:
    def __init__(self, printer=print, module_loader=None, module_extension=".kit"):
        self.printer = printer
        self.loader = module_loader
        self.extension = module_extension
        self.global_env = Env()
        self.env = self.global_env
        self.root = None
        self.path = None
        self.cache = {}
        self.loading = set()
        builtins = {
            "range": Builtin("range", lambda *args: list(range(*map(int, args)))),
            "len": Builtin("len", len, 1),
            "push": Builtin("push", lambda array, value: (array.append(value) or array), 2),
            "pop": Builtin("pop", lambda array: array.pop() if array else None, 1),
            "first": Builtin("first", lambda array: array[0] if array else None, 1),
            "last": Builtin("last", lambda array: array[-1] if array else None, 1),
            "join": Builtin("join", lambda array, separator: separator.join(map(str, array)), 2),
            "split": Builtin("split", lambda value, separator: value.split(separator), 2),
            "keys": Builtin("keys", lambda mapping: list(mapping.keys()), 1),
            "values": Builtin("values", lambda mapping: list(mapping.values()), 1),
            "has": Builtin("has", lambda mapping, key: key in mapping, 2),
            "type": Builtin("type", self.type_name, 1),
            "str": Builtin("str", self.stringify, 1),
            "json_parse": Builtin("json_parse", json.loads, 1),
            "json_stringify": Builtin("json_stringify", json_stringify, 1),
        }
        for name, function in builtins.items():
            self.global_env.define(name, function)

    def run(self, program, source_path=None):
        if source_path is not None:
            self.path = Path(source_path).resolve()
            self.root = self.path.parent
        try:
            for statement in program.statements:
                self.stmt(statement)
        except ReturnSignal as error:
            raise RuntimeLangError("return used outside a function") from error
        except (BreakSignal, ContinueSignal) as error:
            raise RuntimeLangError("loop control used outside a loop") from error
        except LanguageError:
            raise
        except Exception as error:
            raise RuntimeLangError(f"runtime operation failed: {error}") from error

    def block(self, body, env):
        previous = self.env
        self.env = env
        try:
            for statement in body:
                self.stmt(statement)
        finally:
            self.env = previous

    def import_module(self, statement):
        if not self.loader or not self.path or not self.root:
            raise RuntimeLangError("imports require a file-backed program")
        requested = Path(statement.path)
        if requested.is_absolute() or requested.suffix != self.extension:
            raise RuntimeLangError("invalid module path or extension")
        try:
            target = (self.path.parent / requested).resolve(strict=True)
        except OSError as error:
            raise RuntimeLangError(f"cannot resolve module: {error}") from error
        if not target.is_relative_to(self.root):
            raise RuntimeLangError("module path escapes the project directory")
        if target in self.loading:
            raise RuntimeLangError("cyclic module import detected")
        if target not in self.cache:
            self.loading.add(target)
            previous_path = self.path
            previous_env = self.env
            module_env = Env(self.global_env)
            try:
                self.path = target
                self.env = module_env
                source = target.read_text(encoding="utf-8")
                self.block(self.loader(source).statements, module_env)
                self.cache[target] = {
                    name: value for name, value in module_env.values.items()
                    if not name.startswith("_")
                }
            finally:
                self.path = previous_path
                self.env = previous_env
                self.loading.remove(target)
        self.env.define(statement.alias, self.cache[target])

    def stmt(self, statement):
        if isinstance(statement, ast.ImportStmt):
            self.import_module(statement)
        elif isinstance(statement, ast.VarDecl):
            self.env.define(statement.name, self.expr(statement.expr))
        elif isinstance(statement, ast.Assign):
            self.env.assign(statement.name, self.expr(statement.expr))
        elif isinstance(statement, ast.IndexAssign):
            self.expr(statement.target)[self.expr(statement.index)] = self.expr(statement.expr)
        elif isinstance(statement, ast.FunctionDecl):
            self.env.define(statement.name, Function(statement, self.env, self))
        elif isinstance(statement, ast.IfStmt):
            branch = statement.then_body if self.expr(statement.condition) else statement.else_body
            self.block(branch, Env(self.env))
        elif isinstance(statement, ast.WhileStmt):
            while self.expr(statement.condition):
                try:
                    self.block(statement.body, Env(self.env))
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
        elif isinstance(statement, ast.ForStmt):
            for value in self.expr(statement.iterable):
                loop_env = Env(self.env)
                loop_env.define(statement.name, value)
                try:
                    self.block(statement.body, loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
        elif isinstance(statement, ast.ReturnStmt):
            raise ReturnSignal(self.expr(statement.expr))
        elif isinstance(statement, ast.BreakStmt):
            raise BreakSignal()
        elif isinstance(statement, ast.ContinueStmt):
            raise ContinueSignal()
        elif isinstance(statement, ast.PrintStmt):
            self.printer(self.stringify(self.expr(statement.expr)))
        elif isinstance(statement, ast.ExprStmt):
            self.expr(statement.expr)

    def expr(self, expression):
        if isinstance(expression, ast.Literal):
            return expression.value
        if isinstance(expression, ast.Variable):
            return self.env.get(expression.name)
        if isinstance(expression, ast.Array):
            return [self.expr(item) for item in expression.items]
        if isinstance(expression, ast.Map):
            return {self.expr(key): self.expr(value) for key, value in expression.pairs}
        if isinstance(expression, ast.Index):
            return self.expr(expression.target)[self.expr(expression.index)]
        if isinstance(expression, ast.Unary):
            value = self.expr(expression.expr)
            return not bool(value) if expression.op == "not" else -value
        if isinstance(expression, ast.Binary):
            left = self.expr(expression.left)
            if expression.op == "and":
                return bool(left) and bool(self.expr(expression.right))
            if expression.op == "or":
                return bool(left) or bool(self.expr(expression.right))
            right = self.expr(expression.right)
            operations = {
                "+": lambda: left + right,
                "-": lambda: left - right,
                "*": lambda: left * right,
                "/": lambda: left / right,
                "%": lambda: left % right,
                "==": lambda: left == right,
                "!=": lambda: left != right,
                "<": lambda: left < right,
                "<=": lambda: left <= right,
                ">": lambda: left > right,
                ">=": lambda: left >= right,
            }
            return operations[expression.op]()
        if isinstance(expression, ast.Call):
            function = self.expr(expression.callee)
            args = [self.expr(item) for item in expression.args]
            if not callable(function):
                raise RuntimeLangError("value is not callable")
            return function(args)
        raise RuntimeLangError("unknown expression")

    def type_name(self, value):
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            return "text"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "map"
        return "function" if callable(value) else type(value).__name__

    def stringify(self, value):
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            return "[" + ", ".join(map(self.stringify, value)) + "]"
        if isinstance(value, dict):
            pairs = (
                f"{self.stringify(key)}: {self.stringify(item)}"
                for key, item in value.items()
            )
            return "{" + ", ".join(pairs) + "}"
        return str(value)
