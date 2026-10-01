I read `/var/folders/.../skill/SKILL.md` in full and followed it (no separate `references/` lookup was needed: the relevant harness, error-prone's `CompilationTestHelper` on JUnit 4, isn't one of the covered assertion libraries, so §0 rule 5 applies — I read what the existing `springValueFieldTest` already does with it instead of guessing).

## What I did

The fix changed `SpringHandler.containsNullSpELExpression`'s heuristic. The nearest existing test of that exact heuristic is `FrameworkTests.springValueFieldTest`, which already groups several `@Value` SpEL cases (negative and positive) under one `doTest()` call — and that call already reports every mismatch, by file/line/content, across however many fields are declared. Per §9, a new case of the same rule joins that existing test rather than getting a new method, so I added three fields to it instead of writing a new test:

- `NegativeCases.nullCheckedInTernaryCondition` — `#{someBean != null ? someBean.value : 'default'}`, the exact shape from the bug report; must **not** be flagged.
- `NegativeCases.reversedNullCheckedInTernaryCondition` — `#{someBean == null ? 'default' : someBean.value}`; covers the other side of the regex's alternation (`null` before the operator, and the `==` form), so both branches of `NULL_COMPARISON_PATTERN` are exercised, not just the one from the issue.
- `PositiveCases.nullStillReachableBesideNullCheck` — `#{someBean != null ? null : 'default'}`, the case the commit message itself calls out as still needing to be flagged. This is the control that matters most: it's the case where stripping the comparison text could plausibly have also swallowed the real `null` literal if the regex anchoring were off, and it proves it doesn't.

I verified these aren't change detectors: I built a disposable worktree at the parent commit (`HEAD~1`, before the fix), copied over just the edited test file, and ran it there — it fails with exactly the false-positive symptom the PR describes (`NegativeCases.java:13` and `:15` flagged as "unexpected error"), and `PositiveCases.java:12` still correctly flags on both commits. Then I removed the worktree. On `HEAD`, `./gradlew :nullaway:test --tests "com.uber.nullaway.FrameworkTests"` and `./gradlew :nullaway:buildWithNullAway` both pass. No production code was touched, and nothing is committed.

## One thing I'm proposing, not doing

`AGENTS.md`/`CLAUDE.md` names no test stack line (§0), so I'm not editing either file. If you want one, the natural line for this repo would be something like: *"Tests: JUnit 4 engine; `com.google.errorprone.CompilationTestHelper` as both engine and assertions — one `doTest()` call reports every `// BUG: Diagnostic contains:` mismatch across all added sources, naming each by file and line."* That would save the next contributor from having to re-derive this the way I just did. Happy to add it if you agree.
