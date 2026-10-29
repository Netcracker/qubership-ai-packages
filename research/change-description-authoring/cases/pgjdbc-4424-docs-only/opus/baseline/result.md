**Title:** `docs: replace JUnit 4 suite instructions in TESTING.md and merge the PR template test items`

---

`TESTING.md` and the pull request template both tell contributors to register a new test class in a test suite, but that suite doesn't exist. All tests under `pgjdbc/src/test` are JUnit 5, and Gradle discovers them without a suite class. This PR replaces those instructions in both files. It changes no code.

## TESTING.md

[Section 5](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/TESTING.md#5---extending-the-test-suite-with-new-tests) used to say that most tests were JUnit 4, and it told contributors to add their test class to the test suite. It now says that new tests use JUnit 5 and go under `pgjdbc/src/test/java/org/postgresql`. It also names the two modules that keep JUnit 4 tests because they need a JUnit 4 runner:

- `pgjdbc-junit4-test` holds the class-unloading test, which needs the JUnit 4 runner of the classloader-leak-test library.
- `pgjdbc-osgi-test` holds the OSGi tests, which run on Pax Exam.

[Section 6](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/TESTING.md#6---guidelines-for-developing-new-tests) replaces the JUnit 4 `Assert` examples with the JUnit 5 `Assertions` methods `assertEquals` and `assertThrows`.

I checked the new text against `master` in two ways:

- `git grep -lE 'org\.junit\.(Test|Assert|runner)' -- pgjdbc/src/test` prints nothing. Running the same search over the whole repository finds files only under `pgjdbc-junit4-test` and `pgjdbc-osgi-test`.
- [Lines 157–162 of `pgjdbc/build.gradle.kts`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/build.gradle.kts#L157-L162) reject `junit:junit` on the test compile classpath. As a result, a JUnit 4 test under `pgjdbc` doesn't compile:

  ```kotlin
          testCompileOnly("junit:junit") {
              because("We use JUnit 5 for testing, so we do not like to have JUnit 4 on the classpath")
              version {
                  rejectAll()
              }
          }
  ```

## Pull request template

The template asked about tests in two places, "New Feature Submissions" and "Changes to Existing Features". One of its questions asked whether new test classes were added to a suite in alphabetical order. A single [Tests and style](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/.github/pull_request_template.md#tests-and-style) section now replaces "New Feature Submissions" and asks four questions:

- Are the changes covered by tests?
- For a bug fix, does the new test fail without the fix?
- Do the tests pass locally?
- Does `./gradlew styleCheck` pass?

The item asking for an explanation of what the changes do moves to "All Submissions" because it applies to every pull request. "Changes to Existing Features" keeps only the question about breaking existing behavior.

## Testing

This PR changes only documentation, so I didn't add or run any tests.
