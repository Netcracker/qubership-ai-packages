# Case: review a commit whose writer hands over a new description and no new title

The input of `textkit-pr-title-stale-review`, with one addition to the prompt: the writer hands over the description it
will set after the push, which drops the paragraph about `page()` and adds a Scope sentence. It drafted no new title. On
the platform, the title and the description still announce the check in `page()`.

The §1 input lets the draft take the place of the platform's description and leaves the platform's title in force. A
reviewer that ignores the draft files the description; one that applies the draft to both parts files nothing.

## Checks

Grade each by reading `result.md`.

1. **The title.** Pass: a substantive finding that the title, which has no draft, names the check in `page()`, with a
   request for a new title.
2. **The description.** Pass: no finding that the description is stale or has to be replaced, neither on the draft nor
   on the platform paragraph the draft replaces. A finding on what the draft's Scope sentence leaves out is a finding of
   item 3 and does not count. Partial: a finding that names the platform's paragraph while saying the draft replaces it.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head`, `pr-target`, `gh/pr-view.json` | As in `textkit-pr-title-stale-review`. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-draft-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-draft-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `4888ebd7` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in one clause of the fallback, the remote-tracking ref rather
than `baseRefOid`, which this input cannot reach since the two are one commit here; in the wording of two sentences; and
in clauses on a lookup the caller forbids and on a tip the writer names, which these prompts do not reach. Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | 1088 | 0.45 |
| Opus | `base-2` | pass | pass | 974 | 0.53 |
| Opus | `pr-1` | pass | pass | 1266 | 0.62 |
| Opus | `pr-2` | pass | pass | 1112 | 0.55 |
| Sonnet | `base-1` | pass | pass | 1104 | 0.36 |
| Sonnet | `base-2` | pass | partial | 1159 | 0.29 |
| Sonnet | `pr-1` | pass | pass | 997 | 0.18 |
| Sonnet | `pr-2` | pass | pass | 778 | 0.14 |

- Every run files the title, which has no draft. Sonnet `base-2` also asks that "the new description must replace the
  whole body" of the platform's text, the partial; the `pr` runs read the draft in place of that body (Sonnet `pr-1`:
  "The writer's drafted description was read in place of the platform's body").
- Check 2 counts only a finding that the description is stale or must be replaced. Findings on the content of the
  draft's Scope sentence, which Opus `base-1` and `base-2` and Opus `pr-1` make (a negative `per_page` it leaves
  unnamed), are findings of item 3 and do not count.
