package testifyorder

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

// Expected first: the labels are right.
func TestExpectedFirst(t *testing.T) { assert.Equal(t, 0, ensureBytes(-1)) }

// Actual first: the bug is printed as the expectation.
func TestSwapped(t *testing.T) { assert.Equal(t, ensureBytes(-1), 0) }
