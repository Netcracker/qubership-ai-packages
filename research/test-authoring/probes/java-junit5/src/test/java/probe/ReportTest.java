package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static probe.Stream.ensureBytes;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class ReportTest {
    @Test
    void negativeCountIsRefused() {
        assertEquals(0, ensureBytes(-1), "ensureBytes(-1)");
    }

    @Test
    @DisplayName("a negative count is refused")
    void displayName() {
        assertEquals(0, ensureBytes(-1));
    }

    @Nested
    class WhenTheStreamIsClosed {
        @Test
        void negativeCountIsRefused() {
            assertEquals(0, ensureBytes(-1));
        }
    }
}
