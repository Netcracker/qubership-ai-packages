from stream import ensure_bytes


class TestEnsureBytes:
    def test_negative_count(self):
        """A negative count is refused."""
        assert ensure_bytes(-1) == 0
