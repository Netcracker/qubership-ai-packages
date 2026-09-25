I added six regression tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`. Nothing is committed and the production code is unchanged. All six fail on the base commit and pass on HEAD. The whole `:nullaway:test` suite and `:nullaway:buildWithNullAway` both pass.

---

**Message for the author**

The fix adds six new silences to NullAway's rejections and no tests, so I added one regression test for each partition whose outcome the fix moves. They go in `WildcardTests`, next to the existing wildcard containment tests. They're compile-and-check tests of the kind the module calls unit tests: each compiles one source in-process.

| Test | Reported case | Silent controls beside it |
|---|---|---|
| `typeVariableArgumentIsRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>`, `T extends @Nullable Object` → `Box<? extends Object>` | `Box<@NonNull T>`; `Box<T>` with `T extends Object` |
| `wildcardArgumentBoundedByTypeVariableIsRejectedByNonNullWildcardOnlyWhenTheBoundAdmitsNull` | `Box<? extends T>`, same `T` → `Box<? extends Object>` | the same with `T extends Object` |
| `unboundedTypeVariableArgumentIsRejectedByNonNullWildcardOnlyWhenDeclaredInUnmarkedCode` | `Box<T>` where `T` is declared in `@NullUnmarked` code | the same class in `@NullMarked` code |
| `typeVariableArgumentIsRejectedByWildcardOfAnotherTypeVariableOnlyWhenItMayBeNullAndTheOtherMayNot` | `Box<S>`, `S extends @Nullable T` → `Box<? extends T>` | `Box<R extends T>`; `Box<T>`; the same `S` where `T` itself may be null |
| `typeVariableArgumentIsRejectedByNonNullTypeVariableWildcardOnlyWhenItMayBeNull` | `Box<V>` → `Box<? extends @NonNull V>` | `Box<@NonNull V>` |
| `overrideReturningTypeVariableArgumentIsRejectedByNonNullTypeVariableWildcardOnlyWhenItMayBeNull` | override returning `List<V>` where the overridden method returns `List<? extends @NonNull V>` | override returning `List<@NonNull V>` |

The override test repeats the fifth test's rule through override checking, because the changelog promises that behavior separately.

**Evidence**
- **Red on the base commit:** with `nullaway/src/main` checked out from `HEAD~1`, all six fail with the bug's symptom: `Did not see an error on line N matching … There were no errors.` No existing test's expectation moved.
- **Hand-made mutants of the fix, scored against `WildcardTests`:** each of these makes at least one new test fail:
  - removing `admitsNull(lhsBound) ||`
  - removing the `lhsBound instanceof Type.TypeVar` branch
  - forcing `!admitsNull(rhsUpperBound)` to true
  - ignoring `@NonNull` in `hasNullnessAnnotation`
  - comparing a type variable by its raw declared bound instead of `typeVariableUpperBound`

**Test shape**
- Error Prone's `CompilationTestHelper` stops at the first missing `// BUG: Diagnostic contains:` marker (`DiagnosticTestHelper.java:264-267`, 2.50.0). It also fails on any unmarked line that gets a diagnostic (`:289`), and it names a case only by its line number.
- So each test holds exactly one input that expects a report, with its silent controls in the same source, and the test's name states the rule.
- Several neighbors in `WildcardTests` put two or more reported markers in one source; the new tests don't follow that shape, because the first missing marker hides the rest (§7 and §9 of the test-authoring skill).

**Proposed, not done**
1. **Unresolved: nothing reaches the capture exception.** Removing `rhsTypeArgument instanceof Type.CapturedType ||` fails nothing in the whole `:nullaway` suite. Temporary logging showed the branch is reached, but the captured wildcard always kept `@NonNull V`, so the clause never changed the result. I couldn't build an input where capture drops the annotation, as the commit message describes. Could you add the input that motivated the clause as a test, or drop the clause?
2. **The library-model path of `typeVariableUpperBound` has no test.** That's a model that overrides a type variable's bound (`onOverrideClassTypeVariableUpperBound` / `onOverrideMethodTypeVariableUpperBound`). It needs the library-models test setup, so I left it out.
3. **The diagnostic drops `@NonNull`.** The fifth test's report reads `Box<V> cannot be converted to Box<? extends V>`, which looks like a legal assignment. Printing `? extends @NonNull V` would make the report clearer.
4. **The harness names cases only by line number.** A label for each `// BUG:` marker would need a change to Error Prone's test helper, so this is a possible upstream issue. I filed nothing.
5. **A stack line for `AGENTS.md`.** I didn't edit it. Something like: `Tests: JUnit 4 engine and assertions; Error Prone CompilationTestHelper for checker tests — one doTest() stops at the first missing "// BUG: Diagnostic contains:" marker, fails on any unmarked line that gets a diagnostic, and names a case only by its line number.` Should I add it?
