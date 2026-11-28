# Case: review a commit that drops half of its pull request's title, with the pull request's text and no start

The input of `textkit-pr-title-stale-review`, with the start left out. The title and the second paragraph of the
description say that `page()` rejects a `per_page` below 1, and the tree under review has no such check, so they are
false from any start. The sentence about `page_count(11, 5)` holds in that tree. `textkit-pr-text-nostart-review` is the
input where the text is true and the start is missing.

## Checks

Grade each by reading `result.md`.

1. **The title.** As check 1 of `textkit-pr-title-stale-review`.
2. **The description.** As check 2 of `textkit-pr-title-stale-review`.
3. **The sentence that holds.** As check 3 of `textkit-pr-title-stale-review`.
4. **The missing start.** Pass: the report says that the start was not handed over, or asks for it.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, and the base and head of that case. |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title and description, and no start. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-nostart-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-nostart-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `0994d670` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `f99ddfd4` differs from `0994d670` only in wording: it calls the commit the diff starts
from the merge base throughout and restores two relative pronouns, so the results stand for it. Opus and Sonnet, two
runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | 3 holds | 4 the missing start | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | pass | fail | 1140 | 0.45 |
| Opus | `base-2` | pass | pass | pass | fail | 1226 | 0.41 |
| Opus | `pr-1` | pass | pass | pass | pass | 1218 | 0.36 |
| Opus | `pr-2` | pass | pass | pass | pass | 1343 | 0.83 |
| Sonnet | `base-1` | pass | pass | pass | fail | 1253 | 0.33 |
| Sonnet | `base-2` | pass | pass | pass | fail | 1339 | 0.33 |
| Sonnet | `pr-1` | pass | pass | pass | pass | 1162 | 0.34 |
| Sonnet | `pr-2` | pass | pass | pass | pass | 1051 | 0.27 |

- **Both trees file the text.** Every run files the title and the second paragraph of the description, which the tree
  under review contradicts (Sonnet `pr-1`: "the tree has no such check", `result.md:91`), and none files the sentence
  about `page_count(11, 5)`. Every `pr` run says the start was missing and that it files only what is false whatever the
  start (Opus `pr-1`, `result.md:5`).
