# Case: review a test added in answer to a review, with the pull request's text and no start

The input of `textkit-pr-text-holds-review`, with the start left out: the caller hands over the title and the
description of the open pull request and not the commit its diff starts from. The change under review is the third
commit alone, a test; the title and the description name the `page_count()` fix in the first commit. A reviewer that
takes the base of the change under review as the start reads the title against a diff that adds one test, and files it
as false. Every sentence of the text holds in the tree under review, so no claim here is false whatever the start;
`textkit-pr-title-nostart-review` is the input with such claims.

## Checks

Grade each by reading `result.md`.

1. **No finding on the title or the description.** Pass: no finding, of any label, that asks to change the title or a
   sentence of the description.
2. **The missing start.** Pass: the report says that the start was not handed over, or asks for it. Fail: it reads the
   text against a start it chose, such as `<base>`, without saying so.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | As in `textkit-pr-text-holds-review`. |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title and description, and no start. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-nostart-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-nostart-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `0994d670` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `f99ddfd4` differs from `0994d670` only in wording: it calls the commit the diff starts
from the merge base throughout and restores two relative pronouns, so the results stand for it. Opus and Sonnet, two
runs each, graded by reading `result.md`.

| Model | Run | 1 no finding | 2 the missing start | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | fail | 804 | 0.49 |
| Opus | `base-2` | pass | fail | 894 | 0.72 |
| Opus | `pr-1` | pass | pass | 745 | 0.55 |
| Opus | `pr-2` | pass | pass | 937 | 0.45 |
| Sonnet | `base-1` | pass | fail | 812 | 0.25 |
| Sonnet | `base-2` | pass | fail | 973 | 0.27 |
| Sonnet | `pr-1` | pass | pass | 828 | 0.28 |
| Sonnet | `pr-2` | pass | pass | 982 | 0.27 |

- **No run files the text.** The tree before this change reads the description's sentences as claimed cases of the
  change and finds them covered by tests outside its range (Sonnet `base-1`, `result.md:15`). Every `pr` run says the
  start is missing, files only what would be false whatever the start, and finds none (Opus `pr-1`, `result.md:11`).
- **The missing start.** No `base` run mentions a start: that tree has none to miss.
