package probe;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

/** Compiled only by the missing-call case: each line is a form JUnit 4 or Hamcrest does not have. */
public class MissingCallTest {
  @Test
  public void formsThatDoNotExist() {
    int actual = new Stream().ensureBytes(-1);
    assertEquals(0, actual, "message last");
    assertEquals(0, actual, () -> "message supplier");
    assertThat(actual, is(0), "reason last");
  }
}
