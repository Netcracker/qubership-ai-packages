/** Sums the integers in [0, n); a non-positive n sums nothing. */
export function sumBelow(n: number): number {
  let total = 0;
  for (let i = 0; i < n; i++) {
    total += i;
  }
  return total;
}

/** Whether n is strictly positive. */
export function isPositive(n: number): boolean {
  return n > 0;
}

/** A label for n, which no test reads. */
export function label(n: number): string {
  return "n=" + n;
}
