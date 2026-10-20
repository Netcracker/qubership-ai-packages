# Task

Write, for the change below, the commit message (the branch has one commit), the pull request description, and the
entry for `CHANGELOG.md` if the change needs one, in Markdown. The facts come from the author's notes, which were
checked against the build; treat every fact in them as verified, and add none that they do not carry.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`; the maintainers squash or rebase each pull request as they see fit.
- The history uses Conventional Commits subjects with a lowercase verb after the prefix. No issue was filed. No pull
  request template is used.
- `CHANGELOG.md` follows Keep a Changelog, with `### Fixed`, `### Changed`, and `### Security` lists under
  `[Unreleased]`, each entry ending in `[PR #n](…)` and `[Issue #n](…)` links.

## The diff

````diff
diff --git a/build-logic/jvm/src/main/kotlin/build-logic.test-base.gradle.kts b/build-logic/jvm/src/main/kotlin/build-logic.test-base.gradle.kts
index 4e6b90482b..a09e2dab7b 100644
--- a/build-logic/jvm/src/main/kotlin/build-logic.test-base.gradle.kts
+++ b/build-logic/jvm/src/main/kotlin/build-logic.test-base.gradle.kts
@@ -22,7 +22,6 @@ tasks.configureEach<Test> {
     testLogging {
         showStandardStreams = true
     }
-    exclude("**/*Suite*")
     jvmArgs("-Xmx1536m")
     jvmArgs("-Djdk.net.URLClassPath.disableClassPathURLCheck=true")
     if (buildParameters.testJdkVersion >= 21) {
diff --git a/pgjdbc/build.gradle.kts b/pgjdbc/build.gradle.kts
index f5c8a7568d..1a7dbff000 100644
--- a/pgjdbc/build.gradle.kts
+++ b/pgjdbc/build.gradle.kts
@@ -442,7 +442,6 @@ val sourceDistribution = tasks.register<Tar>("sourceDistribution") {
     into("src/test") {
         from("$withoutAnnotations/src/test") {
             exclude("*/org/postgresql/test/osgi/**")
-            exclude("**/*Suite*")
             exclude("*/org/postgresql/test/sspi/*.java")
             exclude("*/org/postgresql/replication/**")
         }
diff --git a/pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTestSuite.java b/pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTest.java
similarity index 97%
rename from pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTestSuite.java
rename to pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTest.java
index 1706fce785..89c8c36e57 100644
--- a/pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTestSuite.java
+++ b/pgjdbc/src/test/java/org/postgresql/test/socketfactory/SocketFactoryTest.java
@@ -18,7 +18,7 @@
 import java.sql.Connection;
 import java.util.Properties;
 
-class SocketFactoryTestSuite {
+class SocketFactoryTest {
 
   private static final String STRING_ARGUMENT = "name of a socket";
 
````

## The author's notes

- The Gradle test task excluded every class matching `**/*Suite*`, a leftover from the JUnit 4 suite classes. No
  suite classes remain, but the mask still matched `SocketFactoryTestSuite`, a plain JUnit 5 test, so CI never ran
  it. The source distribution dropped the file for the same reason.
- The exclusion in `build-logic.test-base.gradle.kts` is inherited by the `test` task of every module; the other is
  in the `sourceDistribution` copy spec. The class is renamed to `SocketFactoryTest`, so the name no longer suggests
  a suite, and Maven Surefire in the source distribution picks it up by its default `*Test` pattern.
- `./gradlew :postgresql:test --tests 'org.postgresql.test.socketfactory.SocketFactoryTest'` passes against the
  docker server. The test asserts that the custom socket factory created exactly one socket. The GSS matrix jobs in
  CI are the first place it runs with a GSS or SSL fallback that could open a second socket.
- Nothing in the driver jar changes.
