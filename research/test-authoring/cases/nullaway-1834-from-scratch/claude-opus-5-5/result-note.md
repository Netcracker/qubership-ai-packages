I added five tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, right after `wildcardActualArgumentNoInference`. All five fail on the commit before your fix and pass on it; the full `:nullaway:test` and `:nullaway:buildWithNullAway` both pass. Production code is unchanged and nothing is committed.

Here is the message for the pull request author:

---

**Tests added for "Report a type argument whose bound admits null where a non-null wildcard is required"**

Each test compiles one source through the existing `makeHelper()` and holds one call that must now be reported, next to calls that differ from it in one respect and must stay silent. That layout is deliberate: Error Prone's `CompilationTestHelper` (2.50.0) stops at the first mismatch it finds and names it only by line number (`DiagnosticTestHelper.java:264-268` and `:288`). So each test holds only one call that should be reported, and the test name states the rule.

| Test | Reported call | Calls that must stay silent |
| --- | --- | --- |
| `typeVariableArgumentMeetsNonNullWildcardOnlyWhenItsBoundExcludesNull` | `Foo<N>` with `N extends @Nullable Object` passed to `Foo<? extends Object>` | `Foo<M>` (non-null bound); `Foo<@NonNull N>` |
| `...ExcludesNullInUnmarkedCode` | `Foo<U>`, where `U` is declared in a `@NullUnmarked` class | `Foo<@NonNull U>` |
| `wildcardArgumentBoundedByTypeVariableMeetsNonNullWildcardOnlyWhenTheVariableExcludesNull` | `Foo<? extends N>` passed to `Foo<? extends Object>` | `Foo<? extends M>` |
| `typeVariableArgumentMeetsWildcardOfAnotherVariableOnlyWhenNullCannotEnterThroughItsBound` | `Foo<S>` with `S extends @Nullable E` passed to `Foo<? extends E>` | `Foo<R extends E>`; `Foo<E>`; the same `S` when `E` itself admits null |
| `typeVariableArgumentMeetsNonNullTypeVariableWildcardOnlyWhenItsBoundExcludesNull` | `Foo<N>` passed to `Foo<? extends @NonNull N>` | `Foo<M>`; `Foo<@NonNull N>` |

**Failing before the fix:** on `HEAD~1` with these tests, each of the five fails on its reported line with `Did not see an error on line N matching incompatible types: … There were no errors.` The missing report is the bug itself.

**Mutants of the changed lines:** I made each change by hand and ran the jspecify tests, confirming each mutant compiled:
- Comparing the actual's bound for a type-variable requirement fails the fourth test with a false report on `Foo<E>` when `E` admits null.
- Replacing `admitsNull(lhsBound)` with `true` fails the fourth and fifth tests. Replacing it with `false` fails the fourth test and four existing tests.
- Replacing `!admitsNull(rhsUpperBound)` with `true` fails the fourth and fifth tests.
- Using `getUpperBound()` in place of `typeVariableUpperBound` fails the unmarked-code test.
- Ignoring `@NonNull` at the use site fails the three tests that have a `@NonNull` call, each on that call's line.

**Not resolved: the captured-actual exception.** Removing `rhsTypeArgument instanceof Type.CapturedType ||` leaves all 1,104 tests in `:nullaway:test` green. I added a temporary print to that branch. Every captured actual that reached it, from existing tests and from several inputs I tried, kept its `@NonNull` on the bound (`capture of ? extends @NonNull V`, bound `@NonNull V`). So the exception changed no outcome. I couldn't reproduce the annotation loss the commit message describes. Either the input that produced it should become a test, or the exception should be justified another way.

**Proposed, not done:**
1. **Diagnostic text.** The message drops `@NonNull` from the requirement: `Test.Foo<N> cannot be converted to Test.Foo<? extends N>`, when the parameter is `Foo<? extends @NonNull N>`. Read alone, the report looks wrong, since `Foo<N>` does fit `Foo<? extends N>`. The fifth test matches today's text and would need updating if the message is fixed.
2. **Override checks.** The changelog says override checks now report too (`List<V>` returned where `List<? extends @NonNull V>` is overridden). That goes through the same containment code, but no test pins it.
3. **Library-model route.** A type variable whose bound admits null only because of a library model reaches the new code through `typeVariableUpperBound`. That route has no test here; it would need a test that supplies library models.
4. **Stack line for `AGENTS.md`.** Something like: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with "// BUG: Diagnostic contains:" markers, which stops at the first mismatch and names it by line number only (no per-marker label)`. I haven't edited `AGENTS.md`; I'll add the line if you want it.

---
