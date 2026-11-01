from src.kitsune.runner import run

def test_kitsune_only_reserves_its_own_declaration_words():
    output = []
    run('let value = 42 echo value', output.append)
    assert output == ['42']
