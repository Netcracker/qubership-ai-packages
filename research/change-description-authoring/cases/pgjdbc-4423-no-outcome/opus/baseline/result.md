**Commit message**

```text
test: stop excluding *Suite* classes so SocketFactoryTest runs

The Gradle test task excluded every class matching `**/*Suite*`, a
leftover from the JUnit 4 suite classes. No suite classes remain, but the
mask still matched `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI
never ran it. The source distribution dropped the file for the same
reason.

Remove the exclusion from `build-logic.test-base.gradle.kts`, which the
`test` task of every module inherits, and from the `sourceDistribution`
copy spec. Rename the class to `SocketFactoryTest` so the name no longer
suggests a suite. Maven Surefire in the source distribution now picks it
up by its default `*Test` pattern.

Nothing in the driver jar changes.
```

**Pull request**

Title: `test: stop excluding *Suite* classes so SocketFactoryTest runs`

CI never ran `SocketFactoryTestSuite`. The Gradle test task excluded every class matching `**/*Suite*`, which is left over from the JUnit 4 suite classes. No suite classes remain, but the mask still matched this test, which is a plain JUnit 5 test. The source distribution also dropped the file because of a second copy of the same mask.

## Changes

- Remove `exclude("**/*Suite*")` from `build-logic.test-base.gradle.kts`. The `test` task of every module inherits this exclusion.
- Remove the same exclusion from the `sourceDistribution` copy spec in `pgjdbc/build.gradle.kts`.
- Rename `SocketFactoryTestSuite` to `SocketFactoryTest` so the name no longer suggests a suite. Maven Surefire in the source distribution picks it up by its default `*Test` pattern.

Nothing in the driver jar changes.

## Testing

`./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the docker server.

## For reviewers

The test asserts that the custom socket factory created exactly one socket. The GSS matrix jobs in CI are the first place where it runs with a GSS or SSL fallback, and either one could open a second socket. A failure in those jobs would come from that assertion, not from the build change.

**CHANGELOG.md**

None. The change only affects the build and the tests, and the driver jar stays the same.
