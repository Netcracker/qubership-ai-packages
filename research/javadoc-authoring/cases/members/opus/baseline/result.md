```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * In-memory cache of byte arrays keyed by string.
 *
 * <p>This class is not thread-safe. A caller that shares one instance between threads has to
 * synchronize access to it.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    /** {@link System#nanoTime()} at the most recent eviction, or 0 before the first one. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any value already stored there.
     *
     * <p>The cache keeps a reference to {@code value}, not a copy, so a later change to the array
     * changes the cached entry.
     *
     * @throws IllegalArgumentException if {@code value} is longer than 1 MiB (1048576 bytes)
     * @throws NullPointerException if {@code value} is {@code null}
     */
    public void put(String key, byte[] value) {
        if (value.length > MAX_ENTRY_BYTES) {
            throw new IllegalArgumentException(
                "entry " + key + " is " + value.length + " bytes, limit " + MAX_ENTRY_BYTES);
        }
        entries.put(key, value);
    }

    /**
     * Removes the entry stored under {@code key} and records the time of the removal for
     * {@link #nanosSinceLastEviction()}. A key with no entry is ignored.
     */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time elapsed since the most recent eviction, in nanoseconds.
     *
     * @return the elapsed time, or an empty value if no entry has been evicted from this cache
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
