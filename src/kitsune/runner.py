from pathlib import Path
from src.common.lexer import Lexer
from src.common.runtime import Interpreter
from .parser_core import KitsuneParser

def run(source, printer=print, source_path=None):
    program=KitsuneParser(Lexer(source).tokens()).parse()
    interpreter=Interpreter(printer, module_loader=lambda text: KitsuneParser(Lexer(text).tokens()).parse(), module_extension='.kit')
    interpreter.run(program, source_path=source_path)
