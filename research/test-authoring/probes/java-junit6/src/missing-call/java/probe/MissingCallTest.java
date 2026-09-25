package probe;

import static org.junit.jupiter.api.Assertions.assertNoSuchCall;

import org.junit.jupiter.api.Test;

/** Calls an assertion the resolved JUnit does not have, as a test written for a newer minor would. */
class MissingCallTest {
    @Test
    void callsAnAssertionThatDoesNotExist() {
        assertNoSuchCall(0, -1);
    }
}
