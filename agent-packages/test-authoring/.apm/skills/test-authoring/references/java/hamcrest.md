# Hamcrest

Which call prints the operands and where the reason goes. Hamcrest is a matcher library, so `assertThat` here is
`org.hamcrest.MatcherAssert.assertThat`, and a project on it borrows grouping and throw assertions from the JUnit
assertions it also has on the class path: open `junit5-assertions.md` or `junit4-assert.md` as well. The rules that
use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assertThat(actual, is(0))` | `Expected: is <0>` and `but: was <-1>` |
| `assertThat("ensureBytes(-1)", actual, is(0))` | `ensureBytes(-1)` then the same two lines |
| `assertThat("ensureBytes(-1)", expected == actual)` | `ensureBytes(-1)` and nothing else |

The two-argument `assertThat(reason, boolean)` prints the reason only; use a matcher (`is`, `equalTo`, `contains`,
`hasItem`, `instanceOf`), which prints both sides, and keep the boolean form for a method that returns a boolean.

- **The reason is the first argument**, before the actual value, the reverse of JUnit 5.
- **The actual value comes before the matcher**, and the matcher wraps the expected value: `assertThat(actual,
  is(expected))`. A swapped pair prints the bug as the expectation.

## Grouping assertions

Hamcrest has no soft assertion. Use JUnit's: `assertAll` from `junit5-assertions.md`, `ErrorCollector.checkThat` from
`junit4-assert.md`, both of which take Hamcrest matchers.

## Errors

Hamcrest has no throw assertion. Use JUnit's `assertThrows`, then match on the exception:
`assertThat(e, instanceOf(…))`, `assertThat(e.getMessage(), containsString(…))` for the part the behavior defines.
