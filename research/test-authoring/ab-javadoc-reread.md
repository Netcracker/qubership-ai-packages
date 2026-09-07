# A/B trial: does a "re-read the comment when the code changes" rule change what the model does?

Run on 2026-09-06 after the [PR #4404 trial](ab-pr4404.md), where three of four cells appended a sentence under the
summary line of `PGbytea.toPGLiteral` and left the summary itself promising the plain literal form, which the pull
request's reviewer had flagged. The question: is that a blind spot a rule would close, or a judgment the model makes
on purpose?

## Setup

Four headless Opus sessions in detached worktrees at the same base commit, with `javadoc-authoring` and
`english-developer-style` installed and `test-authoring` left out. Two tasks, each "make the code change that fixes the
problem; do not write tests; commit": the `PGbytea.toPGLiteral` fix of PR #4404 and the `quoteAndCast` fix of PR #4405.
Two arms. Arm A had the skill as it stands. Arm B had the same skill plus a new section, "When the code under a
comment changes": re-read every sentence against the new body, the summary first; the usual failure is a paragraph
appended below a summary the change made false; three places that go stale unnoticed (a list of supported inputs, a
deprecated sibling that hardcodes the old behavior, the `@return` or `@throws` line), plus a checklist item and a
trigger sentence that loads the skill when a documented member's behavior changes even if no comment is edited. The
report asked each session to list every comment it changed or deliberately left, with the reason.

## Results

| Cell | Fix | `toPGLiteral` summary line | Input list | Deprecated overload | `quoteAndCast` Javadoc | Cost | Turns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A, 4404 | shared helper, all four branches | kept; one sentence appended after it | not updated | left, with the reason stated | – | $2.00 | 21 |
| B, 4404 | shared helper, all four branches | kept; one sentence appended after it | not updated | left, with the reason stated | – | $2.86 | 34 |
| A, 4405 | `E` prefix, inline comment | – | – | – | untouched; "wraps it in single quotes" defended as still true | $2.10 | 21 |
| B, 4405 | `E` prefix, inline comment | – | – | – | typo fixed; the example defended as the default-setting output | $2.61 | 30 |

Both arms loaded `javadoc-authoring` on their own in every cell, because every cell edited a comment, so the trigger
extension never had a chance to matter. Both arms re-read the surrounding comments: every report lists the deprecated
overload, the validation comment, the `bytea` comment in `SimpleParameterList.toString`, and the escaping comment in
`Utils`, each with a sentence on why it still holds. The one comment the reviewer flagged was kept in all four cells,
and kept on purpose: "the summary described one form and now there are two, so the second sentence pays for itself"
(B, 4404), and "`E'…'` is also wrapped in single quotes" (A, 4405). The rule in arm B cost 40 percent more and changed
no output.

## Reading

The append-below-the-summary pattern is not a blind spot. The models read the summary, judged it true because it
says "like" and gives an example, and added the second form below. The reviewer's objection is about the summary
table, where only the first sentence appears and a reader learns of one form: a completeness point under
`javadoc-authoring` §3 ("stands alone in the summary table"), not a truth point, and the arm-B rule was written as a
truth rule ("a summary the change made false"), so it did not bite. Whether a summary that names one of two forms as
an example is acceptable is a judgment the reviewer and the models make differently, and the pull request's own
reviewer said of the deprecated overload's identical summary "worth not fixing that one to match", so the line between
the two is thin.

Decision: the arm-B section is not adopted. What might be worth one checklist line in §3, untested here, is the
narrower case: a member that gained a second form or a second outcome, whose summary still shows one, should name
the rule that picks between them or both forms, because the summary table is all a reader of the table gets.
