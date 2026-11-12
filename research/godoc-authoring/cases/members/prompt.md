The file below is new in this change, in a published Go module (`example.com/cache`, Go 1.22). The repository's
golangci-lint configuration enables neither `revive` nor `golint`, and no linter demands a comment on an exported
name.

Write the doc comments and inline comments this file needs, and none that it does not. Give back the whole file with
your comments in it, in one `go` block, and nothing else.

```go
package cache

import (
	"errors"
	"fmt"
	"time"
)

const DefaultTimeoutSeconds = 30

const maxEntryBytes = 1 << 20

var ErrTooLarge = errors.New("cache: entry too large")

type Policy interface {
	Victim(keys []string) string
}

type oldestFirst struct{}

func (oldestFirst) Victim(keys []string) string { return keys[0] }

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

func (c *EntryCache) Put(key string, value []byte) error {
	if len(value) > maxEntryBytes {
		return fmt.Errorf("entry %s is %d bytes, limit %d: %w", key, len(value), maxEntryBytes, ErrTooLarge)
	}
	c.entries[key] = value
	return nil
}

func (c *EntryCache) Evict(key string) {
	if v, ok := c.entries[key]; ok {
		delete(c.entries, key)
		c.evictedBytes += int64(len(v))
		c.lastEviction = time.Now()
	}
}

func (c *EntryCache) SinceLastEviction() (time.Duration, bool) {
	if c.lastEviction.IsZero() {
		return 0, false
	}
	return time.Since(c.lastEviction), true
}
```
