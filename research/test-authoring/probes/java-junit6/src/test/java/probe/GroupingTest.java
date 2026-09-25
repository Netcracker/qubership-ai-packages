package probe;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static probe.Stream.ensureBytes;

import org.junit.jupiter.api.Test;

/** assertAll, with a heading and without, against a chain of bare assertEquals; each has two failing checks. */
class GroupingTest {
    @Test
    void assertAllReportsBoth() {
        assertAll("account",
                () -> assertEquals(0, ensureBytes(-1), "first"),
                () -> assertEquals(0, ensureBytes(-2), "second"));
    }

    @Test
    void assertAllWithoutHeading() {
        assertAll(
                () -> assertEquals(0, ensureBytes(-1), "first"),
                () -> assertEquals(0, ensureBytes(-2), "second"));
    }

    @Test
    void chainStopsAtFirst() {
        assertEquals(0, ensureBytes(-1), "first");
        assertEquals(0, ensureBytes(-2), "second");
    }
}
