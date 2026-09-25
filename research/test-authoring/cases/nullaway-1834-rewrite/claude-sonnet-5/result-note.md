Working tree changes are in place, uncommitted, as requested.

## Message for the PR author

Applied the `test-authoring` skill to the tests the fix commit added. Production code is untouched; I only rewrote `WildcardTests.java`, and only the parts the skill flagged. Full `:nullaway:test` and `:nullaway:buildWithNullAway` both pass.

**Why:** `CompilationTestHelper.doTest()` scans a source top to bottom and asserts each `// BUG:` marker against a diagnostic; each assertion (via Truth) throws immediately, so it **stops at the first mismatch**. Under that harness, a "case" (an input newly rejected by the fix) and its "control" (the nearest input differing in exactly one respect that's still accepted) can't safely live in separate compilations with duplicated boilerplate — the skill's own worked example (§7, "A case and its control in one check") is built almost verbatim around this exact scenario, including the phrase "a type variable is rejected only when its bound admits null and the requirement does not," which practically named the fix for me.

**What I changed** — merged three pairs/triples of case+control tests that were near-identical copies differing in one line, into one test each, with one compiled source and one method per input:

- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + `aTypeVariableWithANonNullBoundMeetsANonNullWildcardRequirement` + `aTypeVariableWhoseBoundAdmitsNullMeetsANullableWildcardRequirement` → `aTypeVariableIsRejectedOnlyWhenItsBoundAdmitsNullAndTheRequirementDoesNot` (one rejecting method, two accepting controls that each flip one side of the "and").
- `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` + `aNullableWrittenOnATypeVariableUseMeetsANullableWildcardRequirement` → `aNullableWrittenOnATypeVariableUseIsRejectedOnlyWhenTheRequirementForbidsNull`.
- `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + `aTypeVariableThatAdmitsNoNullMeetsAWildcardBoundedByOneThatDoesNot` → `aTypeVariableIsRejectedByAWildcardBoundedByAnotherTypeVariableOnlyWhenItAdmitsNull`.

Each merged test still has at most one input that expects a diagnostic (per §7, a check that stops at the first mismatch may hold at most one such input per test, or a later real bug would hide behind an earlier expected failure). The other ~14 new tests (unmarked-code bound, captured-actual cases, the override-widening case, the wildcard-actual case, etc.) are each a single, self-contained scenario with no naturally-paired near-neighbor among the new tests, so I left them as written.

**Proposed, not done:** the repo's `AGENTS.md`/`CLAUDE.md` names no test stack, so per the skill I'm proposing rather than writing one:
> Tests: JUnit 4 engine; error-prone's `CompilationTestHelper` for compiler-diagnostic assertions (no reference file in this skill) — `doTest()` stops at the first mismatched line, and names a missing diagnostic by line and expected text but an unexpected one only by line number.

I didn't add this line to `AGENTS.md`/`CLAUDE.md` myself since that needs your sign-off. I also considered folding `aNonNullWrittenOnATypeVariableUseMeetsANonNullWildcardRequirement` in as a fourth control of the first merged test (it differs from its case by exactly one respect too — an explicit `@NonNull` override), but the "only when" rule name would have had to grow a third clause about explicit overrides, which felt like it was papering over a distinct rule rather than stating one; I left it as its own standalone test instead. Happy to fold it in if you'd rather have the fuller decision table in one place.
