# Case: review an uncommitted addition that the commit message claims and the pull request does not

The branch `fix/page-count-holds` at its first commit, the `page_count()` fix, whose pull request names that fix and
nothing else. The change under review is uncommitted: `worktree/` adds a public `page_range()` to
`src/textkit/paginate.py` and a new, untracked `src/textkit/cli.py` with a `textkit-pages` command. The prompt gives the
commit message the writer will use, which claims both.

Before the paragraph, item *Claimed cases covered* reads the hunks against the commit message, which claims them. The
paragraph reads the diff of the pull request after the push against the title and the description, which claim neither,
and counts the untracked file as part of that diff.

## Checks

Grade each by reading `result.md`.

1. **The new function.** Pass: a substantive finding that the pull request's title or description does not claim
   `page_range()`, with a request for a sentence that claims it or the hunk moved to a change of its own.
2. **The untracked file.** Pass: the same for `src/textkit/cli.py` and its command.
3. **No claim on the fix.** Pass: no finding on the description's sentence about `page_count(11, 5)`.

## Skill parts

- `final-review`: `SKILL.md` §1 (the input of the pull request's title and description) and §2 item *Claimed cases
  covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, and `5c64077d1856673073ac5efa507247712a712894` twice: the change is not committed. |
| `worktree/` | The edit of `src/textkit/paginate.py` and the new `src/textkit/cli.py`, which `run-review-case.sh` copies over the checkout. |
| `pr-target`, `gh/pr-view.json` | `main` at `669de41a`, and the title and description of the pull request, which name the `page_count()` fix alone. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<gh>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before the paragraph; `pr-<n>` ran it with the paragraph. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before the paragraph (`origin/main` at
`64435a9`), the second the working copy. Use a label that no committed run has: the script replaces the results of a
label it is given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-omitted-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-omitted-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `4888ebd7` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `ac12adbd` differs from it in one clause of the fallback, the remote-tracking ref rather
than `baseRefOid`, which this input cannot reach since the two are one commit here; in the wording of two sentences; and
in clauses on a lookup the caller forbids and on a tip the writer names, which these prompts do not reach. Opus and
Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 new function | 2 untracked file | 3 no claim on the fix | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | partial | partial | pass | 1223 | 0.42 |
| Opus | `base-2` | pass | pass | pass | 1277 | 0.52 |
| Opus | `pr-1` | pass | pass | pass | 1383 | 0.41 |
| Opus | `pr-2` | pass | pass | pass | 1530 | 0.59 |
| Sonnet | `base-1` | fail | fail | pass | 1503 | 0.36 |
| Sonnet | `base-2` | fail | fail | pass | 1193 | 0.33 |
| Sonnet | `pr-1` | pass | pass | pass | 1385 | 0.36 |
| Sonnet | `pr-2` | pass | pass | pass | 1484 | 0.37 |

- **The tree before the paragraph** reads the hunks against the commit message, which claims them: Sonnet `base-2`
  writes "Unclaimed hunks: none. The `paginate.py` and `cli.py` changes are all covered by the commit message." Opus
  reads the saved description unasked, `base-1` as a taste note and `base-2` as a substantive finding.
- **Every `pr` run** files `page_range()` and `cli.py` as hunks the title and the description do not claim (Sonnet
  `pr-2`: "Once this change is pushed, the PR diff also adds `page_range` and `cli.py`").
