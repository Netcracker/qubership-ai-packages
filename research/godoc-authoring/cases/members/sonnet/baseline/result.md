```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

const maxEntryBytes = 1 << 20

// ErrTooLarge reports a value over the entry size limit. [EntryCache.Put]
// returns it wrapped, so match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which entry to evict.
// Victim returns the key in keys to evict.
type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache holds byte-slice entries by key. It is not safe for concurrent
// use. The zero value is not ready to use; create one with [New].
type EntryCache struct {
	name         string
	entries      map[string][]byte
	evictedBytes int64
	lastEviction time.Time
}

// New returns an empty [EntryCache] with the given name.
func New(name string) *EntryCache {
	return &EntryCache{name: name, entries: map[string][]byte{}}
}

func (c *EntryCache) Name() string { return c.name }

// Put stores value under key, replacing any existing entry. It returns an
// error wrapping [ErrTooLarge], and leaves the cache unchanged, if value is
// longer than 1 MiB (1048576 bytes). Put keeps value without copying it, so
// the caller must not modify it afterward.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry stored under key and records the time of the
// eviction for [EntryCache.SinceLastEviction]. It does nothing when key has no
// entry.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. The boolean is false, and the duration zero, when no entry
// has been evicted.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
