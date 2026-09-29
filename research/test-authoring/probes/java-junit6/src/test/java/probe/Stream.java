package probe;

/** The unit under test: {@code ensureBytes(-1)} returns -1 where the tests expect 0. */
final class Stream {
    private Stream() {}

    static int ensureBytes(int count) {
        return count;
    }

    /** Throws the wrong type: the tests expect an IllegalArgumentException. */
    static int refuse(int count) {
        throw new IllegalStateException("count must not be negative: " + count);
    }
}
