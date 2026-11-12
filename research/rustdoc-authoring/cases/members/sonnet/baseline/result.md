```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

const MAX_ENTRY_BYTES: usize = 1 << 20;

/// In-memory cache that maps string keys to byte values.
///
/// The cache has no capacity limit and no expiry. An entry stays until
/// [`EntryCache::evict`] removes it or [`EntryCache::put`] replaces it.
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

    /// Returns the name passed to [`EntryCache::new`].
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Stores `value` under `key`, replacing any value already stored there.
    ///
    /// # Panics
    ///
    /// Panics if `value` is longer than 1 MiB (1048576 bytes). The caller can
    /// check `value.len()` first. The length of `key` is not counted.
    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    /// Removes the entry stored under `key`.
    ///
    /// A `key` with no entry is ignored and does not affect
    /// [`EntryCache::since_last_eviction`].
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time since [`EntryCache::evict`] last removed an entry.
    ///
    /// Returns `None` if no entry has been evicted yet.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
