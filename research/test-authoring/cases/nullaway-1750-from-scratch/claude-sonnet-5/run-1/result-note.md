Only the test file is touched, nothing is committed, as requested.

## Summary

The last commit (`7842aa5`) changed `SpringHandler.containsNullSpELExpression` but added no tests. I found the existing test of this exact rule — `FrameworkTests.springValueFieldTest` — which already bundles multiple `@Value`/SpEL partitions into one `NegativeCases`/`PositiveCases` compilation (the harness, Error Prone's `CompilationTestHelper`, reports every mismatch in one compile and names each by source line), so per the skill's §9 the new cases join that test rather than starting a new one.

Added to `NegativeCases` (no diagnostic expected — this is the bug being fixed): four fields covering the two regex alternatives (`null` after the operator / `null` before it) crossed with both operators (`!=`, `==`):
- `#{someBean != null ? someBean.value : 'default'}` — the exact repro from the bug report
- `#{someBean == null ? 'default' : someBean.value}`
- `#{null != someBean ? someBean.value : 'default'}`
- `#{null == someBean ? 'default' : someBean.value}`

Added to `PositiveCases` (diagnostic still expected): `#{someBean != null ? null : 'default'}`, which proves the fix's comparison-stripping doesn't also swallow a genuine null-producing branch — this was explicitly called out in the fix's own commit message as behavior that must be preserved.

I verified these are real regression tests per the skill's §1: with the production fix reverted to the parent commit, all four negative cases fail with the exact false-positive warning the bug report describes; with the fix restored, the whole suite (and `buildWithNullAway`) is green.

One thing I considered but didn't add: testing a SpEL expression where `null` legitimately appears in a comparison *and* also as a plain standalone token elsewhere unrelated to the ternary result (e.g. a third operand) — I judged this redundant with the `ternaryStillReturnsNullDespiteNullCheck` case already added, since both exercise "stripping doesn't remove a real null occurrence," so I left it out rather than pad the suite.
