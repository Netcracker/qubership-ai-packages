package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class NumbersTest {
    @Test
    void sumsBelowFour() {
        assertEquals(6, Numbers.sumBelow(4));
    }

    @Test
    void positiveAndNegative() {
        assertTrue(Numbers.isPositive(5));
        assertFalse(Numbers.isPositive(-5));
    }
}
