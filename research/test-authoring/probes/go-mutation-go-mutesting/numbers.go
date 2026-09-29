// Package numbers is the code whose mutants the go-mutesting probe measures.
package numbers

import "strconv"

// SumBelow sums the integers in [0, n); a non-positive n sums nothing.
func SumBelow(n int64) int64 {
	var total int64
	for i := int64(0); i < n; i++ {
		total += i
	}
	return total
}

// IsPositive reports whether n is strictly positive.
func IsPositive(n int64) bool {
	return n > 0
}

// Label is a label for n, which no test reads.
func Label(n int64) string {
	return strconv.FormatInt(n+1, 10)
}

// Greet greets name. A test reads it, and its mutant that turns the string + into - does not compile.
func Greet(name string) string {
	return "hi " + name
}
