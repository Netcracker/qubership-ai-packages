I added seven regression tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. All seven fail on the code before the fix and pass on HEAD. The full `:nullaway:test` run and `:nullaway:buildWithNullAway` produced no failures. Production code is unchanged and nothing is committed.

**Message for the PR author**

All seven tests are small compilation tests that sit beside the existing wildcard tests. Each one has a single expected report (`// BUG:` marker) plus nearby lines that must stay silent (controls). I checked how Error Prone's `CompilationTestHelper` reports problems by breaking two markers in one source: it reported only the first, by line number and the expected text. So each test holds one case, and it is named after that case.

| Test | Must be reported | Must stay silent (controls) |
| --- | --- | --- |
| `typeVariableIsRejectedByNonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull` | `Box<T>` with `T extends @Nullable Object` → `Box<? extends Object>` | `Box<U>` with a non-null bound; `Box<@NonNull T>`; `Box<T>` → `Box<? extends @Nullable Object>` |
| `wildcardBoundedByTypeVariableIsRejectedByNonNullWildcardOnlyWhenTheVariableAdmitsNull` | `Box<? extends T>` → `Box<? extends Object>` | `Box<? extends U>` with a non-null bound |
| `typeVariableDeclaredInNullUnmarkedCodeIsRejectedByNonNullWildcard` | `T` declared in a `@NullUnmarked` class, used from `@NullMarked` code | the same class without `@NullUnmarked` |
| `typeVariableWithNullableBoundIsRejectedByWildcardBoundedByNonNullTypeVariable` | `Box<S>` with `S extends @Nullable T` → `Box<? extends T>`, where `T` cannot be null | `Box<R extends T>`; `Box<T>`; the same `S` where `T extends @Nullable Object` |
| `typeVariableWithNullableBoundIsRejectedByWildcardBoundedByNonNullUseOfIt` | `Box<T>` → `Box<? extends @NonNull T>` | `Box<@NonNull T>` |
| `wildcardBoundedByTypeVariableIsRejectedByWildcardBoundedByNonNullUseOfIt` | `Box<? extends T>` → `Box<? extends @NonNull T>` | `Box<? extends @NonNull T>` |
| `overrideReturningTypeVariableWithNullableBoundIsRejectedWhereNonNullWildcardIsReturned` | an override returning `List<V>` where the parent returns `List<? extends @NonNull V>` | an override returning `List<@NonNull V>` |

The sixth test covers a behavior the PR description doesn't mention: a wildcard actual like `Box<? extends T>` is now also checked against a `? extends @NonNull T` requirement.

**How I checked the tests can fail**
- **Before the fix:** with the production sources reset to `HEAD~1`, all seven fail with "Did not see an error on line N … There were no errors". That is the bug itself (the checker stays silent), and it also shows no control line fires on the old code.
- **Breaking parts of the fix:** each of these edits turns at least one of the new tests red:
  - dropping `admitsNull(lhsBound)`
  - dropping the `hasNullnessAnnotation` guard in `typeComparedForNullness`
  - dropping the `hasNullnessAnnotation` guard in `admitsNull`

**Proposed, not done**
1. **The capture exception (`rhsTypeArgument instanceof Type.CapturedType || …`) has no test, because I found no input where it does any good.** With it removed, all 1106 module tests still pass. My probes (`a.self()`, `var` locals, `id(a)`, `l.get(0)`, nested wildcards) behave the same with and without it. The only difference I found is a missed report: with `b` declared as `Box<? extends T>` and `T extends @Nullable Object`, `takes(b)` into `Box<? extends @NonNull T>` is reported, but `takes(b.self())` is silent. If a real input needed the exception, please add it as a test. Otherwise I'd narrow or remove the exception and turn `takes(b.self())` into a test that expects a report. I didn't write a test for the current behavior, because it would lock in that missed report.
2. **The library-model route through `upperBoundIsNullable` has no test of its own.** This is where a model of a library overrides a type variable's bound. The unannotated-code route has one (the third test above).
3. **Test-stack note for `CLAUDE.md`.** The repository's instructions don't name the test stack. I'd propose adding: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper as the harness (stops at the first mismatch; names a missing diagnostic by line and expected text, an unexpected one by line)`. I haven't edited `CLAUDE.md`; that's your call.
