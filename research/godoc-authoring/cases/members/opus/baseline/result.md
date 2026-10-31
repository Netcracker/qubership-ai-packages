```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

// maxEntryBytes is the largest value [EntryCache.Put] accepts, in bytes:
// 1 MiB (1048576 bytes).
const maxEntryBytes = 1 << 20

// ErrTooLarge is wrapped by the error [EntryCache.Put] returns for a value over
// its size limit. Match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy selects an entry to evict.
type Policy interface {
	// Victim returns the element of keys to evict.
	Victim(keys []string) string
}

// oldestFirst assumes keys is non-empty and ordered from oldest to newest.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache maps string keys to byte-slice values and records when an entry
// was last evicted. Create one with [New]; the zero value is not ready to use.
// An EntryCache is not safe for concurrent use.
type EntryCache struct {
	name         string
	entries      map[string][]byte
	evictedBytes int64
	// lastEviction is zero until Evict first removes an entry.
	lastEviction time.Time
}

// New returns an empty EntryCache with the given name.
func New(name string) *EntryCache {
	return &EntryCache{name: name, entries: map[string][]byte{}}
}

// Name returns the name passed to [New].
func (c *EntryCache) Name() string { return c.name }

// Put stores value under key, replacing any value already stored there. The
// cache keeps value without copying it, so the caller must not modify it
// afterwards. A value larger than 1 MiB (1048576 bytes) is not stored, and Put
// returns an error that wraps [ErrTooLarge].
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry stored under key, and [EntryCache.SinceLastEviction]
// then measures from this call. If key is absent, Evict changes nothing.
func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

// SinceLastEviction returns the time elapsed since [EntryCache.Evict] last
// removed an entry, and true. It returns 0 and false if Evict has not removed
// an entry yet.
func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
