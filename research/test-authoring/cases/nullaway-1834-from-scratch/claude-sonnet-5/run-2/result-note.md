Only the test file is modified, nothing committed, as requested. Here's the message I'd leave for the author:

---

**Tests added**: `nullaway/src/test/java/com/uber/nullaway/jspecify/WildcardTests.java`, four new `@Test` methods, one per shape the fix changes:

1. `typeVariableActualWithNullableBoundRejectedByNonNullExtendsWildcard` — `Foo<T>` with `T extends @Nullable Object` rejected by `Foo<? extends Object>`, with a `NonNullBound` control (plain `T`) proving the check doesn't fire on a non-nullable bound.
2. `wildcardActualWithNullableTypeVariableBoundRejectedByNonNullExtendsWildcard` — same, but the actual is `Foo<? extends T>` rather than bare `T`.
3. `parametricExtendsWildcardRejectsNullableActualBoundOnlyWhenTargetCannotBeNull` — the formal itself is `Box<? extends T>` (a parametric requirement); `Box<S>` with `S extends @Nullable T` is rejected only when `T` itself can't be null, with two controls in the same source: `S extends T` (no `@Nullable`) stays accepted, and the whole thing stays accepted when the target's own `T` admits null.
4. `overriddenMethodNonNullExtendsWildcardBoundRejectsNullableTypeVariableReturn` — the override-checking path reached by this fix: overriding `List<V> get()` against overridden `List<? extends @NonNull V> get()` now reports `mismatched type parameter nullability`.

Each test is a genuine regression test, not a change detector: I checked out `CheckIdenticalNullabilityVisitor.java`/`GenericsUtils.java` at `HEAD^` with the new tests in place and confirmed all four fail (`Did not see an error... There were no errors`), then restored `HEAD` and confirmed they pass, plus the full `:nullaway:test` and `:nullaway:buildWithNullAway` are green.

**Not done, proposed for you to consider**: the `rhsTypeArgument instanceof Type.CapturedType` exception in `extendsBoundContains` (the "capture conversion drops type-use annotations" branch) has no dedicated test. I tried to construct one via the `identity(box)`-style capture pattern already used elsewhere in the file, but in every construction I could reason through, `asWildcard` recovers the original wildcard from `capturedType.wildcard` and the nullness answer comes out the same with or without the exception — so I couldn't find a source that actually turns this branch into a surviving mutant without deeper knowledge of the specific capture scenario (possibly from the original issue) that motivated it. If you have a concrete repro for why that check was needed, it's worth pinning down as a fifth test.
