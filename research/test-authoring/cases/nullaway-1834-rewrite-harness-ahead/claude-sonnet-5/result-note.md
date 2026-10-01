Everything checks out: only the test file is modified, production code untouched, nothing committed, and the full suite plus the self-check build pass.

## Summary for the PR author

I rewrote the 20 tests this commit added to `WildcardTests.java` per the `test-authoring` skill, using the repo's established stack line (JUnit 4 + `CompilationTestHelper`, which stops at the first mismatched marker and reports by line, so one compiled source can hold at most one reporting case plus silent controls — the file's own long-standing `testPositive`/`testNegative` idiom). The result is 12 tests instead of 20, same coverage, less redundancy.

**How I verified what actually needed coverage:** rather than trust each test's name, I ran the full new batch against the pre-fix production code (temporarily swapping in the parent commit's `CheckIdenticalNullabilityVisitor.java`/`GenericsUtils.java`, then restoring). Only 7 of the 20 were red on the base commit. For the rest I ran targeted mutants of the new logic (dropping the "respect an explicit use-site annotation" guard, dropping the "declared bound" guard, dropping the captured-actual carve-out) to see which tests actually die. That turned up two tests that never caught anything, pre-fix or under any mutant I tried:

- `aNullableWrittenOnATypeVariableUseFailsAWildcardBoundedByThatVariable` — its rejection came entirely from the pre-existing top-level annotation check in `typeArgumentSubtype`, unchanged by this commit.
- `aCapturedTypeArgumentMeetsABareTypeVariableRequirement` — its direct-return setup never produces a captured actual, so it never reached the carve-out it was named for.

Both are **dropped**.

**What I merged** (case + its controls into one `doTest()` act, each control differing from the case in exactly one respect, per the file's idiom):
- `aTypeVariableWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` + its 3 "meets" siblings (non-null bound, nullable target, unbounded target) → `aBareTypeVariableFailsANonNullWildcardRequirementOnlyWhenItsDeclaredBoundAdmitsNull`.
- `aNullableWrittenOnATypeVariableUseFailsANonNullWildcardRequirement` + its nullable-target and `@NonNull`-override siblings → `aTypeVariableAnnotatedAtItsUseIsJudgedByThatAnnotationNotItsDeclaredBound`. (Kept despite not being base-red: mutation testing showed it's the only test that catches the guard that makes an explicit `@NonNull T` override its nullable declared bound.)
- `aTypeVariableThatAdmitsNullFailsAWildcardBoundedByOneThatDoesNot` + its matching non-null-bound control, same `Holder<T>`.

Everything else (the "under inference," unannotated-code, transitive-bound, captured-actual, override-widening, and wildcard-actual tests) stayed as its own test — each is either explicitly called out in your commit message as a case the fix must keep legal, or exercises a genuinely distinct code path confirmed by the red/mutant check.

**What I did not do:** I didn't add brand-new scenarios (e.g., a clean "S doesn't admit null" control for the transitive-bound test, or an explicit control for the `@NullUnmarked` test) — those would strengthen the suite further but felt like growing scope rather than rewriting what's there. Happy to add them if you want tighter coverage on those two. I also didn't touch any of the pre-existing tests in the file, several of which bundle multiple reporting cases into one act in a way that's arguably out of step with the harness's "first mismatch only" behavior — out of scope here, but worth a look separately.
