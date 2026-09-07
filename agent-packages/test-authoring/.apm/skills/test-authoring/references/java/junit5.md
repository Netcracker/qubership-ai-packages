# JUnit 5 and 6 (Jupiter) as the test engine

What the runner prints, how a parameterized case is named, and how the order of tests is randomized. Assertions are
the assertion library's file: `junit5-assertions.md`, `assertj.md`, `truth.md`, or `hamcrest.md`, whichever the
project uses. The rules that use this file are in `SKILL.md` §7 and §8.

## What the runner prints

The build tool prints the class, the method (or the invocation display name of a parameterized case), the exception
message, and the stack trace. The message is therefore the only free text the T1 reader gets, and it is read after the
class and method names.

A `@Nested` class is printed as part of the container path, so it carries a condition every test inside it shares
(`WhenTheStreamIsClosed`), not a grouping by method. A `@DisplayName` replaces the method name in the report and has to
be kept in step with it; use one only for a name the method identifier cannot spell.

## Parameterized cases

Assume the tests are compiled with `-parameters`. The default display name then prints every argument with its
parameter name: `name()` on both `@ParameterizedTest` and `@ParameterizedClass` defaults to `{default_display_name}`,
which resolves to `junit.jupiter.params.displayname.default` and, where that is unset, to
`[{index}] {argumentSetNameOrArgumentsWithNames}`.

- **Keep the default pattern.** `@ParameterizedTest(name = "{index}: ensureBytes({0}) is refused")` prints the
  arguments the default already prints, and it goes stale as soon as a parameter is added, removed, or reordered,
  because `{0}` then holds a different value.
- **Name the argument, not the pattern,** where its `toString` does not identify the case. `Named.of("empty list",
  List.of())` replaces the `toString` of one argument, and `arguments(named("empty list", List.of()))` is the same
  inside an `Arguments` factory; `argumentSet("minus one", -1)` names a whole row and takes the place of the
  arguments in the default pattern.
- **A class compiled without `-parameters` prints the arguments alone.** Add the compiler flag rather than a pattern
  per method. `@ParameterizedClass` with `@Parameter` field injection prints the field names either way, since it reads
  them from the field rather than from the method signature.
- **Write a `name` of your own only for a fact no argument carries**, such as the expected outcome, and keep
  `{argumentsWithNames}` in it instead of listing `{0}, {1}`. The other placeholders are `{index}`, `{arguments}`,
  `{argumentSetName}`, `{argumentSetNameOrArgumentsWithNames}`, and `{displayName}`. To change the pattern for the whole
  project, set `junit.jupiter.params.displayname.default` in `junit-platform.properties`.

With the case named, the message adds only what the name cannot carry.

## Order and flakiness

`junit.jupiter.testmethod.order.default = org.junit.jupiter.api.MethodOrderer$Random` runs methods in random order and
logs the seed at `CONFIG` level, so raise the logging level to capture it; `junit.jupiter.execution.order.random.seed`
replays it. Fix an order dependence by removing the shared state, not with `@Order` or
`@TestMethodOrder(MethodOrderer.MethodName.class)`.
