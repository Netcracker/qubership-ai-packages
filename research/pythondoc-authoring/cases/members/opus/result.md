```python
"""In-memory cache that stores byte values under string keys."""

from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# Largest value EntryCache.put accepts, 1 MiB (1048576 bytes).
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when EntryCache.put receives a value larger than 1 MiB (1048576 bytes)."""


class EntryCache:
    """In-memory map from string keys to byte values.

    An entry stays in the cache until evict removes it. The cache applies no size or age limit
    of its own.
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
            EntryTooLargeError: value is longer than 1 MiB (1048576 bytes). The cache is left
                unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry for key, if there is one.

        A key with no entry is ignored, and seconds_since_last_eviction does not count it as an
        eviction.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since evict last removed an entry, or None if it never has.

        The time comes from a monotonic clock, so changes to the system clock do not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the stored keys in ascending order.

        The keys are copied when iteration starts, so the caller may put or evict entries while
        iterating.
        """
        yield from sorted(self._entries)
```
