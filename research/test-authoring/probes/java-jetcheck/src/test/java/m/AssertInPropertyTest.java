package m;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

class AssertInPropertyTest {
    final Stream stream = new Stream();

    @Test
    void ensureBytesNeverReturnsANegativeCount() {
        PropertyChecker.customized().withSeed(42L).forAll(Generator.integers(), n -> {
            assertTrue(stream.ensureBytes(n) >= 0, () -> "ensureBytes(" + n + ")");
            return true;
        });
    }
}
