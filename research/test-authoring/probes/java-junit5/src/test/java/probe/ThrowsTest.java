package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import org.junit.jupiter.api.Test;

/** What assertThrows returns, and how assertThrowsExactly treats a subclass of the expected type. */
class ThrowsTest {
    @Test
    void assertThrowsReturnsTheException() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> Integer.parseInt("x"));
        assertEquals("negative", e.getMessage());
    }

    @Test
    void assertThrowsAcceptsSubclass() {
        // NumberFormatException extends IllegalArgumentException, so this passes.
        assertThrows(IllegalArgumentException.class, () -> Integer.parseInt("x"));
    }

    @Test
    void assertThrowsExactlyRefusesSubclass() {
        assertThrowsExactly(IllegalArgumentException.class, () -> Integer.parseInt("x"));
    }
}
