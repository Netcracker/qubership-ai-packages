All four tests are verified: they fail on the pre-fix commit (`09fdea5`) with the exact symptom the fix addresses — a missing diagnostic — and pass on the fixed commit (`614efcf`). No production code was touched, and nothing was committed.

---

**Message for the PR author:**

I added four regression tests for `614efcf`, all in `nullaway/src/test/java/com/uber/nullaway/jspecify/`, none committed:

- `WildcardTests#typeVariableActualWithNullableBoundRejectedByExtendsWildcard` — a `Box<T>` with `T extends @Nullable Object` is now rejected where `Box<? extends Object>` is required; a non-null-bound `T` stays accepted. This is the CHANGELOG's headline example, hitting the `lhsBound` non-`TypeVar` branch of `extendsBoundContains` via `typeComparedForNullness`.
- `WildcardTests#typeVariableActualWithNullableBoundRejectedByExtendsTypeVariableWildcard` — a `Box<S>` with `S extends @Nullable T` is rejected against `Box<? extends T>`; `S extends T` (no `@Nullable`) stays accepted. This hits the `lhsBound instanceof TypeVar` branch's `admitsNull(rhsUpperBound)` check.
- `WildcardTests#typeVariableActualRejectedByExplicitNonNullExtendsWildcard` — `Box<T>` is rejected against `Box<? extends @NonNull T>`; `Box<@NonNull T>` stays accepted. This hits the same branch's `admitsNull(lhsBound)` check, where the wildcard's own bound carries the `@NonNull`.
- `GenericsTests#overrideReturnTypeVariableViolatesNonNullExtendsWildcard` — an override returning `List<V>` against a superinterface returning `List<? extends @NonNull V>` now reports `mismatched type parameter nullability`; returning `List<@NonNull V>` stays accepted. This is the CHANGELOG's override-reach example, confirming the same comparison is wired into override checking, not just assignment.

I verified all four the way §1 of the test-authoring skill asks: I applied the test-only diff to a worktree at the parent commit (`09fdea5`, pre-fix) and all four failed there with `Did not see an error on line N matching ... There were no errors` — the actual symptom the fix addresses, not a missing symbol or crash — then confirmed all pass on `614efcf`. I also ran `:nullaway:buildWithNullAway` clean.

What I deliberately left out:
- The commit's third guard — "a captured actual is the exception… since capture conversion drops type-use annotations" (the `rhsTypeArgument instanceof Type.CapturedType` disjunct in `extendsBoundContains`) — has no test. I tried to construct a minimal case that would be a false positive without that disjunct but couldn't convince myself by hand-tracing javac's capture/inference behavior that a given source snippet actually reaches `extendsBoundContains` with a `Type.CapturedType` actual against a bare `TypeVar` `lhsBound` (as opposed to inference substituting the bound away first), and I didn't want to ship a guessed test. This is a real gap; a targeted test here (or a one-line note in the stack line about which capture patterns exercise this path) would be a good follow-up.
- No stack line exists in `CLAUDE.md`/`AGENTS.md` naming the test stack. Per the skill, I propose one sentence for it here rather than editing the file: `Tests: JUnit 4 engine; error-prone's CompilationTestHelper for assertions (its check stops at the first mismatched line per addSourceLines call, and names a case only by line number).` I did not add it to `CLAUDE.md`/`AGENTS.md` — that's for you to accept or not.
- I didn't add a "second, larger" test (§3) — this is a pure compiler-diagnostics change with no process boundary or external dependency, so the small in-process `CompilationTestHelper` level is the right (and only) level.
