package numbers

import "testing"

func TestSumBelowFour(t *testing.T) {
	if got := SumBelow(4); got != 6 {
		t.Errorf("SumBelow(4) = %d, want 6", got)
	}
}

func TestPositiveAndNegative(t *testing.T) {
	if !IsPositive(5) {
		t.Error("IsPositive(5) = false, want true")
	}
	if IsPositive(-5) {
		t.Error("IsPositive(-5) = true, want false")
	}
}

func TestGreet(t *testing.T) {
	if got := Greet("you"); got != "hi you" {
		t.Errorf("Greet(%q) = %q, want %q", "you", got, "hi you")
	}
}
