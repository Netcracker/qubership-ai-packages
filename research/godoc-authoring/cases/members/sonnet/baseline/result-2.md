```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value [EntryCache.Put] accepts, 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is the error that [EntryCache.Put] wraps when a value exceeds the
// entry size limit. Match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy selects the key to evict from a cache.
type Policy interface {
	Victim(keys []string) string
}

// oldestFirst is a [Policy] that picks the first key, which is the oldest when
// the caller passes keys ordered oldest first. Victim panics if keys is empty.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache is an in-memory store of byte-slice entries keyed by string.
// Create one with [New]; the zero value is not ready to use. It is not safe for
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

// Put stores value under key and replaces any existing entry. It keeps value
// without copying it, so the caller must not modify value afterwards.
//
// Put returns an error wrapping [ErrTooLarge] if value is longer than 1 MiB
// (1048576 bytes). The cache is unchanged in that case.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key and records the time for
// [EntryCache.SinceLastEviction]. A key with no entry is ignored.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. The boolean is false, and the duration zero, if no entry has
// been evicted yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
