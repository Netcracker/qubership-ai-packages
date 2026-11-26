# Case: review a commit that drops half of an open pull request whose title still announces it

A regression case for `final-review` on a change whose branch has an open pull request. The repository is the small
Python package of `textkit-page-count-review`, made for this case: `main` is the commit that adds `page_count()`, and
the branch `fix/page-count-stale` carries three commits. The first fixes the off-by-one in `page_count()`, the second
makes `page()` raise `ValueError` for a `per_page` below 1, and the third, the change under review, reverts the second
because a caller passes 0 on purpose.

The pull request's title and description were written for the first two commits. After the third, the diff of the pull
request holds the `page_count()` fix alone, and both still announce the check in `page()`. The case tests the paragraph
*The pull request* of item *Claimed cases covered*, added after a pull request reached approval with a title that
named a change a later push had removed (`authz-agent-292-pr-title-review` is that input).

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **The title.** Pass: a substantive finding that the title names the `per_page` check in `page()`, which the diff of
   the pull request (`origin/main...HEAD`) no longer makes, and a request for a title without it. Partial: the same
   filed as taste. `grep -niE 'title' result.md`
2. **The description.** Pass: a substantive finding on the description's paragraph about `page(items, 1, 0)` and its
   `ValueError`, with a request to remove or rewrite it. Partial: the same filed as taste. `grep -niE
   'page\(items, 1, 0\)|description' result.md`
3. **The sentence that holds.** Pass: no finding on the paragraph about `page_count(11, 5)`, which the diff still
   makes true.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `textkit-pr.bundle` | The repository: a git bundle of `main` (`a65cf808`: a README typo fix and the 0.4.0 release on top of `669de41a`) and the branches `fix/page-count-stale`, which starts from `669de41a`, `fix/page-count-holds`, and `fix/page-count-earlier`. `textkit-pr-text-holds-review` and `textkit-pr-title-earlier-review` read it too. |
| `repo`, `base`, `head` | The bundle's path, `58d2c74752dcaf0d65f0367c94a777f630812768` (the commit that adds the check to `page()`), and `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` (the commit that drops it). |
| `pr-target`, `gh/pr-view.json` | `main` at `669de41a`, where the branch starts, which `run-review-case.sh` sets as `origin/main`, and the title and description the pull request carried for the first two commits, as `gh pr view --json state,title,body,baseRefName,baseRefOid` prints them. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. It does not say that the branch has a pull request: it says that gh cannot reach GitHub, and that where a skill asks for a gh command, its saved output is under `<gh>`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `named-base-1` and `named-pr-1` ran with an earlier prompt, which said that the branch was the head of an open pull request and named the file with its title and description; `listed-<n>` with a prompt that said `<gh>` held what gh printed for the branch. The `named-pr` and `listed-pr` runs ran earlier wordings of the paragraph, whose trees their `skill-tree` files record. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-stale-review <model> <label> [<rev>]
```

## Results, 2026-11-26

`pr-<n>` ran final-review tree `2a8a0411` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | 3 holds | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | pass | 938 | 0.55 |
| Opus | `base-2` | pass | pass | pass | 1135 | 0.40 |
| Opus | `pr-1` | pass | pass | pass | 1178 | 0.59 |
| Opus | `pr-2` | pass | pass | pass | 927 | 0.45 |
| Sonnet | `base-1` | pass | pass | pass | 1410 | 0.34 |
| Sonnet | `base-2` | pass | pass | pass | 1652 | 0.35 |
| Sonnet | `pr-1` | pass | pass | pass | 1293 | 0.15 |
| Sonnet | `pr-2` | pass | pass | pass | 1229 | 0.33 |

- **The tree before the paragraph passes too.** Its item *Claimed cases covered* already reads hunks against "the commit
  message or the description", and the prompt says where gh output is saved, so every `base` run reads `gh/pr-view.json`
  (Sonnet `base-1` reads it "as a second claim source") and files the title and the description as substantive. So do
  the earlier arms: `named-base-1` and `named-pr-1`, whose prompt said that the branch was the head of an open pull
  request, and `listed-base-1`, `listed-base-2`, `listed-pr-1`, and `listed-pr-2`, whose prompt said that `<gh>` held
  what gh printed for the branch. Once the text is within reach, Opus and Sonnet compare it with the branch with or
  without the paragraph.
- **The input where the old tree fails is not in this harness.** It is a reviewer whose brief names no pull request and
  whose gh answers when called, so that only the §1 input makes it call `gh pr view`. A stub `gh` on the case session's
  `PATH` was refused by the permission classifier of the agent session that ran the cases, not by `run-review-case.sh`.
  `textkit-pr-title-earlier-review` tried the other input that could tell the trees apart, a text made false by an
  earlier commit, and the old tree passes it as well.
- **What the checks catch.** An edit of the paragraph that stops the finding, such as a reading of the change's diff
  alone. They do not fail if the paragraph is removed, since the `base` runs pass.
- **What the paragraph changes.** Every `pr` run names the diff it compared the text with, from the merge base with
  `669de41` (Opus `pr-2`: "The PR diff `669de41..HEAD` only touches `page_count()`"), and every one gives the new title,
  "Count a partial last page in page_count()". The `base` runs compare the text with the branch and ask to drop the
  second half of the title.
- **Not run.** No case gives the reviewer a title or a description that the writer drafted, or a pull request whose
  state is not `OPEN`; the §1 sentences on both are read, not measured.
