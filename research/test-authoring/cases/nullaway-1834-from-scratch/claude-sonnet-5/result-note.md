## Summary for the PR author

Commit `614efcf` changed `extendsBoundContains` and added `GenericsUtils.typeVariableUpperBound`, but shipped with no tests. I read the diff and commit message as the specification and added four `@Test` methods covering the partitions it names, all as regression tests through the public checker (no production code touched):

**`WildcardTests.java`**
- `typeVariableActualCheckedAgainstItsDeclaredBoundForNonNullExtendsWildcard` — a bare `Box<U>` (`U extends @Nullable Object`) and a `Box<? extends U>` are both now rejected by a `Box<? extends Object>` parameter, with `U`-non-null controls proving the report tracks the bound, not the shape. This is the primary silent-bug case from the commit's first paragraph.
- `parametricExtendsWildcardComparesTypeVariablesAsWritten` — when the *target* is itself a bare type variable (`Box<? extends T>`), a `Box<S>` with `S extends @Nullable T` is rejected while `S extends T` and the identity case `Box<T>` (even for a nullable `T`) are accepted. This is the "parametric requirement is not read as its bound, but is not a hole either" paragraph.
- `explicitNonNullWildcardBoundRejectsUnannotatedNullableTypeVariable` — `Box<T>` against `Box<? extends @NonNull T>` is rejected; `Box<@NonNull T>` against the same target is accepted, matching "a use that carries its own nullness is compared as written."

**`GenericInheritanceTests.java`**
- `overrideReturnTypeCheckedAgainstNonNullWildcardBoundOfTypeVariable` — the changelog's own example: overriding `List<? extends @NonNull V> get()` with `List<V> get()` now reports `mismatched type parameter nullability`; `List<@NonNull V>` is accepted.

Each positive case carries a `// BUG: Diagnostic contains:` marker with the diagnostic text I traced back to `errorMessageForIncompatibleTypesAtPseudoAssignment` / `reportInvalidOverridingMethodReturnTypeError` in `GenericsChecks.java`.

What I did **not** do, and why:
- **No red-on-base-commit evidence.** Your task asked me not to run the build, so I can't paste a failing run against the pre-fix code or confirm these tests actually compile and pass post-fix. Please run `./gradlew :nullaway:test --tests "com.uber.nullaway.jspecify.WildcardTests"` and `...GenericInheritanceTests"` before merging.
- **Skipped the `Type.CapturedType` carve-out** in `extendsBoundContains` (the `rhsTypeArgument instanceof Type.CapturedType` branch, new in this diff, guarding against capture conversion dropping annotations when the target is a bare type variable). Constructing a source that produces a captured actual against a type-variable-bound target is intricate, and I didn't want to guess at syntax I couldn't verify compiles. Worth a follow-up test if you want that branch covered directly.
- **No stack line in `AGENTS.md`/`CLAUDE.md`.** The repo's instructions name no test engine/assertion library. This test suite is really driven by Error Prone's `CompilationTestHelper` (a harness this skill has no reference file for), using JUnit 4 only for `@Test`/`@Before`/`@Rule`. I'd propose adding a line such as: *"Tests: JUnit 4 engine; assertions via Error Prone's `CompilationTestHelper.doTest()`, which reports every `// BUG: Diagnostic contains:` mismatch in one compilation and names each case only by source line."* Let me know if you'd like me to add that.
