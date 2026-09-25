package m;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

/** The property of PropertyTest with a pinned seed, so that the counterexample, the blob, and the counts settle. */
@TestMethodOrder(MethodOrderer.MethodName.class)
class SeededTest {
    final Stream stream = new Stream();

    @Test
    void ensureBytesNeverReturnsANegativeCount() {
        PropertyChecker.customized().withSeed(42L)
            .forAll(Generator.integers(), n -> stream.ensureBytes(n) >= 0);
    }

    @Test
    void sameSeedAgain() {
        PropertyChecker.customized().withSeed(42L)
            .forAll(Generator.integers(), n -> stream.ensureBytes(n) >= 0);
    }
}
