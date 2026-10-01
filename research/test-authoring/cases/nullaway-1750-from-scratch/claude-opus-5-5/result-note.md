I added three regression tests for the `SpringHandler` fix, all in `FrameworkTests`. They pass with the fix and fail on the commit before it. Nothing is committed and the production code is untouched. The full `:nullaway:test` suite and `:nullaway:buildWithNullAway` both pass.

Here is the message for the PR author:

---

**Tests for #1750 (`SpringHandler`: `null` used in a SpEL comparison)**

The fix changes which `@Value` strings count as "may be null", so it owes a regression test. These are small tests: one compilation through `CompilationTestHelper`, which is the same level the existing `springValueFieldTest` uses.

Each test holds one case and its control in one source file:
- **The case** is a field whose SpEL mentions `null` only in a comparison. It must not be flagged.
- **The control** is the same expression with one branch changed to return `null`. It must still be flagged, which shows the fix didn't just switch the check off.

| Test | Case (should not be flagged) | Control (still flagged) |
| --- | --- | --- |
| `springValueSpelNullCountsOnlyAsAResultWhenComparedOnTheRight` | `#{bean != null ? bean.name : 'default'}` | `#{bean != null ? null : 'default'}` |
| `springValueSpelNullCountsOnlyAsAResultWhenComparedOnTheLeft` | `#{null == bean ? 'default' : bean.name}` | `#{null == bean ? null : bean.name}` |
| `springValueSpelNullCountsOnlyAsAResultWhenComparedWithoutSpaces` | `#{bean!=null ? bean.name : 'default'}` | `#{bean!=null ? null : 'default'}` |

**Evidence:**
- **Before the fix:** with `SpringHandler.java` reset to `HEAD~1`, all three tests fail with the false positive itself. For example: `Saw unexpected error on line 5 … @NonNull field 'comparedOnly' not initialized`.
- **Each test catches a different wrong fix.** I tried two broken versions of `NULL_COMPARISON_PATTERN`:
  - Dropping the `null ==` / `null !=` alternative fails only `…ComparedOnTheLeft`.
  - Changing `\s*` to `\s+` fails only `…ComparedWithoutSpaces`.

**Why three tests, not one source with all the cases:** I broke cases on purpose to see how `CompilationTestHelper` reports them:
- It lists every unexpected diagnostic, each named by its field.
- It stops at the first missing `// BUG: Diagnostic contains:` marker, so a second missing marker in the same source would go unreported.

So each source has exactly one marker. `springValueFieldTest` already has two markers in one source, so the new cases sit beside it rather than inside it. I left that test's cases and expectations as they were.

**Inputs covered:** the side of the comparison `null` is on (left or right), and no whitespace between operator and `null`. I treated `==` and `!=` as one class, since both are equality comparisons. The right-side test uses `!=` and the left-side test uses `==`.

**One refactor:** `springValueFieldTest` and the new tests now share a new `addSpringValueAnnotationStub` helper (with Javadoc) instead of copying the `@Value` stub. It reuses the file's `ANNOTATION_IMPORTS` and `RETENTION_RUNTIME` constants.

**Proposed, not done:**
- The repository's instructions (`AGENTS.md` / `CLAUDE.md`) don't say which test libraries the project uses or how the test helper reports failures. I suggest adding: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers — reports every unexpected diagnostic with its message, stops at the first missing marker (named by its text and line).` I haven't edited either file; tell me if you want the line added.
- No change to Error Prone's test helper is needed, because one marker per test already gets around the stop-at-first behavior.
