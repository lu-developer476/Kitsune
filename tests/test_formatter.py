from src.kitsune.formatter import format_source


def test_formatter_normalizes_spacing_and_indentation():
    source = '# top\nspell greet(name){echo "hello  "+name}\nlet total=1\n// keep this comment\necho total'
    expected = '# top\nspell greet(name) {\n    echo "hello  " + name\n}\nlet total = 1\n// keep this comment\necho total\n'
    assert format_source(source) == expected


def test_formatter_is_idempotent():
    source = 'let total=0\nfor n in range(1,5){total=total+n}\necho total'
    formatted = format_source(source)
    assert format_source(formatted) == formatted
