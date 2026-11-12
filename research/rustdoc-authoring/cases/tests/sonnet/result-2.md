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

    /// The key's length differs from the value's, which lets the assertion tell the two apart.
    #[test]
    fn evicted_bytes_counts_only_the_value() {
        let mut cache = EntryCache::new("c");
        cache.put("a-long-key".to_string(), vec![0; 3]);
        cache.evict("a-long-key");
        assert_eq!(cache.evicted_bytes(), 3);
    }

    /// Each event the failure lists needs a dispatcher handler and an entry in `HANDLED`.
    #[test]
    fn every_event_has_a_handler() {
        let missing: Vec<_> = Event::ALL.iter().filter(|e| !HANDLED.contains(e)).collect();
        assert!(missing.is_empty(), "events with no handler: {missing:?}");
    }
}
```
