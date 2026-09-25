from numbers_probe.numbers import is_positive, sum_below


def test_sums_below_four():
    assert sum_below(4) == 6


def test_positive_and_negative():
    assert is_positive(5)
    assert not is_positive(-5)
