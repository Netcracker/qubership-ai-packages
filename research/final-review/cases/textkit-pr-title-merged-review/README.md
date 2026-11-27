# Case: review a commit on a branch whose pull request is merged

The input of `textkit-pr-title-stale-review`, with the saved state `MERGED` instead of `OPEN`. The §1 input reads a
state other than `OPEN` as no pull request, so the paragraph has nothing to read, however stale the text is.

## Checks

Grade each by reading `result.md`.

1. **No finding on the text.** Pass: no finding on the title or the description. The skill asks nothing more of the
   report here.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head`, `pr-target` | As in `textkit-pr-title-stale-review`. |
| `gh/pr-view.json` | The title and description of `textkit-pr-title-stale-review`, with `state` set to `MERGED`. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-merged-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-merged-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `4888ebd7` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in one clause of the fallback, the remote-tracking ref rather
than `baseRefOid`, which this input cannot reach since the two are one commit here; in the wording of two sentences; and
in clauses on a lookup the caller forbids and on a tip the writer names, which these prompts do not reach. Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 no finding on the text | Words | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | `base-1` | fail | 1160 | 0.40 |
| Opus | `base-2` | fail | 1301 | 0.46 |
| Opus | `pr-1` | pass | 1227 | 0.88 |
| Opus | `pr-2` | pass | 1099 | 0.54 |
| Sonnet | `base-1` | fail | 1215 | 0.34 |
| Sonnet | `base-2` | fail | 1179 | 0.35 |
| Sonnet | `pr-1` | pass | 989 | 0.36 |
| Sonnet | `pr-2` | pass | 1082 | 0.34 |

- **The tree before the paragraph** files the merged pull request's title and description as substantive in all four
  runs (Opus `base-2`: "The merged PR's title and body still promise the `ValueError`").
- **Every `pr` run** reads the state and stops there (Opus `pr-1`: "`pr-view.json` shows state `MERGED`, which the form
  treats as no open PR, so there was nothing to check").
