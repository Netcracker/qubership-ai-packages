I rewrote the 20 tests from `d55c150` as two tests in `WildcardTests.java`, one per rule. All 66 `WildcardTests` pass, the production code is back as it was, and nothing is committed. I didn't run `buildWithNullAway`, since only a test file changed.

**Message for the author:**

---

The 20 tests the commit added each compiled one input: either a case the fix changes, or a control that behaved the same before the fix. The repo's test instructions say to keep the cases of one rule in one source. So the inputs are now two sources, one per rule, and each case sits next to its controls. Every input from the original 20 tests is still there, with the same expectations.

1. **`aTypeVariableArgumentMeetsANonNullWildcardBoundOnlyWhenItsUseOrItsDeclaredBoundExcludesNull`** covers a requirement like `Box<? extends Object>`.
   - Cases that are reported now: `Box<T>` where `T`'s bound admits null, `Box<S>` where `S extends T`, `Box<? extends T>`, and a `T` declared in `@NullUnmarked` code.
   - Controls: a `T` with a non-null bound, `Box<@NonNull T>`, `Box<@Nullable T>` (already reported before the fix), the `? extends @Nullable Object` and `Box<?>` requirements, plus the two new controls below.
2. **`aWildcardBoundedByATypeVariableAdmitsOnlyAnArgumentNoMoreNullableThanThatVariable`** covers a requirement like `? extends T`.
   - Cases: `S extends @Nullable T` where `T` can't be null, `Box<T>` passed where `Box<? extends @NonNull T>` is required, and the override returning `List<V>`.
   - Controls: the same-variable return, `S extends T` under both kinds of bound, `Box<@Nullable T>`, the `CompletableFuture` inference example, and both captured-type examples.

**New controls.** I added three, each differing from one case in one respect:
- `<T, S extends T>` with a non-null bound
- `Box<? extends T>` with a non-null `T`
- an override returning `List<@NonNull V>`

Each one shows that its case is reported because of the nullable bound, not because of how the source is set up.

**Evidence:**
- **Before the fix:** both new tests fail at a case marker. One is "Did not see an error on line 13 … `Box<T>` cannot be converted to `Box<? extends Object>`", the other is the same message for `Box<? extends T>` at line 26.
- **Controls before the fix:** with the 7 case markers removed, both tests pass on the old code. That covers every control, including the three new ones.
- **The captured-type exception:** replacing the `rhsTypeArgument instanceof Type.CapturedType` check with `false` makes test 2 fail with "Saw unexpected error on line 49", which is `capturedNonNullRequirement`. So the captured examples really do check that exception. I reverted that edit.

**Your call, not done:**
- I didn't add a new label proposal or an issue for the harness. Its error-reporting behaviour is already covered by the repo's test instructions.
- The first test's name is over 100 characters. The pre-commit formatter will wrap it the same way it wrapped the old `aWildcardActual…` name.

---
