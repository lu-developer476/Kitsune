from src.common.errors import ParseError, RuntimeLangError
from src.kitsune.runner import run


def test_invalid_assignment_target_is_a_parse_error():
    with pytest.raises(ParseError, match='Invalid assignment target'):
        run('echo 1 = 2')


def test_loop_control_inside_function_cannot_escape_to_caller():
    with pytest.raises(RuntimeLangError, match='loop control'):
        run('spell stop() { break } while true { stop() }')
