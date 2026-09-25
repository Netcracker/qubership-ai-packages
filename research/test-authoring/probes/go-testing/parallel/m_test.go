package parallel

import (
	"testing"
	"time"
)

// Each parallel subtest waits for the other to arrive; a sequential run would time out.
func TestParallelSubtestsOverlap(t *testing.T) {
	arrived := make(chan struct{}, 2)
	for _, name := range []string{"left", "right"} {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			arrived <- struct{}{}
			deadline := time.After(5 * time.Second)
			for len(arrived) < 2 {
				select {
				case <-deadline:
					t.Fatalf("%s: the other subtest never started while this one ran", name)
				case <-time.After(time.Millisecond):
				}
			}
		})
	}
}
