Everything is green, and only the test file was touched. Here's the message I'd leave for the PR author:

---

**What I added**

The fix commit changed `SpringHandler.containsNullSpELExpression` but added no tests, so I added two, alongside the existing `springValueFieldTest` in `FrameworkTests.java`:

- `nullIsFlaggedOnlyWhenNotMerelyAComparisonOperandTest` — the exact scenario from the bug report (`#{someBean != null ? someBean.value : 'default'}`) now compiles with no diagnostic, paired with a control (`#{someBean != null ? null : 'default'}`) that still reports `field not initialized`, since a comparison null shouldn't hide an actual null-producing branch.
- `nullIsFlaggedOnlyWhenNotMerelyAReversedComparisonOperandTest` — same pair, but with the operand order flipped (`null != someBean ...`), since `NULL_COMPARISON_PATTERN` is two regex alternatives (`x != null` and `null != x`) and only the first was exercised by the PR's own example. I kept it as a second test rather than folding it into the first because the harness (Error Prone's `CompilationTestHelper`) fails at the first mismatched line per compilation, so two independent regression cases sharing one check could hide one another.

**Verification**

I swapped in the pre-fix `SpringHandler.java` (from the parent commit) and confirmed both new tests go red exactly on the regression field's line (`onlyComparedAgainstNull` incorrectly flagged), then restored the fix and confirmed `./gradlew :nullaway:test` and `:nullaway:buildWithNullAway` are green. No production code was touched.

**What I propose but didn't do**

- The repo's instructions (`AGENTS.md`/`CLAUDE.md`) don't record a test-stack line (engine/assertions/doubles) for this module. Worth adding one, e.g.: *"Tests: JUnit 4 engine; Error Prone `CompilationTestHelper`/`// BUG: Diagnostic contains:` markers as the assertion form; the harness fails at the first mismatched line per compilation and names a case only by line number and marker text."* That's a repo-wide fact, not something I should decide unilaterally, so I left it as a proposal rather than editing the file.
- I didn't add a case for the `==` operator specifically (only `!=`, in both orders) — the `[!=]=` character class technically also permits `==`, and a mutant narrowing it to just `!` wouldn't be caught by my two tests. I skipped it to avoid combinatorial bloat for a heuristic regex, but it's a cheap addition if you want tighter coverage.
