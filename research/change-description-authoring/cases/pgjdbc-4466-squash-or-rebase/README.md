# Case: pgjdbc#4466 where squash and rebase are both used

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one is pgjdbc as it is: the classifier prints `merge 0 squash 3 plain 37`, and the maintainers squash or rebase
each pull request. §4 says to write for both: every commit that may land stands alone with the issue number, fix-up
commits are folded, the title is a subject, and the description is not shaped as a commit body, because neither method
copies it.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, template headings), §4
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
2. **Every commit stands alone** (`every_commit_full_with_issue`). Every commit the output keeps has a body of at least
   30 words that references `#2404`. Under rebase each one lands in `git log` with nothing appended.
3. **Fix-ups folded** (`fixups_folded`). No commit with the subject `add tests` or `Apply suggestion …` remains.
4. **The title is a subject** (`title_is_subject`).
5. **The template stays** (`template_headings_kept`), as in the squash-default case.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | Every commit (2) | Fix-ups (3) | Title (4) | Template (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes | passes | passes | passes |
| Haiku r1 | passes | passes | passes | passes | passes |
| Haiku r2 | passes | fails: a separate test commit with a short body and no `#2404` | passes | passes | passes |
| Opus baseline | fails | passes | passes | passes | fails: dropped |
| Haiku baseline | fails | passes | passes | passes | fails: dropped |
| `controls/as-pushed.md` | fails | fails | fails | fails | fails |

The Haiku baseline's commit body ends with a paragraph on the tests after the `Closes #2404` trailer, which lands in
`git log` under rebase.
