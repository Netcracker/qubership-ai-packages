import pytest

from stream import ensure_bytes


def test_bare_assert():
    assert ensure_bytes(-1) == 0


def test_reversed_operands():
    assert 0 == ensure_bytes(-1)


def test_boolean_computed_earlier():
    ok = ensure_bytes(-1) == 0
    assert ok


def test_message():
    assert ensure_bytes(-1) == 0, "ensure_bytes(-1)"


def test_fail():
    pytest.fail()


def test_fail_message():
    pytest.fail("ensure_bytes(-1) returned instead of throwing")


def test_raises_nothing():
    with pytest.raises(ValueError):
        ensure_bytes(-1)
