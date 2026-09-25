package race

import (
	"testing"
	"time"
)

var total int

// Two parallel subtests write one package-level variable. The sleep lets both start before either writes, so the
// writes are not ordered by the runner's own bookkeeping.
func TestSharedState(t *testing.T) {
	for _, name := range []string{"left", "right"} {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			time.Sleep(50 * time.Millisecond)
			total++
		})
	}
}
