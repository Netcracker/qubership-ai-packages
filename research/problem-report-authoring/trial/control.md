# JUnit XML report names for parameterized tests drop the method name and collide across methods

## Summary

For a `@ParameterizedTest` method, the `name` attribute Gradle writes into the JUnit XML report is the invocation's display name only, such as `[1] value = "plain"`, with no method name attached, so two parameterized methods that share an argument source produce identical `<testcase>` names in the same report file, and a `@ParameterizedClass` argument never appears at all.

## Environment

- Gradle 9.7.1
- JUnit Jupiter 6.1.3
- Tests compiled with `-parameters`

## Reproduction

A class with a plain `@Test` method and two `@ParameterizedTest` methods that share a three-row `String` argument source (`""`, `"plain"`, `"a\b"`) reproduces the first part of the problem:

```java
class ReportNamesTest {
    @Test
    void plainTestMethod() {
    }

    @ParameterizedTest
    @MethodSource("values")
    void firstParameterizedMethod(String value) {
    }

    @ParameterizedTest
    @MethodSource("values")
    void secondParameterizedMethod(String value) {
    }

    static Stream<String> values() {
        return Stream.of("", "plain", "a\b");
    }
}
```

A `@ParameterizedClass` with a `@ParameterizedTest` method inside it reproduces the second part:

```java
@ParameterizedClass
@ValueSource(booleans = {true, false})
class ParameterizedClassNamesTest {
    ParameterizedClassNamesTest(boolean flag) {
    }

    @ParameterizedTest
    @ValueSource(strings = {"x", "y"})
    void methodInParameterizedClass(String value) {
    }
}
```

Run both classes with `gradle test` and inspect `build/test-results/test/TEST-*.xml`.

## Expected behavior

Each `<testcase>` element identifies which method produced it and, for a `@ParameterizedClass`, which class-level argument row it ran under, the same way JUnit's own console output does for the same run:

```text
ParameterizedClassNamesTest > [1] flag = true > methodInParameterizedClass(String) > [1] value = "x"
```

## Actual behavior

`TEST-example.ReportNamesTest.xml` has one `<testcase>` per plain test method, naming the method, and one `<testcase>` per parameterized invocation, naming only the invocation's display name:

```xml
<testcase name="plainTestMethod()" classname="example.ReportNamesTest"/>
<testcase name="[1] value = &quot;&quot;" classname="example.ReportNamesTest"/>
<testcase name="[2] value = &quot;plain&quot;" classname="example.ReportNamesTest"/>
<testcase name="[3] value = &quot;a\\b&quot;" classname="example.ReportNamesTest"/>
<testcase name="[1] value = &quot;&quot;" classname="example.ReportNamesTest"/>
<testcase name="[2] value = &quot;plain&quot;" classname="example.ReportNamesTest"/>
<testcase name="[3] value = &quot;a\\b&quot;" classname="example.ReportNamesTest"/>
```

Six of the seven `<testcase>` elements do not say which method ran, and each of the three parameterized names is written twice, once for `firstParameterizedMethod` and once for `secondParameterizedMethod`, with nothing in the element that tells the two apart.

`TEST-example.ParameterizedClassNamesTest.xml` has the same problem plus a second one: all four invocations, two per constructor argument row, land under only two distinct names, `[1] value = "x"` and `[2] value = "y"`, each written twice. Nothing in the report says whether a given `<testcase>` ran with the constructor argument `flag = true` or `flag = false`.

A test report reader cannot tell, from either file alone, which of several duplicate `<testcase>` entries corresponds to which failure, and cannot use the reported name to re-run one specific case.

## Investigation notes

Reading Gradle's JUnit Platform result-collection code as a starting point, I found two places that disagree about which name to use for a test method result:

- The JUnit Platform test listener stores `TestIdentifier.getLegacyReportingName()` into `TestMethodResult.name`.
- `JUnitXmlResultWriter.discreteTestCase` writes `getDisplayName()` into the `<testcase name="...">` attribute instead of using that stored legacy reporting name.

`getLegacyReportingName()` is documented in the JUnit Platform API to return a JUnit 4-style name that includes the method, which would resolve the collision; `getDisplayName()` is the free-form, human-readable name that for a parameterized invocation is only the argument list. I have not traced why the XML writer path ends up using `getDisplayName()` when a name meant to include the method is already available on the same result, and this is a reading of the source rather than a confirmed root cause.

Setting `junit.jupiter.params.displayname.default` to include `{displayName}` and the method name brings the method name back into each parameterized invocation's display name, which fixes the collision between `firstParameterizedMethod` and `secondParameterizedMethod`. It does not fix the `@ParameterizedClass` case: the configured pattern expands only inside the method-level display name, and the class-level `[1] flag = true` name applies to a container that never gets its own `<testcase>` element in Gradle's XML output, so the constructor argument has nowhere to appear.

For comparison, `junit-platform-console-standalone` writes `methodInParameterizedClass(String)[2][1]` for the same case, which does encode both the method and the two levels of invocation index.

## Possibly related JUnit changes

Searching the JUnit 5 repository, I found two merged pull requests that mention reporting names, #5441 and #5524, and a reference to a 5.14.x maintenance branch. I have not checked what either PR changed or which JUnit release contains them, so I cannot say whether they affect this report. Flagging them here in case they are relevant to whoever picks this up.

## Impact

Any project running more than one `@ParameterizedTest` method against the same or an equally-shaped argument source, or any `@ParameterizedClass`, gets a JUnit XML report where distinct test cases share a `<testcase>` name with no way to distinguish them. This affects CI systems and dashboards that read the Gradle-produced XML report to show which specific case failed.
