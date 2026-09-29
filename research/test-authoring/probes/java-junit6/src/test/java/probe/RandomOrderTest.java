package probe;

import static org.junit.jupiter.api.Assertions.fail;

import org.junit.jupiter.api.Test;

/** Five tests that fail with their own name, so the order they ran in is the order of the failures. */
class RandomOrderTest {
    @Test
    void a() {
        fail("a");
    }

    @Test
    void b() {
        fail("b");
    }

    @Test
    void c() {
        fail("c");
    }

    @Test
    void d() {
        fail("d");
    }

    @Test
    void e() {
        fail("e");
    }
}
