No production changes, as required. Here's the message for the PR author:

---

I added four small tests for the fix in `614efcf`, none of which existed before. I did not touch production code or commit.

**Where they went, and why:**

- `WildcardTests.typeVariableActualAdmitsNullIntoNonNullExtendsWildcard` — the core bug: a bare type-variable actual `Foo<T>` (`T extends @Nullable Object`) passed where `Foo<? extends Object>` is required, with a control using a non-null-bounded `T` to show the rule tracks the bound's nullability, not just "is a type variable."
- `WildcardTests.extendsWildcardNamingATypeVariableComparesActualAsWritten` — the invariant the commit message calls out explicitly: when the *requirement* itself names a type variable (`Foo<? extends T>`), the actual is compared as written, not against `T`'s bound. Three cases in one act: `Foo<T>` and `Foo<S extends T>` into `Foo<? extends T>` stay legal; `Foo<S extends @Nullable T>` into the same requirement is now rejected. This guards specifically against the "simpler but wrong" fix the commit message warns would silence the real report.
- `WildcardTests.extendsWildcardWithExplicitNonNullTypeVariableBound` — `Foo<T>` into `Foo<? extends @NonNull T>`, contrasted with the same `Foo<T>` into bare `Foo<? extends T>`, which stays legal.
- `GenericsTests.overrideReturnTypeWithNonNullExtendsBoundWildcard` — the override-checking path named in the CHANGELOG entry: overriding `List<? extends @NonNull V>` with `List<V>` is now flagged when `V` admits null, and left alone when it can't.

All four fail with "There were no errors" (the exact silent-acceptance symptom the commit describes) when run against the parent commit's production code, and pass against `HEAD`; I verified this by temporarily swapping in the pre-fix `CheckIdenticalNullabilityVisitor.java`/`GenericsUtils.java`, running the new tests, then restoring. Full `:nullaway:test` and `:nullaway:buildWithNullAway` pass on the final state.

**What I looked at and decided not to add a test for:** the `rhsTypeArgument instanceof Type.CapturedType` exception in `extendsBoundContains` (the "capture conversion drops type-use annotations" guard). I tried two reproductions — a direct `identity()`-style capture into a bare-type-variable destination — and in both, `GenericsUtils.asWildcard` already recovers the original wildcard (and its annotation) from the captured type via its `.wildcard` field, so the guard never got exercised; removing it from the code didn't break any existing test either. The surrounding comment suggests this guards a classfile-read case (pre-JDK 23 wildcard/type-variable association, the same corner `BytecodeGenericsTests` exists for), which would need a separate precompiled-library fixture to reach. I'm reporting this as unresolved rather than forcing a test that doesn't actually exercise the line — happy to build the bytecode fixture if you want that covered.

**Stack line:** this repository's `AGENTS.md`/`CLAUDE.md` has no line naming the test stack. Based on every neighboring test, it's `CompilationTestHelper` (JUnit4) with inline `// BUG: Diagnostic contains:` markers; that harness stops at the first unmatched expectation per compiled source rather than reporting every mismatch, which is why each test above pairs a case with its controls in one file instead of relying on the suite to surface more than one break. Worth adding a line to that effect if you'd like it recorded — I didn't add it myself since that's your call to make.
