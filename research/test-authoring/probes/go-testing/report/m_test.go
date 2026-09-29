package report

import (
	"testing"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

func TestEnsureBytes(t *testing.T) {
	t.Run("negative count is refused", func(t *testing.T) {
		if got := ensureBytes(-1); got != 0 {
			t.Errorf("ensureBytes(-1) = %d, want 0", got)
		}
	})
	t.Run("bare fatal", func(t *testing.T) {
		if ensureBytes(-1) != 0 {
			t.Fatal("mismatch")
		}
	})
	t.Run("no message", func(t *testing.T) {
		if ensureBytes(-1) != 0 {
			t.Fail()
		}
	})
}
