Clean: only `FrameworkTests.java` is touched, nothing committed, production code untouched.

---

**Message for the PR author:**

The fix shipped with no tests, so I added three fields to the existing `springValueFieldTest` in `FrameworkTests.java` (nearest existing test of this unit — `SpringHandler`'s `containsNullSpELExpression` is private, so it's exercised the same way its neighbors are: through the full compilation pipeline, via `@Value`-annotated fields and NullAway's "not initialized" diagnostic).

Added, partitioning the input the diff actually touched (the new `NULL_COMPARISON_PATTERN` stripping):
- `NegativeCases.nullOnlyInComparison` — `#{someBean != null ? someBean.value : 'default'}`, the exact false positive from the bug report. No diagnostic expected.
- `NegativeCases.nullOnlyInReversedComparison` — `#{null == someBean ? someBean.value : 'default'}`. The fix's regex has a second alternative specifically for this reversed-operand order, and the new Javadoc calls it out by name, so it gets its own case rather than being assumed from the forward-order one.
- `PositiveCases.nullValueDespiteComparison` — `#{someBean != null ? null : 'default'}`, the non-regression control the PR description itself names: `null` appears both as a comparison operand and as the actual ternary value, and the field must still be flagged.

I verified all three the way §1 of the test-authoring skill asks: checked out `SpringHandler.java` as it stood one commit before this fix (production code only, tests kept at HEAD) and reran `springValueFieldTest` — it failed with exactly the bug's symptom, a spurious `@NonNull field 'nullOnlyInComparison'/'nullOnlyInReversedComparison' not initialized` warning on both new negative cases. Restored the fix and reran: `:nullaway:test` and `:nullaway:buildWithNullAway` both pass.

I didn't add a second, larger test — this is an in-process regex/string heuristic with no real dependency or process boundary involved, so the compilation-level test is the right (and only) level owed.

One open item I didn't act on: the repository's `AGENTS.md`/`CLAUDE.md` name no test-stack line (engine + assertion library) for this module. I inferred JUnit 4 + Error Prone's `CompilationTestHelper` from the file's existing imports and neighbors rather than from a declared convention. If you'd like, I can propose adding that line to `AGENTS.md`/`CLAUDE.md` in a follow-up, but I didn't touch the instructions file since that's a separate decision for you to confirm.
