package testifyforms

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"

	"probes.example/gotesting/stream"
)

var ensureBytes = stream.EnsureBytes

var ErrNegativeCount = errors.New("negative")

type P struct{ A, B int }

func TestEqual(t *testing.T)            { assert.Equal(t, 0, ensureBytes(-1)) }
func TestEqualMessage(t *testing.T)     { assert.Equal(t, 0, ensureBytes(-1), "ensureBytes(%d)", -1) }
func TestEqualStrings(t *testing.T)     { assert.Equal(t, "Hello world", "Hello, world") }
func TestEqualStructs(t *testing.T)     { assert.Equal(t, P{1, 2}, P{1, 3}) }
func TestTrue(t *testing.T)             { assert.True(t, ensureBytes(-1) == 0) }
func TestTrueMessage(t *testing.T)      { assert.True(t, ensureBytes(-1) == 0, "ensureBytes(-1) must refuse") }
func TestErrorIs(t *testing.T)          { assert.ErrorIs(t, errors.New("other"), ErrNegativeCount) }
func TestEqualError(t *testing.T)       { assert.EqualError(t, errors.New("other"), "negative") }
func TestNoError(t *testing.T)          { assert.NoError(t, errors.New("boom")) }
func TestInSubtest(t *testing.T) {
	t.Run("negative count is refused", func(t *testing.T) { assert.Equal(t, 0, ensureBytes(-1)) })
}
