I added five regression tests for the fix in #1750. All five fail on the code before the fix and pass after it. `:nullaway:test --tests FrameworkTests` passes (75 tests) and so does `:nullaway:buildWithNullAway`. I changed only `FrameworkTests.java`, and nothing is committed.

---

**Message for the author of #1750**

Thanks for the fix. Here are the tests it needs. They are small compile-and-check tests in `FrameworkTests`, placed next to `springValueFieldTest`.

**What I added**

- **Five tests, one for each way the fix can see `null` in a comparison:**
  - `bean != null`
  - `bean == null`
  - `null != bean`
  - `null == bean`
  - `bean!=null` with no spaces

  Each test compiles one class with two `@Value` fields:
  - `comparisonOnly`: `null` appears only in the comparison, and it must not be reported. This is the false positive you fixed.
  - `nullResult`: the same expression, but one branch returns `null`, so it must still be reported. This is the control. It shows the silence comes from the comparison rule and not from the test setup.
- **One test per operator and side, not one class with every case.** I ran Error Prone's test helper with two cases broken on purpose. It stops at the first mismatch, and it names an unexpected warning only by line number ("Saw unexpected error on line 18"). Putting the cases in one class would hide every failure after the first.
  - With one case and its control per test, the test name says which case failed, and a line number is never ambiguous. The only unexpected warning possible is on the field that should be silent, and a missing warning is named by its marker text.
  - So I don't propose a labelling feature for the helper.
- **A shared helper, `checkOnlyNullResultSpelIsReported(comparisonOnlySpel, nullResultSpel)`.** It writes the class out in full, and each test passes in only the two SpEL strings.
- **A small helper, `addSpringValueAnnotationStub`, for the `@Value` stub.** It is modelled on `addSpringMockAnnotationStubs`. `springValueFieldTest` now calls it too, and its expectations are unchanged.

**Checks I ran**

- **Before the fix:** I ran the tests with `SpringHandler.java` temporarily put back to `HEAD~1`, then restored it.
  - All five failed with `Saw unexpected error on line 5`. Line 5 is the `comparisonOnly` field, so the failure is the original false positive, not a missing class or method.
  - The controls passed before the fix too.
- **Deliberately breaking the fix:** each break failed exactly the test for that case.
  - Removing the `null ==` / `null !=` half of `NULL_COMPARISON_PATTERN` failed the two `null`-on-the-left tests.
  - Changing `\s*` to `\s+` failed the no-spaces test.

**Proposed, not done**

- **`ne` / `eq` comparisons:** SpEL also accepts the word forms `ne` and `eq` for `!=` and `==`. `@Value("#{bean ne null ? bean.name : 'default'}")` is still reported as not initialized; I confirmed this with a temporary test that I then removed. The PR describes the fix as covering "equality comparisons". Either extend `NULL_COMPARISON_PATTERN` to handle `ne` and `eq` and add a test like the five above, or narrow the description to `==` and `!=`. I didn't add a failing test for it, because that would need a production change.
- **Test-stack line for `CLAUDE.md` / `AGENTS.md`:** neither file says which test libraries the repo uses. I suggest adding this line, which I haven't written into either file: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper for checker tests: one doTest() stops at the first mismatch, names a missing diagnostic by its marker text and an unexpected one by line number only.`
- **`springValueFieldTest` layout:** it still keeps cases that should stay silent and cases that should be reported in separate files. I left it as it is because it isn't part of this change.
