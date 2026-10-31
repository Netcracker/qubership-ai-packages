The test file below is new in this change, in a Go module (`example.com/cache`, Go 1.22, standard `testing` only). It
tests `EntryCache`, whose `Evict` adds the evicted value's length to a running total and whose `Put` returns an error
wrapping `ErrTooLarge` for a value over `maxEntryBytes`. `Event` is an enum-like type in the same package with the
constants listed in `allEvents`; `handled` is the set of events the dispatcher has a handler for.

`TestEvictedBytesCountsOnlyTheValue` is the regression test for issue #57: `Evict` used to add the key's length to the
total as well as the value's, so the total came out too large. Nothing returned an error.

Write the doc comments and inline comments this file needs, and none that it does not. Give back the whole file with
your comments in it, in one `go` block, and nothing else.

```go
package cache

import (
	"errors"
	"testing"
)

func TestPutThenGetReturnsTheValue(t *testing.T) {
	c := New("c")
	if err := c.Put("k", []byte{1, 2}); err != nil {
		t.Fatal(err)
	}
	if got := c.Get("k"); string(got) != "\x01\x02" {
		t.Errorf("Get(%q) = %v, want [1 2]", "k", got)
	}
}

func TestAValueOverTheLimitIsRejected(t *testing.T) {
	c := New("c")
	err := c.Put("k", make([]byte, maxEntryBytes+1))
	if !errors.Is(err, ErrTooLarge) {
		t.Errorf("Put of %d bytes: err = %v, want ErrTooLarge", maxEntryBytes+1, err)
	}
}

func TestEvictedBytesCountsOnlyTheValue(t *testing.T) {
	c := New("c")
	_ = c.Put("a-long-key", make([]byte, 3))
	c.Evict("a-long-key")
	if got := c.EvictedBytes(); got != 3 {
		t.Errorf("EvictedBytes() = %d, want 3", got)
	}
}

func TestEveryEventHasAHandler(t *testing.T) {
	for _, e := range allEvents {
		if !handled[e] {
			t.Errorf("event %v has no handler", e)
		}
	}
}
```
