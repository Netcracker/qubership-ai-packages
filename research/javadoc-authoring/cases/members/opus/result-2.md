```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values in memory under string keys.
 *
 * <p>An entry stays in the cache until {@link #evict} removes it or {@link #put} replaces it. The cache has no
 * capacity limit and no expiry.
 *
 * <p>Instances are not thread-safe. A caller that shares one across threads must synchronize every access.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest value, in bytes, that {@link #put} accepts: 1 MiB ({@value} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /** {@link System#nanoTime()} at the latest eviction, or {@code 0} before the first one. */
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
     * <p>The cache keeps the array itself, not a copy, so a later write to the array changes the cached entry.
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

    /** Removes the entry stored under {@code key}, or does nothing if there is none. */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time elapsed since {@link #evict} last removed an entry, in nanoseconds.
     *
     * @return the elapsed time, or an empty value if {@link #evict} has not removed an entry yet
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
