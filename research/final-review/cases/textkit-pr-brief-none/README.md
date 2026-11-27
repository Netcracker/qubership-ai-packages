# Case: the writer briefs final-review on a branch with no pull request

The quiet input for the trigger: the history of `textkit-pr-brief-history`, except that the user asked the writer not to
push or open a pull request yet. The trigger asks for a pull request's text only where the change goes into an open one,
so the brief has none to give.

## Checks

Grade each by reading `result.md`.

1. **No pull request.** Pass: the brief hands over no pull request title, description, or start, and invents none; a
   sentence that there is no pull request passes.

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

From the repository root. The first command runs the trigger as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-none claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-none claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran the trigger with this change (blob `bada4a13`) and final-review tree `f99ddfd4` (version 1.4.0), `base-<n>`
the trigger before it (blob `1d3f0a96`) and tree `ca8233fb` (version 1.3.0, `origin/main` at `64435a9`). Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 no pull request | Words | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | 379 | 0.11 |
| Opus | `base-2` | pass | 356 | 0.11 |
| Opus | `pr-1` | pass | 361 | 0.14 |
| Opus | `pr-2` | pass | 331 | 0.11 |
| Sonnet | `base-1` | pass | 445 | 0.04 |
| Sonnet | `base-2` | pass | 458 | 0.04 |
| Sonnet | `pr-1` | pass | 356 | 0.04 |
| Sonnet | `pr-2` | pass | 352 | 0.04 |

- No brief hands over or invents a title, a description, or a merge base for a pull request; each says there is none
  (Sonnet `pr-2`: "There is no pull request yet, so there is no title or description", `result.md:16`).
- One `base` brief and all four `pr` briefs also point the reviewer at the whole branch from the commit it started on
  (Opus `base-1`, `result.md:10`; Sonnet `pr-1`, `result.md:20`). Nothing is pushed, so the whole branch is the change,
  and the check does not count it.
