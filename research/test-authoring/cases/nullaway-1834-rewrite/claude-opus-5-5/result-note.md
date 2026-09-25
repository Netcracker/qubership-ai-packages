I rewrote the tests the last commit added to `WildcardTests.java`: 20 tests became 9, one per rule. The whole `WildcardTests` class passes (55 tests, 0 failures). Production code is unchanged and nothing is committed. I only ran the one test class, not `:nullaway:buildWithNullAway`, since only a test file changed.

---

**Message for the author**

**How the test harness behaves.** Error Prone's `CompilationTestHelper` (2.50.0) has no reference file in the skill, so I read its source. `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines` does three things that matter here:
- It **stops at the first mismatch**: the first marker with no matching report, or the first unmarked line that gets a report ("Saw unexpected error on line N").
- It **names a failure only by a line number** and has no per-case label.
- A **line with no marker therefore expects no report.**

The skill says that under a harness like this, each rule gets its own test. That test holds the one input that should draw the report, next to the nearest inputs that should not (the controls), all in one source file. Before, a case and its control were separate tests, each with its own copy of the class, and nothing kept the copies in step. So a silent test could be silent because its copy had drifted, not because the check works. The file already uses this shape (`simpleWildcardNoInference`).

**What changed.** Each new test is named for the rule it establishes:

| Rule (new test) | Reported case | Controls (not reported) |
| --- | --- | --- |
| `aBareTypeVariableIsRejectedByANonNullWildcardBoundOnlyWhenItsDeclaredBoundAdmitsNull` | `<T extends @Nullable Object> Box<T>` → `? extends Object` | same `b` passed to `? extends @Nullable Object` and to `?`; `<T> Box<T>`; `Box<@NonNull T>` |
| `aTypeVariableDeclaredInUnannotatedCodeIsRejectedByANonNullWildcardBound` | `T` from an `@NullUnmarked` holder | **new:** the same holder when it is `@NullMarked` |
| `aTypeVariableBoundedByAVariableThatAdmitsNullIsRejectedByANonNullWildcardBound` | `S extends T`, where `T extends @Nullable Object` | **new:** `<T, S extends T>` |
| `aWildcardBoundedByATypeVariableThatAdmitsNullIsRejectedByANonNullWildcardBound` | `Box<? extends T>`, where `T extends @Nullable Object` | **new:** `<T> Box<? extends T>` |
| `aNullableWrittenOnATypeVariableUseIsRejectedByANonNullWildcardBound` | `<T> Box<@Nullable T>` → `? extends Object` | same `b` passed to `? extends @Nullable Object`; **new:** `<T> Box<T>` |
| `aNullableUseOfATypeVariableIsRejectedByAWildcardBoundedByThatVariable` | `Box<@Nullable T>` → `? extends T` | `Box<T>` passed as an argument and as a return value; the `CompletableFuture` inference case; the captured `Map<…, ? extends V>` case |
| `aWildcardBoundedByATypeVariableRejectsAnActualThatAdmitsNullOnlyWhenTheVariableDoesNot` | `S extends @Nullable T`, where `T` cannot be null | `S extends T` with either kind of `T`; **new:** `S extends @Nullable T`, where `T extends @Nullable Object` |
| `aTypeVariableThatAdmitsNullIsRejectedByAWildcardBoundedByItsNonNullUse` | `Box<T>` → `? extends @NonNull T` | **new:** `Box<@NonNull T>`; the captured `CompletableFuture<Map<…, ? extends @NonNull V>>` case |
| `anOverrideReturningATypeVariableThatAdmitsNullIsRejectedWhereTheOverriddenWildcardBoundIsNonNull` | an override returning `List<V>` | **new:** an override returning `List<@NonNull V>` |

- **The new controls** are each the input nearest to the reported case that should stay silent. Several of the old silent tests differed from their reported counterpart in more than one thing, so on their own they did not show which condition decides the outcome.
- **No expected diagnostic text changed.** Every reported line keeps the exact `Diagnostic contains:` text it had.
- **The two captured-type and the `CompletableFuture` reproductions** keep their original bodies. They now sit as nested `Loader` interfaces in the source of the rule they control, instead of standing alone.

**Evidence that the tests can fail.** I made two temporary production edits and reverted both with `git checkout HEAD -- nullaway/src/main`.
- **Pre-fix code:** I put back the production sources from before the fix (`HEAD~1`). The 7 tests for new behaviour fail, each with `Did not see an error on line N`, which is the bug's symptom: a missing report. The 2 tests for `@Nullable` written on the type variable pass, because that was already reported before the fix.
- **Capture exception removed:** I deleted the `rhsTypeArgument instanceof Type.CapturedType` exception. Only the `asyncLoadAll` control catches it, with `Saw unexpected error on line 27`.
- **One control dropped:** a simpler captured control I had tried (`Box<? extends @NonNull T>` passed as an argument) stayed silent under that change, so it guarded nothing and I removed it. The capture exception is therefore guarded by the `Map`/`CompletableFuture` reproduction alone.

**Proposed, not done:**
1. **A line naming the test stack in `CLAUDE.md`/`AGENTS.md`**, which currently have none. For example: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper, which stops at the first mismatch and names a case only by its line number (no per-case label).` The skill says to add it only if you agree.
2. **A follow-up on the harness's missing label:** a red report names a line number, never the case. The fix would be an issue or change against Error Prone's test helpers to let a `// BUG:` marker carry a label. I did not check their tracker for an existing report.
3. **Writing and doc-comment guidance:** the skill defers wording to `english-developer-style` and comments to `javadoc-authoring`. Neither is available in this session, so I did not apply them. The new test methods have no Javadoc, which `CLAUDE.md` allows for tests.
