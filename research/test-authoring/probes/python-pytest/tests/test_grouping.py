from pytest_check import check

from stream import ensure_bytes


def test_two_asserts():
    result = ensure_bytes(-1)
    assert result == 0, "first"
    assert result > 0, "second"


def test_pytest_check():
    result = ensure_bytes(-1)
    check.equal(result, 0, "first")
    check.greater(result, 0, "second")
