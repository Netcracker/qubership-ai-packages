package missingcall

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMissingCall(t *testing.T) { assert.NoSuchCall(t, 0) }
