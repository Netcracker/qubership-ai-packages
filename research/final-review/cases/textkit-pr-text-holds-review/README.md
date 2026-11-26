# Case: review a test added in answer to a review, under a pull request whose title and description still hold

The negative control of `textkit-pr-title-stale-review`. The repository is the same bundle, on the branch
`fix/page-count-holds`: the first commit fixes the off-by-one in `page_count()`, the second merges `main`, which has
since fixed a typo in the README and released 0.4.0, and the third, the change under review, adds a test for one item
that a reviewer asked for. The title and the description of the pull request name the `page_count()` fix, and a
`**Scope.**` paragraph says that the `per_page` check in `page()` is left to a later change. The merge and the third
commit leave all of it true.

The merge is not pushed yet: the pull request's `baseRefOid` is still `669de41`, where the branch started, while
`origin/main` stands for the tip a fetch would bring, `a65cf80`. A diff from the merge base with `baseRefOid` carries
the README typo and the version bump of `main`, and the bump would read as a hunk that no text claims; the diff from
the merge base with the tip carries neither.

On this input the paragraph *The pull request* of item *Claimed cases covered* has its condition met, an open pull
request, and nothing to report. A reviewer that applies it to every input asks for the test or the review round to be
mentioned in the description, files the version bump or the typo that came with the merge, rewords a title that is
correct, or reads the Scope sentence as a claim that the diff changes `page()`.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **No finding on the title or the description.** Pass: no finding, of any label, that asks to change the title or a
   sentence of the description. `grep -niE 'title|description' result.md`
2. **No record of the round.** Pass: no request to mention `test_page_count_single_item`, the review, or the merge in
   the description.
3. **The Scope sentence and the merge.** Pass: no finding on the `**Scope.**` paragraph, and none on the README typo
   or the `pyproject.toml` version that `main` brought in, which are not in the diff of the pull request.
   `grep -niE 'pyproject|0\.4\.0|version' result.md`

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, `38d3d04d9f3cd7d5267b6f77ed6351b712cc7d82` (the merge of `main`), and `cb32362b8967080fee8fa44406fed5c4a0a4659c` (the added test). |
| `pr-target`, `gh/pr-view.json` | `main` at `a65cf808`, the tip a fetch would bring, which `run-review-case.sh` sets as `origin/main`, and the title and description of the pull request, as `gh pr view --json state,title,body,baseRefName,baseRefOid` prints them, with `baseRefOid` at `669de41a`. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. It does not say that the branch has a pull request: it says that gh cannot reach GitHub, and that where a skill asks for a gh command, its saved output is under `<gh>`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, once per model and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-holds-review <model> <label> [<rev>]
```

## Results, 2026-11-26

`pr-<n>` ran final-review tree `2a8a0411` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0). Opus and Sonnet,
two runs each, graded by reading `result.md`.

| Model | Run | 1 no finding | 2 no record | 3 Scope and merge | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | pass | 852 | 0.44 |
| Opus | `base-2` | pass | pass | pass | 751 | 0.37 |
| Opus | `pr-1` | pass | pass | pass | 797 | 0.41 |
| Opus | `pr-2` | pass | pass | pass | 777 | 0.46 |
| Sonnet | `base-1` | pass | pass | pass | 926 | 0.26 |
| Sonnet | `base-2` | pass | pass | pass | 820 | 0.25 |
| Sonnet | `pr-1` | pass | pass | pass | 771 | 0.16 |
| Sonnet | `pr-2` | pass | pass | pass | 813 | 0.28 |

- Every `pr` run compares the text with the diff from `a65cf80`, the remote-tracking copy that is newer than
  `baseRefOid`, and says so (Opus `pr-1`: "the PR diff uses the remote-tracking `origin/main`, which is newer than the
  recorded `baseRefOid`"). Sonnet `pr-2` adds that against `baseRefOid` "the README typo and the 0.4.0 version bump
  would appear". No run files the bump, the typo, the Scope sentence, or the title, and none asks to record the review.
- The `base` runs pass because they read only the change's diff; Sonnet `base-1` reads the saved description and takes
  the Scope sentence as the reason `page()` is left alone.
- The paragraph adds no length: the `pr` reports run 771 to 813 words against 751 to 926 for `base`.
