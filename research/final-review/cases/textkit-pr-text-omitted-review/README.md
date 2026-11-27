# Case: review an uncommitted addition that the commit message claims and the pull request does not

The branch `fix/page-count-holds` at its first commit, the `page_count()` fix, whose pull request names that fix and
nothing else. The change under review is uncommitted: `worktree/` adds a public `page_range()` to
`src/textkit/paginate.py` and a new, untracked `src/textkit/cli.py` with a `textkit-pages` command. The prompt gives the
commit message the writer will use, which claims both, and the caller hands over the title, the description, and the
start commit `669de41`.

Before this change, item *Claimed cases covered* counted a hunk as claimed where the commit message claimed it. The
paragraph reads the pull request's diff against the title and the description alone.

## Checks

Grade each by reading `result.md`.

1. **The new function.** Pass: a substantive finding that the title or the description does not claim `page_range()`,
   with a request for a sentence that claims it or the hunk moved to a change of its own. Partial: the same filed as
   taste.
2. **The untracked file.** Pass: the same for `src/textkit/cli.py` and its command.
3. **No claim on the fix.** Pass: no finding on the description's sentence about `page_count(11, 5)`.

## Skill parts

- `final-review`: `SKILL.md` §1 (the pull request's title, description, and start, as the caller hands them over) and
  §2 item *Claimed cases covered*, the paragraph *The pull request*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The bundle in `textkit-pr-title-stale-review`, and `5c64077d1856673073ac5efa507247712a712894` twice: the change is not committed. |
| `worktree/` | The edit of `src/textkit/paginate.py` and the new `src/textkit/cli.py`, which `run-review-case.sh` copies over the checkout. |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. It hands over the pull request's title, description, and start commit as the trigger now asks a caller to. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran final-review from `origin/main` at `64435a9`, before this change; `pr-<n>` ran it with the change. `skill-tree` records the tree of each skill. |

## How to run

From the repository root. The first command runs final-review as it was before this change (`origin/main` at `64435a9`),
the second the working copy. Use a label that no committed run has: the script replaces the results of a label it is
given again.

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-omitted-review claude-opus-5-5 base-9 64435a981367155a6fc95a55f9901224323fad87
research/final-review/cases/run-review-case.sh research/final-review/cases/textkit-pr-text-omitted-review claude-opus-5-5 pr-9
```

## Results, 2026-11-27

`pr-<n>` ran final-review tree `67598690` (version 1.4.0), `base-<n>` tree `ca8233fb` (version 1.3.0, `origin/main` at
`64435a9`). The committed tree `f99ddfd4` differs from `67598690` in how it names and defines the commit the pull
request's diff starts from (the merge base of the target branch's tip and the commit to be pushed, which the base of the
change under review is only where the caller says so), in what happens where none is handed over or the repository does
not have it, and in wording; this prompt hands over that merge base, and the repository has it, so the `pr` results
stand for `f99ddfd4`. Opus and Sonnet, two runs each, graded by reading `result.md`.

| Model | Run | 1 new function | 2 untracked file | 3 no claim on the fix | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| Opus | `base-1` | partial | partial | pass | 1353 | 0.43 |
| Opus | `base-2` | pass | pass | pass | 1496 | 0.84 |
| Opus | `pr-1` | pass | pass | pass | 1624 | 0.61 |
| Opus | `pr-2` | pass | pass | pass | 1524 | 0.56 |
| Sonnet | `base-1` | pass | pass | pass | 1491 | 0.36 |
| Sonnet | `base-2` | pass | pass | pass | 1690 | 0.38 |
| Sonnet | `pr-1` | pass | pass | pass | 1455 | 0.33 |
| Sonnet | `pr-2` | pass | pass | pass | 1604 | 0.34 |

- **The tree before this change mostly passes too** once the text is handed over: three of four `base` runs file the
  title and the description as substantive for leaving out `page_range()` and the command, and Opus `base-1` files it as
  taste. The paragraph makes it substantive in all four `pr` runs.
- Every run also files the missing tests, the missing console-script entry, and the README; those are item 2 and 7
  findings on the change itself.
