# Task

Write the pull request description for the change below, in Markdown, ready to paste into GitHub. The facts come from
the author's notes, which were checked against the repository; treat every fact in them as verified, and add none
that they do not carry.

## Repository facts

- Repository: pgjdbc/pgjdbc, the PostgreSQL JDBC driver. Target branch: `master`.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/master` prints
  `merge 0 squash 3 plain 37`. The squash commits carry the branch commit messages as `* subject` bullets.
- The pull request template is not used for descriptions in this repository: the maintainers' own pull requests
  replace it with prose.
- The pull request has one commit and lives on the target repository. `git merge-base origin/master HEAD` is
  `f171cd8af6fc5f341c765309af0c1ab0db6fbfb7`; the head commit of the pull request is
  `e6bf0181251063d4cb2fc8324e28fc4f6cde1313`.

## The commit message

```text
docs: replace JUnit 4 suite instructions in TESTING.md and merge the PR template test items

TESTING.md said most tests were JUnit 4 and told contributors to add a
test class to the test suite, and the pull request template asked
whether new test classes were added to a suite in alphabetical order.
Tests under pgjdbc/src/test are all JUnit 5 now, and Gradle discovers
them without a suite class, so both instructions sent contributors
looking for something that does not exist.

TESTING.md now says that new tests use JUnit 5 and go under
pgjdbc/src/test, and names the two modules that keep JUnit 4 tests
because they need a JUnit 4 runner: pgjdbc-junit4-test
(classloader-leak-test) and pgjdbc-osgi-test (Pax Exam). The JUnit 4
Assert examples become JUnit 5 Assertions.

