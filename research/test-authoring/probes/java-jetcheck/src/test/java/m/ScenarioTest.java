package m;

import java.util.ArrayList;
import java.util.List;
import org.jetbrains.jetCheck.Generator;
import org.jetbrains.jetCheck.ImperativeCommand;
import org.jetbrains.jetCheck.PropertyChecker;
import org.junit.jupiter.api.Test;

class ScenarioTest {
    @Test
    void reservedCountsNeverGoNegative() {
        PropertyChecker.customized().withSeed(42L).checkScenarios(() -> env -> {
            Stream stream = new Stream();
            List<Integer> reserved = new ArrayList<>();
            ImperativeCommand reserve = cmd -> {
                int n = cmd.generateValue(Generator.integers(), "reserve %s");
                int got = stream.ensureBytes(n);
                if (got < 0) {
                    throw new AssertionError("ensureBytes(" + n + ") returned " + got + " after " + reserved);
                }
                reserved.add(got);
            };
            env.executeCommands(Generator.constant(reserve));
        });
    }
}
