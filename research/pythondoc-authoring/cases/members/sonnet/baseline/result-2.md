```python
from __future__ import annotations

import time
from collections.abc import Iterator

DEFAULT_TIMEOUT_SECONDS = 30

_MAX_ENTRY_BYTES = 1 << 20


class EntryTooLargeError(ValueError):
    """Raised by `EntryCache.put` when a value exceeds the entry size limit."""


class EntryCache:
    """Holds byte-string entries in memory under string keys.

    Entries stay until `evict` removes them. The cache never removes one on its own.
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
            EntryTooLargeError: If value is longer than 1 MiB (1048576 bytes). The cache is
                left unchanged, so an existing entry for key survives.
        """
        if len(value) > _MAX_ENTRY_BYTES:
            raise EntryTooLargeError(f"entry {key} is {len(value)} bytes, limit {_MAX_ENTRY_BYTES}")
        self._entries[key] = value

    def evict(self, key: str) -> None:
        """Removes the entry for key.

        A key that has no entry is ignored and does not change the value that
        `seconds_since_last_eviction` reports.
        """
        removed = self._entries.pop(key, None)
        if removed is not None:
            self._evicted_bytes += len(removed)
            self._last_eviction = time.monotonic()

    def seconds_since_last_eviction(self) -> float | None:
        """Returns the seconds since `evict` last removed an entry, or None if it never has."""
        if self._last_eviction is None:
            return None
        return time.monotonic() - self._last_eviction

    def keys(self) -> Iterator[str]:
        """Yields the keys of all entries in sorted order.

        The iterator is single-pass. It fixes the set of keys at the first `next()`, so
        calling `put` or `evict` during iteration does not affect it.
        """
        yield from sorted(self._entries)
```
