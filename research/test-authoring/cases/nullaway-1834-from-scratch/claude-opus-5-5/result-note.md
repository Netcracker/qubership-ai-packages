I added six regression tests, one for each way the fix can now report. All six fail on the base commit `09fdea5` and pass on `614efcf`. I didn't change production code or commit anything. The full `./gradlew :nullaway:test` and `./gradlew :nullaway:buildWithNullAway` both pass.

**Message for the PR author**

---

**Tests added** (small tests, run through `CompilationTestHelper`)

`WildcardTests`:
- `typeVariableArgumentIsRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull`: a `Box<N>` with `N extends @Nullable Object` passed to `Box<? extends Object>` is reported. Two controls stay silent: a `Box<M>` whose bound is non-null, and a `Box<@NonNull N>` (a use-site annotation beats the bound).
- `wildcardArgumentIsRejectedByNonNullWildcardOnlyWhenItsTypeVariableBoundAdmitsNull`: the same rule for `Box<? extends N>`, with `Box<? extends M>` as the control.
- `typeVariableArgumentIsRejectedByNonNullWildcardOnlyWhenDeclaredInUnmarkedCode`: the unannotated-declaration branch of `typeVariableUpperBound`. A `U` declared in a `@NullUnmarked` class and used in a `@NullMarked` method is reported; the same `U` declared in marked code is the control.
- `typeVariableArgumentIsRejectedByWildcardOfNonNullTypeVariableOnlyWhenItsBoundAdmitsNull`: a `Box<S extends @Nullable T>` passed to `Box<? extends T>` with `T` non-null is reported. The silent controls are `Box<R extends T>` and `Box<T>`, plus a requirement whose `T extends @Nullable Object` accepts the same `S`.
- `typeVariableArgumentIsRejectedByWildcardOfNonNullUseOnlyWhenItsBoundAdmitsNull`: a `Box<T>` passed to `Box<? extends @NonNull T>` is reported; `Box<@NonNull T>` is the control.

`GenericsTests`:
- `overrideReturningTypeVariableIsRejectedByWildcardOfNonNullUseOnlyWhenItsBoundAdmitsNull`: the override path the CHANGELOG promises. Returning `List<V>` where the overridden method returns `List<? extends @NonNull V>` reports `mismatched type parameter nullability`; `List<@NonNull V>` is the control. It is the only test that reaches the visitor through override checking.

**Evidence**
- **Red on the base commit:** every test fails at its expected line with `Did not see an error on line N matching … There were no errors.`, which is the bug's symptom (the silence). The controls were silent on the base too, so the fix moves the outcome of exactly one input per test.
- **Mutation runs**, done by hand on a scratch copy and run against the `jspecify` tests. Each of these fails at least one new test:
  - dropping `admitsNull(lhsBound)`
  - dropping `!admitsNull(rhsUpperBound)`
  - dropping the `lhsBound instanceof Type.TypeVar` branch
  - ignoring use-site annotations in `admitsNull`
  - ignoring use-site annotations in `typeComparedForNullness`
  
  Before the new tests, the `lhsBound instanceof Type.TypeVar` branch and both use-site-annotation mutants were caught by nothing.

**Shape.** The rest of `WildcardTests` puts several `// BUG:` markers in one source. Each new test holds exactly one input that expects a report, with its silent controls beside it. The reason is the harness: `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` (error_prone_test_helpers 2.50.0, lines 264–289) stops at the first mismatch. For a missing diagnostic it prints the marker text, and for an unexpected one the line number plus the source line. So a second reporting input in the same source would be hidden whenever the first one fails (test-authoring skill §7, §9).

**Not done, proposed**
1. **Unresolved surviving mutant.** Removing `rhsTypeArgument instanceof Type.CapturedType ||` breaks nothing: not the full `:nullaway:test` run (1105 tests), not `buildWithNullAway`, and not my probes. The probes passed `Box<? extends @NonNull T>` through parameters, returns, locals and member substitution such as `s.values()` and `subList`. I can't tell whether the exception is unreachable or needs a specific input. Could you add the input that motivated it as a test, or remove the clause if no such input exists?
2. **The message drops `@NonNull`.** For a `? extends @NonNull T` requirement it prints `Box<T> cannot be converted to Box<? extends T>`, which reads as if the two types were compatible. My marker matches that text as it is. I'd suggest a follow-up that keeps the annotation in the message.
3. **Library-model branch untested.** The `onOverrideClassTypeVariableUpperBound` / `onOverrideMethodTypeVariableUpperBound` branch of `typeVariableUpperBound` has no test on the new type-variable path. It needs a library-model handler setup, so I left it out.
4. **Proposed line for `CLAUDE.md`/`AGENTS.md`** (I didn't edit either): `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatch and names a missing diagnostic by its marker text and an unexpected one by line and source line.`

---
