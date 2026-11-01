class LanguageError(Exception):
    def __init__(self, message, line=None, column=None):
        self.message = str(message)
        self.line = line
        self.column = column
        location = ''
        if line is not None:
            location = f' (line {line}'
            if column is not None:
                location += f', column {column}'
            location += ')'
        super().__init__(self.message + location)

class RuntimeLangError(LanguageError):
    pass

class LexError(LanguageError):
    pass

class ParseError(LanguageError):
    pass
