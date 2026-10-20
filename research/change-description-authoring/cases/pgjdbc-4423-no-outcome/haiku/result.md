**Commit message**

```text
test: stop the Suite exclusion from hiding SocketFactoryTest

The Gradle test task excluded every class matching **/*Suite*, a
pattern left over from the JUnit 4 suite classes. No suite classes
remain, but the pattern still matched SocketFactoryTestSuite, a plain
JUnit 5 test, so CI never ran it. The source distribution dropped the
file for the same reason. An excluded test fails nothing, so the defect
has no symptom beyond the test never running.

The test asserts that the custom socket factory creates exactly one
socket. The GSS matrix jobs are the first CI jobs that run it with a
GSS or SSL fallback that could open a second socket.

Remove the exclusion from the test task convention in
build-logic.test-base.gradle.kts, which every module inherits, and from
the sourceDistribution copy spec in pgjdbc/build.gradle.kts. Remove it
rather than narrow it, because no suite classes remain for it to match.
Rename the class to SocketFactoryTest so the name does not suggest a
suite. Maven Surefire in the source distribution picks it up by its
default *Test pattern. The driver jar does not change.
```

**Pull request title**

test: run SocketFactoryTest in CI and the source distribution

**Pull request description**

The Gradle `test` task excluded every class whose name matches `**/*Suite*`, a pattern left over from the JUnit 4 suite classes. No suite classes remain, but the pattern still matched `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI never ran it. The source distribution dropped the file for the same reason. An excluded test fails nothing, so the defect shows only as a test that never runs.

The exclusion is removed from the test task convention in `build-logic.test-base.gradle.kts`, which every module inherits, and from the `sourceDistribution` copy spec in `pgjdbc/build.gradle.kts`. It is removed rather than narrowed, because no suite classes remain for it to match. The class is renamed to `SocketFactoryTest`, so the name no longer suggests a suite, and Maven Surefire in the source distribution picks it up by its default `*Test` pattern. The driver jar does not change.

The test asserts that the custom socket factory creates exactly one socket. Run `./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` against the docker server; it passes. The test is renamed, not new, but this change makes CI run it.

The GSS matrix jobs are the first CI jobs that run this test with a GSS or SSL fallback that could open a second socket, so that is where the one-socket assertion first applies in CI.

**CHANGELOG.md**

No entry. The change touches only test and build configuration, and the driver jar does not change.
