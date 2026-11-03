Only the test file changed, nothing committed, as asked.

---

Message for the author of the PR:

I rewrote the 20 tests the last commit added to `WildcardTests.java`, per `test-authoring`. No production code changed; nothing is committed.

**What changed and why:** The file already has an established convention — visible in `simpleWildcard`, `wildcardSuperFormalNoInference`, `superOrUnboundedWildcardAssignedToExtendsBoundedWildcard`, etc. — of putting a case together with its control(s) in one `@Test`/one source, since CompilationTestHelper's `doTest()` is written here as if it reported every mismatch (per the repo's test-stack note). The 20 new tests broke that convention: each was its own `@Test` holding either a single failing case or a single passing control, with no control alongside its case. That's the shape `test-authoring` §9 flags ("a new test takes the shape of its neighbors... the usual such shapes are... a silent case kept apart from its control").

I merged cases that are direct case/control pairs of one rule into single tests, renamed for the rule, keeping every original scenario (zero loss of coverage, same expected diagnostics):
- `aBareTypeVariableActualIsJudgedByWhetherItsDeclaredBoundAdmitsNull` — merges the explicit-nullable-bound-fails, nonnull-bound-passes, nullable-bound-vs-nullable-req, nullable-bound-vs-unbounded-req, and transitive-bound-fails cases.
- `anExplicitAnnotationOnATypeVariableUseOverridesItsDeclaredBound` — merges the `@Nullable`/`@NonNull`-on-use cases.
- `extendingATypeVariableMeetsAWildcardBoundedByItUnlessTheExtendingBoundIsWrittenNullable` — merges the `S extends T` family (nullable-T-bound control, nonnull-T-bound control, and the nullable-override-on-S failing case), using `NullableBoundHolder`/`NonNullBoundHolder` to avoid clashing `Holder` declarations.
- `anExplicitAnnotationThatDivergesFromAWildcardsTypeVariableBoundIsReported` — merges the two mirror-image "annotation on one side diverges from the other" failing cases.

Left standalone, unchanged: the two "meets a wildcard bounded by itself" tests (direct and under-inference — different enough mechanisms, each already a meaningful regression guard on its own), the unmarked-code case (matches the file's existing precedent of giving `@NullUnmarked` scenarios their own test), the two captured-type-argument tests, the override-widening test, and the wildcard-actual (not bare-variable) failing case — each is a distinct scenario without a natural case/control sibling among the new tests.

Net effect: 20 `@Test` methods → 11, same assertions, same diagnostics, `:nullaway:test --tests WildcardTests` and `:nullaway:buildWithNullAway` both green.

**What I propose but didn't do:** `GenericsUtils.typeVariableUpperBound` names three sources of an admits-null bound — explicit `@Nullable`, a library model override, and a declaration in unannotated code. This commit's tests cover the first and third; I didn't add a case for the library-model-override partition, since that would be a new test rather than a rewrite of an existing one, and it's outside what you asked me to do here.
