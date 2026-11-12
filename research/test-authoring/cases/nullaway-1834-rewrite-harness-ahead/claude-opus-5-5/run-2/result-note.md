I rewrote the 20 tests the last commit added to `WildcardTests.java` as 3 tests, one per rule. Production code is untouched and nothing is committed. `./gradlew :nullaway:test` passes. When I put the production code back to the base commit, each of the 3 tests fails at a diagnostic that never appears. That is the bug itself (the silence), not a compile error.

---

**Message for the author of the PR**

Thanks for the fix and for testing it from both sides. I've regrouped the tests in `WildcardTests.java`. Every input and expected diagnostic you wrote is still there.

**What changed**

- **20 tests became 3, one per rule.** Each pair like `…FailsANonNullWildcardRequirement` / `…MeetsANonNullWildcardRequirement` had two copies of the same source differing in one line. Nothing kept those copies in sync, and a reader had to compare them to find the difference. Our convention (CLAUDE.md) is that the cases of one rule live in one source. So each rule now has one source, and each case is a method in it whose signature shows what differs on one line:
  - **`aTypeVariableThatMayBeNullIsRejectedOnlyByAConcreteWildcardBoundThatExcludesNull`** covers `Box<? extends Object>`, `Box<? extends @Nullable Object>` and `Box<?>` as targets. It checks a nullable bound, a non-null bound, a bound inherited through `S extends T`, `Box<? extends T>`, `@Nullable T` and `@NonNull T` at the use site, and a type variable declared in `@NullUnmarked` code.
  - **`aWildcardBoundedByATypeVariableRejectsATypeArgumentOnlyWhereItMayBeNullAndTheBoundMayNot`** covers targets that name a type variable (`? extends T`, `? extends @NonNull T`). It checks `T` with a nullable bound and with a non-null bound, the `CompletableFuture` inference case, and both captured-type cases. The captured and inference cases expect no report, so they now sit in the same source as the cases that do report. That way a broken setup can't make them pass by accident.
  - **`anOverrideIsReportedOnlyWhenItsReturnTypeArgumentMayBeNullWhereTheOverriddenOneMayNot`**: the override case is the one that got a new input.
- **One new input:** an override that returns `List<@NonNull V>` and expects no report. Without it, the override test would also pass if NullAway reported every override of that method. It differs from the reported override in one annotation.
- **Every expectation was checked against the base commit,** one at a time in a throwaway class (now deleted). The 7 expected reports all fail on the base and pass with the fix. One of them is `Box<? extends T>` into `Box<? extends Object>`, which the base also missed. The 14 cases that expect no report hold both before and after the fix.

**Proposed but not done**

- One test still has 7 markers, and `doTest()` stops at the first mismatch and identifies it only by line number. If two cases break at once, the report names just the first. CLAUDE.md accepts that for now. A per-marker label would need a change to Error Prone's `CompilationTestHelper`, which isn't in this repository, so I haven't proposed it here.
