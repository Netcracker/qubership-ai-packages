The class below is new in this change, in a published library (`org.example.cache`, Java 17). The project's other
public classes carry Javadoc and none of them uses `@since`. The build runs no checkstyle rule that demands a comment.

Write the doc comments and inline comments this class needs, and none that it does not. Give back the whole file with
your comments in it, in one `java` block, and nothing else.

```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void put(String key, byte[] value) {
        if (value.length > MAX_ENTRY_BYTES) {
            throw new IllegalArgumentException(
                "entry " + key + " is " + value.length + " bytes, limit " + MAX_ENTRY_BYTES);
        }
        entries.put(key, value);
    }

    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
