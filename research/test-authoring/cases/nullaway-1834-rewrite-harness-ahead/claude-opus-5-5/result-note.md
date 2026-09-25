I rewrote the commit's 20 tests as 2 in `WildcardTests.java`. They pass on the fixed code, and `buildWithNullAway` passes. Only that test file changed; nothing is committed. While doing this I found a false positive that the fix introduces, described first in the message below.

---

**Message for the PR author**

**A false positive the fix introduces (not fixed here).** An anonymous class written with the diamond form now draws a false report:

```java
interface Getter<V extends @Nullable Object> { List<? extends V> getAll(); }
static <W extends @Nullable Object> Getter<W> make() {
  return new Getter<>() {
    @Override public List<W> getAll() { ... }   // now: "mismatched type parameter nullability"
  };
}
```

`List<W>` overriding `List<? extends W>` is correct, and this is not reported on the parent commit. With an explicit `new Getter<W>()`, or a named class that implements `Getter<V>`, it isn't reported either. It matters for the tests: your override test used exactly this diamond form, so it passed whether the report came from the `@NonNull` on `? extends @NonNull V` or from this false positive. In the rewrite, the override case uses `new Getter<V>()` and sits next to a control, `getAll` overriding `List<? extends V>`, which has to stay silent. I suggest a follow-up that fixes the diamond path and adds a diamond-form test. Neither is in this change, since I left the production code alone.

**What changed in the tests, and why.** The stack line in `CLAUDE.md` says to write CompilationTestHelper tests as if `doTest()` reported every mismatch and told each marker apart, and to keep one rule's cases in one source. The commit had one test per input: each reported case had its control in a separate test with its own copy of the source, and nothing kept those copies the same. One compilation checks all of them, and each method is checked on its own, so each rule is now one test holding its cases and their controls in one source. The earlier multi-case tests in this file already have that shape.

- **`aTypeVariableArgumentMeetsANonNullWildcardOnlyWhenItsUseOrItsBoundExcludesNull`**: a concrete requirement, `Box<? extends Object>`.
  - Four cases are now reported, one for each way a bound can admit null: an explicit `@Nullable` bound; `S extends T` where `T`'s bound admits null; a `? extends T` argument; and `T` declared in `@NullUnmarked` code.
  - Each case sits next to a control that differs in one respect and passes: a non-null bound, `@NonNull T` at the use, a nullable or unbounded (`?`) requirement, and a `@Marked` holder.
  - `@Nullable T` at the use, which was already reported before the fix, stays as the use-site control.
  - Three controls are new: `<T, S extends T>`, `Box<? extends T>` with a non-null `T`, and the marked holder. The commit's only control for those three cases differed from them in more than one respect.
- **`aWildcardBoundedByATypeVariableRejectsAnArgumentThatMayBeNullWhereTheVariableMayNot`**: a requirement bounded by a type variable, `Box<? extends T>`.
  - Three cases are now reported: `S extends @Nullable T` with a non-null `T`; `Box<T>` passed where `Box<? extends @NonNull T>` is required; and the override, as described above.
  - The controls are the same variable, `S extends T` under both kinds of bound, `@Nullable T` (already reported before the fix), the inferred `CompletableFuture` case, the two captured-wildcard cases, and the new `getAll` override.

**Red run on the parent commit.** I ran the commit's original tests against the parent commit's production code. Exactly 7 failed, each with `Did not see an error … There were no errors`, for the 7 inputs listed as cases above; the 13 others passed there too. The rewritten tests also fail on the parent commit and report no unexpected errors, so every control is silent before and after the fix. Each test shows only its first missing marker per run, which the stack line accepts.

**Level.** The tests are small, compiled in memory through `CompilationTestHelper` like their neighbours. Nothing crosses a process boundary, so no larger test is needed.

Proposed and not done: the diamond fix and its test, described above. The stack line already records what the harness does, so I propose nothing about it.
