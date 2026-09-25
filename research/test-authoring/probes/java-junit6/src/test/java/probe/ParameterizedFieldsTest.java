package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static probe.Stream.ensureBytes;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.Parameter;
import org.junit.jupiter.params.ParameterizedClass;
import org.junit.jupiter.params.provider.ValueSource;

/** A @ParameterizedClass with field injection: its default name reads the field name, not a method signature. */
@ParameterizedClass
@ValueSource(ints = {-1})
class ParameterizedFieldsTest {
    @Parameter
    int count;

    @Test
    void negativeCountIsRefused() {
        assertEquals(0, ensureBytes(count));
    }
}
