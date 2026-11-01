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
