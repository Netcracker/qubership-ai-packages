## Commit message

```text
test: drop the **/*Suite* exclusion so SocketFactoryTest runs

The Gradle test configuration excluded every class matching **/*Suite*.
The pattern was left over from the JUnit 4 suite classes. No suite
classes remain, but it still matched SocketFactoryTestSuite, which is a
plain JUnit 5 test, so CI never ran it. The exclusion lived in
build-logic.test-base.gradle.kts, so the test task of every module
inherited it. The sourceDistribution copy spec had the same pattern and
left the file out of the source distribution.

The commit removes both exclusions and renames the class to
SocketFactoryTest. The name no longer suggests a suite, and Maven
Surefire in the source distribution picks the class up through its
default *Test pattern. The pattern is removed rather than kept beside
the rename because the only classes it still matched were tests that
should run.

Not changed:
The driver jar has the same contents.
```

## Pull request

**Title:** `test: run SocketFactoryTest, which the **/*Suite* test exclusion skipped`

The Gradle test configuration excluded every class matching `**/*Suite*`, which was left over from the JUnit 4 suite classes. No suite classes remain, but the pattern still matched `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI never ran it. The exclusion is in `build-logic.test-base.gradle.kts`, which the `test` task of every module inherits. The `sourceDistribution` copy spec had the same pattern and left the file out of the source tarball.

This change removes both exclusions and renames the class to `SocketFactoryTest`. The name no longer suggests a suite, and Maven Surefire in the source distribution picks the class up through its default `*Test` pattern. Nothing in the driver jar changes.

The test asserts that the custom socket factory created exactly one socket. The GSS matrix jobs are the first place it runs with a GSS or SSL fallback that could open a second socket. That means this pull request gives the first result for those configurations.

## CHANGELOG.md

No entry. The change affects only test runs and the test sources in the source distribution, and the driver jar has the same contents.
