import json

import pytest

from src.common.errors import RuntimeLangError
from src.kitsune.runner import run


def evaluate(source):
    output = []
    run(source, output.append)
    return output


def test_json_stringify_uses_stable_key_order():
    assert evaluate('echo json_stringify({"z": 3, "a": 1})') == ['{"a":1,"z":3}']


def test_json_parse_and_stringify_round_trip():
    assert evaluate('echo json_stringify(json_parse("null"))') == ["null"]


@pytest.mark.parametrize("payload", ["NaN", "Infinity", "-Infinity", "1e999", "-1e999"])
def test_json_parse_rejects_nonstandard_or_unrepresentable_numbers(payload):
    with pytest.raises(RuntimeLangError):
        run(f"echo json_parse({json.dumps(payload)})")


def test_json_parse_rejects_duplicate_object_keys():
    with pytest.raises(RuntimeLangError):
        run(f"echo json_parse({json.dumps('{\"x\":1,\"x\":2}')})")


def test_json_stringify_rejects_non_text_object_keys():
    with pytest.raises(RuntimeLangError):
        run('echo json_stringify({1: "not a JSON object key"})')


def test_json_stringify_rejects_non_finite_numbers():
    with pytest.raises(RuntimeLangError):
        run(f"echo json_stringify(json_parse({json.dumps('1e999')}))")
