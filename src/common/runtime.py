from pathlib import Path
from . import ast
from .errors import RuntimeLangError
class ReturnSignal(Exception):
 def __init__(self,value): self.value=value
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class Env:
 def __init__(self,parent=None): self.parent=parent; self.values={}
 def define(self,n,v): self.values[n]=v
 def get(self,n):
  if n in self.values: return self.values[n]
  if self.parent: return self.parent.get(n)
  raise RuntimeLangError(f"Undefined name '{n}'")
 def assign(self,n,v):
  if n in self.values: self.values[n]=v; return
  if self.parent: self.parent.assign(n,v); return
  raise RuntimeLangError(f"Undefined name '{n}'")
class Function:
 def __init__(self,decl,closure,interpreter): self.decl=decl; self.closure=closure; self.interpreter=interpreter
 def __call__(self,args):
  if len(args)!=len(self.decl.params): raise RuntimeLangError(f'{self.decl.name} expected {len(self.decl.params)} args, got {len(args)}')
  env=Env(self.closure)
  for n,v in zip(self.decl.params,args): env.define(n,v)
  try: self.interpreter.block(self.decl.body,env)
  except ReturnSignal as r: return r.value
  except (BreakSignal,ContinueSignal) as e: raise RuntimeLangError('loop control used outside a loop') from e
  return None
class Builtin:
 def __init__(self,name,fn,arity=None): self.name=name; self.fn=fn; self.arity=arity
 def __call__(self,args):
  if self.arity is not None and len(args)!=self.arity: raise RuntimeLangError(f'{self.name} expected {self.arity} args, got {len(args)}')
  try: return self.fn(*args)
  except Exception as e: raise RuntimeLangError(f'{self.name} failed: {e}') from e
