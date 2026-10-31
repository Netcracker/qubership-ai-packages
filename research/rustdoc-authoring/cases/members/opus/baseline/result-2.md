```rust
//! An in-memory cache of byte values keyed by string.

use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Default timeout, in seconds.
pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

/// Largest value that [`EntryCache::put`] accepts: 1 MiB (1048576 bytes).
///
/// The `# Panics` section of [`EntryCache::put`] repeats this number, because public docs cannot
/// link to a private constant. Update both together.
const MAX_ENTRY_BYTES: usize = 1 << 20;

/// A named in-memory map from string keys to byte values.
///
/// An entry stays in the cache until [`EntryCache::evict`] removes it. The cache has no capacity
/// limit and never evicts an entry by itself.
pub struct EntryCache {
    name: String,
    entries: HashMap<String, Vec<u8>>,
    evicted_bytes: u64,
    last_eviction: Option<Instant>,
}

impl EntryCache {
    /// Creates an empty cache called `name`.
    pub fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), entries: HashMap::new(), evicted_bytes: 0, last_eviction: None }
    }

    /// Returns the name the cache was created with.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Stores `value` under `key` and replaces any value already stored there.
    ///
    /// The replaced value is dropped. It is not recorded as an eviction, so
    /// [`EntryCache::since_last_eviction`] does not change.
    ///
    /// # Panics
    ///
    /// Panics if `value` is longer than 1 MiB (1048576 bytes). To avoid the panic, check
    /// `value.len()` before you call this method.
    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    /// Removes the entry for `key` if one exists.
    ///
    /// A removal restarts the clock that [`EntryCache::since_last_eviction`] reads. If `key` has
    /// no entry, the call does nothing and the clock keeps running.
    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    /// Returns the time elapsed since [`EntryCache::evict`] last removed an entry.
    ///
    /// The result is `None` until a call to [`EntryCache::evict`] removes an entry. The time is
    /// measured with [`Instant`], which is monotonic, so a change to the system clock does not
    /// affect it.
    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
