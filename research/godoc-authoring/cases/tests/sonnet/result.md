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

// The key is longer than the value, so a key length added to the total gives a
// different number than the value length alone.
func TestEvictedBytesCountsOnlyTheValue(t *testing.T) {
	c := New("c")
	_ = c.Put("a-long-key", make([]byte, 3))
	c.Evict("a-long-key")
	if got := c.EvictedBytes(); got != 3 {
		t.Errorf("EvictedBytes() = %d, want 3", got)
	}
}

// Every event in allEvents has a handler in the dispatcher, recorded in handled.
// Add each new Event constant to allEvents; the test checks only the events
// listed there.
func TestEveryEventHasAHandler(t *testing.T) {
	for _, e := range allEvents {
		if !handled[e] {
			t.Errorf("event %v has no handler", e)
		}
	}
}
```
