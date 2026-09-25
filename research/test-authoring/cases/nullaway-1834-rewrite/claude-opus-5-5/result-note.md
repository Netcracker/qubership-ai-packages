I rewrote the 20 tests the last commit added to `WildcardTests.java` as 13 tests. The production code is unchanged and nothing is committed. `./gradlew :nullaway:test` and `./gradlew :nullaway:buildWithNullAway` both pass.

Here is the message for the author of the pull request:

---

**What changed in the tests, and why**

On the code before the fix, 7 of the 20 new tests fail: each one expects a report that the old code never made. The other 13 passed on the base code too. Most of those were the silent twin of a failing case: the same source with one thing changed and the opposite outcome, written as a separate test with its own copy of the source. The skill's rule is that a case and the controls that a single compilation can check go into one source, so the silent side can't drift from the reporting side. I merged them on that basis.

Error Prone's `CompilationTestHelper` stops at the first mismatch (`DiagnosticTestHelper.java:264-268` and `:288` in 2.50.0). So each test holds exactly one input whose outcome the fix moved, plus the controls that narrowly miss it. Each test name now states the rule that the case and its controls establish:

| Case the fix now reports | Silent controls in the same source |
| --- | --- |
| `Box<T>`, `T extends @Nullable Object` → `Box<? extends Object>` | `<T>`; `Box<@NonNull T>`; requirement `? extends @Nullable Object`; requirement `Box<?>` |
| `T` declared in `@NullUnmarked` code | the same `T` in a `@NullMarked` class |
| `S extends T`, `T extends @Nullable Object` | `S extends T`, `T` non-null |
| `Box<? extends T>`, `T` admits null | `T` non-null |
| `Box<S extends @Nullable T>` → `Box<? extends T>`, `T` non-null | `S extends T`; `T extends @Nullable Object` |
| `Box<T>` → `Box<? extends @NonNull T>` | `Box<@NonNull T>`; requirement `? extends T` |
| override `List<V>` for `List<? extends @NonNull V>` | override `List<@NonNull V>` |

- **Unchanged-outcome reports:** two inputs with `@Nullable T` at the use site were already reported before the fix. Each got its own test with its silent control, because under a harness that stops at the first mismatch they can't share a test with a moved case.
- **Kept as standalone tests:** four inputs that must stay silent and aren't a one-change control of any case. These are the two captured-type tests, the inference test, and `aTypeVariableMeetsAWildcardBoundedByTheVariableItExtends`.
- **Removed:** `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable` no longer exists as its own test. Its input (`Box<T>` → `Box<? extends T>`) is now a control in two tests, passed as an argument rather than returned.
- **Distinct argument names:** each input now passes its argument under its own name (`takeNonNull(nonNullUse)`). When a diagnostic appears where none is expected, the harness prints the source line, so the report now names the input by content and not only by line number.

**How I checked it**

- **Base code:** all 7 case tests fail, each on its own case.
- **Mutant 1**, which judges `@NonNull T` by its bound: the `nonNullUse` control catches it.
- **Mutant 2**, the naive fix that also reads a type-variable requirement by its bound: 6 tests catch it.
- **Mutant 3**, which drops the exception for captured types: the captured-type test catches it.

**Proposed, not done**

- **Stack line:** add this to `AGENTS.md`/`CLAUDE.md`: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper for checker tests, which stops at the first mismatch and names a case by line number and source line.` I didn't edit either file.
- **Follow-up for the harness:** `// BUG: Diagnostic contains:` markers can't carry a label. A missing expected diagnostic is reported only by its line and pattern. That could become an Error Prone issue. I couldn't check their tracker for an existing report, because this session had no network access.
