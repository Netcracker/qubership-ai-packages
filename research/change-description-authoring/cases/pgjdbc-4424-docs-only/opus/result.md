TESTING.md said most tests were JUnit 4 and told contributors to add a new test case to the test suite. The pull request template also asked whether new test classes were added "to an existing test suite in alphabetical order". Both instructions are out of date. The tests under `pgjdbc/src/test` are all JUnit 5, and Gradle finds them without a suite class. Contributors who followed either instruction went looking for a suite that does not exist.

[TESTING.md §5 Extending the test suite with new tests](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/TESTING.md#5---extending-the-test-suite-with-new-tests) now says that new tests use JUnit 5 and go under `pgjdbc/src/test`. It also names the two modules that keep JUnit 4 tests because they need a JUnit 4 runner: `pgjdbc-junit4-test` (classloader-leak-test) and `pgjdbc-osgi-test` (Pax Exam). In [§6 Guidelines for developing new tests](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/TESTING.md#6---guidelines-for-developing-new-tests), the JUnit 4 `Assert` examples are replaced with JUnit 5 `Assertions`.

The template asked about tests in two places: "New Feature Submissions" and "Changes to Existing Features". One [Tests and style](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/.github/pull_request_template.md#tests-and-style) section now holds all the test questions, and it adds one more: for a bug fix, does the new test fail without the fix? The item that asks for an explanation of the changes moves to [All Submissions](https://github.com/pgjdbc/pgjdbc/blob/e6bf0181251063d4cb2fc8324e28fc4f6cde1313/.github/pull_request_template.md#all-submissions), because every pull request needs one.

The JUnit 4 statements in the new text were checked against `master`. `git grep -lE 'org\.junit\.(Test|Assert|runner)' -- pgjdbc/src/test` prints nothing. The same search over the whole repository finds files only under `pgjdbc-junit4-test` and `pgjdbc-osgi-test`. A JUnit 4 test under `pgjdbc` would not compile either, because [`pgjdbc/build.gradle.kts`](https://github.com/pgjdbc/pgjdbc/blob/f171cd8af6fc5f341c765309af0c1ab0db6fbfb7/pgjdbc/build.gradle.kts#L157-L162) rejects `junit:junit` on the test compile classpath:

```kotlin
        testCompileOnly("junit:junit") {
            because("We use JUnit 5 for testing, so we do not like to have JUnit 4 on the classpath")
            version {
                rejectAll()
            }
        }
```
