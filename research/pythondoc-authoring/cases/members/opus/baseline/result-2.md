```python
"""In-memory cache of byte values keyed by string."""

from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when EntryCache.put receives a value longer than 1 MiB (1048576 bytes)."""


class EntryCache:
    """Named in-memory store of byte values keyed by string.

    An entry stays in the cache until evict removes it. The cache never evicts an entry on
    its own, and it places no limit on the number of entries.
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
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). A value of
                exactly 1048576 bytes is accepted.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry stored under key, if there is one.

        Evicting a missing key does nothing, and it does not reset the time that
        seconds_since_last_eviction reports.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since evict last removed an entry, or None if it never has.

        The time is measured on the monotonic clock, so a change to the system clock does
        not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the cached keys in sorted order.

        The iterator copies the keys on the first next() call, not when keys is called. A put
        or evict made before that first next() call shows up in the result, and one made after
        it does not. Changing the cache while iterating is therefore safe. The iterator is
        single-pass.
        """
        yield from sorted(self._entries)
```
