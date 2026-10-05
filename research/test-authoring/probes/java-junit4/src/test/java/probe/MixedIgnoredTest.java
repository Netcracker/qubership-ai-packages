package probe;

import org.junit.Ignore;

/** A class-level @Ignore: the Jupiter method is not the Vintage engine's to skip. */
@Ignore("ignored by JUnit 4")
public class MixedIgnoredTest {
  @org.junit.Test
  public void junit4Method() {
    System.out.println("JUnit 4 @Test in an @Ignore class");
  }

  @org.junit.jupiter.api.Test
  void jupiterMethod() {
    System.out.println("Jupiter @Test in an @Ignore class");
  }
}
