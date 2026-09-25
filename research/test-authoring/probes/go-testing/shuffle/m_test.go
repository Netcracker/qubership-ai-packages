package shuffle

import "testing"

// Eight top-level tests with three subtests each, declared in order, so a run shows whether the top-level order
// and the subtest order change under -shuffle.
func sub(t *testing.T) {
	for _, name := range []string{"x", "y", "z"} {
		t.Run(name, func(t *testing.T) {})
	}
}

func TestA(t *testing.T) { sub(t) }
func TestB(t *testing.T) { sub(t) }
func TestC(t *testing.T) { sub(t) }
func TestD(t *testing.T) { sub(t) }
func TestE(t *testing.T) { sub(t) }
func TestF(t *testing.T) { sub(t) }
func TestG(t *testing.T) { sub(t) }
func TestH(t *testing.T) { sub(t) }
