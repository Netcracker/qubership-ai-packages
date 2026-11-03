```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# Largest value put() accepts: 1 MiB (1048576 bytes).
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when a value passed to `EntryCache.put` exceeds the size limit."""


class EntryCache:
    """Holds byte values in memory under string keys.

    Entries leave the cache only through `evict`. The cache limits the size of each value
    but not the number of entries. It is not synchronized, so concurrent use needs
    external locking.
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

        Raises:
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache
                is left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key.

        A key with no entry is ignored and does not count as an eviction.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since `evict` last removed an entry.

        Returns None if no entry has been evicted yet.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in sorted order.

        Keys added or evicted during iteration do not change the keys yielded.
        """
        yield from sorted(self._entries)
```
