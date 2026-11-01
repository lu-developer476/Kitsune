from dataclasses import dataclass

@dataclass
class Program: statements: list
@dataclass
class ImportStmt: path: str; alias: str
@dataclass
class VarDecl: name: str; expr: object
@dataclass
class Assign: name: str; expr: object
@dataclass
class IndexAssign: target: object; index: object; expr: object
@dataclass
class FunctionDecl: name: str; params: list; body: list
@dataclass
class IfStmt: condition: object; then_body: list; else_body: list
@dataclass
class WhileStmt: condition: object; body: list
@dataclass
class ForStmt: name: str; iterable: object; body: list
@dataclass
class ReturnStmt: expr: object
@dataclass
class BreakStmt: pass
@dataclass
class ContinueStmt: pass
@dataclass
class PrintStmt: expr: object
@dataclass
class ExprStmt: expr: object
@dataclass
class Literal: value: object
@dataclass
class Variable: name: str
@dataclass
class Binary: left: object; op: str; right: object
@dataclass
class Unary: op: str; expr: object
@dataclass
class Call: callee: object; args: list
@dataclass
class Array: items: list
@dataclass
class Map: pairs: list
@dataclass
class Index: target: object; index: object
