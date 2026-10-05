I rewrote the CALCITE-7051 tests in `core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java`. Production code is unchanged and nothing is committed. All 554 tests in `SqlValidatorTest` pass on the fixed code, and checkstyle and autostyle pass.

The skill references I used were JUnit 5 (engine), Hamcrest, and JUnit 5 assertions, chosen from the file's imports because the repository has no `AGENTS.md` or `CLAUDE.md`.

---

**Message to the author**

Thanks for the fix. I rewrote the two tests the commit added. The fix looks right, but I found one case it misses (point 1 under "Not done").

**What changed in the tests and why**

- **The tests now check the result, not just that validation succeeds.** The old tests ended in `.ok()`, which only checks that nothing threw, so they would also pass if the column were expanded wrongly. Each test now calls `rewritesTo(...)` and checks the expansion: `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)`, named the way the select list spells it.
- **Each query is now its own test.** `testSelectJoinUsingCommonColumnCaseSensitive` and `testNaturalJoinCommonColumn` each ran four queries in a row, so the first failure hid the rest and the test name couldn't say which query broke. There are now nine tests, each named for its scenario, such as `testJoinUsingCaseInsensitiveNamesColumnAsSpelledInSelect`.
- **The repeated setup is in one helper.** The four lines of configuration copied into every case are now in `sqlCaseInsensitive(sql)`, which takes only settings. Each query is still written out in full in its test.
- **One new control for case-sensitive matching.** `testJoinUsingCaseSensitiveRejectsColumnSpelledDifferentlyInSelect` checks that `select deptno … using (DEPTNO)` is still rejected when names are case-sensitive. Without it, nothing would fail if the fix ignored the case-sensitivity setting.
- **Every input from the original tests is kept.**

**Evidence**

- **Red on the base commit:** with your test changes applied to the parent commit's `SqlValidatorImpl`, 7 of the 9 tests fail with the bug's symptoms. Six report "Column 'deptno' is ambiguous" or "Column 'DEPTNO' is ambiguous", and the lowercase USING case hits the `assert qualifiedNode.size() == 2` in `expandExprFromJoin`. The two controls pass on both commits: `DEPTNO`/`DEPTNO` with case-insensitive matching, and the case-sensitive rejection.
- **NATURAL JOIN was broken in every mode, not just case-insensitive.** With identifier expansion on, it reported "ambiguous" even with case-sensitive names. So the two case-sensitive NATURAL tests are regression tests too, and their comments say so.
- **Two hand-made mutants of the fix are both caught:**
  - Naming the column with the USING spelling instead of the select spelling fails 3 tests.
  - Hard-coding `caseSensitive = false` fails the new case-sensitive control, and only that test.
- **Where the expected strings come from:** the `COALESCE` of both sides and the column name follow from the intended behavior. The `FROM …` part is how `rewritesTo` prints the query, which I checked against an actual run.
- **Test level:** these run the validator in-process, and no larger test is needed because nothing crosses a process boundary.

**Not done: proposals**

1. **The fix misses a column alias with a different spelling.** With case-insensitive names, `select deptno as x from emp join dept using (DEPTNO)` still fails with "Column 'deptno' is ambiguous". The same happens for `select DEPTNO as x … using (deptno)`. The cause is that `getFieldAliases` stores aliases under the select's spelling, but `fieldAliases.containsKey(name)` looks them up with the USING spelling. I didn't add a failing test because I couldn't change production code. Once that lookup uses the same name matcher, a test in the same shape should follow. Matching spellings work today: `select DEPTNO as x … using (DEPTNO)` expands to `COALESCE(...) AS x`.
2. **Joins of three or more tables (existing limitation, unrelated to case).** `select deptno from emp join dept using (deptno) join dept as d2 using (deptno)` hits `assert qualifiedNode.size() == 2` even with default settings. I left it alone.
3. **A test-stack line for the repository instructions.** The repository has no `AGENTS.md`, so I created none. If the maintainers want one, I'd suggest: `Tests: JUnit 5 engine; Hamcrest with JUnit 5 assertions; validator tests use SqlValidatorFixture (ok/fails/type/rewritesTo), one query per validation`.
