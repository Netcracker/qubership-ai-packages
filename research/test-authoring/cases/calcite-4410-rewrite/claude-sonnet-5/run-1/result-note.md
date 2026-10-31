This is complete and passes. Here's the message for the PR author:

---

**What I changed in the tests, and why**

The commit added two test methods, each chaining four `sql(...).ok()` calls. I split them into seven separate `@Test` methods and replaced `.ok()` with `.type(...)`.

1. **Each `sql(...).ok()` call masks the ones after it.** `ok()` throws immediately on failure, so when four independent queries share one test body, only the first failure is ever reported — the rest never run. I confirmed this empirically: reverting just the production fix and running the two original tests as written shows only one failure each, even though 6 of the 8 individual queries are actually broken on the base commit. I split each query into its own `@Test` so every case fails under its own name.

2. **`.ok()` only asserts "no exception," which isn't what this bug is about.** The JIRA title is about *matching* the wrong column, and the fix also changes *which casing the resulting column is named with* (`expandExprFromJoin` now builds the alias from `identifier.getSimple()` — the select list's own casing — instead of from the `USING`-clause name). A test that only checks "no exception" can't see that part of the fix regress. `testJoinUsing` elsewhere in this file already asserts the row type with `.type(...)` for the same `USING`/`NATURAL JOIN` scenarios, so I followed that existing convention and asserted the exact `RecordType(...)` string, including the column's letter case, for every case.

3. **One case in the `USING` group turned out to be a non-case.** `select DEPTNO from emp join dept using (DEPTNO)` already worked before the fix (the literal text matches the catalog's own uppercase spelling, so plain string equality succeeded even in the old code) — I kept it as the "both sides already uppercase" baseline, not as a regression claim.

4. **Two cases in the `NATURAL JOIN` group were accidental duplicates.** `caseSensitive(true)` with select item `DEPTNO`, and the same with select item `deptno`, parsed to the *same* query, because neither case set `withUnquotedCasing(Casing.UNCHANGED)`, so the parser's default casing uppercased `deptno` to `DEPTNO` before validation — the two "cases" ran the identical check twice. I merged them into one `testNaturalJoinCommonColumnCaseSensitive`.

5. **Verified every surviving case is a real regression test.** I checked out the parent commit, re-applied only the new tests (unfixed production code), and ran each individually: 6 of the 7 fail there (the `AssertionError` for mismatched-case `USING` columns, or `Column 'DEPTNO' is ambiguous` for `NATURAL JOIN`), and the "both sides already uppercase" baseline passes on both commits, as expected. All 7 pass on this commit, and the full `SqlValidatorTest` suite (552 tests) still passes.

**What I propose but did not do**

- A control test that a genuinely mismatched-case column is still *rejected* under `caseSensitive(true)` (proving the fix didn't accidentally loosen case-sensitive matching) would strengthen the suite further, but it's new coverage beyond what this commit's tests exercised, so I left it as a suggestion rather than adding it unasked.
