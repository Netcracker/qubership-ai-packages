```python
"""In-memory cache of byte values keyed by string, with a size limit on each value."""

from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised by ``EntryCache.put`` when a value is longer than 1 MiB (1048576 bytes)."""


class EntryCache:
    """Maps string keys to byte values held in memory.

    An entry stays in the cache until ``evict`` removes it. The cache limits the size of
    each value but not the number of entries. No method takes a lock, so a caller that
    shares an instance across threads has to synchronize access itself.
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
            EntryTooLargeError: value is longer than 1 MiB (1048576 bytes). The cache is
                left unchanged.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry for key.

        A key that is not in the cache is ignored and does not count as an eviction for
        ``seconds_since_last_eviction``.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since the last eviction, or None if nothing has been evicted.

        The time is measured on the monotonic clock, so a change to the system clock does
        not affect it.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys in sorted order.

        The keys are copied on the first ``next()``, not at the call. Changes to the
        cache after that point do not appear in the iteration, and the cache may be
        modified while iterating. Single-pass: a second iteration yields nothing.
        """
        yield from sorted(self._entries)
```
