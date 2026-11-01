import pytest

from src.common.errors import ParseError, RuntimeLangError
from src.common.lexer import Lexer
from src.kitsune.runner import run


def test_boolean_operators_short_circuit():
    output = []
    run('echo false and missing_name\necho true or another_missing_name', output.append)
    assert output == ['false', 'true']


@pytest.mark.parametrize('source', ['echo 1 / 0', 'echo [][0]', 'echo len(1)'])
def test_python_runtime_failures_are_language_errors(source):
    with pytest.raises(RuntimeLangError):
        run(source)


def test_parser_errors_have_a_language_error_type_and_location():
    with pytest.raises(ParseError) as error:
        run('let = 10')
    assert error.value.line == 1
    assert error.value.column is not None


def test_lexer_errors_have_a_language_error_type_and_location():
    with pytest.raises(Exception) as error:
        Lexer('echo 1\n@').tokens()
    assert getattr(error.value, 'line', None) == 2
