class LanguageError(Exception):
    pass

class RuntimeLangError(LanguageError):
    pass

class LexError(LanguageError):
    pass

class ParseError(LanguageError):
    pass
