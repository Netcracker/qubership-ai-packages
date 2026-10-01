Only the test file is modified, as required; production code is untouched and nothing was committed.

---

Here's the message I'd leave for the author:

**What I changed and why**

The two new tests (`testSelectJoinUsingCommonColumnCaseSensitive`, `testNaturalJoinCommonColumn`) called `.ok()` on eight SQL fixtures, i.e. they only asserted that validation didn't throw. That's a "passes only because nothing threw" test: it wouldn't catch a regression where the common column resolves to the wrong table, gets the wrong alias case, or is coalesced in the wrong order. I replaced every `.ok()` with `.rewritesTo(expected)`, which this file already uses extensively for expansion checks (e.g. `testRewriteWithIdentifierExpansion`) and which asserts the actual unparsed, expanded SQL — so the test now pins down *what* the validator rewrites `DEPTNO`/`deptno` to, not just that it doesn't error.

I also cut the case count from 8 to 5 and renamed/re-split the methods, after checking each case against the pre-fix code (by temporarily swapping in the parent commit's `SqlValidatorImpl.java`, never committing it):

- Dropped `select DEPTNO ... using (DEPTNO)` and one of the two natural-join exact-case variants: they already passed before the fix too (same-case strings match under plain `String.equals`/`List.contains` regardless of case sensitivity), so they're redundant — nothing you can name would make them fail.
- Kept and renamed the two USING cases where the select-list identifier and the USING-list identifier differ in case (`testJoinUsingCommonColumnCaseInsensitiveSelectUppercase` / `...UsingUppercase`): both are genuine regressions (ambiguous-column error pre-fix), and I kept both directions because the `COALESCE`'s alias takes the case of the SELECT identifier, not of the USING list — so the two directions assert different expected output, not the same case twice.
- Added back a same-case-both-sides USING case (`testJoinUsingCommonColumnCaseInsensitive`, `deptno`/`deptno`) that the original test didn't have: this one fails pre-fix with an `AssertionError` (not even a clean validator exception), because the row-type field lookup was a case-sensitive `List.contains` against the catalog's upper-case field names — a different code path than the identifier-vs-USING-list match, worth its own case.
- Kept `testNaturalJoinCommonColumn` but discovered it's a regression test regardless of case sensitivity: pre-fix, `expandExprFromJoin` only special-cased `JoinConditionType.USING`, so a NATURAL JOIN's named common column was never expanded at all and always came out "ambiguous," even with an exact-case, case-sensitive match. I documented that in the Javadoc since it wasn't obvious from the JIRA title.
- Added `testNaturalJoinCommonColumnCaseInsensitive` for the case-insensitive-mismatch variant specific to NATURAL JOIN.

I verified all 5 surviving tests fail (red) on the pre-fix code and pass (green) on the actual fix, and ran the full `SqlValidatorTest` class (550 tests) plus checkstyle, both clean.

**What I propose but didn't do**

- This file has no stated test-stack convention (no `AGENTS.md`/`CLAUDE.md`); I'd propose adding one line naming JUnit 5 + the `SqlValidatorFixture`/`rewritesTo` convention, so future contributors know `.ok()` alone is discouraged for expansion-sensitive changes.
- I kept each case as its own `@Test` method rather than chaining multiple `sql(...)` calls in one method (as `testJoinUsing` and many neighbors do), because `.rewritesTo()` aborts on the first mismatch — chaining would let an earlier failure hide a later one. This is a minor departure from the file's dominant style; if you'd rather keep the old multi-call-per-test shape for consistency, I can fold them back in at the cost of per-case failure isolation.
