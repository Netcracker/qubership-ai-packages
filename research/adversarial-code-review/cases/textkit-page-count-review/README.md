# Case: review a one-line fix with its test and an unclaimed typo

A case for `adversarial-code-review` on an input where the rule on unclaimed hunks is noise. The change is the one of
`research/final-review/cases/textkit-page-count-review`, fetched from the bundle there: one commit, `fix off-by-one in
page_count()`, with the fixed line, its regression test, and a typo fixed in `README.md` that the commit message does
not mention. The fix is correct and the test fails on the base commit.

At `925b910` the skill made every hunk that no sentence claims a `blocking` finding however small, and all four `base`
runs returned `REQUEST_CHANGES` for the typo alone.

## Checks

Grade each by reading `result.md`.

1. **The typo blocks nothing.** Pass: no finding on the `README.md` hunk. Partial: a `non-blocking` one. Fail: a
   `blocking` one. `grep -niE 'typo|Paginaton|README' result.md`
2. **The result.** Pass: `Result: APPROVE (0 blocking, 0 non-blocking)`, or `APPROVE` with a non-blocking finding that is
   not on the typo.
3. **Length.** Pass: at most 200 words (`wc -w result.md`). The `base` runs wrote 179 to 221, about half of it the typo
   finding.

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Intent and scope*; §Result

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The path of the bundle in the `final-review` case, relative to this directory, and the same two commits. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran tree `27ba4f1b` (commit `925b910`); `draft-<n>` tree `775e67de`, the first wording of the condition; `cond-<n>` tree `5a29ff5e`, the committed wording. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/textkit-page-count-review <model> <label> [<rev>]
```

## Results, 2026-10-31

Opus and Sonnet, two runs per arm, graded by reading `result.md`.

| Model | Arm | 1 typo | 2 result | 3 length | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base` | fail, fail | fail, fail | fail, pass | 221, 196 | 0.25, 0.21 |
| Opus | `draft` | pass, pass | pass, pass | fail, fail | 208, 265 | 0.22, 0.22 |
| Opus | `cond` | pass, pass | pass, pass | pass, pass | 165, 161 | 0.20, 0.21 |
| Sonnet | `base` | fail, fail | fail, fail | pass, pass | 179, 181 | 0.09, 0.09 |
| Sonnet | `draft` | pass, pass | pass, pass | pass, pass | 198, 165 | 0.09, 0.09 |
| Sonnet | `cond` | pass, pass | pass, pass | fail, fail | 262, 212 | 0.08, 0.09 |

Every `base` run returns `REQUEST_CHANGES (1 blocking, 0 non-blocking)` on the typo alone. Every later run returns
`APPROVE (0 blocking, 0 non-blocking)`. The `draft` wording kept a bullet on the unclaimed hunk in the review notes
(Opus `draft-2`: "the commit message does not mention the `README.md:3` change. It only fixes the spelling"); the
committed wording adds that such a hunk is not mentioned, and Opus drops it. Sonnet `cond` still names the typo in one
scope bullet and writes a longer list of review notes, which the skill's report template does not ask for; check 3
fails on those notes, not on a finding.

The committed tree `13ff7802` differs from `5a29ff5e` only by line wrapping.

Sonnet's output grew on this input although the typo finding is gone: 262 and 212 words in `cond` against 179 and 181 in
`base`, where about half of each `base` report was that finding. The extra words are a list of review notes
(correctness, other paths, scope, tests, coverage) that the report template does not ask for when there are no findings.
Opus fell from 221 and 196 to 165 and 161. The case covers a typo in prose, `README.md`, not one in a comment of a
source file.
