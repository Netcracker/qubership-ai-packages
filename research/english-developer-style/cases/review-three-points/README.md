# Case: a review comment with three points

The input is one review comment on a pull request that makes three points: the new test duplicates an existing one, the
new exception could break callers, and a question about a subclass. The author agrees with nothing outright, disputes
the first two with evidence, and answers the third from the code. The case checks that the 2.2.0 module, which limits
sections, headings, and restatement to a comment with several points, still produces them here.

## Skill parts

- `SKILL.md`: §7 (Review replies)

## Checks

1. **A heading per point** (`heading_per_point`). Three headings.
2. **Each section opens with the reviewer's sentence, in the reviewer's order** (`each_point_quoted_in_order`).
3. **Quotes are verbatim** (`quotes_verbatim`). Every quoted line is a substring of the comment.
4. **No count of the points** (`no_count_of_points`). `your three points` is a claim the reviewer has to check.
5. **What holds comes first** (`concedes_before_dispute`, read). The `setFetchSize(-1)` section says that the old code
   allowed the call before it says why the exception stays.
6. **The test question is asked** (`asks_test_decision`, read). The test section asks whether to add the negative case
   to `StatementTest.testSetFetchSize` too.
7. **Length** (`at_most_400_words`).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `0f6d7512`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

| Run | Headings (1) | Quoted in order (2) | Verbatim (3) | No count (4) | Holds first (5) | Asks (6) | Words (7) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | passes | passes | passes | 292, 320 |
| Sonnet r1, r2 | passes | passes | passes | passes | passes | r2 fails: an offer, no question | 331, 312 |
| Opus baseline r1, r2 | passes | passes | passes | r2 fails: "three points" | passes | passes | 328, 351 |
| Sonnet baseline r1, r2 | passes | r2 fails: headings paraphrase, no blockquote | r2 fails: an inline quote with `"` turned into `'` | passes | passes | passes | 329, 275 |

Sonnet r2 ends its test section on `If you want the negative case in testSetFetchSize as well, I'll add it there too.`,
an offer where the module asks for a question. A run on an earlier draft of 2.2.0 did the same, so Sonnet offered in two
of four runs; both Sonnet baselines asked. The rule that asks for a question did not change in 2.2.0. `quotes_verbatim`
reads block quotes only, so the altered inline quote of the Sonnet baseline r2 is a reading.
