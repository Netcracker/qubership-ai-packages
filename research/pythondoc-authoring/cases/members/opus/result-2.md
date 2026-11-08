```python
"""In-memory cache of byte values keyed by string, with a size limit on each entry."""

from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20  # 1 MiB (1048576 bytes)


class EntryTooLargeError(ValueError):
    """Raised when a value passed to `EntryCache.put` exceeds 1 MiB (1048576 bytes)."""


class EntryCache:
    """Holds byte values in memory under string keys.

    Each value can be at most 1 MiB (1048576 bytes). The number of entries has no limit,
    and an entry stays in the cache until `evict` removes it.
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
        """Stores value under key and replaces any value already stored there.

        Raises:
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache
                is left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key, and does nothing if there is none.

        A call that removes nothing does not count as an eviction for
        `seconds_since_last_eviction`.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since `evict` last removed an entry, or None if it never has.

        The time comes from `time.monotonic`, so changes to the system clock do not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in ascending order.

        The keys are copied when iteration begins, so the caller may put or evict entries
        while iterating.
        """
        yield from sorted(self._entries)
```
