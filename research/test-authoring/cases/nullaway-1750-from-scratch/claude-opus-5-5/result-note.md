I added four regression tests for the `SpringHandler` fix to `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`. All four fail on the code before the fix and pass after it. Production code is unchanged and nothing is committed. `FrameworkTests` and `./gradlew :nullaway:buildWithNullAway` both pass.

**Message for the PR author:**

> This fix had no tests, so I added four regression tests next to `springValueFieldTest`. They are small tests: each compiles one source with the `@Value` stub through `CompilationTestHelper`. No larger test is needed, because the change is a string heuristic inside the handler.
>
> **Shared setup.** The new tests and `springValueFieldTest` now get the `@Value` stub from one helper, `addSpringValueAnnotationStub`, built the same way as `addSpringMockAnnotationStubs`. The existing test's expectations are unchanged.
>
> **What each test covers.** Each test checks one way `null` can appear as an equality operand. In each, a field whose `null` is only compared must get no warning, and a control field must still be reported. The control differs only by having `null` as a possible result.
>
> | Test | Field that must not be reported | Control that must still be reported |
> | --- | --- | --- |
> | `springValueSpelNullIsAValueOnlyWhenNotAnOperandOfNotEquals` (the case from the issue) | `#{someBean != null ? someBean.value : 'default'}` | `#{someBean != null ? null : 'default'}` |
> | `…NotAnOperandOfEquals` | `#{someBean == null ? 'default' : someBean.value}` | same, with `null` as the result |
> | `…NotTheLeftOperandOfAComparison` | `#{null != someBean ? …}` (covers the regex's `null !=` branch) | same, with `null` as the result |
> | `…NotAnOperandOfAComparisonWithoutSpaces` | `#{someBean!=null?someBean.value:'default'}` (covers `\s*` matching no spaces) | same, with `null` as the result |
>
> **Why one rule per test.** I broke two cases on purpose: one compilation stops at the first mismatch. It names a missing diagnostic by line number plus the `// BUG: Diagnostic contains:` text. For an unexpected one it gives the line number and prints every diagnostic with its source line. So each test holds one case and its control, and the markers name the field so the report says which case broke.
>
> **Red run on the base commit** (`HEAD~1`'s `SpringHandler.java` with the new tests): 4 of 5 failed, each one with:
> ```
> java.lang.AssertionError: Saw unexpected error on line 5. All errors:
> /Test.java:5: warning: [NullAway] @NonNull field 'comparedOnly' not initialized
> /Test.java:8: warning: [NullAway] @NonNull field 'comparedAndReturned' not initialized
> ```
> The false positive is reported on line 5, and the control on line 8 still reports before the fix.
>
> **Proposed, not done:**
> - **SpEL's word operators are still flagged.** `#{someBean ne null ? … }` and `eq null` still get the false positive, because the new pattern only matches `==` and `!=`. I wrote no test for this because it would fail against the current code. It's worth a follow-up fix with its own tests.
> - **Test stack line.** `CLAUDE.md`/`AGENTS.md` don't name the test stack. I suggest adding: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper with // BUG: Diagnostic contains: markers, which stops at the first mismatch and names it by line plus marker text.` I didn't edit either file.
