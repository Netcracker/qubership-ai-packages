Confirmed, no such file exists. That proposal goes into the message below rather than any file edit.

---

**Message for the pull request author:**

The two tests this commit added (`testSelectJoinUsingCommonColumnCaseSensitive`, `testNaturalJoinCommonColumn`) only called `.ok()`, which asserts that validation doesn't throw — nothing else. I replaced both with seven focused tests, each using the existing `rewritesTo(expected)` fixture method to assert the actual expanded/coalesced SQL (alias casing included), since `.ok()` alone can't tell "validated correctly" from "validated by accident."

What I found while deriving the expected literals (by running each case against both `HEAD` and `HEAD~1`, i.e. before your production fix):

- Of the 4 original USING-clause cases, only one (`DEPTNO`/`DEPTNO`, matching the catalog's physical uppercase casing) already passed before your fix — I kept it as a non-regression control (`testJoinUsingCommonColumnCaseInsensitiveMatchingCatalogCasing`). The other three are genuine regressions, and interestingly they fail for *two different reasons* pre-fix: same-casing-but-non-catalog-casing (`deptno`/`deptno`) trips a `assert qualifiedNode.size() == 2` `AssertionError` deep in the old code (not even a validation error), while the mismatched-casing pairs (`DEPTNO`/`deptno` and `deptno`/`DEPTNO`) surface as a user-facing "Column is ambiguous" error. I split these into three separate tests so each failure mode is named and visible on its own.
- For `testNaturalJoinCommonColumn`, two of the four original cases (both `caseSensitive=true`, one spelled `DEPTNO` and one `deptno`) are byte-for-byte duplicates after parsing: Calcite's default unquoted-casing policy (`TO_UPPER`) erases the spelling difference before validation ever sees it, so both exercise the identical code path. I dropped the duplicate and made the surviving `caseSensitive=true` case's casing config explicit instead of implicit. I also confirmed that *every* `caseSensitive` setting for NATURAL JOIN failed pre-fix (not just the case-insensitive ones) — the old `expandExprFromJoin` didn't handle NATURAL JOIN at all, independent of case-sensitivity — so the `caseSensitive=true` case is as much a regression test as the other two.
- I verified red-before/green-after directly: reverted `SqlValidatorImpl.java` to `HEAD~1`, ran all 7 new tests (6 failed as predicted, the control passed), then restored it and confirmed all 7 pass, plus the full `SqlValidatorTest` class (552 tests, 0 failures).

What I propose but didn't do: this repository has no `AGENTS.md`/`CLAUDE.md`, so there's no place to record the project's test stack (JUnit 5 + Hamcrest, per the imports) for future changes — worth adding a one-line stack note if you want future contributions to skip rediscovering that. I also didn't touch `SqlValidatorImpl.java` or commit anything, per the task.
