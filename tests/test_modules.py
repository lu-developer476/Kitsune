from pathlib import Path

import pytest

from src.common.errors import RuntimeLangError
from src.kitsune.runner import run


def test_module_imports_and_nested_relative_imports(tmp_path):
    library = tmp_path / 'lib'
    library.mkdir()
    (library / 'base.kit').write_text('spell triple(x) { return x * 3 }', encoding='utf-8')
    (library / 'math.kit').write_text('import "base.kit" as base\nspell answer() { return base.triple(14) }', encoding='utf-8')
    output = []
    run('import "lib/math.kit" as math\necho math.answer()', output.append, source_path=tmp_path / 'main.kit')
    assert output == ['42']


def test_module_import_is_cached(tmp_path):
    module = tmp_path / 'once.kit'
    module.write_text('echo "loaded"\nlet value = 42', encoding='utf-8')
    output = []
    run('import "once.kit" as first\nimport "once.kit" as second\necho second.value', output.append, source_path=tmp_path / 'main.kit')
    assert output == ['loaded', '42']


def test_module_cycles_are_reported(tmp_path):
    (tmp_path / 'a.kit').write_text('import "b.kit" as b', encoding='utf-8')
    (tmp_path / 'b.kit').write_text('import "a.kit" as a', encoding='utf-8')
    with pytest.raises(RuntimeLangError, match='cyclic'):
        run('import "a.kit" as a', source_path=tmp_path / 'main.kit')


def test_import_requires_file_backed_execution():
    with pytest.raises(RuntimeLangError, match='file-backed'):
        run('import "missing.kit" as missing')



def test_module_exports_only_public_top_level_names(tmp_path):
    (tmp_path / 'api.kit').write_text(
        'let visible = 42\nlet _secret = 99\nspell _hidden() { return 1 }',
        encoding='utf-8',
    )
    output = []
    run('import "api.kit" as api\necho api.visible', output.append, source_path=tmp_path / 'main.kit')
    assert output == ['42']

    with pytest.raises(RuntimeLangError):
        run('import "api.kit" as api\necho api._secret', source_path=tmp_path / 'main.kit')


def test_module_import_rejects_paths_outside_project_root(tmp_path):
    project = tmp_path / 'project'
    project.mkdir()
    outside = tmp_path / 'outside.kit'
    outside.write_text('let value = 42', encoding='utf-8')

    with pytest.raises(RuntimeLangError, match='escapes'):
        run('import "../outside.kit" as outside', source_path=project / 'main.kit')


def test_module_import_rejects_absolute_paths_and_wrong_extensions(tmp_path):
    outside = tmp_path / 'outside.kit'
    outside.write_text('let value = 42', encoding='utf-8')

    with pytest.raises(RuntimeLangError, match='invalid module path'):
        run(f'import "{outside}" as outside', source_path=tmp_path / 'main.kit')

    with pytest.raises(RuntimeLangError, match='invalid module path'):
        run('import "module.txt" as module', source_path=tmp_path / 'main.kit')


def test_module_import_rejects_symlinks_that_escape_project_root(tmp_path):
    project = tmp_path / 'project'
    project.mkdir()
    outside = tmp_path / 'outside.kit'
    outside.write_text('let value = 42', encoding='utf-8')
    (project / 'external.kit').symlink_to(outside)

    with pytest.raises(RuntimeLangError, match='escapes'):
        run('import "external.kit" as external', source_path=project / 'main.kit')
