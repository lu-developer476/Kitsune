import pytest

from src.common.errors import RuntimeLangError
from src.kitsune.runner import run


def test_json_stringify_uses_stable_key_order():
    output = []
    run('echo json_stringify({"z": 3, "a": 1})', output.append)
    assert output == ['{"a":1,"z":3}']


def test_json_parse_and_stringify_round_trip():
    output = []
    run('echo json_stringify(json_parse("null"))', output.append)
    assert output == ["null"]


def test_invalid_json_is_reported_as_a_language_runtime_error():
    with pytest.raises(RuntimeLangError):
        run('echo json_parse("not-json")')
