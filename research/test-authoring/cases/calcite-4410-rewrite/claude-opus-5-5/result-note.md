I rewrote the two tests from the last commit as eight tests: seven cases and one control. All of `SqlValidatorTest` passes with the fix, and checkstyle on the test sources is clean. Six of the new tests fail when run against the production code from before the fix, and they fail with the bug itself. The production code is unchanged and nothing is committed.

**Message for the author:**

> I rewrote the tests for CALCITE-7051 in `SqlValidatorTest` and left the production code alone.
>
> **What the old tests could not catch.** They ended in `.ok()`, which only checks that validation doesn't throw. So they couldn't catch the expansion being wrong, for example a different alias on the expanded column. They also put four or five queries in one method, so the first failure hid the rest.
>
> **What the new tests check.** Each case is now its own method and checks the expanded SQL with `rewritesTo`. That shows the `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)` and the alias the select item gets.
>
> **The new helper.** `sqlCaseInsensitive(sql)` holds the settings the case-insensitive cases share (case-insensitive matching, unchanged casing, identifier expansion) and takes the whole query as its argument.
>
> **The cases.** All but `testNaturalJoinExpandsCommonColumn` match names case-insensitively.
> - `testJoinUsingCaseInsensitiveExpandsColumnSpelledAsInCatalog`: USING with every name spelled as in the catalog. It also passed before the fix, and I kept it.
> - `testJoinUsingCaseInsensitiveExpandsColumnSpelledUnlikeCatalog`: the USING list spelled unlike the catalog. Before the fix this hit `AssertionError` in `expandExprFromJoin`.
> - `testJoinUsingCaseInsensitiveAliasesExpansionAsSelectItemSpellsIt`: the select item spelled unlike the USING list. Before the fix: "Column 'DEPTNO' is ambiguous". This test also pins the alias change: the alias follows the select item's spelling, not the USING list's.
> - `testJoinUsingCaseInsensitiveExpandsSelectItemSpelledUnlikeCatalog`: the USING list spelled as in the catalog, the select item not. Before the fix: "Column 'deptno' is ambiguous".
> - NATURAL JOIN: one case-sensitive test, plus a case-insensitive test for each spelling. All three said "Column 'DEPTNO' is ambiguous" (or 'deptno') before the fix, because NATURAL JOIN columns were never expanded.
>
> **New control.** `testJoinUsingCaseSensitiveRejectsSelectItemSpelledUnlikeCatalog` is the same query as the last USING case, but with case-sensitive matching. It must still fail with "Column 'deptno' not found in any table". It would catch a fix that ignores `caseSensitive`. It passes both before and after the fix. Its table names are uppercase, as case-sensitive matching needs, so the case it controls uses uppercase tables too.
>
> **Dropped.** The case-sensitive `select deptno from emp natural join dept` was the same input as its `DEPTNO` twin, because the default casing upper-cases it. It also failed before the fix, so it wasn't a control.
>
> **Proposed, not done:**
> - A case-insensitive test for a chain of joins, such as `... join dept using (deptno) join bonus using (ename)`. It goes through the left-deep recursion in `expandExprFromJoin`, which the fix also changed.
> - The expected SQL also pins the expanded FROM clause and its `EMP` versus `emp` qualifiers, as the file's other `rewritesTo` tests do. If that turns out to break too easily, `.type("RecordType(INTEGER NOT NULL deptno) NOT NULL")` checks the alias alone.
> - The repository has no `AGENTS.md` or `CLAUDE.md`. I'd suggest adding a one-line note of the test stack: "Tests: JUnit 5 engine; Hamcrest and JUnit 5 assertions; Calcite's `SqlValidatorFixture` for validator tests."
