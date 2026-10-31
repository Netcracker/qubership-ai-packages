```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values in memory under string keys and records when an entry was last evicted.
 *
 * <p>An instance is not thread-safe. A caller that shares one across threads must synchronize every call.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    /** {@link System#nanoTime()} at the most recent eviction, or 0 until the first one. */
    private long lastEvictionNanos;

    /**
     * Creates an empty cache with the given name.
     */
    public EntryCache(String name) {
        this.name = name;
    }

    /**
     * Returns the name this cache was created with.
     */
    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any entry already stored there.
     *
     * <p>The cache stores the array without copying it, so a change the caller makes to the array later changes the
     * stored entry. Replacing an entry does not update {@link #nanosSinceLastEviction()}.
     *
     * @throws IllegalArgumentException if {@code value} is longer than 1 MiB (1048576 bytes); the cache is left
     *     unchanged
     * @throws NullPointerException if {@code value} is null
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
     */
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
     * @return the elapsed time in nanoseconds, measured with {@link System#nanoTime()}, or an empty value if no call
     *     to {@link #evict(String)} has removed an entry yet
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
