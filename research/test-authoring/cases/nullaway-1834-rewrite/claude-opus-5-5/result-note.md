I rewrote the 20 tests the commit added to `WildcardTests.java` as 12. The production code is unchanged and nothing is committed. `./gradlew :nullaway:test` and `:nullaway:buildWithNullAway` both pass.

**Message for the PR author**

I reorganized the tests the PR adds to `WildcardTests.java` around one rule each. Most of the 20 tests checked one input alone, and 13 of them expected no warning. A test that expects silence proves little alone: it would also pass if the setup were wrong. So each test now holds one new case and, in the same source, the inputs that differ from it in one respect and get the opposite outcome (controls). For example, `aTypeVariableFailsANonNullWildcardOnlyWhenItsWrittenBoundAdmitsNull` puts the reported `Box<T extends @Nullable Object>` next to four silent controls: a `<T>` bound, a `@NonNull T` use, a `? extends @Nullable Object` requirement and a `Box<?>` requirement. Each test name states the rule its inputs establish.

Each test holds only one new case because of how Error Prone's `CompilationTestHelper` reports. One compilation stops at the first missing or unexpected diagnostic and names it only by line number (`DiagnosticTestHelper.java:268` and `:289` in 2.50.0; I checked by breaking two markers in one source). Two cases in one source would hide each other. With one case per test, the test name identifies the failure, so no label for the harness is needed.

**Evidence**
- **Red on base:** with `nullaway/src/main` reverted to `HEAD~1`, exactly the 8 regression tests fail, each with `Did not see an error on line N matching incompatible types: …`, which is the missing report itself. The other 4 pass there, because they check behaviour that already existed.
- **Controls hold on base:** with the case markers removed, the 8 regression tests pass on base, so no control depends on the fix.
- **Mutation check:** I disabled, one at a time, the five checks the fix adds: the captured-type exemption, `admitsNull(lhsBound)`, `!admitsNull(rhsUpperBound)`, the bound lookup in `typeComparedForNullness`, and its `hasNullnessAnnotation` guard. At least one rewritten test fails for each. The first attempts at the third and fourth mutants did not compile (Error Prone flags them), so I reran those in a form that does.

**Inputs added**
- **A new case:** a captured `Map<? extends K, V>` passed where `? extends Map<? extends K, ? extends @NonNull V>` is required. It is reported after the fix and was silent before, and the PR didn't test it. It sits in `aNonNullBoundedWildcardRejectsABareUseOfATypeVariableThatAdmitsNullUnderCapture`, next to the original `? extends @NonNull V` input, which stays silent.
- **Reporting controls for the silent tests:**
  - The inference test gains `@Nullable V loadNullable()` into `CompletableFuture<? extends V>`.
  - The capture test gains `Map<? extends K, @Nullable V>` into `Map<? extends K, ? extends V>`.
  - The override test gains an override returning `List<@NonNull V>`, which stays silent.
  - The `S extends @Nullable T` test gains a holder whose `T` admits null, where it is accepted.

  All of these reports appear both before and after the fix.

**Inputs reshaped**
`Box<T>` → `Box<? extends T>` (both as an argument and as a returned value) and `Box<S extends T>` → `Box<? extends T>` now use a class-level `T` inside one `Holder`, next to the `@Nullable T` input that reports. Before, they were three separate tests, partly with method-level type variables. The comparison path is the same either way. No input that passed before the fix was dropped.

**Proposed, not done**
- **Test-stack line:** `CLAUDE.md` doesn't name the test stack. I suggest adding: `Tests: JUnit 4 engine; checker tests use Error Prone CompilationTestHelper with // BUG: Diagnostic contains: markers, where one compilation stops at the first missing or unexpected diagnostic and names it by line number.` I didn't edit the file.
- **A possible gap I didn't pursue:** while probing controls, I found that `V load()` with `V extends @Nullable Object`, passed through `CompletableFuture.supplyAsync(() -> load())` into a `CompletableFuture<? extends Object>`, is silent on both base and HEAD. Inference probably picks a non-null type there. It may deserve its own issue, but it is outside this PR.
- **Placement:** the new tests still sit after the private `makeHelper` methods at the end of the class, where the PR put them. Moving them above the helpers would match the rest of the file.
