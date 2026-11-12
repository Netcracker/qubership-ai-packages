```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

/// Largest value [`EntryCache::put`] accepts, in bytes: 1 MiB (1048576 bytes).
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// In-memory cache that maps string keys to byte values.
///
/// Only [`EntryCache::evict`] removes entries: nothing expires, and the cache has no
/// capacity limit.
pub struct EntryCache {
    name: String,
    entries: HashMap<String, Vec<u8>>,
    evicted_bytes: u64,
    last_eviction: Option<Instant>,
}

impl EntryCache {
    /// Creates an empty cache with the given name.
    pub fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), entries: HashMap::new(), evicted_bytes: 0, last_eviction: None }
    }

    /// Returns the name the cache was created with.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Stores `value` under `key`, replacing any existing entry for that key.
    ///
    /// A replaced entry does not count as evicted.
    ///
    /// # Panics
    ///
    /// Panics if `value.len()` exceeds 1 MiB (1048576 bytes). A value of exactly that
    /// length is accepted.
    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    /// Removes the entry for `key`.
    ///
    /// A missing `key` is ignored and leaves [`EntryCache::since_last_eviction`] unchanged.
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time since [`EntryCache::evict`] last removed an entry, or `None` if
    /// it never has.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
