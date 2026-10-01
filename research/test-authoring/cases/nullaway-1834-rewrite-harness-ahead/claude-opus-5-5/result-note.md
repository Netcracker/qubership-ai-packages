I rewrote the tests the last commit added to `WildcardTests.java`: 20 one-input tests are now 3, one per rule, and all 20 inputs are kept. Production code is unchanged and nothing is committed. `WildcardTests` passes (49 tests, 0 failures) and `:nullaway:buildWithNullAway` passes.

**Message for the PR author:**

> The fix moves seven of the 20 inputs the commit added: I ran the new tests on the pre-fix production code and exactly those seven failed. The other 13 already held before the fix, so they are controls, and the rewrite keeps every one of them.
>
> The repository's test-stack instructions let the cases of one rule share one source, as if `doTest()` reported every mismatch. So I grouped the inputs by rule, three tests in all. Each case now stands next to its controls in one source.
>
> 1. **`aTypeVariableIsJudgedByItsDeclaredBoundAgainstAConcreteWildcardBound`**
>    - Cases (silent before the fix):
>      - a bound that admits null;
>      - a bound inherited from another variable;
>      - the variable reached through `? extends T`;
>      - a variable declared in `@NullUnmarked` code.
>    - Controls:
>      - a non-null bound;
>      - the same box passed to `? extends @Nullable Object` and to `?`;
>      - `@Nullable T` and `@NonNull T` written at the use.
> 2. **`aWildcardBoundedByATypeVariableRejectsOnlyAnActualThatMayBeNullWhereTheBoundMayNot`**
>    - Cases:
>      - `S extends @Nullable T` with a non-null `T`;
>      - `Box<T>` passed to `? extends @NonNull T`.
>    - Controls:
>      - the same variable;
>      - `S extends T` under both kinds of bound;
>      - `@Nullable T`;
>      - the inferred `CompletableFuture`;
>      - the two captured actuals.
>
>    The capture inputs are the exception inside this rule, not a rule of their own, so they sit beside the controls that do report.
> 3. **`anOverrideIsReportedWhenItsReturnTypeArgumentMayBeNullWhereTheOverriddenOneMayNot`**
>    - Case: the `List<V>` override.
>    - I added one control, a `List<@NonNull V>` override, which is silent before and after the fix. Without it, the test doesn't show that the report comes from `V` rather than from the setup.
>
> Other changes:
> - Each source reads as one program, and method names such as `boundExcludesNull` and `nullableAtTheUse` say what the input varies.
> - I named `Box`'s own type parameter `E` everywhere, so it doesn't get confused with the actual `T` in the messages.
> - The tests now sit before the private `makeHelper()`, as in the rest of the file, instead of after it.
>
> How I checked:
> - On the fixed code, all three tests pass.
> - On the pre-fix code, each test fails at a case marker.
> - On the pre-fix code with only the seven case markers removed, all three pass, so every control holds before the fix.
>
> Not done:
> - Because `doTest()` stops at the first mismatch, the pre-fix run reports one case per test. The instructions accept that ("a second run to see the next mismatch"), so I propose no change to the harness.
> - Please put the run against the pre-fix code in the PR description. Either put the tests in a commit ahead of the fix, or paste the failure it prints, for example `Did not see an error on line 13 matching incompatible types: Box<T> cannot be converted to Box<? extends Object>`.
