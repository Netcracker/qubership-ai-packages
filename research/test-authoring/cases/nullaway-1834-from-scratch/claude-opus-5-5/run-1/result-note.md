I added six regression tests for the fix in `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. All six fail on the code before the fix and pass after it. I changed no production code and committed nothing. `./gradlew :nullaway:test` and `./gradlew :nullaway:buildWithNullAway` both pass.

One clause of the fix is still untested: no test in the module fails when the exemption for captured types is removed, and I couldn't find an input that reaches it.

**Message for the author of the pull request**

> I added six tests to `WildcardTests`, next to the existing wildcard containment tests. Each one checks a single case that is now reported. The same source also holds controls: inputs that differ from the case in one way and must still compile clean. `CompilationTestHelper` stops at the first mismatch and identifies it by line number, so I kept to one case per test. If two cases shared a source, a failure in the first would hide the second.
>
> - `typeVariableIsRejectedByNonNullExtendsWildcardOnlyWhenItsBoundAdmitsNull`: `Box<T>` with `T extends @Nullable Object` passed to `Box<? extends Object>` is reported. These stay silent: a type variable whose bound excludes null, a use written as `@NonNull T`, and the same `T` passed to `Box<? extends @Nullable Object>`.
> - `wildcardBoundedByTypeVariableIsRejectedByNonNullExtendsWildcardOnlyWhenItsBoundAdmitsNull`: the same rule when the argument is `Box<? extends T>`.
> - `typeVariableIsRejectedByNonNullExtendsWildcardOnlyWhenDeclaredInNullUnmarkedCode`: a type variable declared in `@NullUnmarked` code counts as admitting null. The control is the same class without `@NullUnmarked`.
> - `typeVariableIsRejectedByExtendsWildcardOfAnotherTypeVariableOnlyWhenOnlyTheActualAdmitsNull`: `Box<S>` with `S extends @Nullable T` passed to `Box<? extends T>` is reported. `Box<T>`, `Box<R extends T>`, and the same `S` in a class where `T` itself admits null stay silent.
> - `typeVariableWithNullableBoundIsRejectedByExtendsWildcardOfItsNonNullUse`: `Box<T>` passed to `Box<? extends @NonNull T>` is reported. `Box<@NonNull T>`, `Box<? extends @NonNull T>`, and `Box<T>` passed to `Box<? extends T>` stay silent.
> - `overrideReturningTypeVariableIsRejectedWhereOverriddenReturnsExtendsWildcardOfItsNonNullUse`: the override check from the changelog. Returning `List<V>` is reported; returning `List<@NonNull V>` is not.
>
> **How I checked them:** with the pre-fix versions of `CheckIdenticalNullabilityVisitor` and `GenericsUtils`, all six tests fail with "Did not see an error on line N … There were no errors". No control fired there.
>
> I also tried three temporary changes to the fix, and reverted each one:
> - **Dropping `admitsNull(lhsBound)`:** the new tests catch it, along with `issue1522`, `issue1522SelfContained` and `wildcardSuperBoundsAndInference`.
> - **Making `typeComparedForNullness` ignore an annotation at the use site:** the `@NonNull T` control catches it.
> - **Dropping the `rhsTypeArgument instanceof Type.CapturedType` exemption:** nothing fails. That covers the whole `:nullaway:test` suite and `buildWithNullAway`.
>
> For that last clause, I tried capturing `Box<? extends @NonNull T>` through a parameter, a field, a method result, a list element, inference on a generic method, a for-each loop and method references. None of them reach the exemption. I'm reporting it as unresolved rather than covered. If you have the input that made you add the exemption, please add it as a test; otherwise it may be dead code.
>
> **Proposed but not done:**
> - A test where a library model overrides a type variable's bound. That is the third way `typeVariableUpperBound` can decide a bound admits null, and it needs a handler or library-model setup that `WildcardTests` doesn't have.
> - Javac prints `? extends @NonNull T` without the annotation. That is why the expected message in the fifth test reads `Box<? extends T>`, and a comment above it says so.

One more thing, for you rather than the pull request: the repo's `CLAUDE.md` doesn't say how the test harness reports failures. I'd suggest adding one line: tests use JUnit 4 with Error Prone's `CompilationTestHelper`, which stops at the first mismatch and identifies it by line number and the expected text. I worked that out with a run. I haven't edited the file; should I add it?
