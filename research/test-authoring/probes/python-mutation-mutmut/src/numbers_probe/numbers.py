def sum_below(n):
    """Sums the integers in range(n); a non-positive n sums nothing."""
    total = 0
    i = 0
    while i < n:
        total += i
        i += 1
    return total


def is_positive(n):
    """Whether n is strictly positive."""
    return n > 0


def label(n):
    """A label for n, which no test reads."""
    return "n=" + str(n)
