# Google Truth

Which call prints the operands, where the message goes, how several assertions report together, and how an exception
is asserted. Truth has no throw assertion of its own, so a project on it also opens `junit5-assertions.md` or
`junit4-assert.md` for `assertThrows`. The rules that use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assertThat(actual).isEqualTo(0)` | `expected: 0` and `but was : -1` |
| `assertWithMessage("ensureBytes(-1)").that(actual).isEqualTo(0)` | `ensureBytes(-1)` then the same two lines |
| `assertThat(expected == actual).isTrue()` | `expected to be true` |
| `assertThat(List.of(1, 2, 3)).contains(4)` | `expected to contain: 4` and `but was : [1, 2, 3]` |

`assertThat(a == b).isTrue()` prints `expected to be true` and no values; put the value inside `assertThat` and the
expectation in the method, and keep `isTrue()` for a method that returns a boolean.

- **The actual value goes inside `assertThat`**, the expected value in the method.
- **The message goes through `assertWithMessage(…).that(actual)`**, and is added as a first line above the operands.
  `assertWithMessage("ensureBytes(%s)", n)` formats it.

## Grouping assertions

`Expect` as a JUnit 4 `@Rule` records each `expect.that(…)` failure and reports them together at the end of the
test. On JUnit 5 there is no Truth mechanism; wrap the `assertThat` calls in JUnit's `assertAll`
(`junit5-assertions.md`). A chain of bare `assertThat` calls stops at the first.

## Errors

Truth has no throw assertion; use JUnit's `assertThrows` to catch the exception, then `assertThat(e)` for the
`ThrowableSubject`: `hasCauseThat()`, `hasMessageThat().contains(…)` for the part the behavior defines.
