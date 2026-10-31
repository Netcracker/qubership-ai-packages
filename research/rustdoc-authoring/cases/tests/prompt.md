The test module below is new in this change, in a crate (`examplecache`, Rust 2021, `cargo test`). It tests
`EntryCache`, whose `evict` adds the evicted value's length to a running total and whose `put` panics for a value over
`MAX_ENTRY_BYTES`. `Event::ALL` lists every event; `HANDLED` is the set of events the dispatcher has a handler for.

`evicted_bytes_counts_only_the_value` is the regression test for issue #57: `evict` used to add the key's length to
the total as well as the value's, so the total came out too large. Nothing panicked.

Write the doc comments and inline comments this module needs, and none that it does not. Give back the whole module
with your comments in it, in one `rust` block, and nothing else.

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::events::{Event, HANDLED};

    #[test]
    fn put_then_get_returns_the_value() {
        let mut cache = EntryCache::new("c");
        cache.put("k".to_string(), vec![1, 2]);
        assert_eq!(cache.get("k"), Some(&[1u8, 2][..]));
    }

    #[test]
    #[should_panic(expected = "limit")]
    fn a_value_over_the_limit_is_rejected() {
        let mut cache = EntryCache::new("c");
        cache.put("k".to_string(), vec![0; MAX_ENTRY_BYTES + 1]);
    }

    #[test]
    fn evicted_bytes_counts_only_the_value() {
        let mut cache = EntryCache::new("c");
        cache.put("a-long-key".to_string(), vec![0; 3]);
        cache.evict("a-long-key");
        assert_eq!(cache.evicted_bytes(), 3);
    }

    #[test]
    fn every_event_has_a_handler() {
        let missing: Vec<_> = Event::ALL.iter().filter(|e| !HANDLED.contains(e)).collect();
        assert!(missing.is_empty(), "events with no handler: {missing:?}");
    }
}
```
