I rewrote the CALCITE-7051 tests in `core/src/test/java/org/apache/calcite/test/SqlValidatorTest.java`. Production code is unchanged and nothing is committed. `SqlValidatorTest` passes on the fix (553 run, 0 failed), and autostyle passes. Checkstyle did not run: the build is offline and checkstyle 8.28 isn't in the local cache. All new lines are within 100 columns.

## Message for the PR author

**What I changed in the tests, and why**

1. **Each test now checks the expansion, not just that validation passes.** The original tests ended in `.ok()`, which only proves that validation didn't throw. What the fix defines is the rewrite: the common column becomes `COALESCE(EMP.DEPTNO, DEPT.DEPTNO)`, aliased with the select item's spelling. Each test now asserts that rewrite with `rewritesTo(...)`, the same form the file's `testRewrite*`/`testCoalesce*` tests use. The expected strings are written out by hand, and a failure prints both the expected and the actual SQL. This also pins the alias change (`identifier.getSimple()` instead of `name`): `select deptno … using (DEPTNO)` must produce `` AS `deptno` ``.

2. **Each query is its own test.** The two original methods each validated four separate queries, so the first failure hid the other three, and the report couldn't say which spelling broke. There are now eight tests, each named for its scenario, for example `testJoinUsingCaseInsensitiveMatchesSelectItemSpelledOtherThanUsingColumn`. This departs from the file's habit of putting several `sql(...)` calls in one method, on purpose: one behavior per test.

3. **The repeated four-line fixture setup is in one helper.** `sqlCaseInsensitiveKeepingCase(sql)` sets case-insensitive matching, `Casing.UNCHANGED` for both quoted and unquoted identifiers, and identifier expansion. The query and the expected rewrite stay in each test.

4. **Inputs are split by how the spellings relate to the catalog's `DEPTNO`.**

   | Join | Select item / USING list | Test | On the base commit |
   | --- | --- | --- | --- |
   | USING, case-insensitive | same spelling as catalog | `…ExpandsColumnSpelledAsInCatalog` | passes (control) |
   | USING, case-insensitive | same as each other, not as catalog | `…ExpandsColumnSpelledOtherThanCatalog` | fails with a bare `AssertionError` |
   | USING, case-insensitive | select matches catalog, USING doesn't | `…MatchesUsingColumnSpelledOtherThanSelectItem` | fails: "Column 'DEPTNO' is ambiguous" |
   | USING, case-insensitive | USING matches catalog, select doesn't | `…MatchesSelectItemSpelledOtherThanUsingColumn` | fails: "Column 'deptno' is ambiguous" |
   | USING, case-sensitive | `"deptno"` vs `DEPTNO` | `…CaseSensitiveDoesNotMatchSelectItem…` (new) | passes (control) |
   | NATURAL, case-sensitive | — | `testNaturalJoinCaseSensitiveExpandsCommonColumn` | fails: ambiguous |
   | NATURAL, case-insensitive | same spelling as catalog | `…ExpandsColumnSpelledAsInCatalog` | fails: ambiguous |
   | NATURAL, case-insensitive | not the catalog's spelling | `…ExpandsColumnSpelledOtherThanCatalog` | fails: ambiguous |

   To get the base column, I temporarily restored `SqlValidatorImpl.java` from `HEAD~1`, ran these tests, and then restored the fixed file. Six failed and the two intended controls passed.

   - **New control test.** With case-sensitive matching, `select "deptno" … using (deptno)` must still fail with "Column 'deptno' not found in any table". Without this test, a change that made `Util.matches` always ignore case would pass every other test.
   - **Dropped duplicate.** The original case-sensitive NATURAL test had both `select DEPTNO` and `select deptno`. The parser uppercases unquoted identifiers by default, so both reach the validator as `DEPTNO`. I kept one.
   - **Error message.** The control matches `"Column 'deptno' not found in any table.*"`. The actual message adds the suggestion `did you mean 'DEPTNO', 'DEPTNO'?` (with the name repeated), and I didn't want the test to fail if someone rewords that.

**Proposed, not done**

- **Possible separate bug in the expansion.** With `Casing.UNCHANGED`, the rewrite qualifies the columns as `` `EMP`.`DEPTNO` `` while the FROM alias is `` `emp` ``. It resolves because matching ignores case. This happens on the base commit too, so it is outside this fix. The new expected strings include it, so if someone later changes the qualifier to follow the alias's case, these tests will need updating.
- **Test-stack line for the repository instructions.** The repository has no `AGENTS.md`, so I added nothing. I propose one: `Tests: JUnit 5 engine; Hamcrest assertions, with JUnit 5 Assertions for grouping and throws; SqlValidatorFixture (sql(...).ok()/fails()/rewritesTo()) for validator tests.`
- **Not done:** no mutation run and no checkstyle run.
