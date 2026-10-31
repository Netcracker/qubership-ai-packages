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

// Evict adds the evicted value's length to EvictedBytes and adds nothing for
// the key. The key here is ten bytes and the value three, so any key bytes in
// the total show up in the result. Evict used to add the key's length as well,
// and this total came out as 13 instead of 3 (issue #57).
func TestEvictedBytesCountsOnlyTheValue(t *testing.T) {
	c := New("c")
	_ = c.Put("a-long-key", make([]byte, 3))
	c.Evict("a-long-key")
	if got := c.EvictedBytes(); got != 3 {
		t.Errorf("EvictedBytes() = %d, want 3", got)
	}
}

// A failure names an event that has no entry in handled, so the dispatcher has
// no handler for it: add the handler there. The test checks only the events
// listed in allEvents, so add every new Event constant to allEvents as well.
func TestEveryEventHasAHandler(t *testing.T) {
	for _, e := range allEvents {
		if !handled[e] {
			t.Errorf("event %v has no handler", e)
		}
	}
}
```
