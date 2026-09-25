package m;

public class Stream {
    /** Meant to refuse a negative count by returning 0; the defect is that it returns the count unchanged. */
    public int ensureBytes(int count) {
        return count;
    }
}
