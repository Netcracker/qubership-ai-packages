```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Stores byte-array values under string keys and rejects values over a size limit.
 *
 * <p>The cache keeps each value by reference and does not copy it, so a caller must not modify an
 * array after passing it to {@link #put(String, byte[])}. Instances are not thread-safe; callers
 * must synchronize access externally.</p>
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    /** {@link System#nanoTime()} at the last eviction, or 0 if nothing has been evicted. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores a value under a key, replacing any value already stored under that key.
     *
     * @param key the key to store the value under
     * @param value the value, at most 1 MiB (1048576 bytes) long; the cache keeps this array itself
     *     and does not copy it
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
     * Removes the entry stored under a key.
     *
     * <p>Only a removal counts as an eviction for {@link #nanosSinceLastEviction()}. Evicting a key
     * that has no entry changes nothing.</p>
     *
     * @param key the key whose entry is removed
     */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time since the last eviction, measured with {@link System#nanoTime()}.
     *
     * @return the elapsed time in nanoseconds, or an empty value if no entry has been evicted yet
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
