package probe;

import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

/** Declared out of name order; NAME_ASCENDING runs them a, b, c. */
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class OrderTest {
  @Test
  public void c() {
    System.out.println("ran c");
  }

  @Test
  public void a() {
    System.out.println("ran a");
  }

  @Test
  public void b() {
    System.out.println("ran b");
  }
}
