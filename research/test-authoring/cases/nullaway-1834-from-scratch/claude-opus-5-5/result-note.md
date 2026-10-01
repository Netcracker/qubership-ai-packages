I added eight tests to `WildcardTests.java` (198 lines, nothing else touched, nothing committed). They pass on the fix. On the pre-fix production code, seven of them fail with the symptom the fix removes. The capture exception in the fix still has no test: deleting it breaks nothing, and the one effect I could find is that it hides a real null, which needs your decision.

**Message for the author of 614efcf**

The commit fixes a check that stayed silent, so it owed regression tests. I added eight to `WildcardTests`, one case per test with its controls in the same source. Each is an in-process compilation through `CompilationTestHelper`, the smallest level where the report can be seen; no larger test is needed because nothing crosses a process boundary.

| Test | Case (reported) | Controls |
| --- | --- | --- |
| `typeVariableActualIsRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>`, `T extends @Nullable Object`, into `Box<? extends Object>` | `T extends Object`; `Box<@NonNull T>` |
| `…WhenItsBoundIsANullableTypeVariable` | `Box<S>`, `S extends T extends @Nullable Object` | `S extends T extends Object` |
| `…WhenDeclaredInUnmarkedCode` | `T` declared in a `@NullUnmarked` class | the same shape in marked code |
| `wildcardActualBoundedByTypeVariable…` | `Box<? extends T>` into `Box<? extends Object>` | `T extends Object` |
| `…OfNonNullTypeVariableOnlyWhenItsBoundAdmitsNull` | `Box<S>`, `S extends @Nullable T`, `T` non-null, into `Box<? extends T>` | `S extends T` |
| `…AcceptedByWildcardOfTypeVariableWhoseBoundAdmitsNull` | silent: the same, but `T extends @Nullable Object` | `Box<@Nullable S>`, which is reported |
| `…OfNonNullAnnotatedTypeVariableUnlessNonNullAtUse` | `Box<T>` into `Box<? extends @NonNull T>` | `Box<@NonNull T>` |
| `overrideReturningTypeVariable…` | override returns `Box<V>`, overridden returns `Box<? extends @NonNull V>` (the CHANGELOG sub-bullet) | override returns `Box<@NonNull V>` |

- **Pre-fix run:** with `nullaway/src/main` checked out from `HEAD~1`, the seven reporting cases fail with `Did not see an error on line N matching …. There were no errors.` The sixth test passes there too. It doesn't fail before the fix; it guards the `admitsNull(lhsBound)` branch against reporting too much.
- **Mutants:** I changed each new line by hand, one at a time, and reverted each. All of these are now caught:
  - removing `admitsNull(lhsBound)`;
  - deleting the `lhsBound instanceof Type.TypeVar` branch;
  - ignoring `@NonNull` in `hasNullnessAnnotation`;
  - making `typeComparedForNullness` return the type unchanged.

  Before these tests, the second and third survived the existing JSpecify tests.
- **Why one case per test:** I broke two markers on purpose to see how the harness reports. It stops at the first missing `// BUG` marker and names it by line number and pattern. So the file's usual style of several cases in one source would let one failure hide the next (skill §7, principle 1).
- **Expected message:** the `? extends @NonNull T` diagnostic prints `Box<? extends T>`, without the annotation, so that marker matches the printed text.

**Not done, proposed:**

1. **The capture exception (`rhsTypeArgument instanceof Type.CapturedType`) has no test.** With it removed, the full `:nullaway:test` suite and `buildWithNullAway` still pass. The only effect I found is that it silences a true positive:
   ```java
   class Test<V extends @Nullable Object> {
     void m(Box<? extends V> box) { Box<? extends @NonNull V> b = box.self(); }  // Box<E> self()
   ```
   This flow can carry a null. Without the exception it's reported; with it, and on the pre-fix code, it's silent. The same flow from a `Box<? extends @NonNull V>` is silent either way. So I couldn't build the case the commit message gives as the reason for the exception. Please add a test for the input that needs it, or drop the exception and turn the snippet above into a test.
2. **The library-model route through `upperBoundIsNullable`** (`onOverride*TypeVariableUpperBound`) has no test here. It needs a handler with library models, which this test class doesn't set up.
3. **Proposed line for `CLAUDE.md`, which I didn't edit:** `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with // BUG: Diagnostic contains: markers, which stops at the first missing marker and names it by line and pattern, so a source holds one case with its controls.`

I ran only `WildcardTests` and the `com.uber.nullaway.jspecify.*` tests on the final version, not the full module suite. All production files are back at `HEAD`.
