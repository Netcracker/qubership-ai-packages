# Case: the writer hands final-review the pull request's text and start

A case for the trigger, not the skill. The session is the writer of `textkit-pr-title-stale-review`'s change, with
final-review's trigger in its system prompt, as `apm compile` puts it into a consumer's `AGENTS.md`. The prompt gives
the task, says that the branch has an open pull request, and shows what `gh pr view` and `git merge-base` printed
earlier in the session. The session cannot start a subagent, so it writes the brief it would hand to final-review.

The pull request is in front of the writer here, so the case checks that the hand-over the trigger asks for is made, not
the input that failed: `textkit-pr-brief-history` leaves the pull request in the session history, as in
qubership-authz-agent#292.

## Checks

Grade each by reading `result.md`.

1. **The text.** Pass: the brief carries the pull request's title and description, quoted or by an exact reference to
   where they are.
2. **The start.** Pass: the brief names `669de41` as the commit the pull request's diff starts from.

## Skill parts

- `final-review`: the trigger, `.apm/instructions/final-review.instructions.md`; no part of `SKILL.md`

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | As in `textkit-pr-title-stale-review`. |
| `caller` | Tells `run-review-case.sh` to add the trigger, from the same revision as the skills, to the session's system prompt. |
| `prompt.md` | The writer's task, with `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran the trigger from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill and the trigger's blob. |

## How to run

From the repository root. The first command runs the trigger as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-caller claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-brief-caller claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran the trigger with this change (blob `bada4a13`) and final-review tree `f99ddfd4` (version 1.4.0), `base-<n>`
the trigger before it (blob `1d3f0a96`) and tree `ca8233fb` (version 1.3.0, `origin/main` at `64435a9`). Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 the text | 2 the start | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | 502 | 0.08 |
| Opus | `base-2` | pass | pass | 484 | 0.09 |
| Opus | `pr-1` | pass | pass | 480 | 0.11 |
| Opus | `pr-2` | pass | pass | 406 | 0.09 |
| Sonnet | `base-1` | pass | pass | 505 | 0.04 |
| Sonnet | `base-2` | pass | pass | 511 | 0.04 |
| Sonnet | `pr-1` | pass | pass | 540 | 0.05 |
| Sonnet | `pr-2` | pass | pass | 258 | 0.03 |

- **The case does not separate the triggers.** Every brief carries the title, the description, and `669de41`, which the
  prompt prints, with the trigger before this change as with the new one.
