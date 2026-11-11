I added five tests at the end of `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java` and changed no production code. Nothing is committed. `WildcardTests` and `./gradlew :nullaway:buildWithNullAway` both pass.

All five fail on the code before the fix (`HEAD~1`), each with "Did not see an error on line N matching …". On that code, every source in them compiles with no report at all, so the methods expected to stay silent were already silent there. I put the production files back afterwards.

There's one gap: the capture-conversion exception in `extendsBoundContains` has no test. When I replaced that condition with `false`, every `:nullaway` test still passed, and so did every source I wrote to reach it.

**Message for the pull request author**

Tests added to `WildcardTests`. Each one compiles one source holding a call that should now be reported, plus calls that should stay silent:

- **`typeVariableActualIsRejectedOnlyWhenItsDeclaredBoundAdmitsNull`**: passing a `Box<T>` with `T extends @Nullable Object` to a `Box<? extends Object>` is reported. A `T extends Object`, and a `Box<@NonNull T>` with the same nullable bound, are not.
- **`wildcardActualBoundedByTypeVariableIsRejectedOnlyWhenThatBoundAdmitsNull`**: the same rule when the argument is itself a wildcard, `Box<? extends T>`.
- **`typeVariableActualIsContainedInAWildcardBoundedByATypeVariableUnlessOnlyTheActualAdmitsNull`**: when `T` can't be null, a `Box<S>` with `S extends @Nullable T` passed to a `Box<? extends T>` is reported. `Box<T>` and `Box<S extends T>` are not.
  - It also has a class where `T extends @Nullable Object` and the same `S` passes. Replacing the `admitsNull(lhsBound)` term with `false` makes this test fail, so that term is covered.
- **`typeVariableActualWhoseBoundAdmitsNullIsRejectedByAWildcardBoundedByANonNullUse`**: a `Box<T>` passed to a `Box<? extends @NonNull T>` is reported; a `Box<@NonNull T>` is not.
- **`overrideReturningATypeVariableArgumentWhoseBoundAdmitsNullIsRejectedWhereANonNullUseIsRequired`**: the override check from the changelog. Returning `List<V>` where the overridden method returns `List<? extends @NonNull V>` draws `mismatched type parameter nullability`; returning `List<@NonNull V>` doesn't.

I tested one call site (passing an argument) plus the override check. Assignments and returns go through the same visitor, so I didn't repeat each rule for them.

Not done, proposed:

1. **The capture exception (`rhsTypeArgument instanceof Type.CapturedType`) is untested, and I couldn't settle whether it's needed.** With it replaced by `false`, the whole `:nullaway` suite still passes. I tried calls with captured actuals:
   - a parameter, a field, a method result, a list element and a local, all typed `Box<? extends @NonNull V>`;
   - `Box<? extends V>`, `Box<? extends @Nullable V>`;
   - passed as an argument, returned, or assigned to a `Box<? extends @NonNull V>`.

   Each produced the same diagnostics with and without the exception. Could you share a source where removing it changes a diagnostic? Then it can become a test. If no such source exists, the exception may not be needed.
2. **The diagnostic drops `@NonNull`, so some reports read as self-contradictory.** For `Box<? extends V>` passed to `Box<? extends @NonNull V>`, the message is `incompatible types: Box<? extends V> cannot be converted to Box<? extends V>`. The new tests match the text as it is printed today.
3. **Some ways a bound can admit null are untested on the new path.** `typeVariableUpperBound` also treats a bound as nullable when a library model overrides it, or when the type variable is declared in `@NullUnmarked` code. I couldn't get such a type variable to appear unsubstituted at a checked call site.

A proposal for you, not part of the PR text: `CLAUDE.md` has no line naming the test stack. While working I learned how Error Prone's `CompilationTestHelper` reports failures:
- one `doTest()` stops at the first mismatch ("Did not see an error on line N" / "Saw unexpected error on line N");
- it names that mismatch by line number;
- it lists every reported diagnostic with its source line.

Shall I add a line like this to `CLAUDE.md`? `Tests: JUnit 4 engine; Error Prone CompilationTestHelper (one doTest stops at the first mismatch and names it by line number)`.
