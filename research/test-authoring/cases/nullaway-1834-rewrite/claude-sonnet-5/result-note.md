The diff looks correct: 20 test methods collapsed to 14, no behavioral coverage lost, no production code touched, and both `:nullaway:test` and `:nullaway:buildWithNullAway` pass.

---

Message for the PR author:

I rewrote the 20 tests you added in `WildcardTests.java` per the `test-authoring` skill, without touching production code. Net effect: 20 methods → 14, same coverage.

**What I did:** `CompilationTestHelper.doTest()` checks its embedded `// BUG:` markers by scanning lines in order and throwing on the first mismatch (verified from `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines`'s source: each check is `assertWithMessage(...).isTrue()`, which aborts the loop). It also names a failure only by line number, never by a per-case label — this is exactly the "check that stops at first mismatch, named only by a line number" pattern the skill describes, and it's already the convention this file uses (`testNegative`/`testPositive`, `testNullableExtendsBound`/`testNonNullExtendsBound`, etc.).

Several of the added tests were a case (a `// BUG` scenario) and its nearest passing control, split into two separate `@Test` methods with near-identical bodies — differing by exactly the one condition that flips the outcome. I merged each such pair/group into one `@Test` with multiple methods in one source, so the test name states the rule instead of one branch of it:

- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + `aTypeVariableWithANonNullBoundMeetsANonNullWildcardRequirement` + `aTypeVariableWhoseBoundAdmitsNullMeetsANullableWildcardRequirement` + `aNonNullWrittenOnATypeVariableUseMeetsANonNullWildcardRequirement` → one test, `aTypeVariableFailsANonNullWildcardRequirementOnlyWhenItsEffectiveNullnessAdmitsNull` (one case, three controls: non-null bound, nullable requirement, `@NonNull`-annotated use).
- `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` + `aNullableWrittenOnATypeVariableUseMeetsANullableWildcardRequirement` → `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirementButNotANullableOne`.
- `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends` + `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` → `aTypeVariableUseFailsAWildcardBoundedByThatSameVariableOnlyWhenTheUseIsWrittenNullable`.
- `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + `aTypeVariableThatAdmitsNoNullMeetsAWildcardBoundedByOneThatDoesNot` → `aSubtypeFailsAWildcardBoundedByItsSupertypeOnlyWhenTheSubtypeAdmitsNull`.

I kept the remaining 10 tests standalone: each exercises a structurally distinct partition (unannotated code, transitively-bounded type variables, unbounded wildcards, capture conversion via two different call shapes, the override-widening diagnostic, a wildcard-shaped actual) with no natural one-hop control already present in the diff, so merging them would have meant inventing new scenarios rather than reorganizing existing ones. I verified with `./gradlew :nullaway:test --tests WildcardTests`, the full `:nullaway:test`, and `:nullaway:buildWithNullAway` — all pass, and the diagnostics/messages are byte-for-byte the ones already established by the fix.

**What I propose but didn't do:** the repository's instructions carry no line naming this file's test stack (per the skill's §0). I'd propose adding, to `CLAUDE.md`/`AGENTS.md`: *"Tests: JUnit 4 engine; `CompilationTestHelper`/`doTest()` for NullAway diagnostic checks — one call per source checks every embedded `// BUG:` marker but stops and reports only the first mismatch, naming it by line number only."* I didn't add it myself since that edit needs your sign-off.
