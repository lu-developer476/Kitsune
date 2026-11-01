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
