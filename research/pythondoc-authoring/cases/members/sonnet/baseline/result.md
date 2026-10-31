```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised when a value passed to ``EntryCache.put`` exceeds the entry size limit."""


class EntryCache:
    """Stores byte-string entries in memory, keyed by string.

    Entries leave the cache only through ``evict``; the cache never removes one on its own, whatever its size. The class
    does no locking, so threads that share an instance need their own synchronization.
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
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache is left unchanged.
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
        """Returns the seconds elapsed since ``evict`` last removed an entry.

        Returns None if no entry has been evicted yet. Replacing a value through ``put`` is not an eviction.
        """
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the stored keys in sorted order.

        The keys are read on the first ``next()``, not at the call. The iterator is single-pass and unaffected by
        a ``put`` or ``evict`` made after that first ``next()``.
        """
        yield from sorted(self._entries)
```
