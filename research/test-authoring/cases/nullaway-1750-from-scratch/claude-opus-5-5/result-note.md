I added five regression tests to `nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java`, next to `springValueFieldTest`. All five fail on the code before the fix and pass on it. The production code is unchanged and nothing is committed. `FrameworkTests` passes (75 tests) and so does `:nullaway:buildWithNullAway`.

---

**Message for the author of #1750**

The fix removes a false "field not initialized" report, but the PR has no test for it. These tests cover it.

**What I added.** These are small tests: they compile a source with `CompilationTestHelper`, like the existing Spring tests. Each test covers one way `null` can appear in an equality comparison, as listed in the Javadoc of `NULL_COMPARISON_PATTERN`:

| Test | Field that must not be reported |
| --- | --- |
| `springValueSpelNullAfterNotEqualsIsNotAResult` | `#{bean != null ? bean.name : 'default'}` (the case from the bug report) |
| `springValueSpelNullAfterEqualsIsNotAResult` | `#{bean == null ? 'default' : bean.name}` |
| `springValueSpelNullBeforeNotEqualsIsNotAResult` | `#{null != bean ? bean.name : 'default'}` |
| `springValueSpelNullBeforeEqualsIsNotAResult` | `#{null == bean ? 'default' : bean.name}` |
| `springValueSpelNullAfterUnspacedNotEqualsIsNotAResult` | `#{bean!=null ? …}` (no spaces around `!=`) |

- **Control field:** each source also has a field `nullResult` that must still be reported. It uses the same comparison, but one branch returns `null`, e.g. `#{bean != null ? null : 'default'}`. Without it, a handler that stopped reporting every `@Value` field would still pass.
- **Why five tests and not one source:** `CompilationTestHelper` stops at the first mismatch (`DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines`, Error Prone 2.50.0, lines 264–289). If all five cases were in one source, the first failure would hide the others.
- **How a failure reads:** the report names each field. A missing diagnostic prints the expected text, which includes the field name. An unexpected one prints every diagnostic with its field name.
- **Stub helper:** I added `addSpringValueAnnotationStub`, in the same style as the file's other stub helpers. I left `springValueFieldTest` as it is.

**Evidence.**
- **Before the fix:** all five new tests fail with the bug itself, for example `springValueSpelNullAfterNotEqualsIsNotAResult`: `Saw unexpected error on line 5 … @NonNull field 'comparedWithNull' not initialized`.
- **Mutants of `NULL_COMPARISON_PATTERN`,** each tried by hand and reverted:

  | Mutant | Test that failed |
  | --- | --- |
  | `[!=]=` changed to `!=` on the right side | `…NullAfterEquals…` only |
  | Same change on the left side | `…NullBeforeEquals…` only |
  | Left alternative deleted | both `…NullBefore…` tests |
  | `\s*` changed to one space | the unspaced test only |
  | Pattern changed to strip every `null` | all five controls, plus `springValueFieldTest` |

**Proposed, not done.**
1. **A gap in the fix:** SpEL also has the word operators `eq` and `ne`. `#{bean ne null ? bean.name : 'default'}` is still reported by mistake, because the pattern only matches `==` and `!=`. I did not add a failing test for it, since the change I was given doesn't claim to handle it. Say if you want the pattern extended and tested.
2. **A test-stack line for `AGENTS.md`/`CLAUDE.md`,** which have none. I suggest: *"Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone `CompilationTestHelper` for checker tests, which stops at the first mismatch and reports a missing diagnostic by line and expected text, and an unexpected one by line with the text of every diagnostic."* I did not edit the file.
3. **Duplicate `@Value` stub:** `springValueFieldTest` still defines the stub inline. It could call the new helper instead, which would remove the second copy without changing what it checks. I left it alone because the task was to add tests.
