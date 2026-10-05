package probe;

import static org.junit.Assert.assertEquals;

import java.util.List;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

@RunWith(Parameterized.class)
public class ParameterizedDefaultNameTest {
  @Parameters
  public static List<Integer> counts() {
    return List.of(-1, -2);
  }

  @Parameter(0)
  public int count;

  @Test
  public void refused() {
    assertEquals(0, new Stream().ensureBytes(count));
  }
}
