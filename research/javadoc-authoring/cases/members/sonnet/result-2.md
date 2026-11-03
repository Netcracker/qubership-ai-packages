```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values by string key and records when an entry was last evicted.
 *
 * <p>Instances are not thread-safe. Callers that share one across threads must synchronize
 * access themselves.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /**
     * Largest value, in bytes, that {@link #put} accepts: 1 MiB ({@value #MAX_ENTRY_BYTES} bytes).
     */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /** {@link System#nanoTime()} reading taken at the last eviction, or 0 if nothing was evicted yet. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any previous value.
     *
     * <p>The cache keeps a reference to {@code value} and does not copy it, so the caller must not
     * modify the array afterwards.
     *
     * @param value the bytes to store, at most 1 MiB (1048576 bytes) long
     * @throws IllegalArgumentException if {@code value} is longer than 1 MiB (1048576 bytes)
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
     * <p>Only a call that removes an entry counts as an eviction for
     * {@link #nanosSinceLastEviction()}. Evicting an absent key changes nothing.
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
