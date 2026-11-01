import csv
import io
import json
import math
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



def csv_parse_text(source):
    if not isinstance(source, str):
        raise TypeError("csv_parse expects text")
    if source == "":
        return []
    rows = list(csv.reader(io.StringIO(source, newline=""), strict=True))
    if not rows:
        return []
    headers = rows[0]
    if not headers or any(not header for header in headers):
        raise ValueError("CSV header names must be non-empty")
    if len(set(headers)) != len(headers):
        raise ValueError("CSV header names must be unique")
    result = []
    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) != len(headers):
            raise ValueError(
                f"CSV row {line_number} has {len(row)} fields; expected {len(headers)}"
            )
        result.append(dict(zip(headers, row)))
    return result


def _csv_cell_text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (str, int)):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CSV values must not contain non-finite numbers")
        return str(value)
    raise TypeError(f"CSV cell value of type {type(value).__name__} is not supported")


def csv_stringify_rows(rows):
    if not isinstance(rows, list):
        raise TypeError("csv_stringify expects an array of maps")
    if not rows:
        return ""
    if any(not isinstance(row, dict) for row in rows):
        raise TypeError("csv_stringify expects every row to be a map")
    headers = sorted({key for row in rows for key in row})
    if not headers or any(not isinstance(key, str) or not key for key in headers):
        raise ValueError("CSV column names must be non-empty text")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _csv_cell_text(row.get(key)) for key in headers})
    return output.getvalue()


def csv_filter_rows(rows, column, value):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise TypeError("csv_filter expects an array of maps")
    if not isinstance(column, str) or not column:
        raise TypeError("csv_filter column must be non-empty text")
    expected = _csv_cell_text(value)
    if any(column not in row for row in rows):
        raise ValueError(f"CSV column does not exist: {column}")
    return [row for row in rows if _csv_cell_text(row[column]) == expected]


def csv_select_columns(rows, columns):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise TypeError("csv_select expects an array of maps")
    if not isinstance(columns, list) or any(not isinstance(item, str) or not item for item in columns):
        raise TypeError("csv_select columns must be an array of non-empty text values")
    if len(set(columns)) != len(columns):
        raise ValueError("csv_select columns must be unique")
    for row in rows:
        missing = [column for column in columns if column not in row]
        if missing:
            raise ValueError(f"CSV column does not exist: {missing[0]}")
    return [{column: row[column] for column in columns} for row in rows]


def csv_sort_rows(rows, column):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise TypeError("csv_sort expects an array of maps")
    if not isinstance(column, str) or not column:
        raise TypeError("csv_sort column must be non-empty text")
    if any(column not in row for row in rows):
        raise ValueError(f"CSV column does not exist: {column}")
    return sorted(rows, key=lambda row: _csv_cell_text(row[column]))


def _reject_json_constant(value):
    raise ValueError(f"invalid JSON numeric constant: {value}")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _parse_json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"JSON number is outside the supported range: {value}")
    return number


def json_parse_strict(source):
    if not isinstance(source, str):
        raise TypeError("json_parse expects text")
    return json.loads(
        source,
        parse_constant=_reject_json_constant,
        parse_float=_parse_json_float,
        object_pairs_hook=_unique_json_object,
    )


def _validate_json_value(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be text")
            _validate_json_value(item)
        return
    raise TypeError(f"value of type {type(value).__name__} is not JSON-compatible")


def json_stringify_strict(value):
    _validate_json_value(value)
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
            "json_parse": Builtin("json_parse", json_parse_strict, 1),
            "json_stringify": Builtin("json_stringify", json_stringify_strict, 1),
            "csv_parse": Builtin("csv_parse", csv_parse_text, 1),
            "csv_stringify": Builtin("csv_stringify", csv_stringify_rows, 1),
            "csv_filter": Builtin("csv_filter", csv_filter_rows, 3),
            "csv_select": Builtin("csv_select", csv_select_columns, 2),
            "csv_sort": Builtin("csv_sort", csv_sort_rows, 2),
            "csv_read": Builtin("csv_read", self.csv_read, 1),
            "csv_read_many": Builtin("csv_read_many", self.csv_read_many, 1),
            "csv_write": Builtin("csv_write", self.csv_write, 2),
            "read_text": Builtin("read_text", self.read_text, 1),
            "write_text": Builtin("write_text", self.write_text, 2),
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

    def _project_file(self, value, *, must_exist=False):
        if not isinstance(value, str) or not value:
            raise RuntimeLangError("file path must be non-empty text")
        requested = Path(value)
        if requested.is_absolute():
            raise RuntimeLangError("absolute file paths are not allowed")
        if self.root is None:
            raise RuntimeLangError("file operations require a file-backed program")
        try:
            target = (self.path.parent / requested).resolve(strict=must_exist)
        except OSError as error:
            raise RuntimeLangError(f"cannot resolve file path: {error}") from error
        if not target.is_relative_to(self.root):
            raise RuntimeLangError("file path escapes the project directory")
        if target == self.root:
            raise RuntimeLangError("file path must identify a file")
        return target

    def read_text(self, value):
        target = self._project_file(value, must_exist=True)
        if not target.is_file():
            raise RuntimeLangError("read_text target is not a file")
        try:
            return target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise RuntimeLangError(f"cannot read text file: {error}") from error

    def write_text(self, value, content):
        if not isinstance(content, str):
            raise RuntimeLangError("write_text content must be text")
        target = self._project_file(value)
        if target.exists() and not target.is_file():
            raise RuntimeLangError("write_text target is not a file")
        try:
            target.write_text(content, encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise RuntimeLangError(f"cannot write text file: {error}") from error
        return len(content)

    def csv_read(self, value):
        return csv_parse_text(self.read_text(value))

    def csv_read_many(self, paths):
        if not isinstance(paths, list):
            raise RuntimeLangError("csv_read_many expects an array of paths")
        combined = []
        expected_columns = None
        for path in paths:
            rows = self.csv_read(path)
            if rows:
                columns = set(rows[0])
                if expected_columns is None:
                    expected_columns = columns
                elif columns != expected_columns:
                    raise RuntimeLangError("CSV files in a batch must have matching columns")
                combined.extend(rows)
        return combined

    def csv_write(self, value, rows):
        return self.write_text(value, csv_stringify_rows(rows))

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
