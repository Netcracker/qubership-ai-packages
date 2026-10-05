package probe;

/** The unit the reference quotes: {@code ensureBytes(-1)} returns -1 where the specification wants 0. */
public final class Stream {
  public int ensureBytes(int count) {
    return count;
  }

  public void refuse(int count) {
    throw new IllegalArgumentException("count must not be negative: " + count);
  }
}
