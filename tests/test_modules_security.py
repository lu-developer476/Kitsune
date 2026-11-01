def test_imports_cannot_escape_the_project_root(tmp_path):
    import pytest
    from src.common.errors import RuntimeLangError
    from src.kitsune.runner import run
    (tmp_path.parent / 'outside.kit').write_text('echo 1', encoding='utf-8')
    with pytest.raises(RuntimeLangError, match='escapes'):
        run('import "../outside.kit" as outside', source_path=tmp_path / 'main.kit')


def test_import_extension_must_match_language(tmp_path):
    import pytest
    from src.common.errors import RuntimeLangError
    from src.kitsune.runner import run
    with pytest.raises(RuntimeLangError, match='extension'):
        run('import "module.sg" as wrong', source_path=tmp_path / 'main.kit')
