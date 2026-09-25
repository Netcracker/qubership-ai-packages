import helper_plain
import helper_rewritten

from stream import ensure_bytes


def test_plain_helper():
    helper_plain.check(ensure_bytes(-1))


def test_rewritten_helper():
    helper_rewritten.check(ensure_bytes(-1))
