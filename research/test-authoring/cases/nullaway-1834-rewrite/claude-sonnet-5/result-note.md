Good — only the test file changed, no commit made, as requested.

---

**Message for the PR author:**

I rewrote the 20 tests the last commit added to `WildcardTests.java` per the `test-authoring` skill, without touching production code. No commit was made.

**Why:** the check here is Error Prone's `CompilationTestHelper` — I confirmed from its source (`DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines`) that it stops at the first line-mismatch (a chain of hard `assertWithMessage(...).isTrue()` calls, not a soft/grouped assertion) and names a case only by an embedded line number. That means a reported case and its nearest accepted "control" belong in *one* compiled source so a reviewer can see what differs without comparing two test bodies — exactly the `testPositive`/`testNegative`-in-one-source shape this file already used before the commit (e.g. `simpleWildcardNoInference`). The 20 new tests were instead written as 20 independent one-assertion-each tests, so most cases had no control living beside them.

**What changed:**
- Merged each reported case with its nearest accepted control into one `@Test`/one source, mirroring the file's pre-existing idiom (e.g. bound-admits-null → rejected, paired with the same call but a non-null bound → accepted). This produced 14 tests from the original 20.
- Renamed each surviving `@Test` to state the rule it establishes (e.g. `aTypeVariableFailsANonNullWildcardRequirementOnlyWhenItsDeclaredBoundAdmitsNull`), consistent with a report that should read as a sentence.
- Traced the exact branches in `CheckIdenticalNullabilityVisitor.extendsBoundContains`/`admitsNull` to find real one-respect-different controls for cases that had none in the original 20 (declared-bound-admits-null via a chain of type variables, unannotated-code declarations, wildcard-shaped actuals, an explicit-`@NonNull`-actual case, and a non-widening override) — 6 new control methods total, all verified by running the suite.
- Dropped `aTypeVariableWhoseBoundAdmitsNullMeetsAnUnboundedWildcardRequirement`: by inspection of `GenericsUtils.wildcardUpperBound`, an unbounded `Box<?>` against a class with a nullable-bounded parameter resolves to the same effective `@Nullable Object` bound as `Box<? extends @Nullable Object>`, so it exercised the identical branch as the kept `aTypeVariableWhoseBoundAdmitsNullMeetsANullableWildcardRequirement` and asserted nothing new.
- Fixed `aCapturedTypeArgumentMeetsABareTypeVariableRequirement`: as written, its type variable `V` had a nullable declared bound, so it passed via `admitsNull(lhsBound)` regardless of the capture-conversion exemption it was named for — it couldn't have failed for the reason it claims to test. Removed the nullable bound so the test can only pass because of the capture-conversion exemption (verified: this is the only path left that makes it green).
- `aNullableWrittenOnATypeVariableUseMeetsANullableWildcardRequirement` was dropped as a separate test; it re-established (via the "written" branch) the same "a nullable wildcard accepts a null-admitting actual" fact already covered by `aTypeVariableWhoseBoundAdmitsNullMeetsANullableWildcardRequirement` (via the "bound" branch). Marginal value, so I merged its useful half — the explicit-`@NonNull`-overrides-a-nullable-bound direction — into `aNullnessAnnotationWrittenOnATypeVariableUseOverridesItsDeclaredBound` instead of keeping a fifth near-duplicate method there.

All 14 tests, including every newly written control, were run (`./gradlew :nullaway:test --tests com.uber.nullaway.jspecify.WildcardTests`) and pass; `buildWithNullAway` also passes.

**What I proposed but didn't do:** the repository has no stack line naming its test engine/assertion library (JUnit 4 + `CompilationTestHelper`, which isn't one of the skill's reference files). Per the skill this should be proposed to a human rather than written into `AGENTS.md`/`CLAUDE.md` unasked — happy to add it if you'd like, something like: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper for diagnostics (stops at the first line mismatch on doTest(), no per-case label beyond the source line)`.
