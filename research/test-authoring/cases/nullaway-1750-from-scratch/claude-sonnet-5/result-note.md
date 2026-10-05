Here's the message for the PR author:

---

**Tests added (`FrameworkTests.springValueFieldTest`, nullaway/src/test/java/com/uber/nullaway/FrameworkTests.java):**

The fix touches `containsNullSpELExpression`'s handling of `null` tokens that are comparison operands rather than actual values. I joined the existing `springValueFieldTest` (same rule, same `doTest()` act, which already reports every mismatch by file:line) instead of adding a new test method, since that's the shape its neighbors already use for this exact heuristic.

- `NegativeCases.ternaryGuardedByNullCheckOnRight` — `#{someBean != null ? someBean.value : 'default'}`, the exact pattern from the issue (`!= null` on the right). No diagnostic expected; the field is also dereferenced (`.toString()`) to show it's treated as non-null end to end, matching the style of the other negative cases in that class.
- `NegativeCases.ternaryGuardedByNullCheckOnLeft` — `#{null == someBean ? 'default' : someBean.value}`, covering the other regex alternative (`null` on the left of the comparison). `==` and `!=` share one character class in `NULL_COMPARISON_PATTERN`, so testing one operator per branch is enough; a second operator on the same side wouldn't exercise different code.
- `PositiveCases.ternaryCanStillReturnNull` — `#{someBean != null ? null : 'default'}`, the control explicitly called out in the PR description: a `null` check should strip the comparison occurrence but must leave the real one, so the field is still flagged uninitialized.

I verified both the red/green sides by hand: with `SpringHandler.java` reverted to the pre-fix version, `springValueFieldTest` fails exactly on the two new negative cases (`Saw unexpected error on line 13 / 15`, naming `ternaryGuardedByNullCheckOnRight`/`Left`); with the fix restored, the whole class is green. `:nullaway:buildWithNullAway` also passes. I didn't commit, as instructed.

**What I didn't do, and propose instead of deciding myself:**
- The repo's `CLAUDE.md`/`AGENTS.md` name no test stack line (engine + assertion library) for this project. The nearest tests show JUnit 4 (`org.junit.Test`) as the engine, with error-prone's `CompilationTestHelper` playing the assertion role via `// BUG: Diagnostic contains:` markers (one `doTest()` call reports every mismatch, named by file:line, not by a harness-assigned label). Worth adding a one-line stack entry to `CLAUDE.md` so future test-authoring doesn't have to rediscover this each time; I didn't add it myself since that's a repo-instructions change, not a test.
- `CHANGELOG.md`'s Unreleased section doesn't mention #1750 — not a testing concern, but you may want to add the entry before merging.
