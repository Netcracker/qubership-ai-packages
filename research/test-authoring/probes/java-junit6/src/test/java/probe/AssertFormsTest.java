package probe;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertIterableEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static probe.Stream.ensureBytes;
import static probe.Stream.refuse;

import java.util.List;
import org.junit.jupiter.api.Test;

/** One JUnit assertion per test, each failing, in the order of the table in junit5-assertions.md. */
class AssertFormsTest {
    @Test
    void assertEqualsPlain() {
        assertEquals(0, ensureBytes(-1));
    }

    @Test
    void assertEqualsMessage() {
        assertEquals(0, ensureBytes(-1), "ensureBytes(-1)");
    }

    @Test
    void assertEqualsSupplier() {
        assertEquals(0, ensureBytes(-1), () -> "ensureBytes(-1)");
    }

    @Test
    void assertEqualsSwapped() {
        assertEquals(ensureBytes(-1), 0);
    }

    @Test
    void assertTruePlain() {
        int expected = 0;
        assertTrue(expected == ensureBytes(-1));
    }

    @Test
    void assertTrueMessage() {
        int expected = 0;
        assertTrue(expected == ensureBytes(-1), "ensureBytes(-1) must refuse");
    }

    @Test
    void assertNotNullOfNull() {
        assertNotNull(null);
    }

    @Test
    void assertArrayEqualsDiffer() {
        assertArrayEquals(new int[] {1, 2, 3}, new int[] {1, 2, 4});
    }

    @Test
    void assertIterableEqualsDiffer() {
        assertIterableEquals(List.of(1, 2, 3), List.of(1, 2, 4));
    }

    @Test
    void assertThrowsOtherType() {
        assertThrows(IllegalArgumentException.class, () -> refuse(-1));
    }

    @Test
    void assertThrowsNothing() {
        assertThrows(IllegalArgumentException.class, () -> ensureBytes(-1));
    }

    @Test
    void failPlain() {
        fail();
    }

    @Test
    void failMessage() {
        fail("ensureBytes(-1) returned instead of throwing");
    }
}
