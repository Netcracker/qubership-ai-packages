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
     * Evicting an entry adds only the length of its value to {@link EntryCache#evictedBytes()}.
     * Before issue #57 was fixed, {@code evict} also added the length of the key, so the total came out too
     * large and no exception was thrown.
     */
    @Test
    void evictedBytesCountsOnlyTheValue() {
        EntryCache cache = new EntryCache("c");
        // The key is longer than the value, so a total that includes the key's length fails the assertion.
        cache.put("a-long-key", new byte[3]);
        cache.evict("a-long-key");
        assertThat(cache.evictedBytes()).isEqualTo(3);
    }

    /**
     * Fails when a {@link CacheEvent} constant has no handler in {@link EventDispatcher}. The assertion prints
     * the constants missing from {@link EventDispatcher#HANDLED}. Add a handler for each one.
     */
    @Test
    void everyEventHasAHandler() {
        Set<CacheEvent> missing = EnumSet.allOf(CacheEvent.class);
        missing.removeAll(EventDispatcher.HANDLED);
        assertThat(missing).isEmpty();
    }
}
```
