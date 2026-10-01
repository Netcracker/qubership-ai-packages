I added five regression tests to `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. Each one fails on the code before the fix and passes on the fix. `FrameworkTests` and `./gradlew :nullaway:buildWithNullAway` both pass. Production code is unchanged and nothing is committed.

**Message for the PR author:**

The fix changes when `SpringHandler` decides a `@Value` SpEL expression can produce `null`, and it came with no tests. I added one test per comparison form that your new `NULL_COMPARISON_PATTERN` handles:

- `springValueSpelNullAfterNotEqualsIsNotAPossibleValue`: `bean != null`
- `springValueSpelNullAfterEqualsIsNotAPossibleValue`: `bean == null`
- `springValueSpelNullBeforeNotEqualsIsNotAPossibleValue`: `null != bean`
- `springValueSpelNullBeforeEqualsIsNotAPossibleValue`: `null == bean`
- `springValueSpelNullComparedWithoutSpacesIsNotAPossibleValue`: `bean!=null?…`, which covers the `\s*` in the pattern

Each test compiles one class with two fields:
- **The case:** `null` appears only in the comparison, and no warning is expected.
- **The control:** the same expression, except one branch of the conditional returns `null`. It must still give `@NonNull field '…' not initialized`. That warning fired before the fix too, so it shows the silence comes from the comparison rule and not from the setup.

These are small, in-process compilation tests, which is the same level as the existing `springValueFieldTest`. Nothing outside the compiler is involved, so no larger test is needed.

**Red on the base commit:** I temporarily put back the pre-fix `SpringHandler` and restored it afterwards. All five tests failed for the right reason, for example:
```
FrameworkTests > springValueSpelNullAfterNotEqualsIsNotAPossibleValue FAILED
    java.lang.AssertionError: Saw unexpected error on line 5. All errors:
/TestCase.java:5: warning: [NullAway] @NonNull field 'nameOrDefault' not initialized
/TestCase.java:8: warning: [NullAway] @NonNull field 'nullOrDefault' not initialized
```

**Why five tests instead of one:** I added a temporary test with two missing diagnostics in one compilation. Error Prone's `CompilationTestHelper` reported only the first, by line number (`Did not see an error on line 6 matching field 'a' not initialized`). A second broken case in the same compilation would be hidden, so each case gets its own test with its control.

**Other change in the test file:** the `@Value` stub is now in a helper, `addSpringValueAnnotationStub`, next to `addSpringMockAnnotationStubs`. `springValueFieldTest` now calls it, and its expectations are unchanged.

**Proposed, not done:**
- **Stack line for `CLAUDE.md` / `AGENTS.md`:** neither says how tests are written. I'd add: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers; one compilation stops at the first mismatch and names an unexpected diagnostic by line number.` I didn't edit either file because nobody has agreed to it yet.
- **A label for unexpected diagnostics in the harness:** a failure names an unexpected diagnostic only by its line number. Error Prone offers no label for that, and the helper isn't in this repository, so the fix would be an issue against Error Prone. I couldn't check their tracker for an existing issue, and filed nothing.
- **`springValueFieldTest`:** I left it as it is. It checks several cases in one compilation, so one failure can hide the others.
- **A false positive the pattern doesn't cover:** `#{null == null}` would still be flagged. It isn't a regression, so I wrote no test for it.
