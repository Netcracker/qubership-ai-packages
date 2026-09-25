I rewrote the 20 tests from `d55c150` as 12 in `WildcardTests.java`. Production code is untouched and nothing is committed. `WildcardTests` passes on the fixed code (57 tests). I did not run `:nullaway:buildWithNullAway`, since only test code changed. The note for the author follows.

---

**To the author of the change**

**What I changed and why**

I checked how the test harness reports failures first, because that decides how cases can be grouped. Error Prone's `CompilationTestHelper.doTest()` stops at the first mismatch: a missing `BUG:` marker or an unexpected diagnostic. It names the failing case only by its line number, and it offers no way to give a case a label (`DiagnosticTestHelper.java:223-291` in `error_prone_test_helpers` 2.50.0).

Your 20 tests put each case and each of its controls in a separate test, each with its own copy of the class. One compilation can check a case and its controls together. So I grouped them: each test now holds one rule, at most one input that expects a report, and controls that miss the rule's condition in exactly one respect. Each test name states the rule it checks.

| New test | Case (reported) | Controls (silent) | Replaces |
| --- | --- | --- | --- |
| `…OnlyWhenItsBoundIsAnnotatedNullable` | `Box<N extends @Nullable Object>` → `? extends Object` | bound without `@Nullable`; `@NonNull N` at the use; nullable wildcard; `Box<?>` | 1, 2, 3, 8, 12 |
| `…OnlyWhenItIsDeclaredInNullUnmarkedCode` | `T` of a `@NullUnmarked` holder | the same holder without `@NullUnmarked` (new control) | 9 |
| `…OnlyWhenItsBoundIsATypeVariableThatAdmitsNull` | `S extends N`, where `N` admits null | `R extends M`, where `M` does not (new) | 10 |
| `aWildcardIsRejected…ATypeVariableThatAdmitsNull` | `Box<? extends N>` | `Box<? extends M>` (new) | 20 |
| `aNullableTypeVariableUseIsRejectedByANonNullWildcardWhateverItsBound` | `Box<@Nullable T>` | `Box<T>`; nullable wildcard | 4, 5 |
| `…BoundedByAnotherOnlyWhenItAdmitsNullAndTheOtherDoesNot` | `S extends @Nullable T` → `? extends T`, where `T` cannot be null | `R extends T`; the same three calls in a holder whose `T` admits null | 6, 11, 14, 15 |
| `…BoundedByItselfAnnotatedNonNullOnlyWhenItsUseAdmitsNull` | `Box<T>` → `? extends @NonNull T` | `Box<@NonNull T>` (new) | 18 |
| `aNullableTypeVariableUseIsRejectedByAWildcardBoundedByThatVariable` | `Box<@Nullable T>` → `? extends T` | `Box<T>` (new) | 13 |
| `anOverrideIsReportedOnly…` | override returning `List<V>` | override returning `List<@NonNull V>` (new) | 19 |
| `aCapturedTypeArgumentMeets…` | — | both captured cases in one interface | 16, 17 |
| `anInferredTypeArgumentMeets…` | — | unchanged except the name | 7 |

Grouping follows the harness: two reports in one compilation would hide each other, so cases of the same rule that each draw a report stay in separate tests.

**Evidence**

- **Pre-fix code:** I ran the new tests against the production code from `HEAD~1`. Exactly the 7 tests whose report the fix adds go red, and each fails with `Did not see an error on line N matching …` on its own case. Your original 7 tests of the same cases also go red there. The other tests pass on both versions.
- **Mutants:** I tried three mutants of `CheckIdenticalNullabilityVisitor`, and the tests catch all three:
  - Dropping the exception for captured types breaks the captured test.
  - Removing the branch for requirements that name a type variable breaks both `? extends T` tests and the captured test.
  - Ignoring the annotation written on a type-variable use breaks the `@Nullable`-use test, and the `@NonNull`-use control in the first test.

**Proposed, not done**

1. **A stack line for `CLAUDE.md` / `AGENTS.md`**, for example: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper, whose doTest() stops at the first mismatch and names a case only by line number`. That tells the next author how to group cases without re-reading the harness source.
2. **A way to label cases in the harness.** Error Prone's `BUG: Diagnostic contains:` marker has no label, so a failure reads `line 13` and you have to open the file to see which case it is. This would be a request against Error Prone. I couldn't check their tracker for an existing report.
3. **A possible missed report.** While probing, I found that returning a captured `Map<? extends K, ? extends V>` (with `V extends @Nullable Object`) where `Map<? extends K, ? extends @NonNull V>` is required draws no report. The exception for captured types seems to let this through. I did not add a test, because the expected behavior is a decision for you. If it should be reported, it belongs as the case in `aCapturedTypeArgumentMeets…`.
4. **Two silent cases none of my three mutants catches:** `anInferredTypeArgumentMeets…` and the bare captured `pass()` case. I kept both. If they came from a failure you saw during development, a one-line comment naming that failure would tell a reviewer what they guard. If they didn't, they could be dropped.
