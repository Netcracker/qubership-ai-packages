package m;

/** Meant to load each key once; the defect is that it never keeps what it loaded. */
public class Cache {
    private final Backend backend;

    public Cache(Backend backend) {
        this.backend = backend;
    }

    public String get(String key) {
        return backend.load(key);
    }
}
