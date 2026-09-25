package subtests

import (
	"testing"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

func TestEnsureBytes(t *testing.T) {
	tests := []struct {
		name string
		n    int
	}{
		{"minus one", -1},
		{"minus two", -2},
		{"same", -3},
		{"same", -4},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := ensureBytes(tt.n); got != 0 {
				t.Errorf("ensureBytes(%d) = %d, want 0", tt.n, got)
			}
		})
	}
}
