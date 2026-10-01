This looks clean. Everything compiles and the full `SqlValidatorTest` suite passes (551 tests, 0 failed). Here's the message for the PR author:

---

I rewrote the two tests this commit added (`testSelectJoinUsingCommonColumnCaseSensitive`, `testNaturalJoinCommonColumn`) into six focused tests, per the `test-authoring` skill. No production code changed, nothing committed.

**What I changed and why:**

1. **Split each bundled test into one `@Test` per scenario.** Each original method ran four independent `sql(...).ok()` validations — four separate acts — but reported under one name. If one failed, you'd have to open the file and count statements to find which. Each case now has its own name and javadoc stating the scenario and why it matters.

2. **Replaced `.ok()` with `.rewritesTo(...)`.** `.ok()` only checks that validation doesn't throw; it can't tell a correct COALESCE expansion from a wrong one. I ran each case against the pre-fix `SqlValidatorImpl` (checked out from `HEAD~1`, production code only, never committed) to see what actually happens, then asserted the exact rewritten SQL. This also exercises the second half of the fix that `.ok()` couldn't: the COALESCE's alias now takes the select item's own case (`identifier.getSimple()`) rather than the USING clause's case.

3. **Dropped one case I couldn't justify.** `testSelectJoinUsingCommonColumnCaseSensitive`'s first case (`DEPTNO`/`DEPTNO` matching exactly) passes identically before and after the fix — I verified this by running it against the pre-fix code. No plausible regression in this change would make it fail that the other three cases wouldn't already catch, so per the skill ("if nothing you can name would fail it, do not write it") I removed it rather than keep a test that asserts nothing.

4. **Dropped one duplicate.** `testNaturalJoinCommonColumn`'s first two cases (`DEPTNO` and `deptno`, both with `caseSensitive(true)`) parse to the identical tree under default casing (unquoted identifiers are upper-cased), so they were the same test twice — confirmed by identical failures when run against pre-fix code. I kept one, renamed to state what it actually establishes (NATURAL JOIN support was entirely missing from `expandExprFromJoin` before this fix, independent of case sensitivity).

**What I propose but didn't do:** this repository has no `AGENTS.md`/`CLAUDE.md` naming its test stack (JUnit 5 engine, no generic assertion library — tests go through the project's own `SqlValidatorFixture` fluent helpers). Per the skill, I'm flagging this as a one-line proposal rather than creating the file myself: `Tests: JUnit 5 engine; SqlValidatorFixture's own ok/fails/type/rewritesTo assertions for the SQL validator`. Worth adding if you'd like future test contributions to follow a stated convention instead of inferring it from neighbors each time.
