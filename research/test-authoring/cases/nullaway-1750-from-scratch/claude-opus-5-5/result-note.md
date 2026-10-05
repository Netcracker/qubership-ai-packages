I added four regression tests to `FrameworkTests.java` for the SpEL `null`-comparison fix. Production code is unchanged and nothing is committed. `FrameworkTests` passes (74 tests) and so does `:nullaway:buildWithNullAway`. I ran the new tests against the pre-fix `SpringHandler` and they failed, then restored the file.

Here is the message I'd leave for the author of #1750:

---

**Tests added (in `FrameworkTests`, beside `springValueFieldTest`)**

The fix changed behavior and came with no test, so I added one test for each comparison form named in the Javadoc of `NULL_COMPARISON_PATTERN`:

- `springValueNullAfterNotEqualsIsNotAPossibleValue`: `settings != null`
- `springValueNullAfterEqualsIsNotAPossibleValue`: `settings == null`
- `springValueNullBeforeNotEqualsIsNotAPossibleValue`: `null != settings`
- `springValueNullBeforeEqualsIsNotAPossibleValue`: `null == settings`

Each test compiles one class with two `@Value` fields:
- **The case:** the ternary yields a non-null value, e.g. `#{settings != null ? settings.name : 'default'}`. It must not be reported.
- **A control:** the same expression with that branch replaced by `null`. It must still be reported as not initialized.

The control shows that the case goes silent because of the comparison rule, not because of the setup. Fields are checked one at a time, so the two can share one compilation.

These are ordinary `CompilationTestHelper` tests that compile in-process, the smallest level where the handler can be seen through the NullAway check. `containsNullSpELExpression` is private, so it is tested only through that check.

**Evidence**
- **Red on the base commit:** with `SpringHandler` from `HEAD~1`, all four fail with `Saw unexpected error on line 5 … @NonNull field 'nameOrDefault' not initialized`. That is the false positive from the bug report. All four controls report on both the old and the new code.
- **They tell the forms apart:** I narrowed the pattern to `!=\s*\bnull\b|\bnull\b\s*==` and exactly `…AfterEquals…` and `…BeforeNotEquals…` failed. With only two cases, that change would have gone unnoticed.

**Why four separate tests instead of one class with all of them**

I checked how `CompilationTestHelper` reports failures by breaking two cases on purpose:
- It stops at the first mismatch.
- It identifies that mismatch by line number. A missing diagnostic also shows the marker's text; an unexpected one also lists every diagnostic.

Putting four cases in one compilation would mean a failure in one hides the others. Each `// BUG: Diagnostic contains:` marker names its field, so a missing diagnostic still says which case it was.

**Refactoring of an existing test**

I moved the `@Value` annotation stub into a helper, `addSpringValueAnnotationStub`, written like the existing `addSpringMockAnnotationStubs`. `springValueFieldTest` now calls it, and its expectations are unchanged.

**Proposed, not done**
- **A stack line for `CLAUDE.md`/`AGENTS.md`**, for example: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper, which stops at the first mismatch and names it by line number (missing diagnostics also show the marker text).` I didn't edit either file.
- **No-space operators are untested.** Forms like `settings!=null` rely on `\s*` and could get one more case if you want it.
- **Other comparisons still count as a possible value.** `null` used as a method argument (`#{T(java.util.Objects).equals(a, null)}`) or with `<`, `>`, `<=`, `>=` is still flagged. This is likely a remaining false positive, outside this fix and with no test.
