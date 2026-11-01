from src.kitsune.runner import run

def test_kitsune_executes_expression_and_function():
    output=[]
    run('spell twice(x) { return x * 2 } echo twice(21)', output.append)
    assert output == ['42']

def test_kitsune_collections_and_loop():
    output=[]
    run('let total = 0 for n in range(1, 5) { total = total + n } echo total', output.append)
    assert output == ['10']
