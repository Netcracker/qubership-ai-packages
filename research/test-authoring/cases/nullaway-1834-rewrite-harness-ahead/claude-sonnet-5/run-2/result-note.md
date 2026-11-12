Only the test file changed, as required. Not committing, per instructions.

---

**Message for the PR author:**

I rewrote the 20 tests this commit added to `WildcardTests.java` per the `test-authoring` skill, applying the repo's documented harness convention — `CompilationTestHelper.doTest()` stops at the first mismatched marker, but we write as if it reported every mismatch, so related cases of one rule share one source.

What changed: I merged five groups of case/control tests that were sharing one conceptual rule but living in separate `@Test` methods with separate (often near-duplicate) `Box`/helper declarations:
- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + `...WithANonNullBoundMeets...` + `...MeetsANullableWildcardRequirement` → one test, `aBareTypeVariableActualsEffectiveNullnessComesFromItsDeclaredUpperBound`, with three sibling methods sharing one `Box`/`takeNonNull`/`takeNullable` setup.
- The three "written `@Nullable`/`@NonNull` on the use" tests → `aNullnessAnnotationWrittenOnATypeVariableUseOverridesItsDeclaredBound`.
- `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable` + `...MeetsAWildcardBoundedByTheVariableItExtends` → `aWildcardBoundedByATypeVariableAcceptsThatVariableAndAnythingDeclaredToExtendIt`. The commit message itself states these two facts together ("That is what keeps `Box<T>` and `Box<S extends T>` assignable to a `Box<? extends T>`"), so they're one rule, not two.
- `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + its silent control → `aWildcardBoundedByANonNullableTypeVariableRejectsOnlyAnActualThatMayBeNull` (a proper case+control pair in one `Holder`, per §7 principle 3).
- `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` + `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement` → `anExplicitNullnessAnnotationOnEitherSideOfATypeVariableBoundedWildcardIsReadLiterally`, since they're mirror images of the same fact (an explicit annotation on either side of a type-variable-named wildcard is read literally, not overridden by the other side's bound).

This took 20 tests down to 13, each named for the rule it establishes rather than a bare scenario, each avoiding the duplicated `Box`/helper boilerplate the originals repeated. I left the 8 genuinely distinct single-scenario tests alone (unbounded-wildcard, `@NullUnmarked` bound source, transitive-bound chain, under-inference variant, the two captured-actual regression checks, the override check, and the uncaptured-wildcard-actual regression check) — each exercises its own mechanism and has no natural same-shape counterpart among this commit's additions, so forcing a merge would have diluted the test name or fabricated an unrelated case.

I ran `:nullaway:test --tests WildcardTests` and `:nullaway:buildWithNullAway` after the rewrite and after `spotlessApply`; both pass.

What I proposed and did not do: I considered merging the two captured-actual tests (`aCapturedTypeArgumentMeets...`) with the uncaptured-wildcard-actual test (`aWildcardActualBoundedBy...`) to make the "captured actual is the exception" carve-out an explicit case+control triple, but their generic shapes (`Map`/`CompletableFuture` inference vs. a direct `Box` call) differ enough that I'd have had to invent a new, less faithful reduction rather than reorganize existing code — I left that for you to decide rather than guessing at a "bug" case the commit didn't already type by hand.
