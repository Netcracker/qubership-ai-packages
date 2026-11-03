```go
// Package cache provides [EntryCache], an in-memory cache of byte-slice
// entries keyed by string.
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value Put accepts, in bytes: 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is the error [EntryCache.Put] wraps when a value is over the
// entry size limit. Match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which entry to evict. Victim returns one of keys.
type Policy interface {
	Victim(keys []string) string
}

// oldestFirst evicts keys[0], so it assumes keys is ordered oldest first.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache is an in-memory cache of byte-slice entries keyed by string.
//
// Create one with [New]; the zero value is not ready to use. An EntryCache is
// not safe for concurrent use.
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

// Put stores value under key and replaces any earlier value for that key.
//
// It stores value without copying it, so the caller must not modify value
// afterward. A value over 1 MiB (1048576 bytes) is refused with an error that
// wraps [ErrTooLarge], and the cache is left unchanged.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key and records the eviction time reported by
// [EntryCache.SinceLastEviction]. A key with no entry is ignored and records
// nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. The second result is false, and the duration zero, if no
// entry has been evicted yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
