Only the test file changed, as required, and the build/test suite stays green. Here's the message for the PR author:

---

**What changed:** Rewrote the 20 tests the last commit added to `WildcardTests.java` into 11, following `test-authoring`. No test's expected diagnostic was changed or dropped — I verified the resulting file (`./gradlew :nullaway:test --tests WildcardTests`, full `:nullaway:test`, and `:nullaway:buildWithNullAway` all pass) and mapped every original assertion to its new location before removing the original.

The original tests redeclared the same `Box<T extends @Nullable Object>` and `takeNonNull`/`takeNullable`/`takeAny` methods seven times across separate `@Test` methods that each differed from a neighbor by one token (a bound, an annotation, which helper was called). That's the "two cases that share a long setup" shape this skill flags: a reader has to diff two whole class bodies to find what's actually being tested, and `CompilationTestHelper` already reports every mismatch in one compilation (confirmed by reading its source), so these cases belong in one source file, as this file's own older tests (e.g. `wildcardCaptureParameters`, `wildcardCheckingForReturnsAndAssignments`) already do. I merged along four lines:

- `aTypeVariableMeetsANonNullWildcardOnlyWhenNoAnnotationOrBoundAdmitsNull` replaces 7 old tests (bound-admits-null / bound-does-not / `@Nullable`-written / `@NonNull`-written, each checked against both a non-null and nullable/unbounded target) as one `Box`/one set of target methods with 4 small cases.
- `aTypeVariableBoundedByOneThatAdmitsNullMeetsOnlyARequirementParametricInTheSameBound` replaces 2 tests (same `S extends T` actual, concrete target fails / parametric target meets).
- `aParametricWildcardFailsWhenTheActualIsWrittenNullableOrItsBoundIsWrittenNonNull` replaces 2 tests (writing `@Nullable` on the actual, or `@NonNull` on the wildcard's own bound, each defeats a `? extends T` target).
- `aParametricWildcardFailsOnlyWhenTheActualsOwnBoundAdmitsNull` replaces 2 tests (`S extends @Nullable T` vs `S extends T` against the same `? extends T` target).

The remaining 7 tests (same-type-variable wildcard, its inference variant, unannotated-code bound, the two captured-actual regression tests, the override-widening test, and the wildcard-actual-bounded-by-a-typevar test) were already minimal, single-case, and not duplicated with a neighbor, so I left them as they were.

**What I propose and did not do:** The repository's `CLAUDE.md`/`AGENTS.md` carries no line naming the test stack (§0 of the skill), so per the skill I'm proposing one here rather than editing those files myself: *"Tests: JUnit 4 engine; `CompilationTestHelper`-style string-literal assertions (not covered by this skill's reference files) for the generics/JSpecify checks — one compilation (`addSourceLines`/`doTest()`) reports every line's mismatch, naming a missing diagnostic by its expected message text and an extra diagnostic by line number only; no case label beyond the test/method name."* If you'd like, I can add that line to `CLAUDE.md`/`AGENTS.md` in a follow-up.
