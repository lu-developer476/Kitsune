class LanguageError(Exception):
    """Base class for errors intentionally reported by a language implementation."""

    def __init__(self, message, line=None, column=None):
        self.message = str(message)
        self.line = line
        self.column = column
        location = ""
        if line is not None:
            location = f" (line {line}"
            if column is not None:
                location += f", column {column}"
            location += ")"
        super().__init__(self.message + location)


class LexError(LanguageError):
    """Invalid source text."""


class ParseError(LanguageError):
    """Source text that does not match the language grammar."""


class RuntimeLangError(LanguageError):
    """A controlled runtime failure in a language program."""
