package m;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

/** The blob SeededTest's failure prints, fed back as the message says. */
class RecheckTest {
    final Stream stream = new Stream();

    @Test
    void ensureBytesNeverReturnsANegativeCount() {
        PropertyChecker.customized().rechecking("ACoB/////x8=")
            .forAll(Generator.integers(), n -> stream.ensureBytes(n) >= 0);
    }
}
