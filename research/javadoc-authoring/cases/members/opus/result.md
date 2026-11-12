```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * An in-memory map from string keys to byte arrays.
 *
 * <p>An entry stays in the cache until {@link #evict(String)} removes it or
 * {@link #put(String, byte[])} replaces it. The cache does not remove entries on its own and
 * does not limit how many it holds.
 *
 * <p>This class is not thread-safe. Callers that share an instance across threads must
 * synchronize access to it.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest value, in bytes, that {@link #put(String, byte[])} accepts: 1 MiB ({@value} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /**
     * {@link System#nanoTime()} at the last eviction, or 0 if no entry has been evicted.
     * {@code nanoTime()} can return 0 itself, and an eviction at that instant is then reported as
     * no eviction.
     */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key} and replaces any value already stored there.
     *
     * <p>The cache keeps a reference to {@code value}, not a copy, so the caller must not modify
     * the array after this call.
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

    /** Removes the entry stored under {@code key}, and does nothing if there is none. */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time elapsed since {@link #evict(String)} last removed an entry.
     *
     * @return nanoseconds measured with {@link System#nanoTime()}, or an empty value if no entry
     *     has been evicted
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
