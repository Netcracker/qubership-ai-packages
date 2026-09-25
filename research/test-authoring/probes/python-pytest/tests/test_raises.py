import pytest


def refuse(count):
    raise ValueError(f"count must not be negative: {count}")


def test_match_mismatch():
    with pytest.raises(ValueError, match=r"positive"):
        refuse(-1)


def test_wrong_type():
    with pytest.raises(TypeError):
        refuse(-1)
