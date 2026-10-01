I rewrote the 21 tests the commit added to `WildcardTests.java` as 3 tests, one per rule. They all pass on the fix, and each one fails on the base production code. The full `:nullaway:test` run and `:nullaway:buildWithNullAway` both pass. Production code is unchanged and nothing is committed.

**Message for the pull request author**

> **What changed in the tests, and why**
>
> The 21 tests this change added to `WildcardTests` are now 3, one per rule. The repository's stack line asks for the cases of one rule to be kept in one source, written as if `doTest()` reported every mismatch. Before, each input had its own method and its own copy of the class. The 14 silent or already-reporting inputs stood in tests of their own, so nothing showed the silent ones next to an input that reports.
>
> I ran the original tests against the base production code (`d55c150^`) to sort the inputs. Seven failed there: these are the cases this change makes report. The other 14 behave the same before and after the fix: they are controls. The rewrite keeps every one of them.
>
> - **`aTypeVariableArgumentIsCheckedAgainstAConcreteWildcardByItsAnnotationOrElseItsBound`**: a requirement like `Box<? extends Object>`.
>   - Cases: a bound that admits null directly, through another type variable, through `? extends T`, or because the variable is declared in `@NullUnmarked` code.
>   - Controls: a non-null bound, `@NonNull T` and `@Nullable T` written at the use, and the `? extends @Nullable Object` and `Box<?>` requirements.
>   - The calls that differ only in the requirement sit on adjacent lines in one method, so the requirement is the only difference.
> - **`anArgumentForAWildcardBoundedByATypeVariableFailsOnlyWhenItAdmitsANullTheBoundDoesNot`**: a requirement like `Box<? extends T>`.
>   - Cases: `Box<T>` passed to `Box<? extends @NonNull T>`, and `S extends @Nullable T` passed to `Box<? extends T>` where `T` is non-null.
>   - Controls: the same variable, `S extends T`, `@Nullable T`, the return form, and the `CompletableFuture` inference and captured-type inputs, which are now nested interfaces.
>   - The silent captured and inference inputs now share a source with inputs that report.
> - **`anOverrideMayNotReturnATypeVariableWhereANonNullWildcardOfItWasPromised`**: kept separate because the override check reports a different diagnostic. I added one control: an override returning `List<@NonNull V>`, which stays silent before and after the fix.
>
> I added two inputs, both controls that stay silent before and after the fix: the override above, and `takeExtendsT(b)` beside `takeExtendsNonNullT(b)`, so the `@NonNull` on the requirement is the only difference. No input was dropped.
>
> **Evidence:**
> - On the base production code, all three tests fail on a missing report: lines 13, 19 and 11 respectively.
> - With the seven case markers removed, the rewritten sources pass on the base, so every control holds there.
> - On the fix, `:nullaway:test` and `:nullaway:buildWithNullAway` pass.
>
> **Proposed, not done:** The pull request description should include the base-commit run as its evidence. Proposing nothing about `CompilationTestHelper`: the stack line already accepts this form.

The skill also defers to a writing-style skill and a Javadoc skill, but neither is available in this session, so I didn't load them.
