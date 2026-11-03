```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array entries in memory, keyed by string.
 *
 * <p>This class is not thread-safe. Callers that share an instance between threads must synchronize
 * every call on it.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest entry, in bytes, that {@link #put} accepts: 1 MiB ({@value #MAX_ENTRY_BYTES} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /** {@link System#nanoTime()} at the last eviction that removed an entry, or 0 if none has. */
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key} and replaces any entry already stored there.
     *
     * <p>The cache keeps the array itself, not a copy, so a later change to its contents changes the
     * cached entry.
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
     * Removes the entry stored under {@code key}, if there is one.
     *
     * <p>Only a call that removes an entry counts as an eviction for
     * {@link #nanosSinceLastEviction()}.
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
