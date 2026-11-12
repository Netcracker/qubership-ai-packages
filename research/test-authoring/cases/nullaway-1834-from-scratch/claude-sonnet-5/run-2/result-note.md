Only test files touched, no production code changed, and nothing committed, as requested.

---

Message for the PR author:

I added the regression tests this fix owed, since none shipped with it. All five are confirmed red on the pre-fix commit (09fdea5) and green on this one — I checked by running each against both commits directly.

In `WildcardTests.java` (next to the other no-inference extends/super containment tests):
- `extendsBoundWildcardRejectsTypeVariableActualWithNullableBound` — a bare `Box<T>` with `T extends @Nullable Object` passed where `Box<? extends Object>` is required, with a `Box<T>`/non-null-`T` control that still compiles.
- `extendsBoundWildcardRejectsWildcardActualBoundToATypeVariableWithNullableBound` — the same, but the actual is `Box<? extends T>` instead of bare `T` (a different path through `wildcardUpperBound`/`typeComparedForNullness`).
- `extendsBoundWildcardOfATypeVariableRejectsActualWithNullableBoundOverIt` — the new `lhsBound instanceof TypeVar` branch: formal `Box<? extends T>` (T a parametric requirement), with controls `Box<T>` and `Box<S extends T>` (still assignable, per the commit message), and `Box<S extends @Nullable T>` (now rejected).
- `extendsBoundWildcardWithExplicitNonNullBoundRejectsNullableTypeVariableActual` — the explicit-`@NonNull`-bound variant: `Box<T>` (T nullable-bounded) rejected by `Box<? extends @NonNull T>`, with a `Box<@NonNull T>` control.

In `GenericsTests.java` (next to the other override `mismatched type parameter nullability` tests):
- `overrideReturnTypeRejectsNullableBoundWhereOverriddenWildcardRequiresNonNull` — covers the override-checking path the changelog calls out, using a real generic subclass (`BadSub<V>`/`OkSub<V>` implementing `Base<V>`, not an anonymous class with a concrete instantiation — my first attempt at this test used an anonymous class and I found, by running it against the base commit, that it was already green there, i.e. not a real regression test; the generic-subclass form is what actually exercises the fix).

What I proposed and did not do: the commit message also calls out a deliberate exception for captured actuals ("javac's capture of `? extends @NonNull V` prints as capture of `? extends V`, so the actual carries no nullness of its own to compare"). I tried to construct a case that would distinguish the fixed code from a version without that `rhsTypeArgument instanceof Type.CapturedType` carve-out, but every construction I could build this way gave the identical (passing) result on both the base commit and this one — meaning it wasn't actually discriminating, just a compatibility check, which isn't worth adding. Getting a genuinely falsifiable test for that carve-out likely needs the specific capture scenario you had in mind when writing it; I'd suggest you add one directly, or point me at the motivating example and I'll turn it into a test.

I ran `:nullaway:test` (full suite) and `:nullaway:buildWithNullAway`; both pass. Nothing was committed, per your instructions.
