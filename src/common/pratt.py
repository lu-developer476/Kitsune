from . import ast
class ParseError(Exception): pass
class ExpressionParserMixin:
 PRECEDENCE={'or':1,'and':2,'==':3,'!=':3,'<':4,'<=':4,'>':4,'>=':4,'+':5,'-':5,'*':6,'/':6,'%':6}
 def expression(self,min_prec=1):
  left=self.unary()
  while self.peek().kind in self.PRECEDENCE and self.PRECEDENCE[self.peek().kind]>=min_prec:
   op=self.peek().kind; prec=self.PRECEDENCE[op]; self.i+=1; left=ast.Binary(left,op,self.expression(prec+1))
  return left
 def unary(self):
  if self.match('not'): return ast.Unary('not',self.unary())
  if self.match('-'): return ast.Unary('-',self.unary())
  return self.call()
 def call(self):
  e=self.primary()
  while True:
   if self.match('('):
    args=[]
    if not self.check(')'):
     args.append(self.expression())
     while self.match(','): args.append(self.expression())
    self.expect(')'); e=ast.Call(e,args)
   elif self.match('['):
    idx=self.expression(); self.expect(']'); e=ast.Index(e,idx)
   elif self.match('.'):
    e=ast.Index(e,ast.Literal(self.expect('IDENT').value))
   else: return e
 def primary(self):
  if t:=self.match('NUMBER','STRING'): return ast.Literal(t.value)
  if self.match('true'): return ast.Literal(True)
  if self.match('false'): return ast.Literal(False)
  if self.match('nil'): return ast.Literal(None)
  if t:=self.match('IDENT'): return ast.Variable(t.value)
  if self.match('range'): return ast.Variable('range')
  if self.match('['):
   a=[]
   if not self.check(']'):
    a.append(self.expression())
    while self.match(','): a.append(self.expression())
   self.expect(']'); return ast.Array(a)
  if self.match('{'):
   p=[]
   if not self.check('}'):
    k=self.expression(); self.expect(':'); p.append((k,self.expression()))
    while self.match(','):
     k=self.expression(); self.expect(':'); p.append((k,self.expression()))
   self.expect('}'); return ast.Map(p)
  if self.match('('): e=self.expression(); self.expect(')'); return e
  raise ParseError('Expected expression')
