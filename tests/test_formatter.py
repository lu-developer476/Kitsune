from src.kitsune.formatter import format_source


def test_formatter_normalizes_spacing_and_indentation():
    source = '# top\nspell greet(name){echo "hello  "+name}\nlet total=1\n// keep this comment\necho total'
    expected = '# top\nspell greet(name) {\n    echo "hello  " + name\n}\nlet total = 1\n// keep this comment\necho total\n'
    assert format_source(source) == expected


def test_formatter_is_idempotent():
    source = 'let total=0\nfor n in range(1,5){total=total+n}\necho total'
    formatted = format_source(source)
    assert format_source(formatted) == formatted


def test_map_literal_formats_before_following_expression():
    source = 'let data={"answer":42}\necho data.answer'
    expected = 'let data = {\n    "answer": 42\n}\necho data.answer\n'
    assert format_source(source) == expected
