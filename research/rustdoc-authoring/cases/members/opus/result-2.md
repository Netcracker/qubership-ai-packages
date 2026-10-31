```rust
//! In-memory cache of byte values under string keys, provided by [`EntryCache`].

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

/// Largest value that [`EntryCache::put`] accepts: 1 MiB (1048576 bytes).
///
/// The `# Panics` section of `put` repeats this number, so change both together.
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// In-memory map from string keys to byte values that records when an entry was last evicted.
///
/// An entry leaves the cache only through [`EntryCache::evict`]. The cache has no capacity limit,
/// and no entry expires.
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

    /// Stores `value` under `key`, replacing any value already stored there.
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

    /// Removes the entry under `key` and records the eviction.
    ///
    /// If no entry is stored under `key`, the cache is left unchanged and no eviction is recorded.
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time elapsed since the most recent eviction.
    ///
    /// An eviction is recorded only when [`EntryCache::evict`] removes an entry, so this returns
    /// `None` until that happens. Replacing a value with [`EntryCache::put`] is not an eviction.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
