# JUnit 5 and 6 assertions (`org.junit.jupiter.api.Assertions`)

Which call prints the operands, where the message goes, how several assertions report together, and how an exception
is asserted. The rules that use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assertEquals(0, actual)` | `expected: <0> but was: <-1>` |
| `assertEquals(0, actual, "ensureBytes(-1)")` | `ensureBytes(-1) ==> expected: <0> but was: <-1>` |
| `assertTrue(expected == actual)` | `expected: <true> but was: <false>` |
| `assertTrue(expected == actual, "ensureBytes(-1) must refuse")` | `ensureBytes(-1) must refuse ==> expected: <true> but was: <false>` |
| `assertNotNull(null)` | `expected: not <null>` |
| `assertArrayEquals(a, b)` | `array contents differ at index [2], expected: <3> but was: <4>` |
| `assertIterableEquals(a, b)` | `iterable contents differ at index [2], expected: <3> but was: <4>` |
| `assertThrows(IAE.class, …)` when ISE is thrown | `Unexpected exception type thrown, expected: <…IllegalArgumentException> but was: <…IllegalStateException>` |
| `assertThrows(IAE.class, …)` when nothing is thrown | `Expected java.lang.IllegalArgumentException to be thrown, but nothing was thrown.` |
| `fail()` | an empty message |
| `assertAll(…)` with two failures | `Multiple Failures (2 failures)` followed by each failure's own line |

A message on `assertTrue` does not rescue it: the operands are still `true` and `false`. Use `assertEquals`,
`assertArrayEquals`, `assertIterableEquals`, `assertSame`, or `assertThrows`, which print what the reader needs, and
keep `assertTrue` for a method that returns a boolean.

- **Operand order is `(expected, actual)`.** A swapped pair prints the bug as the expectation.
- **The message is the last argument**, a `String` or a `Supplier<String>`, and the framework appends its own clause
  after `==>`. The message carries the function and the input (`ensureBytes(-1)`), never the values.

## Grouping assertions

`assertAll("account", () -> assertEquals(…), () -> assertEquals(…))` runs every assertion and reports all failures
in one `MultipleFailuresError`; a chain of bare `assertEquals` calls stops at the first. Use `assertAll` for several
assertions on the fields of one result.

## Errors

`assertThrows(IllegalArgumentException.class, () -> …)` asserts the type and returns the exception; assert on its
message only for the part the behavior defines (`assertTrue(e.getMessage().contains("negative"))` is a change detector
for wording, so prefer the type, a cause, or a code where one exists). `assertThrowsExactly` refuses a subclass, which
is right only where the subclass is the behavior.
