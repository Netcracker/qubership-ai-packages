package probe;

public final class Numbers {
    private Numbers() {}

    /** Sums the integers in {@code [0, n)}; a non-positive {@code n} sums nothing. */
    public static long sumBelow(long n) {
        long total = 0;
        // A long counter, so a mutant that counts down never wraps around to reach n.
        for (long i = 0; i < n; i++) {
            total += i;
        }
        return total;
    }

    /** Whether {@code n} is strictly positive. */
    public static boolean isPositive(long n) {
        return n > 0;
    }

    /** A label for {@code n}, which no test reads. */
    public static String label(long n) {
        return "n=" + n;
    }
}
