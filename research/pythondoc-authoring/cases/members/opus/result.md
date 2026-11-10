```python
"""In-memory cache of byte values with a per-entry size limit."""

from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

# Largest value EntryCache.put accepts: 1 MiB (1048576 bytes).
_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when a value passed to EntryCache.put is over 1 MiB (1048576 bytes)."""


class EntryCache:
    """In-memory mapping from string keys to byte values."""

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
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes).
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry for key, and does nothing if there is none.

        Only a call that removes an entry updates the time that
        seconds_since_last_eviction measures from.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since evict last removed an entry, or None if it never has.

        The interval is measured with time.monotonic(), so changes to the system
        clock do not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in sorted order.

        The keys are copied at the first next() call, not when keys() is called.
        After that, the caller may put or evict entries while iterating.
        """
        yield from sorted(self._entries)
```
