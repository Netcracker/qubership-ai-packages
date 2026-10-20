## Commit message

```text
test: stop excluding *Suite* classes so SocketFactoryTest runs

The test task of every module excluded classes that match **/*Suite*,
a leftover from the JUnit 4 suite classes. No suite classes remain, but
the pattern still matched SocketFactoryTestSuite, which is a plain
JUnit 5 test, so CI never ran it. The sourceDistribution copy spec had
the same exclusion and left the file out of the source distribution.

Remove both exclusions and rename the class to SocketFactoryTest. The
new name no longer suggests a suite. Maven Surefire also picks it up in
the source distribution through its default *Test pattern.

Not changed: the driver jar.
```

## Pull request

**Title:** `test: stop excluding *Suite* classes so SocketFactoryTest runs`

The test task of every module inherits a `**/*Suite*` exclusion from `build-logic.test-base.gradle.kts`, which is left over from the JUnit 4 suite classes. No suite classes remain. The pattern still matched `SocketFactoryTestSuite`, which is a plain JUnit 5 test, so CI never ran it. The `sourceDistribution` copy spec had the same exclusion and left the file out of the source distribution.

This change removes both exclusions and renames the class to `SocketFactoryTest`. The name no longer suggests a suite, and Maven Surefire in the source distribution picks the class up through its default `*Test` pattern. Nothing in the driver jar changes.

`./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the docker server. The test asserts that the custom socket factory created exactly one socket. The GSS matrix jobs on this pull request are the first place it runs with a GSS or SSL fallback that could open a second socket. A failure there on the one-socket assertion would come from the connection path, not from this build change.

## CHANGELOG.md

No entry. The change affects only which tests run and which test sources the source distribution includes, and the driver jar is the same.
