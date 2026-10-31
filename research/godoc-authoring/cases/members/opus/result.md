```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value Put accepts: 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is the error [EntryCache.Put] wraps when a value exceeds its size
// limit. Match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which cache entry to evict.
//
// Victim returns one of keys. The caller must pass at least one key, ordered
// oldest first.
type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache holds byte values by string key and records when it last evicted
// one. Create one with [New], because Put panics on the zero value. An
// EntryCache is not safe for concurrent use.
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
// value after Put returns.
//
// Put returns an error that wraps [ErrTooLarge] when value is larger than 1 MiB
// (1048576 bytes). In that case it stores nothing.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key and records the time for
// [EntryCache.SinceLastEviction]. If key has no entry, Evict does nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. It returns 0 and false if no entry has been evicted yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
