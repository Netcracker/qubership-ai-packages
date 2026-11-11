I rewrote the 20 tests the last commit added as three tests, one per rule. Each test is a single source that holds every input of its rule, and no input was dropped. All three pass on the fixed code, and `:nullaway:buildWithNullAway` passes. Nothing is committed and the production code is unchanged. The only modified file is `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`.

**Message for the author:**

---

I regrouped the 20 tests you added to `WildcardTests` into three tests, one per rule. Every input you wrote is still there.

- **`aTypeVariableArgumentFailsANonNullWildcardRequirementOnlyWhenItAdmitsNull`**: 10 of your inputs, all checked against `Box<? extends Object>`.
  - Reported: a bound that admits null, an `S extends T` chain, a `? extends T` argument, and a variable declared in `@NullUnmarked` code.
  - Not reported: the same arguments with a non-null bound or `@NonNull` on the use, or passed to a `? extends @Nullable Object` or `?` requirement.
  - `Box<@Nullable T>` is reported and stays reported.
- **`aTypeArgumentFailsAWildcardBoundedByATypeVariableOnlyWhenItAdmitsNullThatVariableExcludes`**: 9 inputs, all checked against `? extends T` or `? extends @NonNull T`.
  - It has two holders, one where `T`'s bound admits null and one where it doesn't.
  - It also includes the `CompletableFuture` inference input and the two captured-`Map` inputs.
- **`anOverrideReturnTypeFailsANonNullWildcardOfATypeVariableOnlyWhenItsArgumentAdmitsNull`**: your override input, plus one new input. An override that returns `List<@NonNull V>` is not reported, so the test shows that the report comes from the type argument and not from the anonymous-class setup.

Why:
- **Most of your tests expected no diagnostic.** A test that expects silence proves little alone, because the silence could come from the setup and not the rule. Each one now sits in the same source as inputs of its rule that are reported.
- **The new layout is what our `CLAUDE.md` asks for.** It says to keep a rule's inputs in one source, even though `doTest()` stops at the first mismatch.
- **Each test name now states the rule.** The method names inside each source say what each input is.
- **I renamed type variables in two places.** `Box`'s parameter is now `E` everywhere, and the unannotated holder's variable is now `U`. Without that, two markers had the same text, and `doTest()` names a mismatch only by line number.
- **I moved the two interfaces inside `Test`.** `Loader` and the `Map` loaders are now nested types of `Test`, so they can share its source. Their declarations are unchanged.

How I checked it, on the commit before the fix (worktree removed afterwards):
- Your original 20 tests: exactly 7 failed. Those were the 7 inputs the fix changed. The other 13 already held, including both `Box<@Nullable T>` inputs.
- The three new tests: each one fails at one of those 7 inputs.
- With the markers for those 7 inputs removed, all three pass. That shows every other input, including the new `List<@NonNull V>` override, holds without the fix.

What I propose and did not do: no test covers the gap your commit message describes. javac prints the capture of `? extends @NonNull V` as the capture of `? extends V`, so a captured `? extends V` argument passed where `? extends @NonNull V` is required is accepted. That looks like a missed report. I'd add it, with a message naming the javac limitation, so whoever fixes it knows the expected value has to change. I left it out because it records a known defect, and whether to record it is your call.
