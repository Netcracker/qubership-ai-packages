```go
// Package cache provides an in-memory cache of byte-slice entries keyed by string.
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value Put accepts, in bytes: 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is wrapped by the error [EntryCache.Put] returns for an oversized value.
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses the key to evict.
type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache maps string keys to byte-slice values. Create one with [New]; the zero
// value is not ready to use. An EntryCache is not safe for concurrent use.
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

// Put stores value under key, replacing any earlier value. It keeps value without
// copying it, so the caller must not modify value afterward.
//
// Put returns an error wrapping [ErrTooLarge] when value is longer than 1 MiB
// (1048576 bytes), and the cache is left unchanged.
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes key and does nothing when key is absent. Only a call that removes an
// entry counts as an eviction for [EntryCache.SinceLastEviction].
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last removed an
// entry. It returns zero and false when no entry has been evicted yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
