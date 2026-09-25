I rewrote the 21 tests the commit added to `WildcardTests.java` as 11, and the class passes: 57 tests, all green. Production code is unchanged and nothing is committed. While adding a control I found a false positive that the fix introduces (item 1 below).

Here is the message I'd leave for the author:

---

**Tests for "Report a type argument whose bound admits null where a non-null wildcard is required"**

**1. The fix introduces a false positive.** With the fix, this is reported; on the base commit it is not:

```java
@NullMarked
interface Test<V extends @Nullable Object> {
  List<? extends V> get();
  static <V extends @Nullable Object> Test<V> make() {
    return new Test<>() {
      @Override public List<V> get() { throw new UnsupportedOperationException(); }
      // warning: Method returns List<V>, but overridden method returns List<? extends V>,
      //          which has mismatched type parameter nullability
    };
  }
}
```

`List<V>` is a valid override of `List<? extends V>` for any `V`. The same override in a named class (`class Impl<W …> implements Test<W>`) is not reported, so the anonymous class with `new Test<>()` seems to be the trigger. I found this while adding the obvious control to `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported`. I left that control out, because asserting the warning would lock in the bug. The CHANGELOG entry says only the `? extends @NonNull V` override is newly reported. I suggest adding this source as a no-warning control to that test when you fix it.

**2. What changed in the tests, and why.**
- **Evidence that the tests catch the bug.** I ran the tests against the base commit's production code. Seven fail with `Did not see an error on line N … There were no errors.`, which is the bug's symptom (the report was missing). They are the seven tests that expect a report the fix adds. The other 14 passed on the base: they are controls, or guards against the fix reporting too much.
- **Each new case sits beside its controls in one source.** Before, a case and its controls were separate tests, each with its own copy of the class, so nothing kept the reporting input and the silent inputs alike. `CompilationTestHelper.doTest()` stops at the first mismatching marker (`DiagnosticTestHelper.java:248–289`, Error Prone 2.50.0). So each test holds at most one input that expects a report, and each test name states the rule it checks.
- **What joined what:**
  - `aNonNullWildcardRejectsATypeVariableOnlyWhenItsBoundIsNullable` merges five old tests: the nullable-bound case, the non-null bound, a `@NonNull T` use, the `? extends @Nullable Object` requirement, and the `?` requirement.
  - `…OnlyWhenDeclaredInUnannotatedCode`, `…OnlyWhenTheVariableItExtendsIsNullable` and `aNonNullWildcardRejectsAWildcardActualOnlyWhenItsTypeVariableBoundIsNullable` each gained one new control that differs from the case in one respect: a `@NullMarked` holder, `<T, S extends T>`, and `Box<? extends T>` with `<T>`.
  - `aWildcardBoundedByATypeVariableRejectsAnActualThatAdmitsNullOnlyWhenTheVariableDoesNot` covers both `<S extends T>` and `<S extends @Nullable T>`, each under a non-null `T` and a nullable `T`. The nullable-`T` / `<S extends @Nullable T>` combination is new.
  - `aWildcardBoundedByANonNullTypeVariableRejectsAnActualOnlyWhenItAdmitsNull` puts the `? extends @NonNull T` case beside a new `@NonNull T` control and the old "same type variable" test.
  - The two tests of a `@Nullable T` use were already reported on the base. Each is now one test with its control.
  - The two captured-type tests are merged into one test.
  - The inference test and the override test are kept as they were.
- **Case labels.** Methods inside each source are named after their case (`nullableBound`, `nonNullOuterBound`, …). The harness reports only a line number, so these names let a reader with the file find the case.
- **Mutants.** I tried two by hand and reverted both.
  - Dropping the `CapturedType` exception fails the captured-type test.
  - Turning off the branch for a requirement that names a type variable (`if (false)`) fails three of the new controls and the captured-type test.
  - Neither mutant fails `passLoadAll` (in the merged captured-type test) or the `CompletableFuture` inference test. They still guard real-world shapes, but no line of this fix depends on them.

**3. Proposed, not done:**
- Add a stack line to `CLAUDE.md`, for example: `Tests: JUnit 4 engine; Truth for assertions; checker tests use Error Prone's CompilationTestHelper, whose doTest() stops at the first mismatching marker and names it only by line number`. I didn't edit it; it's your call.
- The harness has no way to label a `// BUG:` marker, so a failure names only a line. That would be an Error Prone feature request; check their tracker for an existing issue first. I filed nothing.

---
