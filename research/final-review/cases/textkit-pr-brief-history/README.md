# Case: the writer opened the pull request earlier in the session and now briefs final-review

A case for the trigger. The session is the writer of `textkit-pr-title-stale-review`'s change, with final-review's
trigger in its system prompt. Its history says that it opened the pull request earlier, with the title and the
description it wrote then, and that the user then asked it to take the `per_page` check out again. Nothing in the last
step points at the pull request, and nothing in the prompt names the commit its diff starts from: the writer finds it
from the log, where its commits sit on `669de41`, or hands over the base branch by name. The session writes the brief it
would hand to final-review.

The shape of the failure the change answers: in qubership-authz-agent#292 the writer held the pull request's text from
earlier in a long session and handed the reviewer the diff and the task statement only.

## Checks

Grade each by reading `result.md`.

1. **The text.** Pass: the brief carries the pull request's title and description, quoted or by an exact reference to
   them.
2. **The start.** Pass: the brief names `669de41` as the commit the pull request's diff starts from. Partial: it names
   the start only through a branch, as in `main...HEAD` or `git merge-base origin/main HEAD`, which the reviewer's clone
   may not have.

## Skill parts

- `final-review`: the trigger, `.apm/instructions/final-review.instructions.md`; no part of `SKILL.md`

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | As in `textkit-pr-title-stale-review`. |
| `caller` | Tells `run-review-case.sh` to add the trigger, from the same revision as the skills, to the session's system prompt. |
| `prompt.md` | The writer's session so far, with `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran the trigger from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill and the trigger's blob. |

## How to run

From the repository root. The first command runs the trigger as it was before this change, the second the working copy.
Use a label that no committed run has: the script replaces the results of a label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-history claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-history claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran the trigger with this change (blob `bada4a13`) and final-review tree `f99ddfd4` (version 1.4.0), `base-<n>`
the trigger before it (blob `1d3f0a96`) and tree `ca8233fb` (version 1.3.0, `origin/main` at `64435a9`). Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 the text | 2 the start | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | partial | 435 | 0.08 |
| Opus | `base-2` | pass | partial | 432 | 0.08 |
| Opus | `pr-1` | pass | pass | 375 | 0.13 |
| Opus | `pr-2` | pass | pass | 367 | 0.11 |
| Sonnet | `base-1` | pass | partial | 431 | 0.04 |
| Sonnet | `base-2` | pass | partial | 563 | 0.04 |
| Sonnet | `pr-1` | pass | partial | 433 | 0.04 |
| Sonnet | `pr-2` | pass | partial | 472 | 0.04 |

- **The text.** With either trigger, every brief carries the title and the description: the history is enough to put the
  pull request in front of the writer. Sonnet `pr-1` hands over a title and a description it redrafted, which the new
  trigger allows (`result.md:17`).
- **The start.** Every `base` brief hands it over as the range `main...HEAD` (Opus `base-2`, `result.md:27`). With the
  new trigger, both Opus briefs name `669de41`, found as the commit the branch was built on because the clone has no
  `main` (Opus `pr-2`, `result.md:16`), and both Sonnet briefs hand over a `git merge-base` command (Sonnet `pr-2`:
  "`git merge-base main HEAD` (or `origin/main` if `main` is stale locally)", `result.md:21`). The case's clone has no
  `main` (`run-review-case.sh` fetches the head alone), so only a commit resolves there; where the local `main` or
  `origin/main` is the target's tip, every one of these forms gives `669de41`. So the case shows no difference between
  the triggers that would reach a reviewer in the writer's own checkout.
- The omission of the text itself, as in qubership-authz-agent#292, does not happen on this input with either trigger.
