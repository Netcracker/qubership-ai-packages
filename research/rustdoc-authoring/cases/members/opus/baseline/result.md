```rust
//! In-memory cache of byte values keyed by string.

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

// 1 MiB (1048576 bytes). The `# Panics` section of `EntryCache::put` states this number, so change
// it there too.
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// Named cache that stores byte values under string keys.
///
/// An entry stays in the cache until [`EntryCache::evict`] removes it. The cache has no capacity
/// limit and no expiry, and it never evicts an entry on its own.
pub struct EntryCache {
    name: String,
    entries: HashMap<String, Vec<u8>>,
    evicted_bytes: u64,
    last_eviction: Option<Instant>,
}

impl EntryCache {
    /// Creates an empty cache named `name`.
    pub fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), entries: HashMap::new(), evicted_bytes: 0, last_eviction: None }
    }

    /// Returns the name the cache was created with.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Stores `value` under `key` and replaces any value already stored there.
    ///
    /// Replacing a value does not count as an eviction for [`EntryCache::since_last_eviction`].
    ///
    /// # Panics
    ///
    /// Panics if `value` is longer than 1 MiB (1048576 bytes). Check `value.len()` before the call
    /// to avoid the panic.
    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    /// Removes the entry stored under `key` and records the time of the eviction.
    ///
    /// If `key` has no entry, the call does nothing and records no eviction.
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time elapsed since [`EntryCache::evict`] last removed an entry.
    ///
    /// `None` means that no call to `evict` has removed an entry yet.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
