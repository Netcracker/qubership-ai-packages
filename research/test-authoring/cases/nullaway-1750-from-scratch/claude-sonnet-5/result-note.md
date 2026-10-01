Here's the note I'd leave for the PR author:

---

This fix shipped with no tests, so I added six cases to the existing `springValueFieldTest` in `FrameworkTests.java`, joining the test that already covers this exact heuristic rather than starting a new one.

**Added to `NegativeCases`** (should not be flagged) — one per form your new javadoc names (`== null`, `!= null`, `null ==`, `null !=`):
- `ternaryNullCheckBeforeDereference`: `#{someBean != null ? someBean.value : 'default'}` — this is the exact false positive from the bug report.
- `ternaryNullEqualityCheckBeforeDereference`: `#{someBean == null ? 'default' : someBean.value}`
- `ternaryNullBeforeNotEqualsCheck`: `#{null != someBean ? someBean.value : 'default'}`
- `ternaryNullBeforeEqualsCheck`: `#{null == someBean ? someBean.value : 'default'}`

I kept all four rather than just the reported case because `NULL_COMPARISON_PATTERN` is two alternations (`null` after the operator vs. before it) over a two-letter character class (`!=`/`==`); a one-sided regression test wouldn't notice if one alternative or one operator silently stopped matching.

**Added to `PositiveCases`** (should still be flagged) as controls, pairing with two of the above by changing only the ternary's value branch to `null`:
- `ternaryNullCheckWithNullBranch`: `#{someBean != null ? null : 'default'}` — this is your own "still correctly flags" example.
- `ternaryNullBeforeNotEqualsCheckWithNullBranch`: `#{null != someBean ? null : 'default'}`

These show the stripping is selective (removes only the comparison occurrence) rather than accidentally swallowing a real null adjacent to it, in both regex directions.

I verified red/green: with `SpringHandler.java` reverted to the pre-fix revision, all four new negative cases are (wrongly) flagged — confirmed by running `springValueFieldTest`, which prints all four as unexpected errors — and both controls are flagged on both revisions, so they're true non-regression controls, not artifacts of the fix. With the fix restored, `springValueFieldTest`, all of `FrameworkTests`, the full `:nullaway:test` run, and `:nullaway:buildWithNullAway` all pass.

One thing I did **not** do: the repository's `AGENTS.md`/`CLAUDE.md` names no test engine/assertion-library stack line, so per the test-authoring skill I'm only proposing it here rather than writing it into the file myself. Proposed line: `Tests: JUnit 4 engine; CompilationTestHelper (error-prone) as the assertion library — one `doTest()` call compiles all added sources and stops at the first missing expected diagnostic, but reports all unexpected (unmarked) diagnostics at once; a case is named by its field/method identifier since the harness labels failures by file:line plus message.` I confirmed the "stops at first missing, but reports all unexpected at once" split experimentally rather than guessing.
