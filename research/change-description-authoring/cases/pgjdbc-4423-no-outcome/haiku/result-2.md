**Commit message**

```text
fix(test): run SocketFactoryTest in CI and the source distribution

The Gradle test task excluded every class whose name contains "Suite",
a mask left over from the JUnit 4 suite classes. No suite classes
remain, but the mask still matched SocketFactoryTestSuite, a plain
JUnit 5 test, so CI never ran it. The source distribution dropped the
file for the same reason.

No caller observes this. The only symptom is that CI never ran the
test.

Remove the exclusion from the test task in
build-logic.test-base.gradle.kts, which every module inherits, and from
the sourceDistribution copy spec in pgjdbc/build.gradle.kts. Rename the
class to SocketFactoryTest so its name no longer suggests a suite.
Maven Surefire in the source distribution finds it by its default
*Test pattern.
```

**Pull request title**

`fix(test): run SocketFactoryTest in CI and the source distribution`

**Pull request description**

The Gradle test task excludes every class whose name contains `Suite`, a mask left over from the JUnit 4 suite classes. No suite classes remain, but the mask still matches `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI does not run it. The source distribution drops the file for the same reason.

The exclusion is removed from the test task in `build-logic.test-base.gradle.kts`, which every module's `test` task inherits, and from the `sourceDistribution` copy spec in `pgjdbc/build.gradle.kts`. The class is renamed to `SocketFactoryTest`, so the name no longer suggests a suite. Maven Surefire in the source distribution picks it up by its default `*Test` pattern.

`./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the Docker server. The test asserts that the custom socket factory creates exactly one socket. The GSS matrix jobs in CI are the first place it runs with a GSS or SSL fallback that could open a second socket, so those jobs are where that case is first exercised.

Nothing in the driver jar changes.

**CHANGELOG.md**

None. This is CI and build maintenance, and nothing in the driver jar changes.
