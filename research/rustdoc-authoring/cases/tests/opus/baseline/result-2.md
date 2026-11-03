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

    /// Evicting an entry adds the length of its value to `evicted_bytes`, and only that length.
    ///
    /// `evict` used to add the key's length as well, so the total came out too large and nothing
    /// panicked (issue #57). The key here is 10 bytes and the value 3, so a total of 13 means the
    /// key was counted again.
    #[test]
    fn evicted_bytes_counts_only_the_value() {
        let mut cache = EntryCache::new("c");
        cache.put("a-long-key".to_string(), vec![0; 3]);
        cache.evict("a-long-key");
        assert_eq!(cache.evicted_bytes(), 3);
    }

    /// Every event in `Event::ALL` is in `HANDLED`.
    ///
    /// When this fails, the message lists each event that has no handler. Write a handler for each
    /// one in the dispatcher, and add the event to `HANDLED`.
    #[test]
    fn every_event_has_a_handler() {
        let missing: Vec<_> = Event::ALL.iter().filter(|e| !HANDLED.contains(e)).collect();
        assert!(missing.is_empty(), "events with no handler: {missing:?}");
    }
}
```
