// Package stream holds the function the probes test. ensureBytes should refuse a negative count and return 0;
// it returns the count unchanged, so every probe that checks it fails.
package stream

// EnsureBytes returns n, including a negative n, which is the defect the probes report.
func EnsureBytes(n int) int { return n }
