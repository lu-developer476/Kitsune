from pathlib import Path
from src.common.lexer import Lexer, KITSUNE_KEYWORDS
from src.common.runtime import Interpreter
from .parser_core import KitsuneParser

def run(source, printer=print, source_path=None):
    program=KitsuneParser(Lexer(source, keywords=KITSUNE_KEYWORDS).tokens()).parse()
    interpreter=Interpreter(printer, module_loader=lambda text: KitsuneParser(Lexer(text, keywords=KITSUNE_KEYWORDS).tokens()).parse(), module_extension='.kit')
    interpreter.run(program, source_path=source_path)
