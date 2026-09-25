package m;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

class ValueToStringTest {
    final Stream stream = new Stream();

    record Count(int n) {}

    @Test
    void ensureBytesNeverReturnsANegativeCount() {
        PropertyChecker.customized().withSeed(42L)
            .forAll(Generator.integers().map(Count::new), c -> stream.ensureBytes(c.n()) >= 0);
    }
}
