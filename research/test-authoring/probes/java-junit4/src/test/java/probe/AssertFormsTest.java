package probe;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class AssertFormsTest {
  private final Stream stream = new Stream();

  @Test
  public void assertArrayEqualsPlain() {
    assertArrayEquals(new int[] {1, 2, 3}, new int[] {1, 2, 4});
  }

  @Test
  public void assertEqualsPlain() {
    assertEquals(0, stream.ensureBytes(-1));
  }

  @Test
  public void assertEqualsStrings() {
    assertEquals("Hello world", "Hello, world");
  }

  @Test
  public void assertEqualsSwapped() {
    assertEquals(stream.ensureBytes(-1), 0);
  }

  @Test
  public void assertEqualsWithMessage() {
    assertEquals("ensureBytes(-1)", 0, stream.ensureBytes(-1));
  }

  @Test
  public void assertNotNullPlain() {
    assertNotNull(null);
  }

  @Test
  public void assertThrowsNothingThrown() {
    assertThrows(IllegalArgumentException.class, () -> stream.ensureBytes(-1));
  }

  @Test
  public void assertThrowsWrongType() {
    assertThrows(IllegalArgumentException.class, () -> {
      throw new IllegalStateException("closed");
    });
  }

  @Test
  public void assertTruePlain() {
    int expected = 0;
    assertTrue(expected == stream.ensureBytes(-1));
  }

  @Test
  public void assertTrueWithMessage() {
    int expected = 0;
    assertTrue("ensureBytes(-1) must refuse", expected == stream.ensureBytes(-1));
  }

  @Test
  public void failPlain() {
    fail();
  }
}
