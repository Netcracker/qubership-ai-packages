The test class below is new in this change, in a library (`org.example.cache`, Java 17, JUnit 5, AssertJ). It tests
`EntryCache`, whose `evict(String)` adds the evicted value's length to a running total and whose `put` rejects a value
over `MAX_ENTRY_BYTES`. `CacheEvent` is an enum in the same package; `EventDispatcher.HANDLED` is the set of events the
dispatcher has a handler for.

`evictedBytesCountsOnlyTheValue` is the regression test for issue #57: `evict` used to add the key's length to the
total as well as the value's, so the total came out too large. Nothing threw.

Write the doc comments and inline comments this class needs, and none that it does not. Give back the whole file with
your comments in it, in one `java` block, and nothing else.

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
        cache.put("a-long-key", new byte[3]);
        cache.evict("a-long-key");
        assertThat(cache.evictedBytes()).isEqualTo(3);
    }

    @Test
    void everyEventHasAHandler() {
        Set<CacheEvent> missing = EnumSet.allOf(CacheEvent.class);
        missing.removeAll(EventDispatcher.HANDLED);
        assertThat(missing).isEmpty();
    }
}
```
