Only the test file is modified, exactly as intended. No commit was made, as instructed.

---

**Message for the author of the pull request:**

I rewrote the two tests this commit added (`testSelectJoinUsingCommonColumnCaseSensitive`, `testNaturalJoinCommonColumn`) into four smaller tests, per our `test-authoring` skill.

**What changed, and why:**

1. **`.ok()` → `.rewritesTo(...)`.** `.ok()` only checks that validation completes without throwing; it never inspects the expanded `SELECT` list. That's the wrong contract for this fix — the bug isn't "validation throws," it's "the wrong column gets qualified/coalesced, or with the wrong alias." I switched every case to `.rewritesTo(...)`, which asserts the actual unparsed SQL, so a future regression that produces the wrong `COALESCE(...)`/alias (rather than an exception) is caught. I verified this matters concretely: I hand-mutated the fixed `expandExprFromJoin` to revert only the alias-construction line (`new SqlIdentifier(name, ...)` instead of `new SqlIdentifier(identifier.getSimple(), ...)`) and confirmed the new tests still catch it.

2. **Removed the redundant case pairs.** Each original test ran the same query twice with both sides uppercase and both sides lowercase — same equivalence partition (exact-case match), same outcome both before and after the fix, so the duplicate added no signal. I kept one matched-case representative only where it demonstrates something the fix actually changed (see point 3); otherwise I dropped it, since a case that can't be made to fail by any real bug earns no test.

3. **Found and named a partition the original test collapsed: `NATURAL JOIN` support was entirely missing, independent of case-sensitivity.** I checked out the parent commit's `SqlValidatorImpl.java` and ran the new tests against it directly (the skill's "red on the base commit" requirement). Pre-fix, `expandExprFromJoin` returned early for anything that wasn't `USING`, so a `NATURAL JOIN` common column was *never* coalesced — even with `caseSensitive=true` and matching case, `select DEPTNO from emp natural join dept` failed with "Column 'DEPTNO' is ambiguous." That's a different code path (`!join.isNatural()`) from the case-insensitive-matching fix (`Util.matches`/`Util.findMatch`). I split these into two tests — `testNaturalJoinCommonColumnIsCoalesced` (coalescing now happens at all) and `testNaturalJoinCommonColumnMatchesCaseInsensitively` (it also matches case-insensitively) — each confirmed red on the base commit and green on the fix.

4. **Kept both casing directions for `USING`.** `select DEPTNO ... using (deptno)` and `select deptno ... using (DEPTNO)` both exercise case-insensitive matching, but they're not fully redundant: together they establish that the alias always follows the *select list's* casing, not the `USING` clause's — a single direction leaves that ambiguous.

5. **Split into one `@Test` method per case.** The originals chained multiple independent SQL strings inside one `@Test`, so the first failure hid the rest. I split each into its own method with the setup repeated inline (it's short), each named for the scenario and outcome it establishes.

I didn't touch `SqlValidatorImpl.java`; ran the full `SqlValidatorTest` class (549 tests, 0 failures) and checkstyle after the change.

**One thing I'm flagging but didn't do:** this file has no `AGENTS.md`/`CLAUDE.md` stack line naming the test engine/assertion library, and its dominant existing style is large multi-scenario `@Test` methods (e.g. `testJoinUsing()`) that the skill would flag as hiding failures. I followed the skill for the new tests rather than that surrounding convention, but didn't touch the neighboring tests or propose a repo-wide stack line — that's a separate, larger conversation you may want to have with the module's maintainers.
