Here's the message I'd leave for the PR author:

---

I rewrote the tests this commit added to `WildcardTests.java` per the `test-authoring` skill. The repo's own stack line already told us how to read `CompilationTestHelper`: even though `doTest()` stops at the first mismatched marker, we're to write tests as if it reported every mismatch, keeping the cases of one rule in one source. That's exactly the idiom every pre-existing test in this file already follows (`testPositive`/`testNegative` pairs inside one `Test.java`), but the 20 new tests broke from it: each case and its passing control got its own separate test method with its own copy of the `Box<T extends @Nullable Object>` boilerplate.

**What changed:** merged the 20 tests down to 11, each named for the rule it establishes rather than for one outcome, with the case and its nearest control(s) as sibling methods in one source:

- `aTypeArgumentMeetsANonNullWildcardRequirementOnlyWhenItsEffectiveUpperBoundDoesNotAdmitNull` — merges the original bare-`T`-fails, bare-`T`-passes, and wildcard-actual-fails tests, since all three are the same rule applied to the same target.
- `aTypeVariableWhoseBoundAdmitsNullMeetsAWildcardRequirementThatAdmitsNullToo` — merges the nullable-target and unbounded-target controls.
- `aNullnessAnnotationWrittenOnATypeVariableUseIsComparedAsWrittenNotAsItsDeclaredBound` — merges the `@Nullable T`-fails, `@Nullable T`-passes, and `@NonNull T`-passes cases; this is literally the rule stated in your own commit prose ("a use that carries its own nullness is compared as written").
- `aTypeVariablesUseMeetsAWildcardBoundedByThatVariableOnlyWhenItCarriesNoMoreNullnessThanTheWildcardAllows` — merges three cases that shared the exact same `Holder<T extends @Nullable Object>` + `takeExtendsT` scaffold.
- `aTypeVariableExtendingAnotherMeetsAWildcardBoundedByThatVariableOnlyWhenItsOwnBoundDoesNotAdmitNull` — merges the matching pair under `Holder<T>` (non-null `T`).
- `aCapturedTypeArgumentMeetsANullnessAnnotatedAndABareTypeVariableRequirement` — merges the two capture-conversion controls into one interface.
- Five tests (`aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable[UnderInference]`, `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement`, `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement`, `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported`) stayed standalone — each exercises a genuinely distinct mechanism (reflexive identity, inference, unmarked code, transitive bound, override-checking) with no natural control among the added cases, so merging them would have blurred rather than clarified the rule under test.

Every original source snippet, BUG marker, and diagnostic string is preserved verbatim; only method names and the grouping into files changed. I ran `:nullaway:test --tests WildcardTests` and `:nullaway:buildWithNullAway` after the rewrite — both pass, confirming the merges didn't change any outcome.

**Proposed but not done:** I didn't add a stack line for JUnit4/CompilationTestHelper to the repo's own `CLAUDE.md`/`AGENTS.md`, since I only had it as the session's runtime instructions, not confirmed as checked into the repo — worth adding there per §0 of the skill if it isn't already. I also didn't add new "control" cases for the two remaining single-case tests (unannotated-code and transitively-bounded-variable) since no natural nearest-control existed among the tests this commit added; if you want that gap closed, it'd need two new cases (e.g., a transitively-bounded non-null `S extends T` passing the same target) added deliberately, not manufactured from a rewrite.
