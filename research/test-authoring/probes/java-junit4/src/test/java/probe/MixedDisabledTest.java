package probe;

import org.junit.jupiter.api.Disabled;

/** A class-level @Disabled: the JUnit 4 method is not the Jupiter engine's to skip. */
@Disabled("disabled by Jupiter")
public class MixedDisabledTest {
  @org.junit.Test
  public void junit4Method() {
    System.out.println("JUnit 4 @Test in a @Disabled class");
  }

  @org.junit.jupiter.api.Test
  void jupiterMethod() {
    System.out.println("Jupiter @Test in a @Disabled class");
  }
}
