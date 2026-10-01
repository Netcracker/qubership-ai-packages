Only the test file changed, nothing committed, as requested.

---

**Note on stack line (SKILL.md §0):** this repository's `CLAUDE.md` has no line naming the test stack. From the imports, the module runs on JUnit 4 (`org.junit.Test`) with Error Prone's `CompilationTestHelper` as its own engine+assertions for compile-diagnostic tests. I verified empirically (two deliberately-broken markers in one `doTest()` call) that `CompilationTestHelper.doTest()` **stops at the first mismatch** and **names it only by line number**, no label. I propose adding to `CLAUDE.md`:

> Tests: JUnit 4 engine. Compile-diagnostic tests use Error Prone's `CompilationTestHelper`; one `doTest()` call is one act that stops at the first line mismatch and names it only by line number, with no label.

I haven't added this myself per the skill's rule (edits to the instructions file happen only after you agree).

## What I changed

The commit added 20 separate test methods, many of which were a single rule's case and its controls split across unrelated `doTest()` calls. Since `CompilationTestHelper` stops at the first mismatch per compilation and names it only by line, the skill's §7 principle 1 says a case belongs with its controls in *one* compilation, and a genuinely different partition of the same rule gets its own test. I merged four such case+control clusters into one test each (reducing 11 of the 20 methods into 4), and kept the other 9 as standalone tests since each is its own distinct partition or a pure regression guard with no natural in-file control:

- `aTypeVariableIsJudgedByItsDeclaredBoundAgainstAConcreteWildcardRequirement` — merges the old `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` (case) with its three controls (non-null bound, nullable wildcard target, unbounded wildcard target).
- `aNullnessAnnotationWrittenOnATypeVariableUseOverridesItsDeclaredBound` — merges the `@Nullable T`-use failing case with its two controls (`@Nullable T` meeting a nullable target, `@NonNull T` meeting a non-null target).
- `aWildcardBoundedByATypeVariableIsMetByABareUseButNotANullableOne` — merges the `Box<@Nullable T>` vs. `Box<? extends T>` failing case with a bare-use control in the same `Holder` class (I reshaped the old return-statement-based silent test, `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable`, into the same call-argument idiom so it can share the act; I verified this reshaping is behaviorally faithful by running the suite).
- `aWildcardBoundedByATypeVariableRejectsABoundThatAddsNullability` — merges the `S extends @Nullable T` failing case with its `S extends T` control.

I renamed every test (merged or not) to state the rule and its outcome as a sentence, per §7, rather than the acceptable-but-generic originals.

I validated the rewrite by running `./gradlew :nullaway:test --tests WildcardTests` against the fix (all green), then checked out the two pre-fix production files (`CheckIdenticalNullabilityVisitor.java`, `GenericsUtils.java`) from the parent commit and reran: exactly 7 of the 13 rewritten tests go red, and they're the same 7 behaviors that were red when I ran the *original* 20 un-merged tests against the same pre-fix code. So the merges didn't hide or alter what any test actually catches. I also ran `./gradlew :nullaway:test` (full module) and `:nullaway:buildWithNullAway`, both green.

## What I propose but didn't do

- Add the stack-line sentence above to `CLAUDE.md` (needs your sign-off first).
- Several standalone tests are pure "silent" regression guards with no in-file control proving the checker is actually exercised on that shape: `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariableUnderInference`, `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends`, and the two captured-type-argument tests. I didn't fabricate companion failing cases for these because I couldn't derive their expected diagnostics from the specification with confidence rather than from the implementation's current output — that's exactly the trap §5 warns against. If you want these strengthened, they're the ones to look at first.
- `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement`, `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement`, `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement`, `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported`, and `aWildcardActualBoundedByATypeVariableThatAdmitsNullFailsANonNullWildcardRequirement` are each their own rule-partition per §7 principle 1 and were left standalone, same as originally; none had an obvious same-act control among the original 20 that I could borrow without inventing new coverage.
