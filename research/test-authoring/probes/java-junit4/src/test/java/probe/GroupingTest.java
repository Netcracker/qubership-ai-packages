package probe;

import static org.hamcrest.Matchers.is;
import static org.junit.Assert.assertEquals;

import org.junit.FixMethodOrder;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ErrorCollector;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class GroupingTest {
  private final Stream stream = new Stream();

  @Rule
  public final ErrorCollector collector = new ErrorCollector();

  @Test
  public void errorCollectorOneFailure() {
    collector.checkThat("first", stream.ensureBytes(-1), is(0));
  }

  @Test
  public void errorCollectorTwoFailures() {
    int result = stream.ensureBytes(-1);
    collector.checkThat("first", result, is(0));
    collector.addError(new AssertionError("second"));
  }

  @Test
  public void twoAssertsStopAtTheFirst() {
    int result = stream.ensureBytes(-1);
    assertEquals("first", 0, result);
    assertEquals("second", 1, result);
  }
}
