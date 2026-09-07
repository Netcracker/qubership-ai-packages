# AssertJ

Which call prints the operands, where the description goes, how several assertions report together, and how an
exception is asserted. The rules that use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assertThat(actual).isEqualTo(0)` | `expected: 0` and `but was: -1` on separate lines |
| `assertThat(actual).as("ensureBytes(%d)", n).isEqualTo(0)` | `[ensureBytes(-1)]` then the same two lines |
| `assertThat(expected == actual).isTrue()` | `Expecting value to be true but was false` |
| `assertThat(List.of(1, 2, 3)).contains(4)` | `Expecting ListN: [1, 2, 3] to contain: [4] but could not find the following element(s): [4]` |

`assertThat(a == b).isTrue()` prints a boolean and nothing else; put the value inside `assertThat` and the expectation
in the method (`isEqualTo`, `containsExactly`, `isInstanceOf`), and keep `isTrue()` for a method that returns a
boolean.

- **The actual value goes inside `assertThat`**, the expected value in the method. Swapping them prints the bug as the
  expectation.
- **The description goes before the assertion method.** `as("ensureBytes(%d)", n)` written after `isEqualTo`
  describes the next assertion in the chain, not the one that failed. `as()` and `describedAs()` add a bracketed
  prefix; `withFailMessage()` and `overridingErrorMessage()` replace the whole text and lose the operands, so use
  them only for a message that carries the values itself.

## Grouping assertions

`SoftAssertions.assertSoftly(softly -> { softly.assertThat(…).isEqualTo(…); … })` runs every assertion and reports all
failures together; a chain of bare `assertThat` calls stops at the first. Use it for several assertions on the fields
of one result. Do not mix it with JUnit's `assertAll`: one grouping mechanism per test.

## Errors

`assertThatThrownBy(() -> …).isInstanceOf(IllegalArgumentException.class)` asserts the type and continues with the
exception's subject; `hasMessageContaining` pins wording, so use it only for the part the behavior defines, and prefer
`hasCauseInstanceOf` or a code where one exists. `assertThatExceptionOfType(…).isThrownBy(…)` reads the same with the
type first. `assertThatCode(() -> …).doesNotThrowAnyException()` alone is the shape §5 rejects where the contract
defines a result; follow it with an assertion on that result. It stands alone only where completing is the contract
(the repair of §5's row *Passes only because nothing threw*), and the test's name then says what no longer throws.
