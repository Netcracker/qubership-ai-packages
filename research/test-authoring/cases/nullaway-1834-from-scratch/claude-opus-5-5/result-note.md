I added seven tests to `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, right after `wildcardActualArgumentNoInference`. Six of them fail on the parent commit with the bug's symptom, which is that no diagnostic appears at all. The production code is untouched and nothing is committed. The full `:nullaway:test` run has 1106 tests and 0 failures, and `:nullaway:buildWithNullAway` passes.

---

**Message for the PR author**

This PR changes which code NullAway reports, so it needs tests. I added seven to `WildcardTests`, each compiling a single source with `CompilationTestHelper`.

**Tests added.** Each holds one case that should now be reported, next to the closest inputs that should stay silent:

| Test | Reported | Stays silent |
| --- | --- | --- |
| `typeVariableActualIsRejectedByNonNullWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>` with `T extends @Nullable Object` passed to `Box<? extends Object>` | `Box<@NonNull T>`; `Box<U>` where `U`'s bound is non-null |
| `wildcardActualIsRejectedByNonNullWildcardOnlyWhenItsTypeVariableBoundAdmitsNull` | `Box<? extends T>` passed to the same parameter | `Box<? extends U>` |
| `typeVariableFromNullUnmarkedCodeIsRejectedByNonNullWildcardOnlyWhenUnannotated` | `T` declared in a `@NullUnmarked` class, used in a `@NullMarked` method | `Box<@NonNull T>` |
| `subtypeVariableIsRejectedByParametricWildcardOnlyWhenItAdmitsNullAndTheRequirementDoesNot` | `Box<S>` with `S extends @Nullable T` passed to `Box<? extends T>` | `Box<R extends T>`; `Box<T>`; `M extends @Nullable N` passed to `Box<? extends N>` where `N` admits null |
| `typeVariableActualIsRejectedByNonNullTypeVariableWildcardOnlyWhenItsBoundAdmitsNull` | `Box<T>` passed to `Box<? extends @NonNull T>` | `Box<@NonNull T>` |
| `overrideReturningTypeVariableIsRejectedWhereNonNullTypeVariableWildcardIsReturned` | The override case from the CHANGELOG | An override returning `List<@NonNull V>` |
| `nullableTypeVariableUseIsRejectedByParametricWildcardWhoseBoundAdmitsNull` | `Box<@Nullable N>` passed to `Box<? extends N>` | `Box<N>` |

The last test passed before this PR too. It protects the choice the commit message explains: a type-variable requirement is not replaced by its bound. If that choice were reversed, this report would go silent.

**Why one case per test.** I checked Error Prone 2.50.0's `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` (lines 223–292):
- It stops at the first expected diagnostic that doesn't appear, or the first unexpected one.
- It identifies the failing case only by line number and offers no label.

A source with several `// BUG` markers, as most neighbouring tests in this file have, would therefore hide the second failure behind the first. So each test has exactly one expected report, surrounded by silent controls, and its name states the rule being tested. I left the existing tests alone.

**Evidence the tests can fail.**
- **Before the fix:** I cloned the repo into a scratch directory and put back `nullaway/src/main` from `HEAD~1`. Six tests fail with `Did not see an error on line N matching … There were no errors.` The seventh passes, as expected.
- **Mutations:** I also broke the fix in that clone in several ways, one at a time. At least one new test fails for each of these:
  - replacing a type-variable requirement with its bound;
  - dropping `admitsNull(lhsBound)`;
  - ignoring use-site annotations in `typeComparedForNullness` or in `admitsNull`;
  - ignoring `@NonNull` in `hasNullnessAnnotation`;
  - making `typeComparedForNullness` return its argument unchanged;
  - making `typeVariableUpperBound` return the declared bound as written.

**Not resolved: the `CapturedType` short-circuit in `extendsBoundContains`.** Removing it breaks nothing, neither in the full suite nor in the capture forms I tried: return values, fields, locals, `self()` calls and list elements. I added a temporary print statement in the scratch clone, and it showed:
- Captured actuals do reach that branch.
- But `wildcardUpperBound` already restores the annotation there (`capture of ? extends @NonNull T` gives an upper bound of `@NonNull T`), so the actual never looks nullable.

In other words, I couldn't reproduce the situation the commit message describes, where capture drops the annotation. Either there is a source that does it and it deserves a test, or the clause is unnecessary. I'd like you to settle which. I didn't add a test that claims to cover it.

**Not covered:** a type variable whose bound becomes nullable through a library model. The model applies to type variables declared in compiled library classes, and those variables only appear as-is inside the library, which NullAway doesn't check. As far as I can tell, no call site can observe it.

**Proposed, not done:**
- **Diagnostic text:** the diagnostic prints the requirement `Box<? extends @NonNull T>` as `Box<? extends T>`, so users see "`Box<T>` cannot be converted to `Box<? extends T>`". The marker in that test matches only up to `Box<? extends`, so it doesn't lock in the missing annotation. Printing the `@NonNull` looks worth a follow-up.
- **Instructions line:** the repository's instructions don't name its test stack. I suggest adding this to `CLAUDE.md`: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatched diagnostic and names each case only by line number.`
