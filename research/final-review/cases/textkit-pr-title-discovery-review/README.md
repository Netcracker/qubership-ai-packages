# Case: review a commit whose pull request the reviewer has to find for itself

The input of `textkit-pr-title-stale-review` with an ordinary brief: the prompt names no pull request and no saved
output, and lets the reviewer run `gh`. `run-review-case.sh` puts a `gh` on the session's `PATH` that answers `gh pr
view` from `gh/pr-view.json` and fails every other command, as a session with no network would. The reviewer learns that
the branch has a pull request only by calling `gh pr view`, which only the §1 input asks it to do.

This is the input the other cases could not give: there, the prompt said where the saved output was, and the tree before
the paragraph read it unasked.

## Checks

Grade each by reading `result.md`.

1. **The title.** As check 1 of `textkit-pr-title-stale-review`. Only `gh pr view` can give the reviewer the title here,
   so a pass also shows that it found the pull request.
2. **The description.** As check 2 of `textkit-pr-title-stale-review`.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head`, `pr-target`, `gh/pr-view.json` | As in `textkit-pr-title-stale-review`. |
| `gh-stub` | Tells `run-review-case.sh` to put the stub `gh` on the session's `PATH`. The stub answers only the fields `gh/pr-view.json` holds; a request for another field, such as `number`, gets `unknown JSON field`. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-discovery-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-discovery-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `4888ebd7` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in one clause of the fallback, the remote-tracking ref rather
than `baseRefOid`, which this input cannot reach since the two are one commit here; in the wording of two sentences; and
in clauses on a lookup the caller forbids and on a tip the writer names, which these prompts do not reach. Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | fail | fail | 1053 | 0.42 |
| Opus | `base-2` | fail | fail | 946 | 0.43 |
| Opus | `pr-1` | pass | pass | 1311 | 0.50 |
| Opus | `pr-2` | pass | pass | 1291 | 0.50 |
| Sonnet | `base-1` | fail | fail | 1287 | 0.36 |
| Sonnet | `base-2` | fail | fail | 1017 | 0.34 |
| Sonnet | `pr-1` | pass | pass | 1320 | 0.36 |
| Sonnet | `pr-2` | pass | pass | 1241 | 0.35 |

- **The tree before the paragraph fails every check.** No `base` report mentions a pull request: nothing in that form
  asks for one, and nothing in the prompt points at it.
- **Every `pr` run calls `gh pr view`**, finds the open pull request, and files the title and the second paragraph
  against the diff from `669de41` (Sonnet `pr-2`: "`gh pr view` shows an OPEN PR against `main`"). All four give the new
  title.
