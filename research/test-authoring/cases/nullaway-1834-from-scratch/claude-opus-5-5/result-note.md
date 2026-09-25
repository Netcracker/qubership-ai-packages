I added seven compile-level tests to `WildcardTests.java` for the last commit. Six of them fail on the code before the fix and all seven pass on it. Nothing is committed and no production code changed. The full `:nullaway:test` suite passes (1106 tests, 0 failures), and so does `:nullaway:buildWithNullAway`.

---

**Message for the author**

This commit makes NullAway report inputs it used to accept, so the proof it needs is a test that fails on the code before it. I added seven tests to `WildcardTests.java`, next to the existing containment tests. They are at the level those tests use: one source file through `CompilationTestHelper`.

Error Prone's harness stops at the first mismatch and identifies a case only by line number (`DiagnosticTestHelper.java:264–289` in 2.50.0). So each test holds a single case, the one input whose report the fix adds or keeps. Its controls sit beside it in the same source and differ from it in one respect. Each test name states the rule.

| Test | Case | Controls (no report) |
| --- | --- | --- |
| `typeVariableArgumentRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Foo<N>` with `N extends @Nullable Object` passed as `Foo<? extends Object>` | `Foo<M>` whose bound is non-null; `Foo<@NonNull N>` |
| `wildcardArgumentBoundedByTypeVariableRejectedByNonNullWildcardOnlyWhenThatBoundAdmitsNull` | `Foo<? extends N>` passed to the same parameter | `Foo<? extends M>` |
| `typeVariableArgumentRejectedByNonNullWildcardWhenDeclaredInNullUnmarkedCode` | `Foo<U>`, where `U` is declared in an `@NullUnmarked` outer class | the same code with a null-marked outer class |
| `typeVariableArgumentRejectedByTypeVariableWildcardOnlyWhenItAdmitsNullAndTheRequirementDoesNot` | `Foo<S extends @Nullable T>` passed as `Foo<? extends T>`, with `T` non-null | `S extends T`; `Foo<T>` itself; the same `S` where `T extends @Nullable Object` |
| `typeVariableArgumentRejectedByNonNullWildcardOfThatVariableOnlyWhenUnannotatedAtUse` | `Foo<T>` passed as `Foo<? extends @NonNull T>` | `Foo<@NonNull T>` |
| `overrideReturningTypeVariableArgumentRejectedWhereNonNullWildcardOfItIsReturnedOnlyWhenUnannotated` | the override-check case the changelog mentions: `List<V>` returned where the overridden method returns `List<? extends @NonNull V>` | `List<@NonNull V>` |
| `nullableUseOfTypeVariableRejectedByWildcardOfThatVariableEvenWhenItsBoundAdmitsNull` | `Foo<@Nullable T>` passed as `Foo<? extends T>` when `T`'s bound admits null | `Foo<T>` |

**Results on the code before the fix:** the first six tests fail, each with `Did not see an error on line N matching … There were no errors.` That is the missing report the fix adds. The seventh passes before and after the fix, because it guards a report that already existed. The commit message explains why the fix leaves `? extends T` as written rather than substituting its bound, and nothing tested that choice until now.

**Changes I made to the fix to check that the silent controls matter:**
- **Use the bound in place of `? extends T`:** caught by the fourth and seventh tests.
- **Let `typeComparedForNullness` ignore a `@NonNull` written at the use site:** caught by the first test's `Foo<@NonNull N>` control.
- **Remove the `CapturedType` exception:** nothing failed, in these tests or in the whole `:nullaway` suite. I tried arguments that were parameters, call results, locals, returns, list elements, results of generic-method inference, and a type variable from `@NullUnmarked` code. None produced a report without the exception. So either the branch is not needed, or I haven't found the input that reaches it. I'm leaving this unresolved. If you have the input that motivated the exception, it should become a test.

**Proposed but not done:**
- **The diagnostic hides the reason for the report.** The fifth test's message reads `Test.Foo<T> cannot be converted to Test.Foo<? extends T>`. The `@NonNull` on the wildcard bound isn't printed, so the two types look the same. This is like `identicalLookingWildcardNestedInArrayErrorMessage`. The test matches the text NullAway prints today. It is worth fixing in the message.
- **The library-model route is untested for type-variable arguments.** It is one of the three ways a type variable's bound can admit null. I don't think NullMarked code can reach it, because a type variable is only in scope inside its own declaration, and a library model only covers library code. The existing wildcard-bound tests already cover the shared `typeVariableUpperBound` helper.
- **Stack line for `AGENTS.md` / `CLAUDE.md`:** "Tests: JUnit 4 engine; Error Prone `CompilationTestHelper` for checks (`// BUG: Diagnostic contains:` markers). It stops at the first mismatch and has no label, so it identifies a missing expected diagnostic by line number and expected text." I haven't added it, because that needs the maintainers' agreement.
