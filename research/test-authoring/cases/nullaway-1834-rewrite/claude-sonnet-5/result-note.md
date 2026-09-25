Nothing committed, as requested. Here's the message for the PR author:

---

I rewrote the 20 tests this commit added to `WildcardTests.java`, following the `test-authoring` skill. Production code is untouched; only the test file changed (66 → 61 `@Test` methods, all passing, `buildWithNullAway` clean).

**Why**: `CompilationTestHelper` (via `DiagnosticTestHelper.assertHasDiagnosticOnAllMatchingLines`) scans a compiled source line-by-line and hard-asserts on the first mismatch — it does *not* collect every diagnostic before failing. Under that harness, the skill's rule is: one test holds one case (an input whose outcome the fix moved) plus that case's controls (nearby inputs the outcome doesn't move); two inputs that *both* expect a report can't safely share a test, since the first can mask a regression in the second. Several of the 20 added tests were solo BUG assertions with no accepting counterpart in the same source, so nothing in the test actually proved the checker fires *only* under the stated condition rather than unconditionally.

**What changed** — merged 12 of the 20 tests into 6 case+control pairs sharing one compiled source (mirroring the pattern already used elsewhere in this file, e.g. `simpleWildcardNoInference`'s testPositive/testNegative):
- The four bound-admits-null / explicit-@NonNull-override scenarios (bare bound, requirement-side nullable, explicit `@NonNull T`) into one decision-table-style test.
- The explicit-`@Nullable`-use pair (rejected vs. accepted-by-a-nullable-requirement).
- The `S extends T` / `S extends @Nullable T` pair bounded by another variable.

For 5 more tests that had no BUG/OK counterpart in the original commit, I added a minimal single-respect accept control reusing the same declarations already in the test (unannotated-code Holder, transitively-bounded `S`, bare-vs-`@Nullable`-use against `? extends T`, bare-vs-`@NonNull`-annotated wildcard, bare-vs-wildcard actual) — cheap additions that turn a solo "always reports" assertion into a real test of the stated condition. Renamed every touched test to state the rule it establishes (e.g. `aTypeVariableFailsAWildcardRequirementOnlyWhenItsBoundAdmitsNullAndTheRequirementDoesNot`), per the skill's naming rule for a case with its controls.

Left unchanged: `aTypeVariableMeetsAWildcardBoundedByThatSameTypeVariable(UnderInference)`, `...MeetsAnUnboundedWildcardRequirement`, `...MeetsTheVariableItExtends`, the two captured-type-argument tests, and the override-widening test — each already stands on its own distinct fact with no natural single-respect twin among the 20, and forcing a merge would have cost more clarity than it bought.

**What I didn't do, and propose**: this repository has no test-stack line in `CLAUDE.md`/`AGENTS.md` (JUnit 4 + `CompilationTestHelper`, with the harness's stops-at-first-mismatch behavior and line-only case naming established here by reading `DiagnosticTestHelper`'s source). Per the skill, I'm proposing one line for `CLAUDE.md`: *"Tests: JUnit 4 engine; `CompilationTestHelper`/`DiagnosticTestHelper` as the assertion harness — it stops at the first mismatched line per source and names a case only by that line number, so a case and its controls share one compiled source and two cases that could both report go in separate tests."* I didn't add it myself since that's a decision for you to confirm, not something to fold into a test-only change.
