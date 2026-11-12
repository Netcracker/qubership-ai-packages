All green, no production code touched, nothing committed.

---

**Message for the PR author:**

I rewrote the two tests you added for CALCITE-7051 (`testSelectJoinUsingCommonColumnCaseSensitive`, `testNaturalJoinCommonColumn`) per the repo's test-authoring conventions. No production code changed.

**What was wrong with the originals:** every case only called `.ok()`, which just asserts the validator doesn't throw. It never checks *what* the column expanded to. I verified against your fix: with `.ok()`, four of the eight sub-cases across the two tests were already green on the pre-fix commit (`cf91ec8`) — meaning `.ok()` wasn't actually exercising the case-insensitive match at all in those spots, just confirming no exception, which is a weaker claim than the bug warrants. Also, since each test method chains several independent `sql(...).ok()` calls with no shared "report every mismatch" harness behavior, a failure in the first call hides the rest — so a regression in case 2 would silently mask case 3 or 4.

**What I changed:**
- Split each test into one `@Test` method per case, so a failure names exactly which scenario broke and doesn't hide its siblings.
- Replaced `.ok()` with `.rewritesTo(...)`, asserting the actual rewritten SQL (which table each `COALESCE` operand qualifies to, and — this is the part `.ok()` completely missed — that the output alias keeps the *select item's own case*, not the USING column's case, which is the `new SqlIdentifier(identifier.getSimple(), ...)` change in your fix).
- Added two negative controls (`testJoinUsingColumnCaseMismatchFailsWhenCaseSensitive`, `testNaturalJoinCommonColumnCaseMismatchFailsWhenCaseSensitive`) that assert a case-mismatched column is still rejected when `caseSensitive=true`. These pin down that `catalogReader.nameMatcher().isCaseSensitive()` is actually consulted, not that matching became unconditionally case-insensitive.
- Kept `testJoinUsingColumnMatchesCatalogCase` (USING, exact-case match) even though it already passed pre-fix — it's a legitimate control that isolates the other three USING cases: USING clause text is matched against the real catalog field names at a point independent of the select-item comparison, so "using-clause case differs from catalog" and "select-item case differs from using-clause" are two distinct bugs the old code had, each needing its own case (I verified this by bisecting against `HEAD~1` in a scratch worktree — case-by-case, not just the test as a whole).

I confirmed every real case is red on `HEAD~1` with a symptom matching the bug (`Column 'DEPTNO' is ambiguous` for NATURAL JOIN, the `assert qualifiedNode.size() == 2` failing for the USING mismatch), and that both controls already held (or already correctly failed) pre-fix — then confirmed everything passes on `HEAD`.

**What I propose but didn't do:** nothing further seems warranted — the case/control set now covers both independent defects the fix addresses (NATURAL JOIN never being expanded at all, and case-sensitive-only matching inside `expandExprFromJoin`), plus the alias-casing side effect. If you'd rather keep the original two-method grouping for some stylistic reason (e.g. fewer JUnit entries), say so, but I'd flag that as reintroducing the failure-masking problem.
