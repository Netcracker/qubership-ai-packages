I added six regression tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, beside the existing wildcard tests, and changed nothing else. All six fail on the base commit, each with the bug's symptom (the expected diagnostic is missing), and pass on the fix. `./gradlew :nullaway:test` and `./gradlew :nullaway:buildWithNullAway` both pass. Nothing is committed.

The harness stops at the first mismatch. I checked by breaking two lines in one test: the report named only the first. So each test holds one case that reports, plus lines that must stay silent. Every silent line was also silent on the base commit, so the report comes from the rule and not from the setup.

### Message for the PR author

**Tests added** (all in `WildcardTests`; all six fail without the fix):

- `typeVariableArgumentIsRejectedForNonNullWildcardOnlyWhenItsBoundAdmitsNull`: a `Box<N>` with `N extends @Nullable Object` passed where `Box<? extends Object>` is required is reported. `Box<@NonNull N>` and `Box<M>` with a non-null bound stay silent.
- `wildcardArgumentIsRejectedForNonNullWildcardOnlyWhenItsTypeVariableBoundAdmitsNull`: the same rule for a `Box<? extends N>` actual, the second example in the changelog.
- `typeVariableArgumentIsRejectedForNonNullWildcardWhenDeclaredInNullUnmarkedCode`: covers the branch of `typeVariableUpperBound` for a type variable declared in unannotated code. The same declaration in `@NullMarked` code stays silent.
- `typeVariableArgumentIsRejectedForTypeVariableWildcardOnlyWhenItMayBeNullAndTheBoundMayNot`:
  - `Box<S>` with `S extends @Nullable T` passed to `Box<? extends T>` is reported.
  - `Box<T>` and `Box<R extends T>` stay silent; this is the parametric case your message says must keep working.
  - The same `S` stays silent when `T` itself is `extends @Nullable Object`.
- `typeVariableArgumentIsRejectedForNonNullTypeVariableWildcardOnlyWhenItsBoundAdmitsNull`: `Box<T>` passed to `Box<? extends @NonNull T>` is reported. `Box<@NonNull T>`, and `Box<T>` with a non-null bound, stay silent.
- `overrideReturningTypeVariableArgumentIsRejectedWhereNonNullTypeVariableWildcardIsReturned`: the override consequence in the changelog sub-bullet. Returning `Box<V>` where the overridden method returns `Box<? extends @NonNull V>` is reported; `Box<@NonNull V>` is not.

**Proposed, not done:**

1. **Nothing reaches the captured-type exception.** I removed `rhsTypeArgument instanceof Type.CapturedType ||` from `extendsBoundContains` and ran the whole `:nullaway:test` suite: everything stayed green. I tried about eight shapes of captured actual (`b.copy()`, `id(b)`, `subList`, fields, nested boxes) and none behaved differently with the clause removed. So the clause is either unreachable from source or reached by an input I couldn't find. Please add the input that made you write it as a test, or say whether the clause can go.
2. **Diagnostics drop `@NonNull` from a wildcard bound.** `Box<? extends @NonNull T>` prints as `Box<? extends T>`. That makes "`Box<T>` cannot be converted to `Box<? extends T>`" read like a false positive. The tests match the text as printed, with a one-line comment saying why. Printing the annotation would make the report clearer.
3. **No library-model test.** The library-model branch of `typeVariableUpperBound` (a model that makes a type variable's bound nullable) isn't tested for type-variable actuals. That test belongs in the `test-library-models` module, and I only ran `:nullaway` tests, as the repository asks.
4. **A possible separate false positive.** This is a different check, outside this change. With `b` a `Box<? extends @NonNull V>`, the lambda `Supplier<? extends @NonNull V> s = () -> b.get();` reports "returning @Nullable expression", on this commit too.

Separately, a suggestion for you rather than the author: add a stack line to `CLAUDE.md` saying that tests use JUnit 4 with Error Prone's `CompilationTestHelper`, which stops at the first mismatch. It names a missing diagnostic by line and expected text, and an unexpected one by line number with the source line printed. I haven't edited the file; say if you want it.
