```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value, in bytes, that [EntryCache.Put] stores:
// 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge reports a value that [EntryCache.Put] refused because of its size.
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which key to evict from the keys passed to Victim.
type Policy interface {
	Victim(keys []string) string
}

// oldestFirst expects keys to be non-empty and ordered from oldest to newest.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache maps string keys to byte-slice values. Create one with [New]
// because the zero value is not ready to use. An EntryCache is not safe for
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
// it after the call.
//
// If value is longer than 1 MiB (1048576 bytes), Put stores nothing and
// returns an error that wraps [ErrTooLarge].
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key. If key is not in the cache, Evict leaves
// the cache unchanged, and the call does not count as an eviction for
// [EntryCache.SinceLastEviction].
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. If no entry has been evicted yet, it returns 0 and false.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
