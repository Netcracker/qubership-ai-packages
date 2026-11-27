# Case: review under a pull request whose remote-tracking base is older than the fetched tip

The input of `textkit-pr-text-holds-review`, with one difference: `origin` is the case's bundle, so a fetch of `main`
brings `a65cf80`, the tip after the README typo fix and the 0.4.0 release, while `refs/remotes/origin/main` stays at
`669de41`, where the branch started. The merge of `main` into the branch is not pushed yet.

The paragraph *The pull request* of item *Claimed cases covered* takes the tip fetched now and falls back to the
remote-tracking ref only where the fetch fails. A reviewer that takes the remote-tracking ref here reads the typo and
the version bump as part of the pull request's diff, and the bump as a hunk that no text claims.

## Checks

Grade each by reading `result.md`.

1. **No finding on the title, the description, the typo, or the version bump.** As checks 1 and 3 of
   `textkit-pr-text-holds-review`.
2. **The fetched tip.** Pass: the report says that it fetched `main` and that the diff starts at the merge base with
   `a65cf80`, not with the remote-tracking `669de41`.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head`, `prompt.md`, `gh/pr-view.json` | As in `textkit-pr-text-holds-review`. |
| `pr-target` | `main` at `669de41a`, which `run-review-case.sh` sets as `origin/main`: older than the tip a fetch brings. |
| `remote` | Tells `run-review-case.sh` to add the bundle as the remote `origin`, so that `git fetch --refmap= origin main` brings `a65cf808`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-fetched-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-fetched-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `5d66cacc` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in two clauses, on a forbidden lookup and on a tip the writer
names, which this input does not reach. Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 no finding | 2 fetched tip | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | fail | 989 | 0.72 |
| Opus | `base-2` | pass | fail | 1002 | 0.50 |
| Opus | `pr-1` | pass | pass | 937 | 0.46 |
| Opus | `pr-2` | pass | pass | 1066 | 0.71 |
| Sonnet | `base-1` | pass | fail | 1144 | 0.26 |
| Sonnet | `base-2` | pass | fail | 798 | 0.26 |
| Sonnet | `pr-1` | pass | fail | 1097 | 0.31 |
| Sonnet | `pr-2` | pass | pass | 1075 | 0.22 |

- Three of four `pr` runs fetch `main` with `git fetch --refmap= origin main`, start the diff at `a65cf80`, and say that
  the remote-tracking `origin/main` is stale at `669de41` (Opus `pr-1`, `result.md:17`). No `base` run compares the text
  with a diff of the pull request.
- Sonnet `pr-1` does not try the fetch: it reads the prompt's "There is no network" as covering git, takes the
  remote-tracking `669de41`, and then judges the typo and the version bump as part of the merge of `main` rather than of
  the pull request, so it files nothing (`result.md:10` and `:28`).
