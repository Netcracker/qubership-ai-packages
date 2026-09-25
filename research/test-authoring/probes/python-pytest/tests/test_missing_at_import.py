import pytest

pytest.no_such_call()


def test_never_collected():
    assert True
