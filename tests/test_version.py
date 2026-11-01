from src import __version__


def test_package_and_runtime_versions_match():
    assert __version__ == '2.7.0'
