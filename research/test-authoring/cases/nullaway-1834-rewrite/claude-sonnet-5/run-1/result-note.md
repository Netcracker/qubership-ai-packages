Only the test file changed, nothing committed, and the full `WildcardTests` suite plus NullAway's self-check (`buildWithNullAway`) both pass.

## Summary for the PR author

I rewrote the 20 tests this commit added to `WildcardTests.java` per the `test-authoring` skill, going from 20 methods to 12. No production code or test semantics changed — every scenario you wrote is still exercised, verbatim, just regrouped.

**Why:** `CompilationTestHelper`'s `doTest()` scans the source top-to-bottom and throws on the *first* mismatched line — it does not collect and report every mismatch in one run. Under that harness behavior, a test may hold one `// BUG:` case plus as many passing controls as help isolate it, but two independent `// BUG:`-producing scenarios sharing one act would let the first failure mask the second, so they need separate tests. Several of the new tests were a single `// BUG:` case split from its nearest passing control into its own method — these are exactly the "silent case without its control" and "second case sharing an act" patterns the skill flags, and they also broke with every pre-existing test in this file, which all pair a failing case with its controls in one method (e.g. `simpleWildcardNoInference`, `wildcardCaptureParameters`).

What I merged (each merge is a pure reorganization — same `Box`/`Holder` classes and call sites, just repackaged, so there's no new semantic content to review):
- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + its three passing siblings → `aTypeVariableFailsANonNullWildcardRequirementOnlyWhenItsDeclaredBoundAdmitsNull`
- `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` + its two passing siblings → `aTypeVariableUseIsJudgedByItsOwnWrittenNullnessNotItsDeclaredBound`
- `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + its passing sibling → merged into one test (same name)
- `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` + `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends` → merged into one test (same name as the former)
- `aCapturedTypeArgumentMeetsANullnessAnnotatedTypeVariableRequirement` + `aCapturedTypeArgumentMeetsABareTypeVariableRequirement` → `aCapturedTypeArgumentIsComparedAsWrittenRegardlessOfTheRequirementsAnnotation` (both passing, no masking risk, just DAMP)

Ran `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` (green) and `./gradlew :nullaway:buildWithNullAway` (green).

What I considered and deliberately left alone, so you can decide:
- `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement`, `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement`, `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement`, and `aWildcardActualBoundedByATypeVariableThatAdmitsNullFailsANonNullWildcardRequirement` are each lone `// BUG:` cases with no inline passing control. Each is a distinct partition of the rule (unmarked-code defaulting, a transitively-bounded type variable, a `@NonNull`-annotated wildcard bound, a wildcard actual rather than a bare type variable), so none can simply be merged with another case — but each could still get its own nearby control for extra robustness. I didn't add those myself because constructing a correct one means getting the generics/nullness interaction exactly right, which I'd rather you or a reviewer with full context on the fix confirm than have me guess.
- `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable` and its `...UnderInference` counterpart are left standalone since they exercise genuinely different mechanisms (plain containment vs. type inference through a lambda); forcing them together would obscure rather than clarify.
