```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values under string keys and tracks when an entry was last evicted.
 *
 * <p>Instances are not thread-safe. Callers that share one must synchronize access themselves.</p>
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest value length, in bytes, that {@link #put} accepts: 1 MiB ({@value} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    /** {@link System#nanoTime()} reading taken at the last eviction, or 0 if nothing was evicted. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any earlier value for that key.
     *
     * <p>The cache keeps a reference to the array and does not copy it, so the caller must not
     * modify the array afterwards.</p>
     *
     * @param value the bytes to store; must not be {@code null} and must not be longer than
     *     1048576 bytes (1 MiB)
     * @throws IllegalArgumentException if {@code value} is longer than 1048576 bytes
     */
    public void put(String key, byte[] value) {
        if (value.length > MAX_ENTRY_BYTES) {
            throw new IllegalArgumentException(
                "entry " + key + " is " + value.length + " bytes, limit " + MAX_ENTRY_BYTES);
        }
        entries.put(key, value);
    }

    /**
     * Removes the entry for {@code key}, if there is one.
     *
     * <p>Removing an entry sets the time that {@link #nanosSinceLastEviction()} measures from.
     * A key with no entry changes nothing.</p>
     */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the time since the last eviction that removed an entry.
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
