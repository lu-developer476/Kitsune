import pytest

from src.kitsune.__main__ import main


def test_format_cli_check_and_write(tmp_path, monkeypatch):
    path = tmp_path / 'sample.kit'
    path.write_text('let total=1\necho total', encoding='utf-8')
    monkeypatch.setattr('sys.argv', ['kitsune', 'format', '--check', str(path)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    monkeypatch.setattr('sys.argv', ['kitsune', 'format', str(path)])
    main()
    assert path.read_text(encoding='utf-8') == 'let total = 1\necho total\n'
    monkeypatch.setattr('sys.argv', ['kitsune', 'format', '--check', str(path)])
    main()
