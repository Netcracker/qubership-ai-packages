package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static probe.Stream.ensureBytes;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedClass;
import org.junit.jupiter.params.provider.ValueSource;

/** A @ParameterizedClass with constructor injection: its default name needs -parameters like a method's. */
@ParameterizedClass
@ValueSource(ints = {-1})
class ParameterizedConstructorTest {
    private final int count;

    ParameterizedConstructorTest(int count) {
        this.count = count;
    }

    @Test
    void negativeCountIsRefused() {
        assertEquals(0, ensureBytes(count));
    }
}
