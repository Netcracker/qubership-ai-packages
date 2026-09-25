Both the full `nullaway:test` suite and `buildWithNullAway` pass. The test file is the only change, nothing was committed.

## Summary for the PR author

I rewrote the 20 tests this commit added to `WildcardTests.java` down to 14, per the `test-authoring` skill. The test engine here is JUnit 4 (`org.junit.Test`, matching the file's existing imports); assertions run through Error Prone's `CompilationTestHelper`/`DiagnosticTestHelper`, which has no reference file in this skill, so I read its source (`error_prone_test_helpers` 2.50.0) to learn its report behavior directly, per the skill's fallback rule: it stops at the first line whose expected diagnostic (or absence of one) doesn't match, and names a mismatch only by source line number, never by a label.

That harness behavior is exactly the "case and its control in one check" situation the skill describes in its own worked example (§7/§12): several scenarios that share the same class skeleton can live in one compilation as long as at most one of them is the reporting case. I used a base-commit run (via a throwaway git worktree, not committed) to confirm which of the 20 tests actually changed outcome across the fix — 7 did, 13 were already-correct controls — and merged same-skeleton case+control pairs into single checks with names that state the combined rule:

- `aTypeVariableIsRejectedOnlyWhenItsBoundAdmitsNullAndTheWildcardExcludesNull` — merges the 3 tests that varied a type variable's own declared bound and the wildcard's own nullness against one `Box`/`takeNonNull`/`takeNullable` skeleton.
- `aWrittenNullnessAnnotationOverridesTheDeclaredBoundOfATypeVariableUse` — merges the 3 tests where an explicit `@Nullable`/`@NonNull` at the use site overrides the declared bound.
- `aBareSubtypeMeetsAWildcardBoundedByTButAnExplicitlyNullableUseOfTFailsIt` — merges the 2 `Holder<T extends @Nullable Object>` tests.
- `aSubtypeIsRejectedByAWildcardBoundedByTOnlyWhenItsOwnBoundAdmitsNullButTDoesNotAdmitNull` — merges the 2 `Holder<T>` (non-null-bound) tests.

Each merge removed a copy-pasted `Box`/`takeNonNull`/`takeNullable`/`Holder` preamble that differed from its neighbor in exactly one line, and each surviving group still red-lines on the pre-fix commit exactly where the original did (verified by re-running the rewritten file against the parent commit in a worktree). The other 10 tests already had no natural same-skeleton control in this set, so I left them as standalone tests and did not touch their bodies or diagnostics.

What I propose but did not do:
- Add a stack line to `AGENTS.md`/`CLAUDE.md`, e.g.: "Tests: JUnit 4 engine; assertions via Error Prone's `CompilationTestHelper`, which stops at the first line whose expected diagnostic (or its absence) doesn't match, and names a mismatch only by line number." I didn't add this myself since the skill has me propose it rather than edit repo instructions unasked.
- Three of the untouched "moved" tests have no built-in control in this set and could use one: `aTypeVariableBoundedByAnotherWhoseBoundAdmitsNullFailsANonNullWildcardRequirement` (no case where `S extends T` and `T` is non-null-bound), `aTypeVariableThatMayBeNullFailsANonNullAnnotatedWildcardRequirement` (no case meeting a `? extends @NonNull T` wildcard), and `aWildcardActualBoundedByATypeVariableThatAdmitsNullFailsANonNullWildcardRequirement` (no case where the actual is a `? extends T` wildcard whose bound doesn't admit null). I didn't add these since it would mean asserting new diagnostic text I'd have to verify from scratch, beyond reorganizing what's already there.
