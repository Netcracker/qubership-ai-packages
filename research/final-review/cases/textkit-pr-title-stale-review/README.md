# Case: review a commit that drops half of an open pull request whose title still announces it

A regression case for `final-review` on a change whose caller hands over an open pull request's title, description, and
start commit, as the trigger asks. The repository is a small Python package made for this case: `main` adds
`page_count()` and `page()`, and the branch `fix/page-count-stale` carries three commits. The first fixes an off-by-one
in `page_count()`, the second makes `page()` raise `ValueError` for a `per_page` below 1, and the third, the change
under review, takes that check out again because a caller passes 0 on purpose.

The title and the description were written for the first two commits, so after the third they still announce the check
in `page()`, which the diff from the start commit `669de41` no longer makes.

## Checks

Grade each by reading `result.md`.

1. **The title.** Pass: a substantive finding that the title names the `per_page` check in `page()`, which the pull
   request's diff does not make, and a request for a title without it. Partial: the same filed as taste.
2. **The description.** Pass: a substantive finding on the paragraph about `page(items, 1, 0)` and its `ValueError`,
   with a request to remove or rewrite it. Partial: the same filed as taste.
3. **The sentence that holds.** Pass: no finding on the paragraph about `page_count(11, 5)`, which the diff still makes
   true.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `textkit-pr.bundle` | The repository: a git bundle of `main` (`a65cf808`: a README typo fix and the 0.4.0 release on top of `669de41a`) and the branches `fix/page-count-stale`, which starts from `669de41a`, `fix/page-count-holds`, and `fix/page-count-earlier`. Every other `textkit-pr-*` case reads it too. |
| `repo`, `base`, `head` | The bundle's path, `58d2c74752dcaf0d65f0367c94a777f630812768` (the commit that adds the check to `page()`), and `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` (the commit that drops it). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title, description, and start commit as the trigger now asks a caller to. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-stale-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-stale-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `67598690` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `f99ddfd4` differs from `67598690` in how it names and defines the commit the pull
request's diff starts from (the merge base of the target branch's tip and the commit to be pushed, which the base of the
change under review is only where the caller says so), in what happens where none is handed over or the repository does
not have it, and in wording; this prompt hands over that merge base, and the repository has it, so the `pr` results
stand for `f99ddfd4`. Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | 3 holds | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | pass | 1253 | 0.46 |
| Opus | `base-2` | pass | pass | pass | 1353 | 0.53 |
| Opus | `pr-1` | pass | pass | pass | 1081 | 0.43 |
| Opus | `pr-2` | pass | pass | pass | 1037 | 0.44 |
| Sonnet | `base-1` | pass | pass | pass | 1313 | 0.34 |
| Sonnet | `base-2` | pass | pass | pass | 1079 | 0.14 |
| Sonnet | `pr-1` | pass | pass | pass | 1226 | 0.29 |
| Sonnet | `pr-2` | pass | pass | pass | 1268 | 0.35 |

- **Both trees pass.** Once the caller hands over the title, the description, and the start commit, final-review before
  this change compares them with the branch and files the title and the second paragraph in every run. What carries the
  fix is the hand-over, which the trigger now asks for.
- The `pr` runs name the diff from `669de41` (Opus `pr-2`: "PR title and second paragraph claim a `per_page` check that
  the PR diff doesn't make").
