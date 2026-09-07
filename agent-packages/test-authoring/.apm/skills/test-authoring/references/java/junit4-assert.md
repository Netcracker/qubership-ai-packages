# JUnit 4 assertions (`org.junit.Assert`)

Which call prints the operands, where the message goes, and how several assertions report together. The rules that
use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assertEquals(0, actual)` | `expected:<0> but was:<-1>` |
| `assertEquals("ensureBytes(-1)", 0, actual)` | `ensureBytes(-1) expected:<0> but was:<-1>` |
| `assertEquals("Hello world", "Hello, world")` | `ComparisonFailure: expected:<Hello[] world> but was:<Hello[,] world>` |
| `assertTrue(expected == actual)` | `java.lang.AssertionError` and no message at all |
| `assertTrue("ensureBytes(-1) must refuse", expected == actual)` | `ensureBytes(-1) must refuse`, and no values |
| `assertNotNull(null)` | `java.lang.AssertionError` and no message at all |
| `assertArrayEquals(a, b)` | `arrays first differed at element [2]; expected:<3> but was:<4>` |
| `assertThrows(IAE.class, …)` when ISE is thrown | `unexpected exception type thrown; expected:<…IllegalArgumentException> but was:<…IllegalStateException>` |
| `assertThrows(IAE.class, …)` when nothing is thrown | `expected java.lang.IllegalArgumentException to be thrown, but nothing was thrown` |
| `fail()` | `java.lang.AssertionError` and no message at all |

A bare `assertTrue` prints nothing here, not even `expected: <true>`, so the report is the class name and a line
number. Use `assertEquals`, `assertArrayEquals`, `assertSame`, or `assertThrows`, and keep `assertTrue` for a method
that returns a boolean, with a message that names the call.

- **The message is the first argument**, the reverse of JUnit 5, and there is no last-argument overload and no
  `Supplier<String>` form.
- **Operand order is `(expected, actual)`** after the message. A swapped pair prints the bug as the expectation.

## Grouping assertions

There is no `assertAll`. `ErrorCollector` as a `@Rule` collects `checkThat(reason, actual, matcher)` and `addError`
calls and reports them together at the end of the test as `Multiple Failures (2 failures)` with each failure's own
lines; its matchers are Hamcrest's, so the operand order inside `checkThat` is `hamcrest.md`'s.

## Errors

`assertThrows(IllegalArgumentException.class, () -> …)` asserts the type and returns the exception; assert on its
message only for the part the behavior defines. The engine's own `@Test(expected = …)` form is `junit4.md`'s.
