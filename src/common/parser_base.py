from .errors import ParseError

class ParserBase:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
    def peek(self, offset=0):
        return self.tokens[min(self.i + offset, len(self.tokens) - 1)]
    def check(self, *kinds):
        return self.peek().kind in kinds
    def match(self, *kinds):
        if self.check(*kinds):
            token = self.peek()
            self.i += 1
            return token
        return None
    def expect(self, kind, message=None):
        token = self.match(kind)
        if token is not None:
            return token
        found = self.peek()
        raise ParseError(message or f'Expected {kind}, got {found.kind}', found.line, found.column)
