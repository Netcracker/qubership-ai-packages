package testifygrouping

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

func TestAssertContinues(t *testing.T) {
	assert.Equal(t, 0, ensureBytes(-1), "first")
	assert.Equal(t, 0, ensureBytes(-2), "second")
}

func TestRequireStops(t *testing.T) {
	require.Equal(t, 0, ensureBytes(-1), "first")
	t.Log("reached after require")
}
