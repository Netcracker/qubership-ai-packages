## Commit message

```text
test: run SocketFactoryTest in CI and the source distribution

The Gradle test task excluded every class matching "**/*Suite*", a
pattern left over from the JUnit 4 suite classes. No suite class
remains, but the pattern still matched SocketFactoryTestSuite, a plain
JUnit 5 test. The test asserts that the custom socket factory creates
exactly one socket, and no CI job ran that assertion. The
sourceDistribution copy spec dropped the same file for the same reason.

The defect has no symptom to observe: the excluded test never ran, so
nothing failed.

Remove the exclusion from build-logic.test-base.gradle.kts, which the
test task of every module inherits, and from the sourceDistribution
copy spec in pgjdbc/build.gradle.kts. Keeping the pattern would keep a
rule that excludes nothing, since no suite class remains. Rename the
class to SocketFactoryTest: the name no longer suggests a suite, and
Maven Surefire in the source distribution finds it by its default
*Test pattern.
```

## Pull request title

test: run SocketFactoryTest in CI and the source distribution

## Pull request description

```markdown
`SocketFactoryTest` never ran in CI, and the source distribution left it out. The Gradle `test` task of every module excluded `**/*Suite*`, a pattern left over from the JUnit 4 suite classes. No suite class remains, but the pattern still matched `SocketFactoryTestSuite`, a plain JUnit 5 test. The `sourceDistribution` copy spec excluded the same file for the same reason. The test asserts that the custom socket factory creates exactly one socket, so no CI job checked that assertion.

CI and the source distribution now include `SocketFactoryTest`. The pattern is removed rather than narrowed: no suite class remains, so a narrower pattern would exclude nothing. The rename stops the name from suggesting a suite, and it lets Maven Surefire in the source distribution find the class by its default `*Test` pattern. Nothing in the driver jar changes.

The class passes locally against the docker server. The GSS matrix jobs are the first CI jobs to run it with a GSS or SSL fallback that could open a second socket, so those jobs are where to look.
```

## CHANGELOG.md

No entry. The change touches only build configuration and a test class, and nothing in the driver jar changes.
