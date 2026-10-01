I rewrote the tests from that commit in `SqlValidatorTest.java`. They now check the SQL the validator actually produces instead of only checking that validation succeeds. Six of the new tests fail on the code before the fix and pass after it. Nothing is committed and the production code is unchanged. All 553 tests in `SqlValidatorTest` and checkstyle pass.

---

**Message for the author**

I changed the tests for CALCITE-7051 in `SqlValidatorTest.java`. The production code is unchanged.

**What changed**

- **They now assert the result, not just that validation passes.** Each query used `.ok()`, which only checks that validation doesn't throw. A wrong expansion, such as the wrong alias or a column left unexpanded, would still pass. Each test now uses `rewritesTo(...)`. It checks the expanded SQL, like `COALESCE(`EMP`.`DEPTNO`, `DEPT`.`DEPTNO`) AS `deptno``, and prints both versions when it fails.
- **One query per test.** The two old methods each ran four queries in a row. The first failure hid the rest, and the report named only the method. Each query is now its own test method, named for what it shows, for example `testJoinUsingCaseInsensitiveAliasesColumnAsSelectListSpellsIt`.
- **The repeated setup is written once.** The four configuration calls (`withCaseSensitive(false)`, identifier expansion, unchanged quoted and unquoted casing) were copied into six queries. They now live in one helper, `sqlCaseInsensitive(String)`, so each test shows only its query and its expected result.
- **Added a case-sensitive test.** It runs `select ^deptno^ from EMP join DEPT using (DEPTNO)` with case-sensitive matching and checks that it still fails with "Column 'deptno' not found". Without it, nothing fails if the new matching ignores the `caseSensitive` setting. I checked this: making the match always case-insensitive fails only this test. The tables are spelled `EMP`/`DEPT` because lowercase table names would fail first, on the table lookup.
- **Dropped one redundant case.** The old natural-join test had `select DEPTNO` and `select deptno` with case-sensitive matching. With the default casing both read as `DEPTNO`, so they test the same thing. I kept one as `testNaturalJoinExpandsCommonColumn`.

**Evidence**

I swapped in the pre-fix `SqlValidatorImpl` and ran the new tests:

| Test | Before the fix | After the fix |
| --- | --- | --- |
| `using (DEPTNO)` with `select DEPTNO` (spelled as the tables spell it) | passes | passes |
| The case-sensitive `not found` test | passes | passes |
| The other six | fail | pass |

Of those six, five fail before the fix with `Column '…' is ambiguous`. `select deptno … using (deptno)` hits an `AssertionError` (the `assert qualifiedNode.size() == 2` line). Note that `NATURAL JOIN` also failed before the fix with case-sensitive matching, so that test checks more than case handling.

I also tried a second deliberate break: taking the alias from the `USING` clause instead of the select list. Three tests fail on it, including `…AliasesColumnAsSelectListSpellsIt` and `…AliasesLowerCaseColumnAsSelectListSpellsIt`.

**Proposed, not done**

1. **Test a column from the inner join of a three-table join.** `select deptno from emp e join dept d using (deptno) join bonus using (ename)` fails before the fix with the same `AssertionError` and works after it. No test covers it. It would fill the one gap in what this change touched.
2. **A separate bug, before and after this fix.** `select deptno from emp e join dept d using (deptno) join emp e2 using (empno)` stops on `assert qualifiedNode.size() == 2`, because three tables have `DEPTNO`. This should be its own JIRA issue.
3. **Spelling in the expected SQL.** The expected SQL qualifies columns as `EMP`.`DEPTNO` while the table alias is `AS emp`. That is how the validator already writes them; I kept it as is and did not treat it as a bug.
4. **A line about the test setup in a repository instructions file.** The repository has none (no `AGENTS.md` or `CLAUDE.md`), so I created nothing. A line like this would help: `Tests: JUnit 5 engine; JUnit 5 assertions and Hamcrest; validator tests use SqlValidatorFixture, where each sql(...).rewritesTo/fails/ok checks one query and stops at the first mismatch.`
