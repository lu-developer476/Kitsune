"""Deterministic source formatter for Kitsune."""

from src.common.lexer import Lexer, KITSUNE_KEYWORDS
from .parser_core import KitsuneParser


def _scan(source):
    tokens = []
    i = 0
    while i < len(source):
        char = source[i]
        if char in " \t\r":
            i += 1
            continue
        if char == "\n":
            tokens.append(("NEWLINE", "\n"))
            i += 1
            continue
        if char == "#" or source.startswith("//", i):
            start = i
            while i < len(source) and source[i] != "\n":
                i += 1
            tokens.append(("COMMENT", source[start:i]))
            continue
        if char == '"':
            start = i
            i += 1
            while i < len(source):
                if source[i] == "\\":
                    i += 2
                    continue
                if source[i] == '"':
                    i += 1
                    break
                i += 1
            tokens.append(("STRING", source[start:i]))
            continue
        if char.isalpha() or char == "_":
            start = i
            i += 1
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            tokens.append(("WORD", source[start:i]))
            continue
        if char.isdigit():
            start = i
            i += 1
            while i < len(source) and source[i].isdigit():
                i += 1
            if i + 1 < len(source) and source[i] == "." and source[i + 1].isdigit():
                i += 1
                while i < len(source) and source[i].isdigit():
                    i += 1
            tokens.append(("NUMBER", source[start:i]))
            continue
        pair = source[i:i + 2]
        if pair in {"==", "!=", "<=", ">=", "->"}:
            tokens.append(("OP", pair))
            i += 2
            continue
        tokens.append(("PUNCT", char))
        i += 1
    return tokens


def format_source(source):
    KitsuneParser(Lexer(source, keywords=KITSUNE_KEYWORDS).tokens()).parse()
    tokens = _scan(source)
    output = []
    line = ""
    indent = 0
    previous = None
    blank_pending = False
    statement_words = {"let", "spell", "echo", "if", "while", "for", "return", "break", "continue", "import"}

    def flush():
        nonlocal line
        if line.strip():
            output.append(line.rstrip())
        line = ""

    def add(value, space=False):
        nonlocal line
        if not line:
            line = "    " * indent
        elif space and not line.endswith(" "):
            line += " "
        line += value

    for kind, value in tokens:
        if kind == "NEWLINE":
            if line.strip():
                flush()
                blank_pending = False
            elif output and output[-1] != "":
                blank_pending = True
            previous = ("NEWLINE", value)
            continue
        if blank_pending and output and output[-1] != "":
            output.append("")
            blank_pending = False
        if kind == "COMMENT":
            add(value, space=bool(line.strip()))
            flush()
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == "}":
            flush()
            indent = max(0, indent - 1)
            add("}")
            flush()
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == "{":
            add("{", space=True)
            flush()
            indent += 1
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == ";":
            add(";")
            flush()
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == ",":
            add(",")
            line += " "
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == ".":
            line = line.rstrip()
            add(".")
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value in ")]":
            line = line.rstrip()
            add(value)
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value in "([":
            add(value)
            previous = (kind, value)
            continue
        if kind == "PUNCT" and value == ":":
            line = line.rstrip()
            add(": ")
            previous = (kind, value)
            continue
        if kind == "OP":
            line = line.rstrip()
            unary = value == "-" and (
                previous is None or previous[1] in {"(", "[", "{", ",", ":", "+", "-", "*", "/", "%", "=", "==", "!=", "<", "<=", ">", ">=", "and", "or", "not"}
            )
            if unary:
                add(value)
            else:
                add(" " + value + " ")
            previous = (kind, value)
            continue
        if kind == "WORD" and value in statement_words and line.strip():
            if previous and previous[1] not in {".", "=", "+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "and", "or", "not", ",", ":"}:
                flush()
        ends_value = previous and previous[0] in {"WORD", "NUMBER", "STRING"} or previous and previous[1] in {")", "]", "}"}
        add(value, space=bool(line.strip() and ends_value))
        previous = (kind, value)
    flush()
    while output and output[-1] == "":
        output.pop()
    return "\n".join(output) + ("\n" if output else "")
