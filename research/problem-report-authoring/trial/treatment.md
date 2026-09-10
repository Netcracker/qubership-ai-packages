# Notes for whoever files this (not part of the issue body)

- **Target and form.** gradle/gradle, bug report form (`.github/ISSUE_TEMPLATE/10_contributor_bug_report.yml`). The draft below uses that form's field labels and order: Current Behavior, Expected Behavior, Context, Self-contained Reproducer Project, Gradle version, Build scan URL, Your Environment.
- **No AI policy found.** I checked `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/*.yml`, and `.github/ISSUE_TEMPLATE/config.yml` in the local `gradle/gradle` checkout for an AI-disclosure clause or checkbox and found none, so no disclosure line is added to the draft. Confirm this is still current before filing.
- **Raising, not deciding (skill §10):** can whoever files this explain and defend it, and answer follow-up questions, without this draft in hand? That's a question for the human, not something I can certify.
- **Tracker search not done.** I have no browser access in this session, so I have not searched gradle/gradle's issue tracker for an existing report. Search for terms such as `JUnitXmlResultWriter displayName parameterized` and `testcase name parameterized duplicate` before filing, and add the query and nearest hit to the issue.
- **One report, not two.** Both example scenarios below trace to the same line, `JUnitXmlResultWriter.discreteTestCase`, so the same commit would plausibly fix both. See the Expected Behavior section for why they're merged.
- **Reproducer not re-run here.** The Java sources under "Self-contained Reproducer Project" are reconstructed from the investigation notes to match the classes that produced the pasted output, but I did not re-run them in this drafting session (the scratch project isn't present in this environment). Re-run `./gradlew test` against the actual project before filing, and attach the real project (a repository or an archive) rather than this reconstruction, per the form's own field text.

---

# Suggested title

Parameterized test invocations get duplicate or ambiguous names in the JUnit XML report

### Current Behavior

Running parameterized JUnit Jupiter tests through the `test` task writes a JUnit XML report whose `<testcase name="...">` attribute does not identify which test actually ran. Two scenarios show this, both against Gradle 9.7.1 with JUnit 6.1.3 and `-parameters` enabled on the test compile task.

**Scenario 1: two parameterized methods sharing an arguments source.** `example.ReportNamesTest` has one plain `@Test` method, `plainTestMethod()`, and two `@ParameterizedTest` methods, `firstParameterizedMethod(String)` and `secondParameterizedMethod(String)`, both fed the same three-row string source (`""`, `"plain"`, `"a\b"`). `build/test-results/test/TEST-example.ReportNamesTest.xml` reports the plain test correctly, `<testcase name="plainTestMethod()" classname="example.ReportNamesTest"/>`, but all six parameterized invocations collapse onto three repeated names: `<testcase name="[1] value = &quot;&quot;" .../>`, `[2] value = "plain"`, and `[3] value = "a\\b"`, each name written once for `firstParameterizedMethod` and once again for `secondParameterizedMethod`. Six of the seven `<testcase>` entries in the file don't say which method produced them, and three of those six names are indistinguishable from their counterpart under the other method.

**Scenario 2: a `@ParameterizedClass` argument.** `example.ParameterizedClassNamesTest` is a `@ParameterizedClass` with a boolean constructor parameter, `flag` (rows `true` and `false`), containing one `@ParameterizedTest` method, `methodInParameterizedClass(String)`, with two rows (`"x"`, `"y"`). That's four distinct invocations, but `TEST-example.ParameterizedClassNamesTest.xml` reports only two names, `[1] value = "x"` and `[2] value = "y"`, each written twice. Nothing in the file says whether a given entry ran with `flag = true` or `flag = false`.

For contrast, JUnit's own console output for the same run names every invocation uniquely and shows the full chain, for example `ParameterizedClassNamesTest > [1] flag = true > methodInParameterizedClass(String) > [1] value = "x"`. Running the same classes through `junit-platform-console-standalone` instead of Gradle's `test` task also produces a unique name per invocation, `methodInParameterizedClass(String)[2][1]` for that same case, using a class-invocation index and a method-invocation index rather than the argument values. So the information needed to tell these invocations apart exists and is used elsewhere in the same test run; the Gradle-written XML file is the one place it's lost.

Setting the system property `junit.jupiter.params.displayname.default` to a pattern that includes `{displayName}` puts the method name back into `firstParameterizedMethod`/`secondParameterizedMethod`'s invocation names in Scenario 1. It does not help Scenario 2: the pattern is expanded per method, and the `@ParameterizedClass` constructor argument is attached to a container node that Gradle's XML writer never visits, so `flag` stays invisible regardless of this setting.

**Where I traced this (read from the Gradle 9.7.1 source, not yet confirmed with a patched build):**

```
$ git show v9.7.1:platforms/software/testing-base/src/main/java/org/gradle/api/internal/tasks/testing/junit/result/JUnitXmlResultWriter.java | sed -n '225,227p'
    private TestCase discreteTestCase(String className, long classId, TestMethodResult methodResult) {
        return new TestCase(methodResult.getDisplayName(), className, methodResult.getDuration(), discreteTestCaseExecutions(classId, methodResult));
    }
```

`discreteTestCase` writes `methodResult.getDisplayName()` as the `<testcase name>` attribute. `TestMethodResult` (same version) carries a separate `name` field that isn't used here:

```
$ git show v9.7.1:platforms/jvm/testing-jvm-infrastructure/src/main/java/org/gradle/api/internal/tasks/testing/junitplatform/JUnitPlatformTestExecutionListener.java | sed -n '376p'
                return createTestDescriptor(node, node.getLegacyReportingName(), node.getDisplayName());
```

The listener already reads both `TestIdentifier.getLegacyReportingName()` and `getDisplayName()` off the same JUnit Platform node and stores them as two separate fields (`name` and `displayName`) on the Gradle-internal test result. `discreteTestCase` uses only `displayName` when it writes the `<testcase>` element. `git blame` shows this line unchanged since commit `46d60a4c6d72` (November 16, 2020), so this isn't new.

This also isn't a stale-JUnit-version artifact: `getLegacyReportingName()`'s current shape, the one that produces `methodInParameterizedClass(String)[2][1]`-style names, comes from junit-team/junit-framework pull requests #5441 and #5524, both of which are already included in JUnit 6.1.3 (`git tag --contains` on both merge commits lists `r6.1.3`). Whatever the exact fix looks like, it doesn't depend on a JUnit change.

### Expected Behavior

Every `<testcase name="...">` written for a parameterized invocation must let a reader tell, from the name alone, which method (or `@ParameterizedClass` constructor) produced it and which invocation of it this was, using the actual arguments rather than only a position, wherever that content is available from the underlying JUnit Platform node. Per the isolation above, it's available in both scenarios here.

One illustrative rendering that would satisfy this (not a required literal: the exact shape is Gradle's choice, and I haven't confirmed this specific string with a patched build): for Scenario 1, `firstParameterizedMethod(String)[1] value = ""` and `secondParameterizedMethod(String)[1] value = ""` instead of two identical `[1] value = ""` entries; for Scenario 2, a name that carries `flag`'s value alongside the method's own invocation, for example `[flag = true] methodInParameterizedClass(String)[1] value = "x"`.

This covers both scenarios because they reduce to the same root cause: `discreteTestCase` reports `methodResult.getDisplayName()` alone, discarding both the qualifying method name and any enclosing container's own parameters. A fix that makes the written name carry the full chain (the same chain `TestIdentifier.getLegacyReportingName()` already computes, and that the listener already stores in `TestMethodResult.name`) would address both in one change.

Grounding, strongest first:
- **Internal consistency.** Gradle's own `JUnitPlatformTestExecutionListener` already computes and stores a disambiguating name (`TestMethodResult.name`, from `TestIdentifier.getLegacyReportingName()`) for every invocation in both scenarios. `JUnitXmlResultWriter` just never reads that field when it writes the `<testcase>` element. The data the fix needs isn't new; the code already has it.
- **Weaker: what other consumers of the same run expect.** JUnit's own console reporter and `junit-platform-console-standalone`'s report writer both produce a unique name per invocation for this exact run (pasted above), so Gradle's XML writer is the outlier among the tools that consumed it. Tools that key off the JUnit XML `<testcase name>` attribute to attribute a failure to a specific run over time (CI test-history dashboards, flaky-test detectors, IDE report viewers) rely on that attribute being unique per actual invocation across a run.

### Context (optional)

I need every parameterized invocation to have a stable, content-bearing identifier in the JUnit XML report so that CI tooling built on that report (test-history tracking, flaky-test detection) can tell which specific case passed or failed, instead of merging unrelated cases under one repeated name (Scenario 1) or losing the class-level parameter entirely (Scenario 2).

### Self-contained Reproducer Project

`build.gradle.kts`:

```kotlin
plugins {
    java
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:6.1.3"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks.test {
    useJUnitPlatform()
}

tasks.compileTestJava {
    options.compilerArgs.add("-parameters")
}
```

`src/test/java/example/ReportNamesTest.java`:

```java
package example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.stream.Stream;

class ReportNamesTest {

    static Stream<String> values() {
        return Stream.of("", "plain", "a\\b");
    }

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
}
```

`src/test/java/example/ParameterizedClassNamesTest.java`:

```java
package example;

import org.junit.jupiter.params.ParameterizedClass;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

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

Run `./gradlew test`, then inspect `build/test-results/test/TEST-example.ReportNamesTest.xml` and `build/test-results/test/TEST-example.ParameterizedClassNamesTest.xml` for the `<testcase name="...">` values quoted under Current Behavior.

### Gradle version

9.7.1. I confirmed the affected line (`JUnitXmlResultWriter.discreteTestCase`) is unchanged at the exact `v9.7.1` tag (commands above). `git blame` puts its introduction at November 16, 2020, so older Gradle releases likely show the same behavior, though I haven't reproduced on any version other than 9.7.1.

### Build scan URL (optional)

Not established: no build scan was published for this reproduction.

### Your Environment (optional)

Not established: the investigation notes this draft is based on don't record the OS or JDK version used.
