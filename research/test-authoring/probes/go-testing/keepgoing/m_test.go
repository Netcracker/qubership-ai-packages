package keepgoing

import (
	"testing"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

// Two t.Errorf calls: both are reported.
func TestErrorContinues(t *testing.T) {
	if got := ensureBytes(-1); got != 0 {
		t.Errorf("first: ensureBytes(-1) = %d, want 0", got)
	}
	if got := ensureBytes(-2); got != 0 {
		t.Errorf("second: ensureBytes(-2) = %d, want 0", got)
	}
}

// t.Fatalf stops the test: the second check never runs.
func TestFatalStops(t *testing.T) {
	if got := ensureBytes(-1); got != 0 {
		t.Fatalf("first: ensureBytes(-1) = %d, want 0", got)
	}
	if got := ensureBytes(-2); got != 0 {
		t.Errorf("second: ensureBytes(-2) = %d, want 0", got)
	}
}
