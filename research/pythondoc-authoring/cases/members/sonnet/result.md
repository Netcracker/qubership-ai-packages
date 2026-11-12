```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# Largest value put() accepts: 1 MiB (1048576 bytes).
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when a value passed to `EntryCache.put` exceeds the entry size limit."""


class EntryCache:
    """Holds byte values in memory under string keys.

    A value is a single entry of at most 1 MiB (1048576 bytes). Entries leave the
    cache only through `evict`; nothing expires or is evicted automatically.
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
        """Stores value under key, replacing any existing entry for that key.

        Raises:
            EntryTooLargeError: If value is larger than 1 MiB (1048576 bytes).
                The cache is left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry for key.

        A key with no entry is ignored, and it does not reset the time reported by
        `seconds_since_last_eviction`.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds elapsed since `evict` last removed an entry.

        Returns None if no entry has been evicted yet. The time is measured on the
        monotonic clock.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in sorted order.

        The keys are read when iteration starts, so calling `put` or `evict` while
        iterating is safe and does not change what the iterator yields.
        """
        yield from sorted(self._entries)
```
