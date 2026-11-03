I added seven tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java` and changed nothing else. The full `:nullaway:test` suite and `:nullaway:buildWithNullAway` both pass. Nothing is committed.

One proposal for you, separate from the message below: CLAUDE.md could get a stack line, for example `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers, which stops at the first mismatch and names a missing diagnostic only by its line number`. I learned that by deliberately breaking two cases in a throwaway test. I'll add it only if you agree.

---

**Message for the PR author**

**Tests added** (all in `WildcardTests`). Each test holds one case that the fix now reports, plus controls that differ from it in one respect and must stay silent. They are separate tests because `CompilationTestHelper` stops at the first mismatch, so two cases in one source would hide each other.

| Test | Case reported now | Controls that stay silent |
|---|---|---|
| `typeVariableArgumentRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>`, `T extends @Nullable Object` → `Box<? extends Object>` | `<T>`; `Box<@NonNull T>` |
| `wildcardArgumentBoundedByTypeVariableRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<? extends T>`, same `T`, same parameter | `<T>` |
| `typeVariableArgumentRejectedByNonNullWildcardWhenDeclaredInUnmarkedCode` | `T` declared by a `@NullUnmarked` class, used in marked code | same shape, marked class |
| `typeVariableArgumentRejectedByWildcardBoundedByTypeVariableOnlyWhenOnlyTheArgumentAdmitsNull` | `Box<S>`, `S extends @Nullable T` → `Box<? extends T>`, `T` non-null | `S extends T`; `T extends @Nullable Object` |
| `typeVariableArgumentRejectedByWildcardBoundedByNonNullTypeVariableWhenItsBoundAdmitsNull` | `Box<T>` → `Box<? extends @NonNull T>`, nullable `T` | `Box<@NonNull T>`; `T` with a non-null bound |
| `overrideReturningTypeVariableArgumentRejectedWhereNonNullWildcardIsReturned` | override returning `List<V>` where `List<? extends @NonNull V>` is returned (the changelog's sub-bullet) | `List<@NonNull V>` |
| `nullableTypeVariableArgumentStillRejectedByWildcardBoundedByThatVariable` | `Box<@Nullable T>` → `Box<? extends T>` | `Box<T>` |

The last one is a regression guard rather than a fix test. It protects the commit message's claim that substituting the bound for a type-variable requirement would silence an existing report.

**How I checked them:**
- **On the parent commit:** the first six fail, each because the diagnostic is missing ("There were no errors"). That silence is the bug, and it also shows every control already held before the fix. The guard test passes there.
- **Mutants:** I made five edits to the fix, each in a throwaway worktree and reverted:
  - dropping the use-site-annotation check in `typeComparedForNullness`
  - dropping it in `admitsNull`
  - dropping the `admitsNull(rhsUpperBound)` clause
  - dropping the `admitsNull(lhsBound)` clause
  - sending type-variable requirements through the bound path

  Every one of them fails at least one new test, and each fails on the control meant for it.

**Unresolved: the `rhsTypeArgument instanceof Type.CapturedType` clause has no test.** With that clause replaced by `false`, the whole `:nullaway:test` suite (1106 tests) and `buildWithNullAway` still pass. I added a temporary print to that branch and ran the whole module: whenever the actual was a captured type and the requirement a type variable, either the requirement admitted null or the actual did not. In none of those runs did the clause change the result. The captures I tried (parameter, return value, local, `List.get`) also kept their `@NonNull`, unlike the "capture of ? extends V" the commit message describes. So I can't tell whether the clause is still needed or is equivalent code. If you still have the source that needed it, it should become a test; if not, it's a candidate to remove.

**Proposed, not done:**
- **Library-model path:** a type variable whose bound is made nullable by a library model is now judged through `typeVariableUpperBound`, but nothing tests that path. A test belongs in `test-library-models` (`CustomLibraryModelsTests`), and I kept to the `:nullaway` module.
- **Wording mismatch:** the changelog writes `Box<? extends T>` as the second example, while the diagnostic for `Box<? extends @NonNull T>` prints as `Box<? extends T>` (javac drops the annotation when printing). That's why the fifth test's expected message reads `Box<? extends T>`.
