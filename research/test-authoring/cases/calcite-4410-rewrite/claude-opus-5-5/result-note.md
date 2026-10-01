I rewrote the two tests from the CALCITE-7051 commit as seven single-query tests, and each one now checks the expanded SQL instead of only that validation succeeds. The whole `SqlValidatorTest` class passes (552 run, 0 failed, 7 skipped — those were already disabled), and checkstyle and autostyle are clean. Only `SqlValidatorTest.java` changed; the production code is untouched and nothing is committed.

---

**Message for the author of the pull request**

**What I changed in the tests, and why**

1. **One query per test.** `testSelectJoinUsingCommonColumnCaseSensitive` and `testNaturalJoinCommonColumn` each ran four queries in a row. The first query that failed stopped the test and hid the rest. On the code before your fix, each test reported only one of its failing queries. Each query is now its own test, named for what it shows. The tests around them in the file use the same chained style, but here it hides failures, so these tests don't follow it.

2. **They now check the expansion itself.** `.ok()` only showed that validation didn't throw. Each test now uses `rewritesTo` with the expected SQL written out by hand, for example `COALESCE(`EMP`.`DEPTNO`, `DEPT`.`DEPTNO`) AS `deptno``. This also checks your change that takes the alias from the select list instead of the USING list. Undoing just that change makes three of the new tests fail.

3. **New case: case-sensitive matching still rejects a column spelled in a different case.** `testJoinUsingCaseSensitiveDoesNotMatchCommonColumnInOtherCase` runs `select deptno … using (DEPTNO)` with case-sensitive matching and expects `Column 'deptno' not found`. Your fix made the matching depend on `caseSensitive`. If that code ignored the flag and always matched case-insensitively, the original tests would still pass. This test fails in that case.

4. **Shared setup in one helper.** `sqlExpandedInWrittenCase(sql)` turns on identifier expansion and keeps identifiers in the case they are written. Each test still shows its query, its `withCaseSensitive(...)` setting and the expected SQL in full. Table names are now `EMP`/`DEPT` everywhere, so the only lowercase text left is the column name each case is about.

5. **Two queries dropped as duplicates:**
   - The case-sensitive `select deptno from emp natural join dept` with default casing. The parser turns it into `DEPTNO`, so it is the same query as the case-sensitive `DEPTNO` one.
   - The case-insensitive NATURAL `DEPTNO`. Its spelling already matches the catalog, so it runs the same code path as the case-sensitive NATURAL test.

   Both failed before the fix, so dropping them loses no query that passed then. I kept the case-insensitive USING `DEPTNO`/`DEPTNO` query, which did pass before the fix, as `testJoinUsingCaseInsensitiveExpandsCommonColumnInCatalogCase`.

**Evidence**

I ran the new tests against the code before your fix (`SqlValidatorImpl.java` from `HEAD~1`):

| Query | Before the fix | With the fix |
| --- | --- | --- |
| USING, case-insensitive, `deptno` / `(deptno)` | `java.lang.AssertionError` (the `qualifiedNode.size() == 2` check) | passes |
| USING, case-insensitive, `DEPTNO` / `(deptno)` | `Column 'DEPTNO' is ambiguous` | passes |
| USING, case-insensitive, `deptno` / `(DEPTNO)` | `Column 'deptno' is ambiguous` | passes |
| NATURAL, case-sensitive, `DEPTNO` | `Column 'DEPTNO' is ambiguous` | passes |
| NATURAL, case-insensitive, `deptno` | `Column 'deptno' is ambiguous` | passes |
| USING, case-insensitive, `DEPTNO` / `(DEPTNO)` | passes | passes |
| USING, case-sensitive, `deptno` / `(DEPTNO)` | passes | passes |

The last two rows passed before the fix too; they check behavior the fix must keep.

I also made two changes to the fix by hand and checked that the tests catch them:
- **Always matching case-insensitively:** the new case-sensitive test fails.
- **Taking the alias from the USING list again:** three tests fail.

**Note:** NATURAL JOIN with identifier expansion failed with "ambiguous" even with case-sensitive matching and matching spelling. So that half of the fix is not only about case sensitivity, which the issue title doesn't say.

**Proposed, not done**

- The repository has no `AGENTS.md` or `CLAUDE.md` listing its test libraries. I'd add one line: `Tests: JUnit 5 engine; Hamcrest and JUnit 5 assertions; validator tests go through SqlValidatorFixture (one sql(...) per test, since a chain stops at the first failure)`. I didn't create the file.
- The neighbouring tests (`testJoinUsing`, `testSelectAmbiguousField`) chain several queries in one method, so they have the same problem as point 1. I left them as they were because that's outside this change.
