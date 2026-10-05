I rewrote the 20 tests from `d55c150` as two tests in `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, one for each rule the fix implements. No production code changed and nothing is committed. `WildcardTests` passes on the fix and `:nullaway:buildWithNullAway` passes.

**Message for the author of the pull request:**

---

I rewrote the 20 new tests in `WildcardTests` as two tests, one per rule in `extendsBoundContains`. All 20 inputs are kept, written exactly as before.

- **`aWildcardWithAConcreteBoundJudgesATypeVariableArgumentByItsDeclaredBound`** covers a requirement like `Box<? extends Object>`.
  - Cases (reports the fix adds): a `T` whose bound is nullable, a `T` declared in `@NullUnmarked` code, `S extends T` where `T`'s bound is nullable, and `Box<? extends T>` with the same `T`.
  - Controls: a `T` with a non-null bound, `@Nullable T` and `@NonNull T` written at the use site, and the `? extends @Nullable Object` and `?` requirements.
- **`aWildcardBoundedByATypeVariableAcceptsExactlyTheArgumentsThatVariableAdmits`** covers a requirement like `? extends T` or `? extends @NonNull T`.
  - Cases: `S extends @Nullable T` where `T` is non-null, `Box<T>` passed to a `Box<? extends @NonNull T>`, and the override that returns `List<V>`.
  - Controls: the same variable (both directly and through inference), `S extends T`, `@Nullable T`, and the two captured arguments.

**Why:** the repository's `CLAUDE.md` says to write `CompilationTestHelper` tests as if `doTest()` reported every mismatch, and to keep the cases of one rule in one source. The old tests broke that rule in two ways:
- **Copied setup.** Each test had its own copy of `Box` and the methods that take it, so finding what differed between two tests meant comparing two classes line by line.
- **Silent tests with no control beside them.** Each silent test stood alone, so nothing showed that the same setup reports when it should.

Now each case sits beside its controls in one class, often with the difference on adjacent lines. For example, in `boundAdmitsNull` the reporting call to `takeNonNull(b)` is followed by silent calls to `takeNullable(b)` and `takeAny(b)`. The methods and nested types inside each source are named for the case they hold, because the harness reports a mismatch only by line number. The interface-based inputs became nested interfaces of `Test`.

**How I checked which inputs are cases:**
- **Old tests on the base commit:** exactly seven failed, and those seven are the cases above. The other 13 already held before the fix, so they are controls.
- **New tests on the base commit:** both fail.
- **Base commit with only the seven case markers removed:** both pass. So every control still holds on the base, and each case is a report the fix adds.

**Proposed, not done:**
- **Library-model partition is untested.** `typeVariableUpperBound` also treats a bound as nullable when a library model says so (through `upperBoundIsNullable` and the handler), but no test covers that. A case for it would use one of the test library models' type variables with a nullable upper bound, passed to `Box<? extends Object>`, and would belong in the first test.
- **No control for the `? extends @NonNull T` case.** The case is `Box<T>` passed to `takeExtendsNonNullT`, and it has no control that differs in just one respect. Adding `Box<@NonNull T>` passed to the same method, expected to be silent, would show that the report comes from `T` possibly being null.

---
