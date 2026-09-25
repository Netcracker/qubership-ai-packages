I added seven tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, placed after the other tests of wildcard bounds. Production code is unchanged and nothing is committed. The full `./gradlew :nullaway:test` run passes, and so does `./gradlew :nullaway:buildWithNullAway`.

---

**Message for the author**

Your change reports code that used to compile clean. The trouble is that the old defect had no diagnostic, so nothing in the suite could fail on it. These tests cover the new reports, plus one report the change keeps as it was. Like their neighbours, they are in-process compilation tests through `CompilationTestHelper`.

Error Prone's `CompilationTestHelper` (`DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines`, 2.50.0) stops at the first missing or unexpected diagnostic and identifies it only by line number. So each test holds one rule: one case that must be reported, beside controls that each narrowly miss its condition.

| Test | Case reported | Controls accepted |
| --- | --- | --- |
| `unannotatedTypeVariableArgumentMeetsNonNullWildcardOnlyWhenItsBoundExcludesNull` | `Box<N>`, `N extends @Nullable Object` → `Box<? extends Object>` | the same `N` passed to `? extends @Nullable Object`; `Box<@NonNull N>`; `N extends Object` |
| `typeVariableArgumentFromUnmarkedClassDoesNotMeetNonNullWildcard` | `V` declared in a `@NullUnmarked` class (a second way a bound admits null) | the same shape in a `@NullMarked` class |
| `wildcardArgumentBoundedByTypeVariableMeetsNonNullWildcardOnlyWhenThatBoundExcludesNull` | `Box<? extends N>`, nullable `N` → `Box<? extends Object>` (the changelog example) | a non-null `N` |
| `typeVariableArgumentMeetsWildcardBoundedByNonNullTypeVariableOnlyWhenItExcludesNull` | `Box<S>`, `S extends @Nullable T` → `Box<? extends T>` | `S extends T`; `Box<T>` itself; a `T` that is itself nullable |
| `typeVariableArgumentMeetsWildcardBoundedByNonNullUseOfItOnlyWhenItExcludesNull` | `Box<T>` → `Box<? extends @NonNull T>` | `Box<@NonNull T>`; `Box<T>` → `Box<? extends T>` |
| `nullableUseOfTypeVariableDoesNotMeetWildcardBoundedByThatVariable` | `Box<@Nullable T>` → `Box<? extends T>`, the report your message says must survive | `Box<T>` |
| `overrideMeetsNonNullWildcardReturnOnlyWhenItsTypeVariableArgumentIsNonNull` | an override returning `List<V>` where `List<? extends @NonNull V>` is required (the changelog's override note) | `List<@NonNull V>` |

**Red on the base commit.** I checked out `HEAD~1`'s `CheckIdenticalNullabilityVisitor.java` and `GenericsUtils.java`, ran the tests, then restored the fixed files. The first five tests and the override test fail there, each on the missing diagnostic: `Did not see an error on line N matching … There were no errors.` The `@Nullable T` test passes on the base commit, as it should, since that report is the one the change preserves.

**Mutants.** I scoped these to the new clauses, applied them one at a time, and reverted each:
- **Bound substituted under a parametric requirement.** Killed by the `@Nullable T` test and the two parametric tests.
- **`admitsNull(lhsBound)` dropped.** Killed by my tests and by four existing ones.
- **Use-site annotation ignored in `typeComparedForNullness`, or in `admitsNull`.** Each is killed.
- **The `rhsTypeArgument instanceof Type.CapturedType` exception removed.** This one survives the whole jspecify suite, and I have not resolved it:
  - I traced every captured actual the suite reaches. By the time `wildcardUpperBound` returns, it has already put `@NonNull V` back on the bound, so `admitsNull` is false and the capture clause never decides the result.
  - A test I wrote for it passed with and without the clause, so I dropped it rather than keep a test nothing can fail.
  - Either there is an input that needs the clause, in which case please add it as a test, or the clause is redundant and can go.

**Proposed, not done:**
- **The report prints the wrong requirement.** In the `@NonNull T` case it reads `Box<T> cannot be converted to Box<? extends T>`, which drops the `@NonNull` from the requirement and makes the report look wrong. My marker matches only the prefix, so the test doesn't lock in that text. Worth fixing.
- **The library-model partition is untested.** A library model can override a type variable's bound (`onOverride…TypeVariableUpperBound`); I didn't set up a model for that.
- **A stack line for the instructions file.** `AGENTS.md`/`CLAUDE.md` could gain: `Tests: JUnit 4 engine and assertions; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatched marker and identifies it by line number only.` I haven't edited either file; say if you want it added.
- **No marker labels.** The harness offers no way to label a marker, so a failure is named only by test name and line. That would need an issue against Error Prone; I filed nothing.
