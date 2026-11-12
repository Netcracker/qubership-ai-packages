Only the test file changed, as required. No commit was made, per instructions.

---

**Message for the PR author:**

I rewrote the 20 tests this commit added to `WildcardTests.java`, applying the `test-authoring` skill. Net effect: 14 tests, same production coverage, none of the pre-existing tests touched.

The driving issue: `CompilationTestHelper.doTest()` stops at the first mismatched `// BUG:` marker and names it only by source line, so (per the skill's §7) a single act can safely hold at most one failing case, and any "meets the requirement" (silent) test needs a control in the same act proving the setup can actually produce a report — otherwise a silent test is indistinguishable from a broken one. Most of the new tests violated this: many "Meets..." tests stood completely alone with no case anywhere nearby, and several `Fails.../Meets...` pairs that differed in exactly one respect were split into two separate `doTest()` calls instead of sharing one, which is exactly the "two cases that share a long setup, stated nowhere" shape this skill calls out and the file's own established convention (e.g. `simpleWildcardNoInference`'s `testPositive`/`testNegative`) already avoids.

What I did:
- Merged `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` with its three silent siblings (`...MeetsANonNullWildcardRequirement`, `...MeetsANullableWildcardRequirement`, `...MeetsAnUnboundedWildcardRequirement`) into one test, renamed to state the rule as a whole.
- Likewise merged the "nullness written on the use" trio (`aNullableWrittenOnATypeVariableUseFails...`, `...MeetsANullableWildcardRequirement`, `aNonNullWrittenOnATypeVariableUseMeetsANonNullWildcardRequirement`) into one test.
- Merged `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` with `aTypeVariableThatAdmitsNoNullMeetsAWildcardBoundedByOneThatDoesNot` — they differed in one clause (`S extends T` vs `S extends @Nullable T`) and were separate acts.
- Merged `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends` and `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` into one test, and added a bare-use control, since both target `Box<? extends T>`.
- Merged `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement` with a new control (`@NonNull`-written use meets the same `@NonNull`-annotated wildcard).
- Added a control to `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` (a non-null bound through the same chain, meets).
- Added a control to `aTypeVariableDeclaredInUnannotatedCodeFailsANonNullWildcardRequirement` (the same shape under `@NullMarked`, meets) — this isolates that the unannotated declaration, not something else, decides the outcome.
- Added a control to the final wildcard-actual test (same actual with a non-null-bounded `T`, meets).

Left untouched/standalone (deliberately — these follow the file's existing convention for a realistic-pattern regression guard rather than a general-rule partition, and I didn't have enough confidence to safely invent a verified "fails" counterpart for the capture-conversion/inference internals without risking an incorrect test):
- `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable` and its inference variant.
- `aCapturedTypeArgumentMeetsANullnessAnnotatedTypeVariableRequirement` and `...MeetsABareTypeVariableRequirement`.
- `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported` (a different diagnostic/check path — override nullability — not the extends-bound containment path this commit changed).

Verified with `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` (pass), the full `:nullaway:test` (pass), and `:nullaway:buildWithNullAway` (pass). No production code was touched.

What I'd propose but didn't do: a reviewer who trusts the capture-conversion semantics more than I do might want an explicit failing counterpart for `aCapturedTypeArgumentMeetsABareTypeVariableRequirement` (it's a same-type passthrough, so nothing in a naive implementation could make it fail — it may be worth replacing with a case that actually exercises capture against a nullable-admitting bound). I'd rather the author or someone with deeper javac-capture expertise make that call.
