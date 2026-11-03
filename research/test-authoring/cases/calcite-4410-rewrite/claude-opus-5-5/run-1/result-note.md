I rewrote the two CALCITE-7051 tests in `core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java` as seven tests, and production code is unchanged. Six of the seven fail on the code before your fix and pass with it. The full `SqlValidatorTest` class passes (552 run, 0 failed, 7 skipped), and `checkstyleTest` is clean. Nothing is committed.

Here is the message for the author:

---

Thanks for the fix. I rewrote the tests it added in `SqlValidatorTest`; here is what changed and why.

**The old tests could not fail on the wrong result.** Every query ended in `.ok()`, which only checks that validation doesn't throw. Suppose the expansion picked the wrong column, skipped the COALESCE, or took the alias from the wrong place. The tests would still pass as long as nothing threw. Each test now asserts the rewritten SQL with `rewritesTo(...)`, which shows two things:
- The common column becomes `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)`.
- Its alias is spelled as in the select list, not as in the USING clause. That is the `identifier.getSimple()` change.

**One query per test.** `testSelectJoinUsingCommonColumnCaseSensitive` had four queries in one method, so the first failure hid the rest. The name also said "CaseSensitive" while every query ran case-insensitive. Each query is now its own test, named for the case it covers:

| Test | Query | Before the fix |
| --- | --- | --- |
| `testJoinUsingCaseInsensitiveCommonColumnInCatalogCaseIsCoalesced` | `DEPTNO … using (DEPTNO)` | already passed; kept as the control |
| `testJoinUsingCaseInsensitiveCommonColumnInOtherCaseIsCoalesced` | `deptno … using (deptno)` | `AssertionError` in `expandExprFromJoin` |
| `testJoinUsingCaseInsensitiveSelectItemMatchesLowerCaseUsingColumn` | `DEPTNO … using (deptno)` | `Column 'DEPTNO' is ambiguous` |
| `testJoinUsingCaseInsensitiveSelectItemMatchesUpperCaseUsingColumn` | `deptno, empno … using (DEPTNO)` | `Column 'deptno' is ambiguous` |
| `testNaturalJoinCommonColumnIsCoalesced` (case-sensitive) | `deptno, empno … natural join dept` | `Column 'DEPTNO' is ambiguous` |
| `testNaturalJoinCaseInsensitiveCommonColumnInCatalogCaseIsCoalesced` | `DEPTNO … natural join dept` | `Column 'DEPTNO' is ambiguous` |
| `testNaturalJoinCaseInsensitiveCommonColumnInOtherCaseIsCoalesced` | `deptno … natural join dept` | `Column 'deptno' is ambiguous` |

**Other changes:**
- **Shared setup:** the four repeated setup lines (case-insensitive, `Casing.UNCHANGED` for quoted and unquoted names, identifier expansion) are now one helper, `sqlCaseInsensitiveExpanded(sql)`. Only the query differs between tests, and it stays in the test body.
- **A column that is not common:** `empno` is now in two queries. It must stay a plain `EMP.EMPNO`, which catches a name match that accepts too much, or a NATURAL column list that takes every field. It expands the same way before and after the fix.
- **A dropped query:** the case-sensitive `select DEPTNO … natural join dept` duplicated the `deptno` one. The parser upper-cases unquoted names, so both reach the validator as the same query.
- **NATURAL JOIN also changed when case-sensitive.** Before the fix, a NATURAL JOIN with identifier expansion failed as ambiguous even with case-sensitive matching. So `testNaturalJoinCommonColumnIsCoalesced` covers the new NATURAL expansion, not only the case handling. It may be worth saying so in the JIRA issue or the commit message.

**Checks I ran:**
- All seven tests on the code before the fix: six fail as in the table, and the catalog-case control passes.
- With the alias set back to `name`, three tests fail: the two mixed-case USING tests and the lower-case NATURAL one.

**Proposed, not done:**
1. **A three-table join:** `… using (deptno) join bonus using (ename)` with a lower-case `deptno`. On the old code this hit the same `AssertionError` through the recursive call into the inner join. Its NATURAL form would cover `deriveNaturalJoinColumnList` on an inner join.
2. **An outer join:** `left join … using (deptno)`, case-insensitive. That is where taking COALESCE over a single qualified column would give different results.
