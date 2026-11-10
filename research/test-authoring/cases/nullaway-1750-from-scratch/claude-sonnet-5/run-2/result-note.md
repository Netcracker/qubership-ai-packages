Clean, minimal, no production changes, nothing committed.

---

**Message for the PR author:**

The fix had no tests, so I added three cases to the existing `springValueFieldTest` in `FrameworkTests.java`, in the same `NegativeCases`/`PositiveCases` shape the file already uses:

- `NegativeCases.nullCheckInTernaryCondition` — `#{someBean != null ? someBean.value : 'default'}`, the exact false positive from the PR description. I confirmed it's red on the parent commit (`bbceff5`): the old `SpringHandler` flags it as `@NonNull field 'nullCheckInTernaryCondition' not initialized`, and green with your fix.
- `NegativeCases.reversedNullCheckInTernaryCondition` — `#{null == someBean ? 'default' : someBean.value}`, exercising the second alternation branch of `NULL_COMPARISON_PATTERN` (`null` on the left, `==` instead of `!=`). Also red on the base commit, green after.
- `PositiveCases.ternaryNullBranchDespiteNullCheck` — `#{someBean != null ? null : 'default'}`, the control from your own PR description: the comparison is stripped, but `null` is still the branch value, so the field must still be flagged. This one was already correctly flagged on the base commit too (not a false negative you introduced), but it's the case that proves the fix didn't overreach and swallow genuine null-producing expressions.

All three live in the same compilation/`doTest()` call as the existing cases, matching the file's convention of many fields sharing one act with per-field `BUG` markers.

What I did not add, and why: a case combining `==`/`!=` on both sides isn't warranted — the regex's `[!=]=` character class treats both operators identically, so testing one operator per alternation branch (which I did) already exercises both branches without combinatorics for no added signal. I didn't add a case for `null` appearing as a bare identifier elsewhere in the expression (e.g. a variable literally named `nullable`) since that's unchanged, pre-existing `\bnull\b` word-boundary behavior, not something this diff touches.

Ran `:nullaway:test` (full module, green) and `:nullaway:buildWithNullAway` (green).
