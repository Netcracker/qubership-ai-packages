```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value that [EntryCache.Put] accepts: 1 MiB
// (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is the error that [EntryCache.Put] wraps when it rejects a value
// for its size.
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which key a cache evicts.
type Policy interface {
	// Victim returns the key to evict. An implementation must return one of
	// keys.
	Victim(keys []string) string
}

// oldestFirst evicts the first of keys, so it relies on the caller ordering
// keys from oldest to newest.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache maps string keys to byte-slice values in memory. The zero value
// is not ready to use; create one with [New]. An EntryCache is not safe for
// concurrent use.
type EntryCache struct {
	name         string
	entries      map[string][]byte
	evictedBytes int64
	lastEviction time.Time
}

func New(name string) *EntryCache {
	return &EntryCache{name: name, entries: map[string][]byte{}}
}

func (c *EntryCache) Name() string { return c.name }

// Put stores value under key and replaces any value already stored there. The
// cache keeps value itself rather than a copy, so the caller must not modify
// value afterwards.
//
// If value is longer than 1 MiB (1048576 bytes), Put returns an error that
// wraps [ErrTooLarge] and leaves the cache unchanged.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key and records the time of the removal for
// [EntryCache.SinceLastEviction]. If key has no entry, Evict does nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. If Evict has not removed an entry yet, it returns 0 and
// false.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
