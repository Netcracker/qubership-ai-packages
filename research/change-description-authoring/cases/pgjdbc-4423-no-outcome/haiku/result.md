## Commit message

```text
test: run SocketFactoryTest in CI and the source distribution

The Gradle test task excluded every class matching **/*Suite*, a pattern
left over from the JUnit 4 suite classes. No such classes remain, but the
pattern still matched SocketFactoryTestSuite, a plain JUnit 5 test, so no
CI job ran it. The source distribution had the same exclusion, so it
dropped the file too.

The defect has no symptom outside the build: its only effect is that the
test did not run.

Remove both exclusions and rename the class to SocketFactoryTest. The name
no longer suggests a suite, and Maven Surefire in the source distribution
finds the class by its default *Test pattern.
```

## Pull request title

test: run SocketFactoryTest in CI and the source distribution

## Pull request description

The Gradle test task excludes every class whose name matches `**/*Suite*`. That pattern is left over from the JUnit 4 suite classes, which no longer exist, but it still matches `SocketFactoryTestSuite`, a plain JUnit 5 test. CI never runs that test. The source distribution has the same exclusion and drops the file for the same reason.

This change removes both exclusions and renames the class to `SocketFactoryTest`, so the name no longer suggests a suite. The Gradle exclusion is inherited by the `test` task of every module, so removing it applies to all of them. In the source distribution, Maven Surefire picks the class up by its default `*Test` pattern. The driver jar is unchanged.

Locally, `./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the docker server. The test asserts that the custom socket factory creates exactly one socket. The GSS matrix jobs in CI are the first place it runs with a GSS or SSL fallback, which could open a second socket, so please check those jobs before merge.

## CHANGELOG.md

No entry. The change touches only the test build configuration and one test class; the driver's behavior and jar are unchanged.
