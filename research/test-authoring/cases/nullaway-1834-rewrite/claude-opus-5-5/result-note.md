I rewrote the 20 tests the commit added to `WildcardTests.java` as 8, without changing production code or committing. All 8 pass on the fix, and each fails on the base commit on its own `// BUG:` marker. `:nullaway:buildWithNullAway` passes too.

---

**Message for the PR author**

Thanks for the fix. I restructured the 20 new tests in `WildcardTests` into 8. I dropped none of their inputs, and the production code is unchanged.

**Why.** Of the 20 tests, 7 failed on the base commit: those are the cases. The other 13 passed there: those are controls, mostly "this stays silent" tests with no reporting input beside them. A silent test on its own can't tell "the rule doesn't apply here" from "the setup never reached the check".

I needed to know how Error Prone's `CompilationTestHelper` reports, so I broke two markers on purpose and read the output. One compilation stops at the first missing `// BUG:` marker, which it names by line and expected text. It also stops at the first unexpected diagnostic, which it names by line, but it prints every diagnostic with its source line. So one compilation can hold one case plus its controls, and each further case of the same rule gets its own test.

Each test is now one source holding one case next to the controls that differ from it in one respect. Methods stay separate, so each call is checked on its own. Each name states the rule, and the partition where a rule has several tests.

**The new tests (✗ = case that fails on base; the rest are controls):**

1. `aBareTypeVariableIsRejectedByANonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull`
   - ✗ `<T extends @Nullable Object> Box<T>` passed to `Box<? extends Object>`
   - the same `Box<T>` passed to `? extends @Nullable Object` and to `?`
   - `<T>` instead of the nullable bound
   - `Box<@NonNull T>`
   - `Box<@Nullable T>`, which reports and also passes to the nullable wildcard. This one keeps the original's `<T>` bound, so it differs from the `<T>` control in one respect, not from the case.
2. `…OnlyWhenTheTypeVariableItExtendsAdmitsNull`
   - ✗ `S extends T`, `T extends @Nullable Object`
   - new control: `<T, S extends T>`
3. `…OnlyWhenDeclaredInNullUnmarkedCode`
   - ✗ the `@NullUnmarked` holder
   - new control: the same holder `@NullMarked`
4. `aWildcardBoundedByATypeVariableIsRejectedByANonNullWildcardOnlyWhenTheVariableAdmitsNull`
   - ✗ `Box<? extends T>` with a nullable-bounded `T`
   - new control: `<T>`
5. `aTypeVariableIsRejectedByAWildcardOfTheVariableItExtendsOnlyWhenItAdmitsNullAndThatVariableDoesNot`
   - ✗ `S extends @Nullable T` with `Holder<T>`
   - `S extends T`, for both a non-null and a nullable holder
   - new control: `S extends @Nullable T` with a nullable holder
6. `aUseOfATypeVariableIsRejectedByAWildcardOfThatVariableOnlyWhenTheUseMayBeNullAndTheWildcardMayNot`
   - ✗ `Box<T>` passed to `? extends @NonNull T`
   - `Box<T>` passed to `? extends T`
   - new control: `Box<@NonNull T>`
   - `Box<@Nullable T>`, which reports
   - the return form
   - the `supplyAsync` inference form, as a nested `Loader` interface
7. `aReturnedTypeArgumentThatMayBeNullIsRejectedByANonNullWildcardOfItsVariableUnlessCaptured`
   - ✗ new: a non-captured `Map<K, V>` returned as `Map<? extends K, ? extends @NonNull V>`
   - your two captured inputs, which had no reporting input beside them before
8. `anOverrideIsReportedOnlyWhenItsReturnTypeArgumentMayBeNullWhereTheOverriddenWildcardMayNot`
   - ✗ an override returning `List<V>`
   - new control: an override returning `List<@NonNull V>`

**Evidence.** On the fix, all 54 tests in `WildcardTests` pass. On the base commit, each of the 8 new tests fails on its ✗ marker, for example: `Did not see an error on line 12 matching incompatible types: Box<T> cannot be converted to Box<? extends Object>`. In tests 1 and 6, that run's output shows the `Box<@Nullable T>` controls still reporting, so their expectations already held on the base.

The level is the same as before: small, in-process compilation tests.

**Proposed, not done:**
- **A stack line for `CLAUDE.md`/`AGENTS.md`** (the two files are identical), for example: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with // BUG: Diagnostic contains: markers. One compilation stops at the first missing marker, which it names by line and expected text, and at the first unexpected diagnostic, which it names by line while printing every diagnostic.` I didn't edit either file; that's for the maintainers to agree to.
- **A possible missed report, out of scope here:** `default CompletableFuture<? extends @NonNull V> f() { return CompletableFuture.supplyAsync(() -> load()); }`, with `V extends @Nullable Object` and `V load()`, is not reported, either before or after this fix. That's why the inference input has no reporting control on the inference path itself. It may deserve its own issue.
