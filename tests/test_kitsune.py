from src.kitsune.runner import run

def test_kitsune_executes_expression_and_function():
    output=[]
    run('spell twice(x) { return x * 2 } echo twice(21)', output.append)
    assert output == ['42']

def test_kitsune_collections_and_loop():
    output=[]
    run('let total = 0 for n in range(1, 5) { total = total + n } echo total', output.append)
    assert output == ['10']

def test_kitsune_supports_fractional_and_scientific_numbers():
    output = []
    run('echo 1.25e-2 echo 2e3 echo 4.5', output.append)
    assert output == ['0.0125', '2000.0', '4.5']


def test_kitsune_rejects_incomplete_numeric_exponents():
    from src.common.errors import LexError
    import pytest

    with pytest.raises(LexError):
        run('echo 3e+')


def test_file_builtins_read_and_write_project_text(tmp_path):
    from src.common.errors import RuntimeLangError
    import pytest

    source = tmp_path / "main.kit"
    source.write_text('write_text("data.txt", "hola 🌙") echo read_text("data.txt")', encoding="utf-8")
    output = []
    run(source.read_text(encoding="utf-8"), output.append, source_path=source)
    assert output == ["hola 🌙"]
    assert (tmp_path / "data.txt").read_text(encoding="utf-8") == "hola 🌙"

    with pytest.raises(RuntimeLangError):
        run('echo read_text("../outside.txt")', source_path=source)


def test_file_builtins_reject_absolute_paths_and_symlink_escape(tmp_path):
    from src.common.errors import RuntimeLangError
    import pytest

    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    source = project / "main.kit"
    source.write_text("", encoding="utf-8")
    (project / "escape.txt").symlink_to(outside)

    with pytest.raises(RuntimeLangError):
        run(f'echo read_text("{outside.as_posix()}")', source_path=source)
    with pytest.raises(RuntimeLangError):
        run('echo read_text("escape.txt")', source_path=source)


def test_file_builtins_require_file_backed_program():
    from src.common.errors import RuntimeLangError
    import pytest

    with pytest.raises(RuntimeLangError):
        run('echo read_text("data.txt")')


def test_csv_parse_supports_headers_quoted_fields_and_unicode():
    output = []
    run('echo json_stringify(csv_parse("name,note\\nKitsu,\\"hola, mundo\\"\\nLuna,\\"café\\""))', output.append)
    assert output == ['[{"name":"Kitsu","note":"hola, mundo"},{"name":"Luna","note":"café"}]']


def test_csv_stringify_is_deterministic_and_round_trips():
    output = []
    run('let rows = csv_parse("z,name\\n2,Kitsu\\n3,Luna") echo csv_stringify(rows)', output.append)
    assert output == ['name,z\nKitsu,2\nLuna,3\n']


def test_csv_parse_rejects_duplicate_headers_and_ragged_rows():
    import pytest
    from src.common.errors import RuntimeLangError

    with pytest.raises(RuntimeLangError, match="unique"):
        run('echo csv_parse("name,name\\na,b")')
    with pytest.raises(RuntimeLangError, match="expected"):
        run('echo csv_parse("name,age\\nKitsu")')


def test_csv_stringify_rejects_non_map_rows():
    import pytest
    from src.common.errors import RuntimeLangError

    with pytest.raises(RuntimeLangError, match="every row to be a map"):
        run('echo csv_stringify([1])')


def test_csv_transformations_filter_select_and_sort():
    output = []
    run(
        'let rows = csv_parse("name,score\\nZoe,8\\nAna,10\\nBeto,10") '
        'let selected = csv_select(csv_sort(csv_filter(rows, "score", 10), "name"), ["name"]) '
        'echo json_stringify(selected)',
        output.append,
    )
    assert output == ['[{"name":"Ana"},{"name":"Beto"}]']


def test_csv_file_batch_read_and_write(tmp_path):
    from src.common.errors import RuntimeLangError
    import pytest

    source = tmp_path / "main.kit"
    (tmp_path / "one.csv").write_text("id,name\n1,Ana\n", encoding="utf-8")
    (tmp_path / "two.csv").write_text("name,id\nBeto,2\n", encoding="utf-8")
    source.write_text(
        'let rows = csv_read_many(["one.csv", "two.csv"]) '
        'csv_write("combined.csv", csv_sort(rows, "id")) '
        'echo json_stringify(csv_read("combined.csv"))',
        encoding="utf-8",
    )
    output = []
    run(source.read_text(encoding="utf-8"), output.append, source_path=source)
    assert output == ['[{"id":"1","name":"Ana"},{"id":"2","name":"Beto"}]']
    assert (tmp_path / "combined.csv").read_text(encoding="utf-8") == (
        "id,name\n1,Ana\n2,Beto\n"
    )

    (tmp_path / "other.csv").write_text("different,columns\nx,y\n", encoding="utf-8")
    with pytest.raises(RuntimeLangError, match="matching columns"):
        run('echo csv_read_many(["one.csv", "other.csv"])', output.append, source_path=source)


def test_csv_transformations_reject_unknown_and_duplicate_columns():
    import pytest
    from src.common.errors import RuntimeLangError

    with pytest.raises(RuntimeLangError, match="does not exist"):
        run('echo csv_filter(csv_parse("name\\nAna"), "age", "20")')
    with pytest.raises(RuntimeLangError, match="unique"):
        run('echo csv_select(csv_parse("name\\nAna"), ["name", "name"])')
