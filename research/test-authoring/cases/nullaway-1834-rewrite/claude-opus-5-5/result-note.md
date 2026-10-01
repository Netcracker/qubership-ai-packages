I rewrote the 20 tests the commit added to `WildcardTests.java` as 8, and the rewrite turned up a new false positive from the fix. Production code is unchanged and nothing is committed. All 54 tests in `WildcardTests` pass on HEAD, and `./gradlew :nullaway:buildWithNullAway` passes.

**The false positive:** the fix reports an override that is valid. In a static `<V extends @Nullable Object>` method, an anonymous class written with the diamond, `return new Test<>() { @Override public List<V> get() … }`, is now flagged when `Test.get()` returns `List<? extends V>`. The message is "Method returns List<V>, but overridden method returns List<? extends V>, which has mismatched type parameter nullability". Before the fix this compiled clean. Writing `new Test<V>()` instead, or using a named implementing class, is still silent.

So your test `anOverrideThatWidensANonNullProjectionInItsReturnTypeIsReported` passes whether or not `@NonNull` is on the overridden return type. It can't catch the bug it describes. I wrote my override test with `new Test<V>()` so it means something. The diamond false positive needs a fix in `CheckIdenticalNullabilityVisitor` (or wherever the override check gets its substituted `V`), with the diamond form as its regression test. I didn't attempt that, since you asked me to leave production code alone.

Here's the message I'd leave for you as the author:

---

**What changed in the tests and why**

- **Which inputs are cases.** I ran your 20 tests against the code before the fix. Only the 7 tests that expect a new report fail there, which makes them the cases. The other 13 already pass there, so they are controls: they show a report comes from the bound and not from the setup. That includes the two `Box<@Nullable T>` tests that expect a report.
- **What the harness can show.** I broke cases on purpose to see how Error Prone's `CompilationTestHelper` reports. It stops at the first missing `// BUG:` marker, which it names by line and expected text. It names an unexpected diagnostic by line number only. So one source can hold one case with its controls, but not two cases.
- **The new layout.** Each of the 7 cases is now one test that carries its controls in the same source. Each control is a separate method that differs from the case in one respect. The method names say which respect (`nonNullBound`, `nullableRequirement`, `nonNullUse`, `unboundedRequirement`, …).
  - The test name states the rule, plus the case's variant where one rule has several tests. For example: `aTypeVariableIsRejectedByANonNullWildcardOnlyWhenItsDeclaredBoundAdmitsNull`, `…DeclaredInUnannotatedCode…`, `…BoundedByANullableTypeVariable…`, `aWildcardBoundedByANullableTypeVariable…`.
  - The two `Box<@Nullable T>` → `Box<? extends Object>` / `Box<? extends @Nullable Object>` tests became one test, `aNullableTypeVariableUseIsRejectedByAWildcardUnlessItsBoundIsNullable`. Neither moved with the fix; together they guard that a `@Nullable` written at the use site is kept.
  - The inference and captured-type tests that expect silence now share a source with the `? extends @NonNull T` case. Before, each stood alone, with no input next to it that expected a report.
- **Nothing was dropped.** Every input from the original 20 is still there. I added a control to the four cases that had none: a `@NullMarked` holder, `<T, S extends T>`, `<T> Box<? extends T>`, and an override of a plain `List<? extends V>`. To check the controls, I removed only the 7 case markers and ran against the code before the fix: all 54 tests pass there. So every control held before the fix, and every case line was silent before it.
- **Two cosmetic changes.** The type parameter of `Box` is `E` everywhere, so it isn't confused with the method's `T`. The override test uses `new Test<V>()`, for the reason above.

**Proposed, not done**

1. **Fix the diamond false positive** described above, with the diamond form as its regression test.
2. **Add a test stack line to `AGENTS.md`,** for example: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper with // BUG: Diagnostic contains: markers; one compilation stops at the first missing marker, which it names by line and expected text, and names an unexpected diagnostic by line only.` I didn't edit the file; that needs your agreement.
3. **Open an Error Prone issue** asking `CompilationTestHelper` to report every mismatch in one run, and to name an unexpected diagnostic by its source text rather than only "Saw unexpected error on line N". It has no way to label a marker today. I couldn't check their issue tracker for an existing request, since I had no network tools.
