package probe;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;

/**
 * Mixes org.junit.Test and org.junit.jupiter.api.Test in one class. Each lifecycle method prints its engine, so the
 * output shows which half ran it; the static counter shows what one half leaves for the other.
 */
public class MixedEnginesTest {
  static int constructed;

  public MixedEnginesTest() {
    constructed++;
    System.out.println("constructed, count " + constructed);
  }

  @BeforeClass
  public static void junit4BeforeClass() {
    System.out.println("JUnit 4 @BeforeClass");
  }

  @BeforeAll
  static void jupiterBeforeAll() {
    System.out.println("Jupiter @BeforeAll");
  }

  @Before
  public void junit4Before() {
    System.out.println("JUnit 4 @Before");
  }

  @After
  public void junit4After() {
    System.out.println("JUnit 4 @After");
  }

  @BeforeEach
  void jupiterBeforeEach() {
    System.out.println("Jupiter @BeforeEach");
  }

  @AfterEach
  void jupiterAfterEach() {
    System.out.println("Jupiter @AfterEach");
  }

  @org.junit.Test
  public void junit4Method() {
    System.out.println("JUnit 4 @Test");
  }

  @org.junit.jupiter.api.Test
  void jupiterMethod() {
    System.out.println("Jupiter @Test");
  }
}
