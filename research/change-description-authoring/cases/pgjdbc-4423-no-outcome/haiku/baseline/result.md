## Commit message

```text
test: run SocketFactoryTest in CI and the source distribution

The Gradle test task excluded every class matching **/*Suite*. That
pattern is left over from the JUnit 4 suite classes, which no longer
exist, but it still matched SocketFactoryTestSuite, a plain JUnit 5
test. CI therefore never ran it. The source distribution dropped the
file for the same reason.

Remove the exclusion from the convention plugin in
build-logic.test-base.gradle.kts, which every module's test task
inherits, and from the sourceDistribution copy spec in
pgjdbc/build.gradle.kts. Rename the class to SocketFactoryTest so the
name no longer suggests a suite. Maven Surefire in the source
distribution finds it by its default *Test pattern.

The driver jar does not change.
```

## Pull request description

`SocketFactoryTestSuite` never ran in CI. The Gradle `test` task excluded every class whose name matched `**/*Suite*`, a pattern left over from the JUnit 4 suite classes. No suite classes remain, but the pattern still matched this plain JUnit 5 test.

The source distribution dropped the file for the same reason.

## Change

- Remove the `**/*Suite*` exclusion from `build-logic.test-base.gradle.kts`. Every module's `test` task inherits it.
- Remove the same exclusion from the `sourceDistribution` copy spec in `pgjdbc/build.gradle.kts`.
- Rename `SocketFactoryTestSuite` to `SocketFactoryTest`. The new name no longer suggests a suite, and Maven Surefire in the source distribution finds the class by its default `*Test` pattern.

The driver jar does not change.

## Verification

- `./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the docker server.

## Notes for review

The test asserts that the custom socket factory creates exactly one socket. The GSS matrix jobs in CI are the first place it runs with a GSS or SSL fallback that could open a second socket.

## CHANGELOG.md

No entry. The change affects only the test build and the source distribution, and the driver jar does not change.
