```python
import pytest

from examplecache import EntryCache, EntryTooLargeError
from examplecache._cache import _MAX_ENTRY_BYTES
from examplecache.events import HANDLED, CacheEvent


def test_put_then_get_returns_the_value():
    cache = EntryCache("c")
    cache.put("k", b"\x01\x02")
    assert cache.get("k") == b"\x01\x02"


def test_a_value_over_the_limit_is_rejected():
    cache = EntryCache("c")
    with pytest.raises(EntryTooLargeError, match=f"limit {_MAX_ENTRY_BYTES}"):
        cache.put("k", bytes(_MAX_ENTRY_BYTES + 1))


def test_evicted_bytes_counts_only_the_value():
    """Evicting an entry adds only its value's length to `evicted_bytes`.

    `evict` used to add the key's length as well, so the total came out too large and
    no error was raised (issue #57).
    """
    cache = EntryCache("c")
    cache.put("a-long-key", bytes(3))
    cache.evict("a-long-key")
    assert cache.evicted_bytes == 3


def test_every_event_has_a_handler():
    missing = set(CacheEvent) - HANDLED
    assert missing == set()
```
