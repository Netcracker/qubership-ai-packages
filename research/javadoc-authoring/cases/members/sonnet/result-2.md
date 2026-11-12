```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Stores byte-array entries by string key and removes them only on an explicit {@link #evict}.
 *
 * <p>Instances are not thread-safe. Callers that share one across threads must synchronize
 * access themselves.</p>
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest entry, in bytes, that {@link #put} accepts: 1 MiB ({@value} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /** {@link System#nanoTime()} reading taken at the last removal, or 0 if nothing was removed. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any earlier entry for that key.
     *
     * <p>The cache keeps the array itself and does not copy it, so changing the array
     * afterwards changes the cached entry.</p>
     *
     * @throws IllegalArgumentException if {@code value} is longer than 1 MiB (1048576 bytes);
     *         the cache is left unchanged
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
     * Removes the entry stored under {@code key}, if there is one.
     *
     * <p>Evicting a key that has no entry changes nothing, including the time that
     * {@link #nanosSinceLastEviction()} reports.</p>
     */
    public void evict(String key) {
        byte[] removed = entries.remove(key);
        if (removed != null) {
            evictedBytes += removed.length;
            lastEvictionNanos = System.nanoTime();
        }
    }

    /**
     * Returns the nanoseconds elapsed since {@link #evict} last removed an entry.
     *
     * @return the elapsed time in nanoseconds, or empty if no entry has been removed yet
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
