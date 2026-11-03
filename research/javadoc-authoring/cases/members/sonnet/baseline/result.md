```java
package org.example.cache;

import java.util.HashMap;
import java.util.Map;
import java.util.OptionalLong;

/**
 * Holds byte arrays in memory under string keys, each at most 1 MiB (1048576 bytes).
 *
 * <p>An entry stays until {@link #evict(String)} removes it or {@link #put(String, byte[])}
 * replaces it. Instances are not thread-safe; callers must synchronize access externally.</p>
 */
public final class EntryCache {
    public static final int DEFAULT_TIMEOUT_SECONDS = 30;

    static final int MAX_ENTRY_BYTES = 1 << 20;

    private final String name;
    private final Map<String, byte[]> entries = new HashMap<>();
    private long evictedBytes;
    // System.nanoTime() at the last eviction that removed an entry; 0 if there has been none.
    private long lastEvictionNanos;

    public EntryCache(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /**
     * Stores {@code value} under {@code key}, replacing any previous value for that key.
     *
     * <p>The cache keeps the array itself and does not copy it, so the caller must not modify
     * the array after this call.</p>
     *
     * @param key the key to store the value under
     * @param value the bytes to store, at most 1 MiB (1048576 bytes); must not be {@code null}
     * @throws IllegalArgumentException if {@code value} is longer than 1 MiB
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
     * {@link #nanosSinceLastEviction()}.</p>
     *
     * @param key the key of the entry to remove
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
     * @return the elapsed time in nanoseconds, or empty if no entry has been evicted
     */
    public OptionalLong nanosSinceLastEviction() {
        if (lastEvictionNanos == 0) {
            return OptionalLong.empty();
        }
        return OptionalLong.of(System.nanoTime() - lastEvictionNanos);
    }
}
```
