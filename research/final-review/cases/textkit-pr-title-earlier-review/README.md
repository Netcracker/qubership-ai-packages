# Case: review a docstring commit under a pull request whose title an earlier commit made false

The branch `fix/page-count-earlier` carries the three commits of `fix/page-count-stale`, the third of which dropped the
`per_page` check from `page()` and was pushed without an edit of the title or the description, and a fourth commit, the
change under review, that adds a sentence to the docstring of `page_count()`. The caller hands over the title and the
description as they stand and the start commit `669de41`.

The change's own diff touches one docstring; the diff from the start commit no longer touches `page()`. The paragraph
reads the text against the second.

## Checks

Grade each by reading `result.md`.

1. **The title.** As check 1 of `textkit-pr-title-stale-review`.
2. **The description.** As check 2 of `textkit-pr-title-stale-review`.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` (the commit that drops the check from `page()`), and `96189d48650cbcfb01fc787a8a701b5a980295ed` (the docstring sentence). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title, description, and start commit as the trigger now asks a caller to. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-earlier-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-earlier-review claude-opus-5-5 pr-9
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
| Opus | `base-1` | pass | pass | 880 | 0.53 |
| Opus | `base-2` | pass | pass | 899 | 0.43 |
| Opus | `pr-1` | pass | pass | 923 | 0.57 |
| Opus | `pr-2` | pass | pass | 971 | 0.56 |
| Sonnet | `base-1` | pass | pass | 1020 | 0.33 |
| Sonnet | `base-2` | pass | pass | 954 | 0.13 |
| Sonnet | `pr-1` | pass | pass | 1087 | 0.32 |
| Sonnet | `pr-2` | pass | pass | 1063 | 0.35 |

- Every run files the title and the second paragraph against the diff from `669de41`, although the change under review
  touches one docstring.
- The tree before this change files the title and the description in all four runs too (Opus `base-1`, `result.md:20`):
  once the text is handed over, item 2 already reads it as a set of claimed cases.
