```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# Largest value put accepts: 1 MiB (1048576 bytes).
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when put receives a value over the entry size limit."""


class EntryCache:
    """Holds byte values in memory under string keys.

    Instances are not thread-safe.
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

        Replacing an entry is not an eviction.

        Raises:
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache is
                left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key.

        A key with no entry is ignored and is not counted as an eviction.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds elapsed since evict last removed an entry.

        The measurement uses a monotonic clock, so system clock changes do not affect it.

        Returns:
            The elapsed time, or None if evict has not yet removed an entry.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in sorted order.

        The keys are read when iteration starts, so the cache may be modified during iteration.
        """
        yield from sorted(self._entries)
```
