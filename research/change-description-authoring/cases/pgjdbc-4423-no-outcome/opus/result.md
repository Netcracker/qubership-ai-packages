## Commit message

```text
test: run SocketFactoryTest, which the *Suite* exclusion skipped

The Gradle test task excluded every class matching **/*Suite*, which was
left over from the JUnit 4 suite classes. No suite classes remain, but
the mask still matched SocketFactoryTestSuite. That class is a plain
JUnit 5 test, so CI never ran it. The sourceDistribution copy spec
excluded the same mask, so the file was also missing from the source
distribution.

Drop the mask from build-logic.test-base.gradle.kts, where the test task
of every module inherits it, and from the sourceDistribution copy spec.
Rename the class to SocketFactoryTest. The name no longer suggests a
suite, and Maven Surefire in the source distribution picks the class up
by its default *Test pattern.

The test asserts that the custom socket factory created exactly one
socket. The GSS matrix jobs in CI are the first configuration to run it
with a GSS or SSL fallback that could open a second socket.

Not changed:
Nothing in the driver jar changes.
```

## Pull request

**Title:** `test: run SocketFactoryTest, which the *Suite* exclusion skipped`

**Description:**

The Gradle test task excluded every class matching `**/*Suite*`, which was left over from the JUnit 4 suite classes. No suite classes remain, but the mask still matched `SocketFactoryTestSuite`. That class is a plain JUnit 5 test, so CI never ran it. The `sourceDistribution` copy spec excluded the same mask, so the file was also missing from the source distribution.

This change drops the mask in both places. The exclusion in `build-logic.test-base.gradle.kts` is inherited by the `test` task of every module, not only `pgjdbc`. The class is renamed to `SocketFactoryTest`, so the name no longer suggests a suite, and Maven Surefire in the source distribution picks it up by its default `*Test` pattern. Nothing in the driver jar changes.

`./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the docker server. The test asserts that the custom socket factory created exactly one socket. The GSS matrix jobs in CI are the first place it runs with a GSS or SSL fallback that could open a second socket, so check those jobs before merging.

## CHANGELOG.md

No entry. The change affects only the test build and the test sources in the source distribution, and nothing in the driver jar changes.
