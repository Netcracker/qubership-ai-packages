package m;

import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

class MinValueTest {
    @Test
    void integersNeverReachMinValue() {
        PropertyChecker.customized().withSeed(42L)
            .forAll(Generator.integers(), n -> n != Integer.MIN_VALUE);
    }
}
