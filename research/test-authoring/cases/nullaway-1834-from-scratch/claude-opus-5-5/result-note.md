I added eight tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. No production code changed and nothing is committed. Seven of them fail on the base commit (the fix's parent), all with the same message: "Did not see an error on line N … There were no errors". That is the bug's symptom, a call that should be reported and isn't. All eight pass with the fix, the full `:nullaway:test` run passes (1107 tests, 0 failures), and `:nullaway:buildWithNullAway` passes.

Here is the message I would leave for the author:

---

**Tests added.** Each test compiles one source holding one case plus its controls. A control is an input that differs from the case in one respect and has the opposite outcome. Every control's expectation also holds on the base commit. I used one case per test because Error Prone's `CompilationTestHelper` stops at the first marker it can't match. I confirmed that with a run where two markers were broken: only the first was reported.

| Test | Case (fails on base) | Controls |
|---|---|---|
| `typeVariableWhoseBoundAdmitsNullIsNotContainedInNonNullWildcard` | `Box<T>`, `T extends @Nullable Object` → `Box<? extends Object>` is reported | `T extends Object`; `Box<@NonNull T>` |
| `typeVariableBoundedByNullableTypeVariableIsNotContainedInNonNullWildcard` | `S extends T` where `T`'s bound is nullable (the bound is inherited through `T`) | same shape, but `T extends Object` |
| `typeVariableDeclaredInUnmarkedCodeIsNotContainedInNonNullWildcard` | `T` declared in a `@NullUnmarked` class, used from a `@NullMarked` method | same class, but null-marked |
| `wildcardBoundedByNullableTypeVariableIsNotContainedInNonNullWildcard` | `Box<? extends T>`, `T` with a nullable bound | `T extends Object` |
| `subtypeVariableAdmittingNullIsNotContainedInWildcardOfNonNullTypeVariable` | `Box<S>`, `S extends @Nullable T` → `Box<? extends T>` with a non-null `T` | `Box<T>`; `Box<S extends T>`; the same `S` against a `T` whose bound is nullable |
| `typeVariableWhoseBoundAdmitsNullIsNotContainedInWildcardOfItsNonNullUse` | `Box<T>` → `Box<? extends @NonNull T>` | `Box<@NonNull T>`; `Box<T>` → `Box<? extends T>` |
| `overrideReturningTypeVariableWhoseBoundAdmitsNullIsReportedAgainstWildcardOfNonNullUse` | the override case from the changelog: `List<V>` overriding `List<? extends @NonNull V>` | `List<@NonNull V>` |
| `wildcardOfNonNullUseIsContainedInWildcardOfNonNullUse` | guard against over-reporting: `Box<? extends @NonNull T>` is accepted (green on both commits) | `Box<? extends @Nullable T>` is reported |

These are compilation tests that run in-process, the same level as the neighbouring tests in this file. No larger test is needed.

**Mutants of the changed lines.** I applied each one by hand, ran it on its own, and confirmed it compiled before reading the result:
- Dropping `admitsNull(lhsBound)`, `!admitsNull(rhsUpperBound)`, the parametric `TypeVar` branch, the bound substitution in `typeComparedForNullness`, or the `@NonNull` half of `hasNullnessAnnotation`: each one fails at least one new test.
- Dropping `rhsTypeArgument instanceof Type.CapturedType ||` **survives**, both in `WildcardTests` and in the whole module.
  - I logged every captured type argument that reaches this branch, across about ten shapes: method results, fields, `filter`/`self` chains, overrides, nested wildcards. In every one the capture kept its `@NonNull`, so `admitsNull` was false on the right-hand side and the clause never changed an outcome.
  - So I could not reproduce the case the commit message describes ("capture of `? extends @NonNull V` prints as capture of `? extends V`"). This is unresolved, not covered. Please add the input that motivated the clause as a test, or drop the clause if no such input exists.

**Proposed, not done:**
- **A testing line for `AGENTS.md`** (`CLAUDE.md` is a symlink to it): "Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone `CompilationTestHelper` for checker tests: it stops at the first unmatched `// BUG: Diagnostic contains:` marker and names it by line and marker text, and names an unexpected diagnostic by line only."
- **A label for unexpected diagnostics.** When a control is wrongly reported, the report gives only "Saw unexpected error on line N" and offers no way to label the control. This would be an issue against Error Prone. I didn't check their tracker for an existing one.
- **Diagnostic wording.** The messages drop the `@NonNull` on the wildcard bound. You get `Test.Box<T> cannot be converted to Test.Box<? extends T>`, and in the override case `List<V>` vs `List<? extends V>`, which reads as if two identical types were rejected. The new markers match today's text; fixing the message is a production change, so I left it.
- **Library-model partition.** I didn't add a test for a type variable whose bound is made nullable by a library model; it needs a model wired up in the test.
- I didn't change the existing tests.