class Interpreter:
 def __init__(self,printer=print,module_loader=None,module_extension='.kit'):
  self.printer=printer; self.loader=module_loader; self.extension=module_extension; self.global_env=Env(); self.env=self.global_env; self.root=None; self.path=None; self.cache={}; self.loading=set()
  builtins={'range':Builtin('range',lambda *a:list(range(*map(int,a)))),'len':Builtin('len',len,1),'push':Builtin('push',lambda a,v:(a.append(v) or a),2),'pop':Builtin('pop',lambda a:a.pop() if a else None,1),'first':Builtin('first',lambda a:a[0] if a else None,1),'last':Builtin('last',lambda a:a[-1] if a else None,1),'join':Builtin('join',lambda a,s:s.join(map(str,a)),2),'split':Builtin('split',lambda s,d:s.split(d),2),'keys':Builtin('keys',lambda m:list(m.keys()),1),'values':Builtin('values',lambda m:list(m.values()),1),'has':Builtin('has',lambda m,k:k in m,2),'type':Builtin('type',self.type_name,1),'str':Builtin('str',self.stringify,1)}
  for n,v in builtins.items(): self.global_env.define(n,v)
 def run(self,program,source_path=None):
  if source_path:
   self.path=Path(source_path).resolve(); self.root=self.path.parent
  try:
   for s in program.statements: self.stmt(s)
  except ReturnSignal as e: raise RuntimeLangError('return used outside a function') from e
  except (BreakSignal,ContinueSignal) as e: raise RuntimeLangError('loop control used outside a loop') from e
 def block(self,body,env):
  old=self.env; self.env=env
  try:
   for s in body: self.stmt(s)
  finally: self.env=old
 def import_module(self,s):
  if not self.loader or not self.path or not self.root: raise RuntimeLangError('imports require a file-backed program')
  p=Path(s.path)
  if p.is_absolute() or p.suffix!=self.extension: raise RuntimeLangError('invalid module path or extension')
  try: target=(self.path.parent/p).resolve(strict=True)
  except OSError as e: raise RuntimeLangError(f'cannot resolve module: {e}') from e
  if not target.is_relative_to(self.root): raise RuntimeLangError('module path escapes the project directory')
  if target in self.loading: raise RuntimeLangError('cyclic module import detected')
  if target not in self.cache:
   self.loading.add(target); oldpath=self.path; oldenv=self.env; env=Env(self.global_env)
   try:
    self.path=target; self.env=env; self.block(self.loader(target.read_text(encoding='utf-8')).statements,env)
    self.cache[target]={k:v for k,v in env.values.items() if not k.startswith('_')}
   finally: self.path=oldpath; self.env=oldenv; self.loading.remove(target)
  self.env.define(s.alias,self.cache[target])
 def stmt(self,s):
  if isinstance(s,ast.ImportStmt): self.import_module(s)
  elif isinstance(s,ast.VarDecl): self.env.define(s.name,self.expr(s.expr))
  elif isinstance(s,ast.Assign): self.env.assign(s.name,self.expr(s.expr))
  elif isinstance(s,ast.IndexAssign): self.expr(s.target)[self.expr(s.index)]=self.expr(s.expr)
  elif isinstance(s,ast.FunctionDecl): self.env.define(s.name,Function(s,self.env,self))
  elif isinstance(s,ast.IfStmt): self.block(s.then_body if self.expr(s.condition) else s.else_body,Env(self.env))
  elif isinstance(s,ast.WhileStmt):
   while self.expr(s.condition):
    try: self.block(s.body,Env(self.env))
    except ContinueSignal: continue
    except BreakSignal: break
  elif isinstance(s,ast.ForStmt):
   for v in self.expr(s.iterable):
    e=Env(self.env); e.define(s.name,v)
    try: self.block(s.body,e)
    except ContinueSignal: continue
    except BreakSignal: break
  elif isinstance(s,ast.ReturnStmt): raise ReturnSignal(self.expr(s.expr))
  elif isinstance(s,ast.BreakStmt): raise BreakSignal()
  elif isinstance(s,ast.ContinueStmt): raise ContinueSignal()
  elif isinstance(s,ast.PrintStmt): self.printer(self.stringify(self.expr(s.expr)))
  elif isinstance(s,ast.ExprStmt): self.expr(s.expr)
 def expr(self,e):
  if isinstance(e,ast.Literal): return e.value
  if isinstance(e,ast.Variable): return self.env.get(e.name)
  if isinstance(e,ast.Array): return [self.expr(x) for x in e.items]
  if isinstance(e,ast.Map): return {self.expr(k):self.expr(v) for k,v in e.pairs}
  if isinstance(e,ast.Index): return self.expr(e.target)[self.expr(e.index)]
  if isinstance(e,ast.Unary): return (not bool(self.expr(e.expr))) if e.op=='not' else -self.expr(e.expr)
  if isinstance(e,ast.Binary):
   a=self.expr(e.left); b=self.expr(e.right)
   return {'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a/b,'%':lambda:a%b,'==':lambda:a==b,'!=':lambda:a!=b,'<':lambda:a<b,'<=':lambda:a<=b,'>':lambda:a>b,'>=':lambda:a>=b,'and':lambda:bool(a) and bool(b),'or':lambda:bool(a) or bool(b)}[e.op]()
  if isinstance(e,ast.Call):
   f=self.expr(e.callee); args=[self.expr(x) for x in e.args]
   if not callable(f): raise RuntimeLangError('value is not callable')
   return f(args)
  raise RuntimeLangError('unknown expression')
 def type_name(self,v):
  if v is None:return 'nil'
  if isinstance(v,bool):return 'bool'
  if isinstance(v,(int,float)):return 'number'
  if isinstance(v,str):return 'text'
  if isinstance(v,list):return 'array'
  if isinstance(v,dict):return 'map'
  return 'function' if callable(v) else type(v).__name__
 def stringify(self,v):
  if v is None:return 'nil'
  if isinstance(v,bool):return str(v).lower()
  if isinstance(v,list):return '['+', '.join(map(self.stringify,v))+']'
  if isinstance(v,dict):return '{'+', '.join(f'{self.stringify(k)}: {self.stringify(x)}' for k,x in v.items())+'}'
  return str(v)
