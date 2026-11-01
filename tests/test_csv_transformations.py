import pytest

from src.common.errors import RuntimeLangError
from src.kitsune.runner import run


def evaluate(source):
    output = []
    run(source, output.append)
    return output


def test_csv_group_by_preserves_group_and_row_order():
    assert evaluate(
        'let rows = csv_parse("team,name\\nred,Ada\\nblue,Lin\\nred,Sam\\n")\n'
        'echo json_stringify(csv_group_by(rows, "team"))'
    ) == ['{"blue":[{"name":"Lin","team":"blue"}],"red":[{"name":"Ada","team":"red"},{"name":"Sam","team":"red"}]}']


def test_csv_distinct_keeps_first_row_for_each_selected_key():
    assert evaluate(
        'let rows = csv_parse("team,name\\nred,Ada\\nred,Grace\\nblue,Lin\\n")\n'
        'echo json_stringify(csv_distinct(rows, ["team"]))'
    ) == ['[{"name":"Ada","team":"red"},{"name":"Lin","team":"blue"}]']


def test_csv_distinct_can_use_a_composite_key():
    assert evaluate(
        'let rows = csv_parse("team,name\\nred,Ada\\nred,Ada\\nred,Grace\\n")\n'
        'echo len(csv_distinct(rows, ["team", "name"]))'
    ) == ["2"]


@pytest.mark.parametrize(
    "source",
    [
        'csv_group_by([{"team":"red"}], "missing")',
        'csv_distinct([{"team":"red"}], ["missing"])',
        'csv_distinct([{"team":"red"}], ["team", "team"])',
        'csv_group_by("not rows", "team")',
    ],
)
def test_csv_transformations_reject_invalid_inputs(source):
    with pytest.raises(RuntimeLangError):
        run(f"echo {source}")