The template asked about tests in both the "New Feature Submissions"
and the "Changes to Existing Features" sections. A single "Tests and
style" section now asks whether the changes are covered by tests,
whether a bug fix's new test fails without the fix, whether the tests
pass locally, and whether styleCheck passes. The
"explanation of what your changes do" item moves to "All Submissions",
since it applies to every pull request.
```

## The diff

````diff
diff --git a/.github/pull_request_template.md b/.github/pull_request_template.md
index 2641c59be5..982f8a2485 100644
--- a/.github/pull_request_template.md
+++ b/.github/pull_request_template.md
@@ -2,18 +2,17 @@
 
 * [ ] Have you followed the guidelines in our [Contributing](https://github.com/pgjdbc/pgjdbc/blob/master/CONTRIBUTING.md) document?
 * [ ] Have you checked to ensure there aren't other open [Pull Requests](../../pulls) for the same update/change?
+* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
 
 <!-- You can erase any parts of this template not applicable to your Pull Request. -->
 
-### New Feature Submissions:
+### Tests and style:
 
-1. [ ] Does your submission pass tests?
-2. [ ] Does `./gradlew styleCheck` pass ?
-3. [ ] Have you added your new test classes to an existing test suite in alphabetical order?
+* [ ] Are your changes covered by tests?
+* [ ] For a bug fix: does the new test fail without your fix?
+* [ ] Do the tests pass locally with your changes?
+* [ ] Does `./gradlew styleCheck` pass?
 
 ### Changes to Existing Features:
 
 * [ ] Does this break existing behaviour? If so please explain.
-* [ ] Have you added an explanation of what your changes do and why you'd like us to include them?
-* [ ] Have you written new tests for your core changes, as applicable?
-* [ ] Have you successfully run tests with your changes locally?
diff --git a/TESTING.md b/TESTING.md
index f6bc2aae22..a43213ce92 100644
--- a/TESTING.md
+++ b/TESTING.md
@@ -133,35 +133,9 @@ The aggregate report is written to:
 
 ## 5 - Extending the test suite with new tests
 
-Most of the tests are written with JUnit4, however it is recommended to create new tests with JUnit5.
-
-If you're not familiar with JUnit, we recommend that you
-first read the introductory article [JUnit Test Infected:
-Programmers Love Writing Tests](http://junit.sourceforge.net/doc/testinfected/testing.htm).
-Before continuing, you should ensure you understand the
-following concepts: test suite, test case, test, fixture,
-assertion, failure.
-
-The test suite consists of test cases, which consist of tests.
-A test case is a collection of tests that test a particular
-feature. The test suite is a collection of test cases that
-together test the driver - and to an extent the PostgreSQL
-backend - as a whole.
-
-If you decide to add a test to an existing test case, all you
-need to do is add a method with a name that begins with "test"
-and which takes no arguments. JUnit will dynamically find this
-method using reflection and run it when it runs the test case.
-In your test method you can use the fixture that is setup for it
-by the test case.
-
-If you decide to add a new test case, you should do two things:
-
-1. Add a test class. It should
-   contain `setUp()` and `tearDown()` methods that create and destroy
-   the fixture respectively.
-2. Add your test class in `$JDBC_SRC/src/test/java/org/postgresql/test`. This will make the test case
-   part of the test suite.
+Write new tests with JUnit 5 and put them under `pgjdbc/src/test/java/org/postgresql`, next to the tests for the same feature. Gradle discovers test classes on its own, so there is no suite class to register a new test in.
+
+Two modules keep JUnit 4 tests that cannot run on JUnit 5: `pgjdbc-junit4-test` holds the class-unloading test, which needs the JUnit 4 runner of the classloader-leak-test library, and `pgjdbc-osgi-test` holds the OSGi tests, which run on Pax Exam. Add a test to one of them only when it needs that runner.
 
 ## 6 - Guidelines for developing new tests
 
@@ -173,16 +147,9 @@ by dropping the table before running the test (ignoring errors).
 The recommended pattern for creating and dropping tables can be
 found in the example in section 7 below.
 
-Please note that JUnit provides several convenience methods to
-check for conditions. See the `Assert` class in the Javadoc
-documentation of JUnit, which is installed on your system. For
-example, you can compare two integers using
-`Assert.assertEquals(int expected, int actual)`. This method
-will print both values in case of a failure.
-
-To simply report a failure use `Assert.fail()`.
-
-The JUnit FAQ explains how to test for a thrown exception.
+Use the assertion methods of JUnit 5 `Assertions`, such as
+`assertEquals(expected, actual)`, which prints both values on failure,
+and `assertThrows` to check for an exception.
 
 As a rule, the test suite should succeed. Any errors or failures
 - which may be caused by bugs in the JDBC driver, the backend or
````

## What the author checked

- `git grep -lE 'org\.junit\.(Test|Assert|runner)' -- pgjdbc/src/test` on `master` prints nothing. The same search over
  the whole repository finds files only under `pgjdbc-junit4-test` and `pgjdbc-osgi-test`.
- At the merge-base commit, lines 157 to 162 of `pgjdbc/build.gradle.kts` reject `junit:junit` on the test compile
  classpath, so a JUnit 4 test under `pgjdbc` does not compile:

  ```kotlin
          testCompileOnly("junit:junit") {
              because("We use JUnit 5 for testing, so we do not like to have JUnit 4 on the classpath")
              version {
                  rejectAll()
              }
          }
  ```

- `TESTING.md` numbers its sections in the heading text. At both commits, section 5 is
  `## 5 - Extending the test suite with new tests` and section 6 is `## 6 - Guidelines for developing new tests`;
  GitHub renders their anchors as `#5---extending-the-test-suite-with-new-tests` and
  `#6---guidelines-for-developing-new-tests`.
- The template's section headings are `### All Submissions:`, `### New Feature Submissions:`, and
  `### Changes to Existing Features:` at the merge base, and `### All Submissions:`, `### Tests and style:`, and
  `### Changes to Existing Features:` at the head commit. GitHub renders them as `#all-submissions`,
  `#new-feature-submissions`, `#changes-to-existing-features`, and `#tests-and-style`.
- No code changes; no test was added or run.
