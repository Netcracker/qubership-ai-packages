Good — only the two test files are modified, nothing committed. Here's the summary for the PR author:

## Tests added (no production code touched, nothing committed)

The fix (`CheckIdenticalNullabilityVisitor`/`GenericsUtils`) changed four distinct, independently-verified behaviors with no existing test coverage. For each, I confirmed **red on the base commit** (silently accepted, no diagnostic) and **green on the fix** by compiling isolated repros against both `09fdea5` (base) and `614efcf` (fix) in a disposable worktree before writing the final test.

**`WildcardTests.java`** (nearest existing tests of this exact unit — `extendsBoundContains`/`wildcardContains`):

- `aTypeVariableActualIsRejectedOnlyWhenItsDeclaredBoundAdmitsNull` — the headline bug: a bare type-variable actual (`Foo<T>`, `T extends @Nullable Object`) passed where `Foo<? extends Object>` is required is now rejected; a non-null-bound `T` is still accepted; the same pair repeated for a wildcard-of-type-variable actual (`Foo<? extends T>`), the other shape the fix touches.
- `aParametricWildcardBoundRejectsAnActualWhoseBoundAdmitsNullWhileItsOwnDoesNot` — the parametric-requirement extension (`Sink<T>.accept(Foo<? extends T>)`): `Foo<T>` and `Foo<S extends T>` stay assignable (non-regression controls, explicitly called out in the commit message), but `Foo<S>` with `S extends @Nullable T` is rejected only when `T` itself cannot be null, and accepted again once `T` can be null — a minimal pair isolating exactly the condition the fix added.
- `anExplicitNonNullWildcardBoundOnATypeVariableRejectsANullableBoundActual` — `Box<T>` rejected where `Box<? extends @NonNull T>` is required, with a non-null-bound `T` control.

**`GenericsTests.java`** (nearest existing override/wildcard test):

- `overrideReturnTypeWithExtendsBoundWildcardOnTypeVariable` — confirms the fix reaches the override-checking call site too (the CHANGELOG's second bullet): overriding `Box<? extends @NonNull V> getNonNull()` with `Box<V> getNonNull()` now reports, with a same-method non-null-instantiation control (`Holder<Object>`) showing the check isn't just always failing.

All 7 new methods pass `./gradlew :nullaway:test` at HEAD and `buildWithNullAway` is unaffected (test-only change).

## Proposed, not done

1. **Test stack line**: `AGENTS.md`/`CLAUDE.md` name no test engine/assertion-library line (JUnit 4 + `CompilationTestHelper`'s own marker-matching, which reports every mismatched line in one compile and names each only by line number — no label). I didn't add this line myself since adding it is conditioned on your agreement; happy to add `Tests: JUnit 4 engine; CompilationTestHelper diagnostic-marker assertions (reports every mismatched line, names each by line number only, no label)` if you want it.
2. **The `Type.CapturedType` carve-out** (`rhsTypeArgument instanceof Type.CapturedType` in `extendsBoundContains`) has no dedicated regression test. I couldn't construct a minimal, non-redundant repro that reaches the new parametric-TypeVar branch specifically *through* capture conversion (as opposed to the existing capture tests, which exercise unrelated LHS-capture/F-bounded recursion paths) without more time — worth a follow-up if you want that carve-out locked down.
