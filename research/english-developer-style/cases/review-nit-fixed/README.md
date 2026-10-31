# Case: a one-line nit the author fixed

The input is a review comment that points out a typo in an exception message, and the commit that fixed it. The case
is the negative control for §7 *Review replies*: before 2.2.0 the module asked for one section per point, each
restating the point, then the answer, then the evidence, and nothing in it said where a short reply ends.

## Skill parts

- `SKILL.md`: §7 (Review replies)

## Checks

1. **Short** (`at_most_15_words`). `Fixed in 3f9c2ab.` is the whole reply; a sentence that repeats the fix or thanks
   the reviewer is over the limit.
2. **No heading** (`no_heading`).
3. **No restatement** (`no_quote`). The reply sits under the comment it answers, so it does not quote it.
4. **Names the commit** (`names_commit`).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `0f6d7512`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

| Run | Short (1) | No heading (2) | No restatement (3) | Commit (4) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes (3 words) | passes | passes | passes |
| Sonnet r1, r2 | passes (3 words) | passes | passes | passes |
| Opus baseline r1, r2 | passes (10 words) | passes | passes | passes |
| Sonnet baseline r1, r2 | fails (16, 23 words) | passes | passes | passes |

Every baseline run added a sentence that repeats the fix ("The message now says "a fetch size"."), and Sonnet also
"Nothing else changed" and thanks.
