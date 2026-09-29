package probe;

import static org.junit.Assert.assertEquals;

import java.util.List;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

/** The first column names the case, the substitute for JUnit 5's {@code Named}; two rows share a name. */
@RunWith(Parameterized.class)
public class ParameterizedConditionTest {
  @Parameters(name = "{0}")
  public static List<Object[]> counts() {
    return List.of(
        new Object[] {"minus one", -1},
        new Object[] {"negative", -2},
        new Object[] {"negative", -3});
  }

  @Parameter(0)
  public String condition;

  @Parameter(1)
  public int count;

  @Test
  public void refused() {
    assertEquals(0, new Stream().ensureBytes(count));
  }
}
