I added seven tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java` and changed no production code. Six of them fail on the commit before the fix, and all seven pass on it. The full `:nullaway:test` run passes (1106 tests, 0 failures) and so does `:nullaway:buildWithNullAway`. Nothing is committed.

## Message for the author of the pull request

**Tests added** (`WildcardTests`). Each test holds one case plus "controls": inputs that differ from the case in one respect and get the opposite outcome. These are small tests, at the module's usual level: an in-process compilation through `CompilationTestHelper`. Nothing crosses a process boundary, so nothing larger is needed.

| Test | Case (now reported) | Controls (accepted) |
| --- | --- | --- |
| `typeVariableIsContainedInNonNullExtendsWildcardOnlyWhenItsBoundExcludesNull` | `Foo<T>`, `T extends @Nullable Object`, passed to `Foo<? extends Object>` | `T` with a non-null bound; `Foo<@NonNull T>`; the same `Foo<T>` passed to `Foo<? extends @Nullable Object>` |
| `wildcardBoundedByTypeVariableIsContainedInNonNullExtendsWildcardOnlyWhenItsBoundExcludesNull` | `Foo<? extends T>` with the same `T` | `Foo<? extends T>` with a non-null `T` |
| `typeVariableDeclaredInNullUnmarkedCodeIsNotContainedInNonNullExtendsWildcard` | `T` declared on a `@NullUnmarked` class, used in a `@NullMarked` inner class | the same code under a marked outer class |
| `typeVariableWithNullableBoundIsContainedInExtendsWildcardOfAnotherVariableOnlyWhenThatAdmitsNull` | `Foo<S>`, `S extends @Nullable T`, `T` non-null, returned as `Foo<? extends T>` | `T extends @Nullable Object`; `S extends T` |
| `typeVariableWithNullableBoundIsContainedInNonNullExtendsWildcardOfItselfOnlyWhenNonNullAtUse` | `Foo<T>` returned as `Foo<? extends @NonNull T>` | `Foo<@NonNull T>` |
| `overrideReturningTypeVariableWithNullableBoundWhereNonNullExtendsWildcardIsReturnedIsReported` | the override case from the changelog: `List<V>` overriding `List<? extends @NonNull V>` | `List<@NonNull V>` |
| `typeVariableIsContainedInExtendsWildcardOfItselfUnlessMarkedNullableAtUse` | guard: `Foo<T>` into `Foo<? extends T>` stays accepted when `T`'s bound is nullable | `Foo<@Nullable T>` is still reported |

**Evidence that the tests can fail:**
- **Base commit (`09fdea5`):** the first six fail there with `Did not see an error on line N matching … There were no errors.` That is the bug itself: nothing was reported.
- **Last test:** it guards new behaviour that was already correct on the base commit, so I broke the fix instead, one piece at a time:
  - Removing the type-variable-requirement branch is caught only by the new tests (the last row and the fourth); nothing in the existing suite notices.
  - Ignoring the use-site annotation in `admitsNull` is caught by the `? extends @NonNull T` test and the override test.
  - Ignoring it in `typeComparedForNullness` is caught by the `Foo<@NonNull T>` control in the first test.

**Unresolved: the captured-actual exemption** (`rhsTypeArgument instanceof Type.CapturedType` in `extendsBoundContains`).
- Removing that clause fails nothing: not the full suite, and not about fifteen inputs I tried (method calls on captured receivers, inference over captured arguments, `subList`, `Optional.filter`, and others).
- Instrumenting the branch showed why: every captured actual that reached it kept its `@NonNull` (`capture of ? extends @NonNull V`). So the clause never decided an outcome, and the commit message's premise that the capture loses the annotation never held there.
- I wrote a test for the clause, but the change it is meant to catch didn't fail it, so I removed it.
- Please supply the input that motivated the clause so it can get a test, or drop the clause.

**Not tested, deliberately:** the library-model branch of `typeVariableUpperBound`. A type variable that user code can pass as a type argument has to be declared in user code, so a library model can't affect it on this path.

**Proposed, not done:**
- **Error text drops `@NonNull`.** The message prints `? extends @NonNull T` as `? extends T`, so a correct report reads `Foo<T> cannot be converted to Foo<? extends T>`, which looks like a false positive. The override message has the same problem. The tests match the current text and need updating if the printer changes.
- **Test-stack line for `CLAUDE.md`/`AGENTS.md`:** `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers; one compilation stops at the first mismatch, naming a missing marker by line and expected text and an unexpected diagnostic by line and its text.` I confirmed that behaviour by running it, not from documentation.
- **Shape differs from the neighbouring tests.** Most neighbouring tests put several cases in one source. Because the harness stops at the first mismatch, a failing case would hide the cases after it, so each new test holds one case with its controls.
