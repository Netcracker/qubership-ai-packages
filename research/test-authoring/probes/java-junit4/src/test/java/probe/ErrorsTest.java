package probe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

import org.junit.FixMethodOrder;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class ErrorsTest {
  private final Stream stream = new Stream();

  @Rule
  public final ExpectedException thrown = ExpectedException.none();

  /** Passes: the setup line throws the expected type, and the act that should have thrown never runs. */
  @Test(expected = IllegalArgumentException.class)
  public void expectedAttributeHidesTheSetup() {
    stream.refuse(-1);
    stream.ensureBytes(-1);
  }

  @Test(expected = IllegalArgumentException.class)
  public void expectedAttributeNothingThrown() {
    stream.ensureBytes(-1);
  }

  /** Passes for the same reason as the attribute form. */
  @Test
  public void expectedExceptionRuleHidesTheSetup() {
    thrown.expect(IllegalArgumentException.class);
    stream.refuse(-1);
    stream.ensureBytes(-1);
  }

  @Test
  public void expectedExceptionRuleNothingThrown() {
    thrown.expect(IllegalArgumentException.class);
    stream.ensureBytes(-1);
  }

  /** assertThrows returns the exception, and the message is asserted on it. */
  @Test
  public void assertThrowsReturnsTheException() {
    IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> stream.refuse(-1));
    assertEquals("count must be positive: -1", e.getMessage());
  }
}
