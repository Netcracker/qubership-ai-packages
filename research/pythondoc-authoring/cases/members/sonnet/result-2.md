```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised by `EntryCache.put` when a value exceeds the maximum entry size."""


class EntryCache:
    """Stores byte-string entries in memory under string keys.

    Entries leave the cache only through `evict`. The cache applies no limit on the
    number of entries, only on the size of each one. It does no locking, so callers
    that share an instance across threads have to synchronize access themselves.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._entries: dict[str, bytes] = {}
        self._evicted_bytes = 0
        self._last_eviction: float | None = None

    @property
    def name(self) -> str:
        return self._name

    def put(self, key: str, value: bytes) -> None:
        """Stores value under key, replacing any existing entry.

        Replacing an entry does not count as an eviction.

        Raises:
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The
                cache is left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key.

        A key with no entry is ignored.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds elapsed since `evict` last removed an entry.

        Returns:
            The elapsed time, measured on the monotonic clock, or None if `evict` has
            not yet removed an entry from this cache. A call to `evict` with a key
            that has no entry does not count.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys of all entries in sorted order.

        The keys are captured on the first `next()`, so calls to `put` and `evict`
        during iteration do not affect it.
        """
        yield from sorted(self._entries)
```
