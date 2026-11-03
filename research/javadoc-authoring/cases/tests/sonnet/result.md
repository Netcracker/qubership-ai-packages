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

    @Test
    void evictedBytesCountsOnlyTheValue() {
        EntryCache cache = new EntryCache("c");
        // The key is longer than the value, so adding the key length to the total changes the result.
        cache.put("a-long-key", new byte[3]);
        cache.evict("a-long-key");
        assertThat(cache.evictedBytes()).isEqualTo(3);
    }

    /**
     * Fails when a {@link CacheEvent} constant is added without a handler in {@link EventDispatcher}.
     *
     * <p>Add the handler and list the event in {@link EventDispatcher#HANDLED}.</p>
     */
    @Test
    void everyEventHasAHandler() {
        Set<CacheEvent> missing = EnumSet.allOf(CacheEvent.class);
        missing.removeAll(EventDispatcher.HANDLED);
        assertThat(missing).isEmpty();
    }
}
```
