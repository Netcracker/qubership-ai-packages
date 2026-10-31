I added two regression tests for the `SpringHandler` fix, both in `FrameworkTests.java`. Neither file is committed and the production code is unchanged. Both tests pass with the fix and both fail on the commit before it. The full `:nullaway:test` suite and `:nullaway:buildWithNullAway` also pass.

**One proposal for you, separate from the PR message:** no reference file covers Error Prone's `CompilationTestHelper`, so I broke two cases on purpose to see what it reports. I suggest adding this line to `CLAUDE.md` (I haven't edited it):

> Tests: JUnit 4 engine and assertions; Error Prone `CompilationTestHelper` stops at the first `// BUG: Diagnostic contains:` marker that gets no diagnostic and names it only by line number; an unexpected diagnostic lists every diagnostic with its field name and source line.

---

**Message for the PR author**

I added two tests to `FrameworkTests` next to `springValueFieldTest`:

- **`springValueNullComparedOnTheRightIsReportedOnlyWhenABranchYieldsNull`** is the case from the PR description, with `null` on the right of `!=`:
  - `#{someBean != null ? someBean.value : 'default'}` gets no report.
  - Control: `#{someBean != null ? null : 'default'}` is still reported. This shows the fix removes only the `null` used in the comparison, not every `null`.
- **`springValueNullComparedOnTheLeftIsReportedOnlyWhenABranchYieldsNull`** covers the other half of the new pattern, with `null` on the left of `==`:
  - `#{null == someBean ? 'default' : someBean.value}` gets no report.
  - Control: the same expression with `null` as a branch result is still reported.

Each test puts the case and its control in one source. They are separate tests because the test helper stops at the first expected diagnostic that's missing and names it only by line number, so two cases in one source could hide each other.

I also moved the `@Value` annotation stub into a helper, `addSpringValueAnnotationStub`, next to `addSpringMockAnnotationStubs`. `springValueFieldTest` now calls it, and its expectations are unchanged.

I checked that both tests catch the bug by running them on the code from before the fix. Both failed with `Saw unexpected error on line 5 … @NonNull field 'comparedOnly' not initialized`, which is the reported false positive. The control fields were reported both before and after the fix.

**Proposed, not done:**
- **Two more operator cases.** `NULL_COMPARISON_PATTERN` accepts `!=` and `==` on both sides, but I tested one operator per side. A test with `== null` on the right and one with `null !=` on the left would catch a regex edit that drops `=` or `!` from `[!=]`. I counted these as variations rather than separate classes of input, but they're cheap to add if you want them.
- **No spaces around the operator.** `someBean!=null` relies on `\s*` allowing zero spaces. A case without spaces would protect that if the pattern gets tightened later.
- **`null` inside a string literal.** `#{'x == null'}` was reported before the fix and is silently accepted now, because the comparison inside the string gets stripped. That's arguably more correct, but it's a change no test pins down. Whether a test is wanted depends on whether the heuristic is meant to see into string literals.
