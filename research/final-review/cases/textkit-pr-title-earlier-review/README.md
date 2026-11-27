# Case: review a docstring commit under a pull request whose title an earlier commit made false

A variant of `textkit-pr-title-stale-review` in which the change under review did not make the pull request's text
false. The branch `fix/page-count-earlier` carries the three commits of `fix/page-count-stale`, the third of which
dropped the `per_page` check from `page()` and was pushed without an edit of the title or the description, and a fourth
commit, the change under review, that adds a sentence to the docstring of `page_count()`.

Item *Claimed cases covered* before the paragraph *The pull request* reads the claims of the change against the change's
own diff, `<base>..HEAD`, which here touches one docstring. The paragraph reads the title and the description against
the diff of the whole pull request, which no longer touches `page()`. The case was built as an input on which the two
trees could differ even when the reviewer reads the saved output of `gh pr view`; the results below show that they do
not.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **The title.** Pass: a substantive finding that the title names the `per_page` check in `page()`, which the diff of
   the pull request (`origin/main...HEAD`) does not make, and a request for a title without it. Partial: the same
   filed as taste, or a finding that names only the description. `grep -niE 'title' result.md`
2. **The description.** Pass: a substantive finding on the description's paragraph about `page(items, 1, 0)` and its
   `ValueError`, with a request to remove or rewrite it. Partial: the same filed as taste.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` (the commit that drops the check from `page()`), and `96189d48650cbcfb01fc787a8a701b5a980295ed` (the docstring sentence). |
| `pr-target`, `gh/pr-view.json` | `main` at `669de41a`, where the branch starts, which `run-review-case.sh` sets as `origin/main`, and the title and description of `textkit-pr-title-stale-review`, as `gh pr view --json state,title,body,baseRefName,baseRefOid` prints them. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. It does not say that the branch has a pull request: it says that gh cannot reach GitHub, and that where a skill asks for a gh command, its saved output is under `<gh>`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-earlier-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-title-earlier-review claude-opus-5-5 pr-9
```

## Results, 2026-11-26

`pr-1` and `pr-2` ran final-review tree `2a8a0411` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0,
`origin/main` at `64435a9`). Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | pass | pass | 936 | 0.64 |
| Opus | `base-2` | pass | pass | 947 | 0.41 |
| Opus | `pr-1` | pass | pass | 962 | 0.45 |
| Opus | `pr-2` | pass | pass | 785 | 0.43 |
| Sonnet | `base-1` | pass | pass | 1285 | 0.36 |
| Sonnet | `base-2` | pass | pass | 1055 | 0.35 |
| Sonnet | `pr-1` | pass | pass | 968 | 0.36 |
| Sonnet | `pr-2` | pass | pass | 943 | 0.34 |

- **The tree before the paragraph passes this input too.** Every `base` run reads `gh/pr-view.json`, checks the
  description's claim against the code at HEAD, and finds that `7f2560c` removed the check (Opus `base-2`: "Finding
  (substantive, outside the reviewed commit)"). Reading the code at HEAD reaches what the diff of the whole pull request
  would show.
- **What the paragraph changes.** Every `pr` run names the pull request's diff, `git diff 669de41 HEAD`, and three of
  four give the new title. Sonnet `pr-1` takes `baseRefOid` as the base and says that it "did not compare it with
  `origin/main`", which the paragraph asks for offline; here both are `669de41`, so its diff is the same.

## Results, 2026-11-27

`pr-<n>` ran final-review tree `4888ebd7` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in one clause of the fallback, the remote-tracking ref rather
than `baseRefOid`, which this input cannot reach since the two are one commit here; in the wording of two sentences; and
in clauses on a lookup the caller forbids and on a tip the writer names, which these prompts do not reach. Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 title | 2 description | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- |
| Opus | `pr-3` | pass | pass | 890 | 0.39 |
| Opus | `pr-4` | pass | pass | 771 | 0.38 |
| Sonnet | `pr-3` | pass | pass | 975 | 0.32 |
| Sonnet | `pr-4` | pass | pass | 1094 | 0.37 |

- On the newer tree, every run passes.
