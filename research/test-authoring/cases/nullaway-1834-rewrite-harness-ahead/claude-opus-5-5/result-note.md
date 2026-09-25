I rewrote the 20 tests the commit added to `WildcardTests.java` as 4 tests, one per rule. The production code is unchanged and nothing is committed. `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` passes. I did not run `buildWithNullAway`, because only test code changed.

---

**Message for the author of the pull request**

**What changed in the tests.** The commit added 20 tests, each one call in its own copy of a class. Many pairs differed in a single line, and a silent test only proved something while its reporting partner still reported on the same source, which nothing enforced. `CLAUDE.md` says to write `CompilationTestHelper` tests as if `doTest()` reported every mismatch, and to keep the cases of one rule in one source. So each rule is now one source, with every reported case next to the silent cases that differ from it in one respect:

1. **`aTypeVariableArgumentMeetsANonNullWildcardOnlyWhenItsDeclaredBoundExcludesNull`** checks a type-variable argument against `Box<? extends Object>`. Four inputs are now reported:
   - `T extends @Nullable Object`
   - `S extends T` where `T` is nullable
   - `Box<? extends T>` where `T` is nullable
   - `T` declared in `@NullUnmarked` code

   The silent cases are a non-null bound, a `? extends @Nullable Object` requirement and a `Box<?>` requirement. I added two of them: `nonNullBoundInherited` and `wildcardOverNonNullBound`. Before, the inherited-bound case and the wildcard case had no silent partner to compare with.
2. **`aTypeVariableUseThatCarriesANullnessAnnotationIsJudgedByItRatherThanByItsBound`** covers `Box<@Nullable T>`, which is reported against `? extends Object` and accepted against `? extends @Nullable Object`, and `Box<@NonNull T>` with a nullable bound, which is accepted. The fix does not change this behaviour. The test catches the fix wrongly applying the declared bound to a type-variable use that carries its own `@Nullable` or `@NonNull`.
3. **`aTypeArgumentMeetsAWildcardBoundedByATypeVariableOnlyWhenItAdmitsNullNoMoreThanThatVariable`** checks a wildcard bounded by a type variable. Reported:
   - `Box<T>` passed where `Box<? extends @NonNull T>` is required
   - `Box<S>` with `S extends @Nullable T`, where `T` is non-null
   - `Box<@Nullable T>` passed where `Box<? extends T>` is required

   Accepted: the same variable, a subtype variable under both kinds of bound, and the inference and capture cases. The capture cases now sit next to the `Box<T>` → `? extends @NonNull T` report they are the exception to. I added one silent case, `nonNullUse`: `Box<@NonNull T>` passed where `? extends @NonNull T` is required.
4. **`anOverrideReturnTypeMeetsANonNullWildcardOfATypeVariableOnlyWhenItsArgumentExcludesNull`** checks overrides against a return type of `List<? extends @NonNull V>`. It keeps the reported `List<V>` override and adds the missing silent case: a `List<@NonNull V>` override, which is accepted.

**Evidence that the tests fail without the fix.** I ran the new tests against the production code from before the commit:
- Test 1 fails with "There were no errors", so all four of its reported cases were silent.
- Test 3 fails, and its "All errors" list holds only the pre-existing `Box<@Nullable T>` report. Both of its new reports were missing.
- Test 4 fails with no errors.
- Test 2 passes, as expected.

This matches the commit's original 20 tests, 7 of which failed on the old code.

**Proposed, not done:**
- The report for `Box<T>` passed where `Box<? extends @NonNull T>` is required reads `cannot be converted to Box<? extends T>`. It drops the `@NonNull` that explains the error. Fixing this means changing production code, so it is out of scope here; the marker matches the message as it is printed today.
- The tests stay where the commit put them, after the `makeHelper()` helper. The rest of the file puts tests before it, so they could move above it.
- I did not run a mutation tool. Instead I checked by hand what each test would catch:
  - Test 1 fails if the argument stops being compared as its declared bound (the `typeComparedForNullness` step).
  - Test 2 fails if the check ignores whether the use carries an annotation (`hasNullnessAnnotation`).
  - Test 3 fails if the "may this be null" check (`admitsNull`) or the exception for captured types is dropped.
