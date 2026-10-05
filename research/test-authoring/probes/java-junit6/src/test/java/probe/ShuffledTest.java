package probe;

import org.junit.jupiter.api.Test;

/** Passing tests, so a run in random order prints nothing that depends on the order. */
class ShuffledTest {
    @Test
    void a() {}

    @Test
    void b() {}

    @Test
    void c() {}
}
