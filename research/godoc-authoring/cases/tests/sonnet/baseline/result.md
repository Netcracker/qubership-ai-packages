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

// EvictedBytes totals the lengths of the evicted values, and the key's length
// is no part of it. Evict used to add the key's length as well, so the total
// came out too large and nothing returned an error (issue #57).
func TestEvictedBytesCountsOnlyTheValue(t *testing.T) {
	c := New("c")
	// The key is longer than the value, so any key bytes in the total show.
	_ = c.Put("a-long-key", make([]byte, 3))
	c.Evict("a-long-key")
	if got := c.EvictedBytes(); got != 3 {
		t.Errorf("EvictedBytes() = %d, want 3", got)
	}
}

// The dispatcher has a handler for every event in allEvents. When this fails,
// add a handler for the event the message names so that it appears in handled.
// Whoever adds an Event constant must also add it to allEvents, which is the
// only list this test checks.
func TestEveryEventHasAHandler(t *testing.T) {
	for _, e := range allEvents {
		if !handled[e] {
			t.Errorf("event %v has no handler", e)
		}
	}
}
```
