I rewrote the two tests from the last commit in `core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java` as nine small tests. Production code is unchanged and nothing is committed. All 554 tests in `SqlValidatorTest` pass and checkstyle is clean. `autostyleJavaCheck` could not run offline because the google-java-format jar isn't cached.

How I checked them:
- **Against the code before the fix:** six of the new tests fail, with the original bug's symptoms ("Column 'DEPTNO' is ambiguous", or an `AssertionError`). The other three still pass there, which is what they are for.
- **Against three deliberate breakages of the fix:** each one makes at least one test fail:
  - always matching case-insensitively;
  - taking the output column name from the USING list instead of the select item;
  - looking up the table's columns with an exact-case `contains` again.

---

**Message for the PR author**

Thanks for the fix. I reworked the tests; here is what changed and why.

1. **The tests now check the result, not just that validation succeeds.** Every case used `.ok()`, which passes as long as nothing throws. It could not catch the second behaviour this PR changes: the output column is now named the way the select item spells it (`identifier.getSimple()` instead of the USING `name`). Each case now asserts the row type, e.g. `select deptno … using (DEPTNO)` gives `RecordType(INTEGER NOT NULL deptno) NOT NULL`. If the alias goes back to the USING name, three tests fail.

2. **One query per test.** The old tests ran four queries each, and the first failure hid the rest. Now each query is its own method, so a red build names the failing case. The four repeated config lines (case-insensitive matching, identifier expansion, casing left as written) now live in one helper, `sqlCaseInsensitive(String sql)`, so each test shows only its query and expected type.

3. **Two new tests check that case-sensitive matching still holds.** With the default case-sensitive settings, `select "deptno" from emp join dept using (deptno)` and the NATURAL JOIN version must still fail with "Column 'deptno' not found". No previous test would have failed if the fix matched case-insensitively all the time. These two do.

4. **Kept, dropped and renamed:**
   - `select DEPTNO … using (DEPTNO)` stays even though it passed before the fix. It shows the other cases fail because of the spelling, not the setup. It has no CALCITE-7051 javadoc, since it isn't a regression case.
   - I dropped one of your two case-sensitive NATURAL JOIN cases. With default casing, `deptno` is upper-cased to `DEPTNO` before validation, so both were the same query. The kept one is `testNaturalJoinExpandsCommonColumn`. Before your fix it failed even in case-sensitive mode, so NATURAL JOIN expansion was broken in general, not only when matching ignores case. That might be worth a line in the commit message.
   - Names now state the outcome, e.g. `testJoinUsingCaseInsensitiveNamesColumnAsSelectItemSpellsIt`.

5. **Error match loosened.** The not-found error now ends with "; did you mean 'DEPTNO', 'DEPTNO'?", so the two new error tests match only the defined part (`… not found in any table.*`).

Suggestions I didn't act on:
- The "did you mean" hint lists `DEPTNO` twice for a common column. That's a small separate wart, probably its own issue.
- No test covers a common column of a nested join, e.g. `emp join bonus using (ename) join dept using (deptno)`. That path goes through the recursive `expandExprFromJoin` call you changed. It works now, but none of my breakages touched it, so a test there would mostly be for the future.
- `.type()` checks the output column's name and type, not that the item became `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)`. A `rewritesTo` check would pin that too, but it also locks in the whole unparsed FROM clause, so I left it out.
