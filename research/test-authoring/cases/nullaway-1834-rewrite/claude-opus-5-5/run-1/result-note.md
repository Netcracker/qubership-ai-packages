I rewrote the 20 tests from the last commit as 7. Each of the 7 failed on the parent commit on its own case's marker and passes on HEAD. `./gradlew :nullaway:test` and `:nullaway:buildWithNullAway` both pass. The production code is unchanged and nothing is committed.

**A fact about the test harness, for you rather than the author.** Error Prone's `CompilationTestHelper.doTest()` stops at the first mismatch. It names a missing expected report by line number and the marker's text, and an unexpected report by line number only, then prints every report. No reference file records this, so I learned it from a deliberate run. If you want it recorded, `CLAUDE.md` could get a line like: `Tests: JUnit 4 engine; Error Prone CompilationTestHelper stops at the first mismatch and names it by line (plus marker text for a missing report)`. I haven't added it; say if you'd like me to.

---

**Message for the author:**

I rewrote the 20 tests this PR adds to `WildcardTests` as 7. The fix and the inputs being checked are the same; only the grouping changed.

**Why.** On the parent commit, 7 of the 20 tests fail. Those are the behavior the fix adds. The other 13 already passed there. They guard against the fix going too far (`Box<T>` into `Box<? extends T>`, the captured and inferred loaders) or pin existing behavior (`Box<@Nullable T>` reports, `Box<?>` accepts). Kept as separate tests, a "nothing is reported" test only says something while a neighbor with a near-identical source still reports, and nothing keeps the two sources in sync.

Each new test holds one newly reported case plus the inputs that differ from it in one respect, in a single source with one method per input. NullAway checks each method on its own. The harness stops at the first mismatch, so I didn't put two new cases in one source. Each test name states the rule and the case it covers:

| Test | Case (reports since the fix) | Inputs moved in from separate tests |
| --- | --- | --- |
| `aNonNullWildcardRequirementRejectsATypeVariableOnlyWhenItsUseOrItsBoundAdmitsNull` | `<T extends @Nullable Object> Box<T>` → `Box<? extends Object>` | `<T>`, nullable wildcard, `Box<?>`, `Box<@NonNull T>`, `Box<@Nullable T>` → both requirements |
| `…RejectsATypeVariableDeclaredInUnannotatedCode` | `@NullUnmarked Holder<T>` | — |
| `…RejectsATypeVariableBoundedByAnotherWhoseBoundAdmitsNull` | `<T extends @Nullable Object, S extends T>` | — |
| `…RejectsAWildcardBoundedByATypeVariableWhoseBoundAdmitsNull` | `Box<? extends T>` | — |
| `aWildcardBoundedByATypeVariableRejectsAnActualOnlyWhereItAdmitsNullAndTheVariableDoesNot` | `<S extends @Nullable T>` into `? extends T` | `<S extends T>` under both holders, `Box<@Nullable T>`, the same-variable return, the inferred and captured loaders |
| `aNonNullWildcardBoundedByATypeVariableRejectsAnUnannotatedUseOfThatVariable` | `Box<T>` into `? extends @NonNull T` | the captured `? extends @NonNull V` loader |
| `anOverrideMayNotReturnAnUnannotatedTypeVariableWhereItsSuperReturnsANonNullWildcard` | `List<V>` override | — |

**What I added.** Five new inputs, each differing from its case in one respect: a `@NullMarked` holder, `<T, S extends T>`, `<T> Box<? extends T>`, `Box<@NonNull T>` into `? extends @NonNull T`, and a `List<@NonNull V>` override. Each is silent on both the parent and HEAD. Without them, four of the cases had nothing showing that the report comes from the nullable bound rather than from the rest of the setup.

**What I dropped.** No input. The two loader interfaces that were each a whole test are now nested `Loader` interfaces inside the case's source.

**Checks I ran:**
- On the parent commit, every rewritten test fails on its case's line. The only reports there come from the inputs that are supposed to report.
- I ran the old and new tests side by side against seven mutations of the fix: removing the capture exception, the type-variable-requirement branch, either `hasNullnessAnnotation` guard, the unannotated-code bound, the `admitsNull(lhsBound)` escape, or `typeComparedForNullness`. Every mutation the old tests caught, the new ones catch too.

**Proposed, not done.** When a source holds several inputs, a report on a line where none is expected is named only by line number, and the harness has no way to label it. I wrote the method names to describe each input so the line is easy to find, but the report itself doesn't name it. Error Prone's test helpers aren't in this repository, so I'm not proposing a change to the harness here.
