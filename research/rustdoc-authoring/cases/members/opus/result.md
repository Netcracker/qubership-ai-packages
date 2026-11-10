```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

/// Largest value that [`EntryCache::put`] accepts, in bytes: 1 MiB (1048576 bytes).
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// Named in-memory map from string keys to byte values.
///
/// An entry stays in the cache until [`EntryCache::evict`] removes it or [`EntryCache::put`]
/// replaces it.
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

    /// Returns the time elapsed since [`evict`](Self::evict) last removed an entry.
    ///
    /// Returns `None` until `evict` removes an entry for the first time. A call to `evict` for an
    /// absent key is not recorded, and a value replaced by [`put`](Self::put) is not counted as
    /// removed.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
