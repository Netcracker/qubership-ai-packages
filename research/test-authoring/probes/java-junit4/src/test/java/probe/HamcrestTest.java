package probe;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.is;

import java.util.List;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class HamcrestTest {
  private final Stream stream = new Stream();

  @Test
  public void booleanWithReason() {
    int expected = 0;
    assertThat("ensureBytes(-1)", expected == stream.ensureBytes(-1));
  }

  @Test
  public void hasItemMatcher() {
    assertThat(List.of(1, 2, 3), hasItem(4));
  }

  @Test
  public void isMatcher() {
    assertThat(stream.ensureBytes(-1), is(0));
  }

  @Test
  public void isMatcherSwapped() {
    assertThat(0, is(stream.ensureBytes(-1)));
  }

  @Test
  public void isMatcherWithReason() {
    assertThat("ensureBytes(-1)", stream.ensureBytes(-1), is(0));
  }
}
