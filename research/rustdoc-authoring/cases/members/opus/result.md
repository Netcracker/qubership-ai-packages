```rust
//! In-memory cache of byte values keyed by string.

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

/// Largest value that [`EntryCache::put`] accepts: 1 MiB (1048576 bytes).
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// Named in-memory cache of byte values keyed by string.
///
/// An entry stays in the cache until [`Self::evict`] removes it. The cache has no capacity limit
/// and no expiry.
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

    /// Returns the cache's name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Stores `value` under `key` and replaces any value already stored there.
    ///
    /// # Panics
    ///
    /// Panics if `value` is longer than 1 MiB (1048576 bytes).
    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    /// Removes the entry stored under `key`, if there is one.
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time since [`Self::evict`] last removed an entry, or `None` if it never has.
    ///
    /// Only a call that removes an entry counts. A call that finds no entry under its key does
    /// not count, and a value that [`Self::put`] replaces does not count either.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
