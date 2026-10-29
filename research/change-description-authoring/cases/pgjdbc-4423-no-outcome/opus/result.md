## Commit message

```text
test: run SocketFactoryTest, hidden by the **/*Suite* exclusion

The test task of every module inherited exclude("**/*Suite*") from
build-logic.test-base.gradle.kts, a leftover from the JUnit 4 suite
classes. No suite classes remain, but the mask still matched
SocketFactoryTestSuite, a plain JUnit 5 test, so CI never ran it. The
sourceDistribution copy spec in pgjdbc/build.gradle.kts carried the same
exclusion, so the source distribution did not include the file.

Remove both exclusions. Rename the class to SocketFactoryTest so that
its name no longer suggests a suite. Maven Surefire in the source
distribution then picks it up by its default *Test pattern.
```

## Pull request

**Title:** `test: run SocketFactoryTest, hidden by the **/*Suite* exclusion`

The Gradle test task excluded every class matching `**/*Suite*`, which was left over from the JUnit 4 suite classes. No suite classes remain, but the mask still matched `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI never ran it. The `sourceDistribution` copy spec had the same exclusion, so the source distribution did not include the file.

This change removes both exclusions. The one in `build-logic.test-base.gradle.kts` applies to the `test` task of every module. The class is renamed to `SocketFactoryTest` so that its name no longer suggests a suite, and Maven Surefire in the source distribution picks it up by its default `*Test` pattern. Nothing in the driver jar changes.

The test asserts that the custom socket factory created exactly one socket. It passes against the docker server. The GSS matrix jobs in CI are the first place it runs with a GSS or SSL fallback that could open a second socket.

## CHANGELOG.md

No entry. The change touches only the build and a test, and nothing in the driver jar changes.
