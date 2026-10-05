"""The function under test in every probe. It returns its argument instead of refusing a negative count."""


def ensure_bytes(count: int) -> int:
    return count
