# Case: review a commit whose writer hands over a new description and the current title

The input of `textkit-pr-title-stale-review`, except that the description the caller hands over is the one the writer
drafted to set after the push: it drops the paragraph about `page()` and adds a Scope sentence. The title is handed over
as it stands and still names the check in `page()`.

## Checks

Grade each by reading `result.md`.

1. **The title.** Pass: a substantive finding that the title names the check in `page()`, with a request for a new
   title.
2. **The description.** Pass: no finding that the description is stale or has to be replaced. A finding on what the
   draft's Scope sentence leaves out is a finding of item 3 and does not count.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | As in `textkit-pr-title-stale-review`. |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title, description, and start commit as the trigger now asks a caller to. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-draft-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-draft-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `67598690` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `f99ddfd4` differs from `67598690` in how it names and defines the commit the pull
request's diff starts from (the merge base of the target branch's tip and the commit to be pushed, which the base of the
change under review is only where the caller says so), in what happens where none is handed over or the repository does
not have it, and in wording; this prompt hands over that merge base, and the repository has it, so the `pr` results
stand for `f99ddfd4`. Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | 1122 | 0.40 |
| Opus | `base-2` | pass | pass | 1118 | 0.48 |
| Opus | `pr-1` | pass | pass | 943 | 0.49 |
| Opus | `pr-2` | pass | pass | 1128 | 0.54 |
| Sonnet | `base-1` | pass | pass | 1204 | 0.38 |
| Sonnet | `base-2` | pass | pass | 1307 | 0.27 |
| Sonnet | `pr-1` | pass | pass | 1115 | 0.35 |
| Sonnet | `pr-2` | pass | pass | 1025 | 0.34 |

- Every run files the title, which is handed over as it stands, and none files the drafted description, with the tree
  before this change as with the new one (Sonnet `base-2`, `result.md:11`).
