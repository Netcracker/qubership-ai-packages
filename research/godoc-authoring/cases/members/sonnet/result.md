```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value [EntryCache.Put] accepts, in bytes: 1 MiB
// (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is the error that [EntryCache.Put] wraps when a value exceeds the
// entry size limit.
var ErrTooLarge = errors.New("cache: entry too large")

type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache is an in-memory cache of byte slices keyed by string. Create one
// with [New]; the zero value is not ready to use. It is not safe for concurrent
// use.
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

// Put stores value under key and replaces any previous value. The cache keeps
// value without copying it, so the caller must not modify it afterwards.
//
// Put returns an error wrapping [ErrTooLarge] and stores nothing when value is
// longer than 1 MiB (1048576 bytes).
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes key and records the time for [EntryCache.SinceLastEviction]. A
// key that is not in the cache is ignored and records nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry. The boolean is false, and the duration zero, while no entry
// has been evicted.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
