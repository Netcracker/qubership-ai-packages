```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value [EntryCache.Put] accepts: 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge reports that [EntryCache.Put] refused a value over the entry size
// limit. Put wraps it, so match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which entry a cache evicts. An implementation's Victim must
// return one of keys.
type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache is an in-memory map from string keys to byte values. The zero
// value is not ready to use; create one with [New]. An EntryCache is not safe
// for concurrent use.
type EntryCache struct {
	name         string
	entries      map[string][]byte
	evictedBytes int64
	// lastEviction is zero until the first eviction.
	lastEviction time.Time
}

func New(name string) *EntryCache {
	return &EntryCache{name: name, entries: map[string][]byte{}}
}

func (c *EntryCache) Name() string { return c.name }

// Put stores value under key and replaces any value already stored there. The
// cache keeps value itself, not a copy, so the caller must not modify it
// afterward. If value is longer than 1 MiB (1048576 bytes), Put stores nothing
// and returns an error that wraps [ErrTooLarge].
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key and records the time of the removal for
// [EntryCache.SinceLastEviction]. When key has no entry, Evict does nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. It returns 0 and false if Evict has not removed an entry yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
