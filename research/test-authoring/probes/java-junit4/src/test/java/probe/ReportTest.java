package probe;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class ReportTest {
  private final Stream stream = new Stream();

  @Test
  public void aNegativeCountIsRefused() {
    assertEquals(0, stream.ensureBytes(-1));
  }
}
