from .errors import RuntimeLangError
class ParserBase:
 def __init__(self,tokens): self.tokens=tokens; self.i=0
 def peek(self,n=0): return self.tokens[min(self.i+n,len(self.tokens)-1)]
 def check(self,*k): return self.peek().kind in k
 def match(self,*k):
  if self.check(*k):
   t=self.peek(); self.i+=1; return t
  return None
 def expect(self,k,msg=None):
  t=self.match(k)
  if t: return t
  p=self.peek(); raise RuntimeLangError(msg or f'Expected {k}, got {p.kind}')
