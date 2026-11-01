from . import ast
from .errors import ParseError

class ExpressionParserMixin:
    PRECEDENCE = {'or': 1, 'and': 2, '==': 3, '!=': 3, '<': 4, '<=': 4, '>': 4, '>=': 4, '+': 5, '-': 5, '*': 6, '/': 6, '%': 6}
    def expression(self, minimum=1):
        left = self.unary()
        while self.peek().kind in self.PRECEDENCE and self.PRECEDENCE[self.peek().kind] >= minimum:
            op = self.peek().kind
            level = self.PRECEDENCE[op]
            self.i += 1
            left = ast.Binary(left, op, self.expression(level + 1))
        return left
    def unary(self):
        if self.match('not'): return ast.Unary('not', self.unary())
        if self.match('-'): return ast.Unary('-', self.unary())
        return self.call()
    def call(self):
        node = self.primary()
        while True:
            if self.match('('):
                args = []
                if not self.check(')'):
                    args.append(self.expression())
                    while self.match(','): args.append(self.expression())
                self.expect(')')
                node = ast.Call(node, args)
            elif self.match('['):
                index = self.expression(); self.expect(']')
                node = ast.Index(node, index)
            elif self.match('.'):
                node = ast.Index(node, ast.Literal(self.expect('IDENT').value))
            else: return node
    def primary(self):
        token = self.match('NUMBER', 'STRING')
        if token is not None: return ast.Literal(token.value)
        if self.match('true'): return ast.Literal(True)
        if self.match('false'): return ast.Literal(False)
        if self.match('nil'): return ast.Literal(None)
        token = self.match('IDENT')
        if token is not None: return ast.Variable(token.value)
        if self.match('range'): return ast.Variable('range')
        if self.match('['):
            items = []
            if not self.check(']'):
                items.append(self.expression())
                while self.match(','): items.append(self.expression())
            self.expect(']'); return ast.Array(items)
        if self.match('{'):
            pairs = []
            if not self.check('}'):
                key = self.expression(); self.expect(':'); pairs.append((key, self.expression()))
                while self.match(','):
                    key = self.expression(); self.expect(':'); pairs.append((key, self.expression()))
            self.expect('}'); return ast.Map(pairs)
        if self.match('('):
            node = self.expression(); self.expect(')'); return node
        token = self.peek()
        raise ParseError('Expected expression', token.line, token.column)
