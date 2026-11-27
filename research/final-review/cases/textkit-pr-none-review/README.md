# Case: review a branch that has no pull request yet

The input of `textkit-pr-title-discovery-review` on a branch named `fix/page-count-stale`, with no pull request: the
stub `gh` answers `gh pr view` with `no pull requests found for branch "fix/page-count-stale"` and exit 1, as gh does
for a branch before its first push. This is the most common input of the paragraph *The pull request* of item *Claimed
cases covered*, and the one where it has nothing to say: §1 counts that answer as no pull request, not as a lookup that
failed.

## Checks

Grade each by reading `result.md`.

1. **No pull request finding.** Pass: no finding on a pull request, its title, or its description.
2. **No failed lookup.** Pass: the report does not say that the pull request could not be read; a sentence that the
   branch has no pull request passes.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description)
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head`, `prompt.md` | As in `textkit-pr-title-discovery-review`. |
| `gh-stub` | The stub `gh`; with no `gh/pr-view.json`, it answers `no pull requests found`. |
| `branch` | The branch the head is checked out on, which the stub names. |
| `<model>/<label>/…` | The outputs of one run. `pr-<n>` ran final-review with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, with the working copy. Use a label that no committed run has: the script replaces the results
of a label it is given again. The tree before the paragraph calls no `gh`, so this case has no `base` arm.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-none-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `ac12adbd` (version 1.4.0), the committed tree. Opus and Sonnet, two runs each, graded by
reading `result.md`.

| Model | Run | 1 no PR finding | 2 no failed lookup | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `pr-1` | pass | pass | 1123 | 0.64 |
| Opus | `pr-2` | pass | pass | 1006 | 0.45 |
| Sonnet | `pr-1` | pass | pass | 1177 | 0.35 |
| Sonnet | `pr-2` | pass | pass | 1044 | 0.34 |

- Every run quotes the answer and reads it as no pull request (Sonnet `pr-1`, `result.md:6`: "`gh pr view` returned `no
  pull requests found for branch "fix/page-count-stale"`, so there is none to read").
- Opus `pr-1` ends with a sentence that it "could not compare against a pull request target because there is no pull
  request" (`result.md:79`): it names the absence, not a failed lookup, so check 2 passes; it is one sentence the report
  did not need.
