Only the test file is modified, nothing committed, production code untouched, worktrees cleaned up. Here's the message for the PR author:

---

**Tests added (in `WildcardTests.java`, beside the file's other `extendsBoundContains`-style cases):**

1. `bareTypeVariableActualIsJudgedByItsDeclaredBound` — the headline case: a bare `T extends @Nullable Object` passed where `Box<? extends Object>` is required is now rejected; a bare `T` with a non-null bound stays legal (control, same act).
2. `parametricExtendsWildcardComparesDeclaredBoundsNotNames` — the parametric-requirement case: `Box<NullableSub>` with `NullableSub extends @Nullable T` is rejected by `Box<? extends T>` when `T` itself can't be null, while `Box<T>` and `Box<NonNullSub extends T>` stay legal against the same formal (controls, same act) — this is the "keeps `Box<T>` and `Box<S extends T>` assignable" property the commit calls out by name.
3. `explicitNonNullWildcardBoundRejectsSameBareTypeVariable` — a bare `T` (nullable-bound, no annotation at the use site) is rejected by `Box<? extends @NonNull T>`; `Box<@NonNull T>` (annotated as written) stays legal (control).

Each test is a regression test per the skill's oracle: I verified all three go red on the parent commit (09fdea5) with exactly `"...There were no errors"` — the silent-acceptance symptom the commit describes — and green on this commit, with the full `:nullaway:test` module and `:nullaway:buildWithNullAway` also passing. I didn't add tests for code the fix didn't change (e.g. explicit `@Nullable T`/`@NonNull T` actuals compared "as written" against a concrete bound) since that path was already a direct comparison before this diff and isn't what changed.

**What I propose and did not do:**

- **No test for the captured-actual exemption** (`rhsTypeArgument instanceof Type.CapturedType` in `extendsBoundContains`). That branch needs a parametric formal (`? extends T`) receiving a *captured* wildcard actual — I couldn't build one quickly enough to confirm by compilation that it actually exercises that exact line (as opposed to the sibling branch in `typeComparedForNullness`, which existing tests like `annotationRestoredFromUpperBoundToCapturedWildcard` do exercise). Worth a follow-up test once someone works out the right capture scenario.
- **Stack line**: `AGENTS.md`/`CLAUDE.md` name no test stack, so per the test-authoring skill I'm proposing one instead of writing it in: *JUnit 4 engine; `CompilationTestHelper` (error-prone) as the assertion library — one `doTest()` call aborts at the first unmatched `// BUG: Diagnostic contains:` marker (or the first diagnostic on an unmarked line), named only by source line, never by content, so new cases normally join an existing test as a case-with-its-controls rather than sharing an act with unrelated cases.* I confirmed this by disassembling `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` and by observation. Let me know if you'd like it added to `CLAUDE.md`/`AGENTS.md`.
