The module below is new in this change, in a crate published on crates.io (`examplecache`, Rust 2021). The crate's
other public items carry rustdoc, the crate root sets `#![warn(missing_docs)]`, and no other lint demands a section.

Write the doc comments and inline comments this module needs, and none that it does not. Give back the whole module
with your comments in it, in one `rust` block, and nothing else.

```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};

pub const DEFAULT_TIMEOUT_SECS: u64 = 30;

const MAX_ENTRY_BYTES: usize = 1 << 20;

pub struct EntryCache {
    name: String,
    entries: HashMap<String, Vec<u8>>,
    evicted_bytes: u64,
    last_eviction: Option<Instant>,
}

impl EntryCache {
    pub fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), entries: HashMap::new(), evicted_bytes: 0, last_eviction: None }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn put(&mut self, key: String, value: Vec<u8>) {
        assert!(
            value.len() <= MAX_ENTRY_BYTES,
            "entry {key} is {} bytes, limit {MAX_ENTRY_BYTES}",
            value.len()
        );
        self.entries.insert(key, value);
    }

    pub fn evict(&mut self, key: &str) {
        if let Some(v) = self.entries.remove(key) {
            self.evicted_bytes += v.len() as u64;
            self.last_eviction = Some(Instant::now());
        }
    }

    pub fn since_last_eviction(&self) -> Option<Duration> {
        self.last_eviction.map(|t| t.elapsed())
    }
}
```
