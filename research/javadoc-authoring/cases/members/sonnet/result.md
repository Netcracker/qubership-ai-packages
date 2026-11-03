```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values in memory under string keys.
 *
 * <p>An entry stays in the cache until {@link #evict(String)} removes it. This class is not
 * thread-safe; callers must synchronize access externally.</p>
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest value, in bytes, that {@link #put(String, byte[])} accepts: 1 MiB ({@value} bytes). */
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

    /**
     * Stores a value under a key, replacing any existing entry for that key.
     *
     * <p>The cache keeps the array itself and does not copy it, so the caller must not modify it
     * after this call.</p>
     *
     * @param value the value to store, at most 1 MiB (1048576 bytes) long
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
     * Removes the entry for a key and records the eviction.
     *
     * <p>Evicting a key that has no entry changes nothing and is not recorded as an eviction.</p>
     */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time since the most recent eviction.
     *
     * @return the elapsed time in nanoseconds, measured with {@link System#nanoTime()}, or an
     *     empty value if no entry has been evicted
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
