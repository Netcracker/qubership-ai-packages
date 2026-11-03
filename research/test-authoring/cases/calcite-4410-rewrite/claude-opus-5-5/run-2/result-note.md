I rewrote the two tests from the CALCITE-7051 commit in `SqlValidatorTest.java` as eight separate tests sharing one small helper. The production code is unchanged and nothing is committed. All 553 `SqlValidatorTest` tests pass, and checkstyle and autostyle pass.

On the base commit (the code before the fix), the five tests for the fix fail with the original errors ("Column 'deptno' is ambiguous" and an `AssertionError`), and the three controls pass. I also changed one production line temporarily to check that the new assertions catch a real bug, then restored it. The original tests did not catch it.

One sentence for you rather than the pull request: the test-authoring skill suggests a line in the repository's instructions file stating that each `sql(…)` check stops at its first mismatch. Say if you want it added; I created no instructions file.

---

**Message for the author of the pull request**

Thanks for the fix. I rewrote the tests it added; here is what changed and why.

**What changed in the tests**

- **A failure now names its case.** Each of the old tests ran four queries in a row, and the first failure hid the other three. Each query is now its own test, named for the case it covers, for example `testCaseInsensitiveJoinUsingResolvesSelectItemInOtherCaseThanUsing`.
- **The tests check the result, not only that validation succeeds.** `.ok()` became `.type("RecordType(INTEGER NOT NULL deptno) NOT NULL")`. This checks the part of the fix that names the output column after the select item rather than after the USING column. To confirm, I changed that line back to `new SqlIdentifier(name, …)`: three of the new tests fail, while every original test still passed.
- **The USING cases cover all four combinations.** The select item can match the USING column's case or not, and the USING column can match the table column's case or not. Only `select DEPTNO … using (DEPTNO)` passed before your fix, so I kept it as the baseline.
- **Two new controls.** These are the same queries with case-sensitive matching. They fail with "Column 'deptno' not found…", both before and after the fix. They show that the new matching depends on the case-sensitivity setting, not on the queries themselves.
- **Shared settings live in one helper, `sqlWithUnchangedCasing(sql, caseSensitive)`.** The four repeated settings are written once. The table names are upper case so that a case and its control differ only in the case-sensitivity flag.
- **Two original queries are gone; they duplicated others.** With default settings, `select deptno` and `select DEPTNO` are read as the same name. And `select DEPTNO … natural join` with case-insensitive matching tests nothing that the case-sensitive version does not.
- **NATURAL JOIN under default settings has its own test, `testNaturalJoinResolvesCommonColumn`.** Your fix also changed this case: before it, `select DEPTNO from emp natural join dept` failed with "Column 'DEPTNO' is ambiguous" even with default case-sensitive settings.

**Proposed, not done**

- **A remaining bug with aliases.** `select deptno as d from emp join dept using (DEPTNO)`, with case-insensitive matching and unchanged casing, still fails after the fix. The error is "Column 'deptno' is ambiguous", reported at line 0, column 0. With `using (deptno)` it passes. The likely cause is `fieldAliases.containsKey(name)` in `expandExprFromJoin`, which looks up the USING spelling exactly. It should probably use `identifier.getSimple()` or a case-insensitive match. That is a production change, so I left it, along with a test for it, to you.
- **GROUP BY is untested.** `expandCommonColumn` is also called when expanding GROUP BY. A test such as `select deptno from EMP join DEPT using (DEPTNO) group by deptno` with case-insensitive matching would cover it.
