```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte-array values in memory under string keys.
 *
 * <p>Instances are not thread-safe. A caller that shares one across threads must synchronize
 * every access to it.
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    /** Largest value {@link #put(String, byte[])} accepts, in bytes: 1 MiB ({@value} bytes). */
    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;

    /** Value of {@link System#nanoTime()} at the most recent eviction, or 0 if none has happened. */
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

    /** Removes the entry for {@code key}, if there is one. */
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
     * @return the elapsed time, measured with {@link System#nanoTime()}, since {@link #evict(String)}
     *     last removed an entry, or an empty value if no call to it has removed an entry yet
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
