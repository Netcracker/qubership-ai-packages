I rewrote the two tests from the last commit as eight tests plus one helper in `SqlValidatorTest.java`. The 553 tests in `SqlValidatorTest` pass on the fix. Checkstyle and autostyle could not run, because their dependencies can't be downloaded offline. I didn't touch the production code and didn't commit; the test file is the only change in the working tree.

On the code before the fix, 6 of the new tests fail with the bug itself: "Column 'deptno' is ambiguous", or an `AssertionError` inside `expandExprFromJoin`. The other 3 pass there, which is expected, since they check behaviour that was already right.

---

**Message for the PR author**

Thanks for the fix. I rewrote the tests for CALCITE-7051 in `SqlValidatorTest`; here is what changed and why.

1. **The tests now check the result, not only that validation succeeds.** `.ok()` only proves nothing was thrown. Each test now asserts the result type, for example `.type("RecordType(INTEGER NOT NULL deptno) NOT NULL")`. That also checks your change to the column alias: the column takes the select item's spelling, not the `USING` list's. Without that change, `select DEPTNO … using (deptno)` and both case-insensitive spellings of the NATURAL JOIN query fail again with "Column … is ambiguous". The old tests would not have noticed.

2. **One query per test.** Each old method validated four queries in a row and stopped at the first failure, so a red build showed one broken spelling and hid the rest. Each query is now its own `@Test`, and the name says which spelling of the select item, the `USING` column or the table column it covers. The repeated case-insensitive settings moved into a helper, `caseInsensitiveWithExpansion(sql)`, so each test body is one line and the SQL is visible whole.

3. **New test: `testJoinUsingCaseSensitiveRejectsItemInOtherCaseThanUsingColumn`.** With case-sensitive matching, `select deptno from EMP join DEPT using (DEPTNO)` must still fail with "Column 'deptno' not found in any table". If the expansion ignored the case-sensitivity setting, every other test would still pass; this one fails.

4. **Kept and dropped queries.**
   * I kept `select DEPTNO … using (DEPTNO)` with case-insensitive matching. It worked before the fix too, and it shows the exact-match spelling still expands.
   * I dropped one of the two case-sensitive NATURAL JOIN queries. With the default upper-casing, `deptno` and `DEPTNO` parse to the same identifier, so the second added nothing.

**Proposed, not done:**
* Checkstyle and autostyle could not run here (dependencies not cached offline), so please run them before merging.
* I asserted the result type rather than the rewritten SQL text. If you also want the `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)` expansion pinned, a `rewritesTo` check on one case-insensitive query would do it.
