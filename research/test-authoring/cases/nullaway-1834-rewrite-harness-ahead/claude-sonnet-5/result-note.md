Both `./gradlew :nullaway:test` and `./gradlew :nullaway:buildWithNullAway` are green with the rewritten tests. No production code was touched. I did not commit, per instructions.

---

**Message to the PR author:**

I rewrote the 20 tests added in `d55c150` for `WildcardTests.java` per the `test-authoring` skill, without touching production code. All tests still pass (`./gradlew :nullaway:test` and `:nullaway:buildWithNullAway`).

**What changed and why:** Most of the 20 original tests were single-case tests whose "control" (the nearest input with the opposite outcome) lived in a separate test with its own copy of the scaffolding (`Box`, `takeNonNull`, etc.), and several were really partitions of the *same* specification rule tested independently. The skill's §7 treats a case and its narrowly-differing controls as belonging in one input where one compilation evaluates them together, named after the rule they establish rather than after one scenario. I folded the 20 tests into 6, one per distinct rule drawn from the fix's own doc comments/commit message:

1. `aTypeVariableFailsAConcreteNonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull` — the `typeComparedForNullness` rule against a concrete requirement (`Box<? extends Object>`), with cases for each reason a bare type variable's bound admits null (explicit `@Nullable`, unannotated code, a bound chain, a wildcard-actual variant) plus the shared non-null control, and the two ways of relaxing the *requirement* itself (nullable, unbounded).
2. `aNullnessWrittenOnATypeVariableUseIsComparedAsWrittenNotAsItsDeclaredBound` — an explicit `@Nullable`/`@NonNull` at the use site overrides the declared bound, against both a concrete and a parametric requirement.
3. `aTypeVariableMeetsAWildcardBoundedByThatSameVariable` — the trivial same-variable containment, directly and under inference.
4. `aBareTypeVariableFailsAParametricWildcardOnlyWhenItAdmitsNullAndTheRequirementDoesNot` — the `admitsNull` rule for a parametric requirement (`Box<? extends T>`), one case per feasible combination.
5. `aCapturedTypeArgumentIsExemptFromTheNullnessGateOnAParametricRequirement` — the capture-conversion carve-out.
6. `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported` — left as-is; it exercises a different diagnostic (override checking), not this containment rule, so it doesn't share a rule with anything else.

Each of the merged tests keeps every original source snippet and expected diagnostic (or lack of one) verbatim as a differently-named method/nested class inside one `Test.java`, so no input or expected outcome changed — I only regrouped and renamed. This also follows the file's own existing convention (several pre-existing tests already bundle multiple cases and multiple `// BUG:` markers in one source).

**What I propose and did not do:**
- The repository's `AGENTS.md`/`CLAUDE.md` has no "stack line" naming the test engine/assertion library (per the skill's §0). This session was given one directly (JUnit 4 engine; Error Prone's `CompilationTestHelper`, which in reality stops at the first mismatched marker and names it only by line number, but which we're directed to write against as if it reported every mismatch and named each marker). I relied on that but did not write it into `AGENTS.md` myself, since the skill says to only do that after the user agrees. I'd suggest adding a line to that effect to `AGENTS.md`/`CLAUDE.md` so future test-writing in this repo doesn't have to rediscover it.
- Per §7, a check that names its cases only by line number (no label) earns a follow-up proposal to ask the harness for a label. I didn't file anything (I was told not to use `gh`), but flagging it here: it would be worth an upstream issue against Error Prone's `CompilationTestHelper` (or a NullAway-side wrapper) for a way to label an expected diagnostic, since these multi-case tests currently rely on descriptive method names as a stand-in for a report-level label.
- I did not attempt to further verify my grouping of test 13 (`Box<@Nullable T>` vs `Box<? extends T>`) by re-deriving the production logic by hand — the interaction between `typeArgumentSubtype`'s top-level "explicitly-nullable-actual vs non-annotated-formal" rejection and the `admitsNull` bound-chasing gate is subtle. I confirmed the grouping empirically (all tests still pass with their original expected diagnostics preserved exactly), which is sufficient evidence the regrouping didn't change behavior, but I'd flag this area of `CheckIdenticalNullabilityVisitor` as worth an extra pair of eyes if anyone revisits it.
