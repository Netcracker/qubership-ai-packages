# What the session established

You spent an afternoon in a scratch project investigating how parameterized JUnit tests appear in the
XML test report Gradle writes. These are your notes. Nothing here has been written up for anyone else.

## The setup

- A scratch Gradle project, Gradle 9.7.1, JUnit 6.1.3, compiled with `-parameters`.
- `example.ReportNamesTest`: one plain `@Test` method `plainTestMethod()`, and two `@ParameterizedTest`
  methods, `firstParameterizedMethod(String)` and `secondParameterizedMethod(String)`, each taking the
  same `String` argument source with three rows: `""`, `"plain"`, `"a\b"`.
- `example.ParameterizedClassNamesTest`: a `@ParameterizedClass` with a boolean constructor parameter
  `flag` (rows `true` and `false`), containing one `@ParameterizedTest` method
  `methodInParameterizedClass(String)` with two rows, `"x"` and `"y"`.

## What you observed

- In `build/test-results/test/TEST-example.ReportNamesTest.xml`, the plain test appears as
  `<testcase name="plainTestMethod()" classname="example.ReportNamesTest"/>`, and the six parameterized
  invocations appear as `<testcase name="[1] value = &quot;&quot;" .../>`, `[2] value = "plain"`,
  `[3] value = "a\\b"` — twice over, once for each method. Six of seven entries do not say which method
  ran, and three names appear twice.
- In `TEST-example.ParameterizedClassNamesTest.xml`, all four cases land under two names,
  `[1] value = "x"` and `[2] value = "y"`, each twice. Nothing says whether a row ran with `flag = true`
  or `flag = false`.
- JUnit's own console output for the same run shows the full chain:
  `ParameterizedClassNamesTest > [1] flag = true > methodInParameterizedClass(String) > [1] value = "x"`.
- You read Gradle's source at `/Users/vlsi/Documents/code/gradle`: the JUnit Platform listener puts
  `TestIdentifier.getLegacyReportingName()` into `TestMethodResult.name`, and
  `JUnitXmlResultWriter.discreteTestCase` writes `getDisplayName()` into the `name` attribute instead.
- `junit-platform-console-standalone` writes `methodInParameterizedClass(String)[2][1]` for the same
  case. You have not tried re-running a single case from any of these names.
- Setting `junit.jupiter.params.displayname.default` brings the method name back into the invocation
  display name. It does not bring back the `@ParameterizedClass` argument: `{displayName}` inside a
  parameterized class expands to the method, and the class-level `name` attribute applies to a
  container that Gradle's XML never shows.
- Searching the JUnit repository you noticed two merged pull requests about reporting names, #5441 and
  #5524, and a mention of a 5.14.x maintenance branch. You have not checked what they changed or which
  release carries them.
- The scratch project is at `/tmp/reproducer` and you can run it, edit it, and re-run anything in it.

## The task

Draft the GitHub issue you would file. Write the finished draft as Markdown to the output file named
in your instructions. Do not open a browser and do not file anything.
