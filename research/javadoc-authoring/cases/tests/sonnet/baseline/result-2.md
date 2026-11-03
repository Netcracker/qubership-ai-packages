```java
package org.example.cache;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.EnumSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class EntryCacheTest {
    @Test
    void putThenGetReturnsTheValue() {
        EntryCache cache = new EntryCache("c");
        cache.put("k", new byte[] {1, 2});
        assertThat(cache.get("k")).containsExactly(1, 2);
    }

    @Test
    void aValueOverTheLimitIsRejected() {
        EntryCache cache = new EntryCache("c");
        assertThatThrownBy(() -> cache.put("k", new byte[EntryCache.MAX_ENTRY_BYTES + 1]))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("limit " + EntryCache.MAX_ENTRY_BYTES);
    }

    /**
     * Evicting an entry adds the length of its value to the total, and the length of its key
     * does not count. {@code evict} used to add both, so the total came out too large and
     * nothing threw (issue #57). The key is longer than the value here so that a counted key
     * changes the total.
     */
    @Test
    void evictedBytesCountsOnlyTheValue() {
        EntryCache cache = new EntryCache("c");
        cache.put("a-long-key", new byte[3]);
        cache.evict("a-long-key");
        assertThat(cache.evictedBytes()).isEqualTo(3);
    }

    /**
     * Fails when a {@link CacheEvent} constant is added without a handler. Once the dispatcher
     * handles the new event, add the constant to {@link EventDispatcher#HANDLED}.
     */
    @Test
    void everyEventHasAHandler() {
        Set<CacheEvent> missing = EnumSet.allOf(CacheEvent.class);
        missing.removeAll(EventDispatcher.HANDLED);
        assertThat(missing).isEmpty();
    }
}
```
