from src.common import ast
from src.common.errors import ParseError
from src.common.parser_base import ParserBase
from src.common.pratt import ExpressionParserMixin

class KitsuneParser(ExpressionParserMixin, ParserBase):
    def parse(self):
        out=[]
        while not self.check('EOF'):
            out.append(self.statement())
        return ast.Program(out)
    def block(self):
        self.expect('{'); out=[]
        while not self.check('}'):
            out.append(self.statement())
        self.expect('}'); return out
    def statement(self):
        if self.match('import'):
            path=self.expect('STRING').value; self.expect('as'); alias=self.expect('IDENT').value
            return ast.ImportStmt(path,alias)
        if self.match('let'):
            name=self.expect('IDENT').value; self.expect('='); return ast.VarDecl(name,self.expression())
        if self.match('spell'):
            name=self.expect('IDENT').value; self.expect('('); params=[]
            if not self.check(')'):
                params.append(self.expect('IDENT').value)
                while self.match(','): params.append(self.expect('IDENT').value)
            self.expect(')'); return ast.FunctionDecl(name,params,self.block())
        if self.match('echo'): return ast.PrintStmt(self.expression())
        if self.match('if'):
            cond=self.expression(); yes=self.block(); no=self.block() if self.match('else') else []
            return ast.IfStmt(cond,yes,no)
        if self.match('while'): return ast.WhileStmt(self.expression(),self.block())
        if self.match('for'):
            name=self.expect('IDENT').value; self.expect('in'); return ast.ForStmt(name,self.expression(),self.block())
        if self.match('return'): return ast.ReturnStmt(self.expression())
        if self.match('break'): return ast.BreakStmt()
        if self.match('continue'): return ast.ContinueStmt()
        target=self.expression()
        if self.match('='):
            value=self.expression()
            if isinstance(target,ast.Variable): return ast.Assign(target.name,value)
            if isinstance(target,ast.Index): return ast.IndexAssign(target.target,target.index,value)
            raise ParseError('Invalid assignment target', self.peek().line, self.peek().column)
        return ast.ExprStmt(target)
