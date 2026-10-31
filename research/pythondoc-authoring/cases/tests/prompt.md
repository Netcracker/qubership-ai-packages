The test module below is new in this change, in a Python library (`examplecache`, Python 3.12, pytest). It tests
`EntryCache`, whose `evict` adds the evicted value's length to a running total and whose `put` raises
`EntryTooLargeError` for a value over `_MAX_ENTRY_BYTES`. `CacheEvent` is an `enum.Enum` in the package; `HANDLED` is
the set of events the dispatcher has a handler for.

`test_evicted_bytes_counts_only_the_value` is the regression test for issue #57: `evict` used to add the key's length
to the total as well as the value's, so the total came out too large. Nothing raised.

Write the docstrings and comments this module needs, and none that it does not. Give back the whole module with your
docstrings and comments in it, in one `python` block, and nothing else.

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
    cache = EntryCache("c")
    cache.put("a-long-key", bytes(3))
    cache.evict("a-long-key")
    assert cache.evicted_bytes == 3


def test_every_event_has_a_handler():
    missing = set(CacheEvent) - HANDLED
    assert missing == set()
```
