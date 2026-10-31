```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

const maxEntryBytes = 1 << 20

// ErrTooLarge is the error that [EntryCache.Put] wraps when it rejects a value
// over the size limit. Match it with [errors.Is].
var ErrTooLarge = errors.New("cache: entry too large")

// Policy chooses which entry an eviction removes.
type Policy interface {
	// Victim returns the element of keys to evict.
	Victim(keys []string) string
}

// oldestFirst is a [Policy] that evicts keys[0], which is the oldest key only
// when keys is ordered from oldest to newest.
type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

// EntryCache maps string keys to byte-slice values. Create one with [New]: the
// zero value is not ready to use, and Put panics on it. An EntryCache is not
// safe for concurrent use.
type EntryCache struct {
	name         string
	entries      map[string][]byte
	evictedBytes int64
	// lastEviction is the zero Time until Evict first removes an entry.
	lastEviction time.Time
}

// New returns an empty EntryCache with the given name.
func New(name string) *EntryCache {
	return &EntryCache{name: name, entries: map[string][]byte{}}
}

// Name returns the name passed to [New].
func (c *EntryCache) Name() string { return c.name }

// Put stores value under key and replaces any value already stored there. The
// cache keeps value itself, not a copy, so the caller must not modify value
// afterwards.
//
// If value is longer than 1 MiB (1048576 bytes), Put stores nothing and returns
// an error that wraps [ErrTooLarge].
func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

// Evict removes the entry for key, if there is one. Only the removal of an
// existing entry resets the time that [EntryCache.SinceLastEviction] reports.
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
