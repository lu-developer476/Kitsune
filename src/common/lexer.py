from dataclasses import dataclass
from .errors import LexError

@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

COMMON_KEYWORDS = {'if', 'else', 'while', 'for', 'in', 'return', 'true', 'false', 'nil', 'and', 'or', 'not', 'break', 'continue', 'import', 'as'}
KITSUNE_KEYWORDS = COMMON_KEYWORDS | {'let', 'spell', 'echo'}
SINGULAR_KEYWORDS = COMMON_KEYWORDS | {'value', 'fn', 'print'}
KEYWORDS = KITSUNE_KEYWORDS | SINGULAR_KEYWORDS
TWO={"==","!=","<=",">=","->"}
ONE=set("+-*/%=<>(){}[],;:.")

class Lexer:
    def __init__(self, source, keywords=None):
        self.source,self.i,self.line,self.col=source,0,1,1
        self.keywords = KEYWORDS if keywords is None else keywords
    def peek(self,n=0):
        j=self.i+n; return self.source[j] if j<len(self.source) else "\0"
    def advance(self):
        ch=self.peek(); self.i+=1
        if ch=="\n": self.line+=1; self.col=1
        else: self.col+=1
        return ch
    def tokens(self):
        out=[]
        while self.peek()!="\0":
            ch=self.peek()
            if ch in " \t\r\n": self.advance(); continue
            if ch=="#" or (ch=="/" and self.peek(1)=="/"):
                while self.peek() not in "\n\0": self.advance()
                continue
            line,col=self.line,self.col
            if ch.isdigit(): out.append(self.number(line,col)); continue
            if ch.isalpha() or ch=="_": out.append(self.identifier(line,col)); continue
            if ch==chr(34): out.append(self.string(line,col)); continue
            pair=ch+self.peek(1)
            if pair in TWO: self.advance(); self.advance(); out.append(Token(pair,pair,line,col)); continue
            if ch in ONE: self.advance(); out.append(Token(ch,ch,line,col)); continue
            raise LexError(f"Unexpected character {ch!r}",line,col)
        out.append(Token("EOF",None,self.line,self.col)); return out
    def number(self,line,col):
        s=""
        while self.peek().isdigit(): s+=self.advance()
        if self.peek()=="." and self.peek(1).isdigit():
            s+=self.advance()
            while self.peek().isdigit(): s+=self.advance()
            return Token("NUMBER",float(s),line,col)
        return Token("NUMBER",int(s),line,col)
    def identifier(self,line,col):
        s=""
        while self.peek().isalnum() or self.peek()=="_": s+=self.advance()
        return Token(s if s in self.keywords else "IDENT",s,line,col)
    def string(self,line,col):
        self.advance(); s=""; escapes={"n":"\n","t":"\t",chr(34):chr(34),"\\":"\\"}
        while self.peek() not in chr(34)+"\0":
            if self.peek()=="\\":
                self.advance(); esc=self.advance(); s+=escapes.get(esc,esc)
            else: s+=self.advance()
        if self.peek()=="\0": raise LexError("Unterminated string",line,col)
        self.advance(); return Token("STRING",s,line,col)
