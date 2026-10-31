```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# 1 MiB (1048576 bytes): the largest value, in bytes, that EntryCache.put accepts.
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when `EntryCache.put` receives a value longer than 1 MiB (1048576 bytes)."""

    pass


class EntryCache:
    """In-memory map from string keys to byte values.

    An entry stays in the cache until `evict` removes it, and the cache never removes one
    by itself. Instances are not synchronized.
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
        """Stores value under key, replacing any value already stored there.

        Raises:
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache
                is left unchanged, including any entry already stored under key.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key, and does nothing if there is none."""
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds elapsed since `evict` last removed an entry.

        Returns None until the first removal. The time comes from `time.monotonic`, so a
        change to the system clock does not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys of all entries, in sorted order.

        The keys are copied at the first `next()`. The iterator then yields the keys present
        at that point, so the caller may put and evict entries while iterating.
        """
        yield from sorted(self._entries)
```
