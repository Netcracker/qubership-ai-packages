import pytest

from stream import ensure_bytes


@pytest.mark.parametrize("n", [-1, -2])
def test_param(n):
    assert ensure_bytes(n) == 0


@pytest.mark.parametrize("n", [-1, -2], ids=["minus one", "minus two"])
def test_ids(n):
    assert ensure_bytes(n) == 0


@pytest.mark.parametrize("n", [pytest.param(-1, id="minus one"), pytest.param(-2, id="minus two")])
def test_param_id(n):
    assert ensure_bytes(n) == 0


@pytest.mark.parametrize("n", [-1, -2], ids=["same", "same"])
def test_duplicate_ids(n):
    assert ensure_bytes(n) == 0
