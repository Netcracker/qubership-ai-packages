I rewrote the 20 tests the last commit added to `WildcardTests.java` as 12 tests. I did not change production code, did not commit, and did not run anything, so **none of this has been compiled or run yet**. Here is the message for the pull request author:

---

**What changed in the tests, and why**

Most of the 20 tests either expected a report or checked that a closely similar input stays silent. But each silent test used its own copy of the source, so nothing guaranteed it matched the source of the test that reports. If the copies drifted apart, a silent test could keep passing for the wrong reason. Now each test puts one case that expects a report in the same source as the controls that must stay silent. The test name states the rule they prove together. Each case and control is in a method named for its condition (`nullableBound`, `nonNullBound`, `nonNullUse`, …), because the harness only reports a line number.

`CompilationTestHelper.doTest()` stops at the first mismatch, so each test holds only one case that expects a report (skill §7). I checked this in the error_prone_test_helpers 2.50.0 sources. `DiagnosticTestHelper.java:264-268` fails at the first expected report that is missing, going down the file. Line 289 fails at the first report on a line that has no marker. Both name the case only by line number.

| New test | Case that reports | Controls that stay silent (old test) |
|---|---|---|
| `anUnannotatedTypeVariableIsRejectedByANonNullWildcardOnlyWhenItsBoundAdmitsNull` | old 1 | non-null bound (2), `? extends @Nullable Object` (3), `Box<?>` (8), `@NonNull T` use (12) |
| `aNullableUseOfATypeVariableIsRejectedOnlyByANonNullWildcard` | old 4 | old 5 |
| `aTypeVariableIsRejectedByANonNullWildcardOnlyWhenDeclaredInUnannotatedCode` | old 9 | **new:** the same holder, `@NullMarked` |
| `aTypeVariableIsRejectedByANonNullWildcardOnlyWhenTheVariableItExtendsAdmitsNull` | old 10 | **new:** `<T, S extends T>` |
| `aWildcardActualIsRejectedByANonNullWildcardOnlyWhenTheVariableBoundingItAdmitsNull` | old 20 | **new:** `<T> Box<? extends T>` |
| `aWildcardBoundedByATypeVariableRejectsANullableUseOfThatVariableOnly` | old 13 | old 6 |
| `aTypeVariableIsRejectedByAWildcardBoundedByTheVariableItExtendsOnlyWhenItAloneAdmitsNull` | old 14 | old 15, old 11 |
| `aWildcardBoundedByANonNullUseOfATypeVariableRejectsOnlyAUseThatMayBeNull` | old 18 | **new:** `Box<@NonNull T>` |

Four tests are unchanged: the inference test (old 7), the two captured-argument tests (old 16 and 17), and the override test (old 19).

**What to check before merging**

- **The four new controls have never been run.** I worked out that they stay silent by reading `extendsBoundContains`, `typeVariableUpperBound` and `upperBoundIsNullable`, which follows `S extends T` through to `T`'s bound.
- **Old test 6 changed form.** It returned `Box<T>` as a `Box<? extends T>` from a generic method. It is now a call to `takeExtendsT` inside `Holder`, so it sits beside the case it controls. If you want to keep the check on the return statement, add the old form back as a second control.
- **The regression tests need to be seen failing on the old code** (skill §1). Please run the tests at `09fdea5` and paste the output. I expect every test in the table except the 6th (old 13) and the 2nd (old 4) to fail there, plus the override test. Those two may have reported before this change, which would make them controls on existing behaviour rather than regression tests.

**Proposed, not done**

- Add a line describing the test setup to `CLAUDE.md`/`AGENTS.md`. I haven't edited either file; I'll add the line only if you agree. For example: `Tests: JUnit 4 engine, JUnit 4 assertions; Error Prone CompilationTestHelper for checker tests (one doTest() call stops at the first mismatch in line order and names it by line number only)`.
- Old tests 7, 16 and 17 expect no report at all, and no test with the same setup reports anything. So if their setup changes, nobody will notice that they no longer prove anything. Adding a reporting case beside each (for example, a `Map<K, V>` returned as `Map<? extends K, ? extends @NonNull V>` next to old 16) needs a run to confirm what the report says.
- The override test has no silent control. The obvious one is an override returning `List<V>` where the overridden method returns `List<? extends V>`, but it needs a run first.
- The harness has no way to label a case in its failure output. A `// BUG: Diagnostic matches: KEY` lookup key is not printed, and a report on a line with no marker gets no name at all. This is worth an issue against Error Prone, after checking their tracker for an existing report. I didn't use the network.
