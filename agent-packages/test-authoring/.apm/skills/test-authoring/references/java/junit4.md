# JUnit 4 as the test engine

What the runner prints, how a parameterized class is named, and what the engine lacks that its successor has. The
assertions that ship with it are `junit4-assert.md`; AssertJ, Truth, and Hamcrest have their own files. The rules that
use this file are in `SKILL.md` §7 and §8.

## What the runner prints

The build tool prints the class, the method, the exception message, and the stack trace, as for JUnit 5. A
parameterized invocation prints the method name followed by the parameter name in brackets: `refused[0]`.

## Parameterized cases

The engine has no parameterized method. `@RunWith(Parameterized.class)` parameterizes the whole class from a static
`@Parameters` method, and every `@Test` in the class runs once per row. Field injection with `@Parameter(0)` replaces
the constructor.

- **Write the `name` pattern; the default is the index.** `@Parameters` with no `name` prints `[0]`, `[1]`, which is a
  location, and the engine has no `{argumentsWithNames}`, so the pattern has to spell the arguments:
  `@Parameters(name = "{index}: ensureBytes({0}) is refused")` prints `refused[0: ensureBytes(-1) is refused]`. The
  placeholders are `{index}` and `{0}`, `{1}`, and so on; keep the pattern in step with the row when a column is
  added.
- **Put the condition in the row where the value cannot say it.** An extra `String` column that names the case, printed
  as `{0}` in the pattern, is the substitute for JUnit 5's `Named`.
- **One parameter set per class.** A second set becomes more rows, or a second class; there is no per-method
  parameterization.

## Errors

The engine's own forms are weaker than an assertion. `@Test(expected = IAE.class)` passes as soon as any line in the
method throws the type, so a setup line that throws it hides whether the act did, and it prints
`Expected exception: java.lang.IllegalArgumentException` with no operands. `ExpectedException` as a `@Rule` states the
expectation before the act and has the same weakness. The assertion library's throw assertion (`junit4-assert.md`,
`assertj.md`) wraps the act alone.

## Order and flakiness

The engine has no random order. `@FixMethodOrder(MethodSorters.NAME_ASCENDING)` pins the order and is not a fix for a
shared-state dependence; remove the shared static instead. A `@ClassRule` or a static field written by one test is the
usual carrier.

## Beside JUnit 5

Where both engines are on the class path (`junit-vintage-engine` runs JUnit 4 classes under the JUnit Platform), a new
test class goes on the engine the neighboring tests of the same unit use. Do not mix `org.junit.Test` and
`org.junit.jupiter.api.Test` in one class. Each engine discovers the class on its own annotations, so the class runs
twice: Vintage constructs it and runs the `org.junit.Test` methods, Jupiter constructs it again and runs the
`org.junit.jupiter.api.Test` methods, and the report lists the class under each engine. The lifecycle splits with the
run. `@Before`, `@After`, and a `@Rule` apply to the Vintage half only; `@BeforeEach`, `@AfterEach`, and an extension
to the Jupiter half only; `@BeforeClass` and `@BeforeAll` each fire once in their own engine's run, so a class-level
fixture is built twice, and where both engines run in one fork, a static field written by one half is read by the
other. A class-level `@Ignore` or `@Disabled`, and a filter or a tag, likewise reaches one half. The silent loss comes
at the build: Surefire on the JUnit 4 provider, or `excludeEngines` in Gradle, runs one engine and reports nothing
about the methods the other would have run, so a green build can mean half the class never executed.
