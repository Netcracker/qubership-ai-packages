package m;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

class PropertyTest {
    final Stream stream = new Stream();

    @Test
    void ensureBytesNeverReturnsANegativeCount() {
        PropertyChecker.forAll(Generator.integers(), n -> stream.ensureBytes(n) >= 0);
    }
}
