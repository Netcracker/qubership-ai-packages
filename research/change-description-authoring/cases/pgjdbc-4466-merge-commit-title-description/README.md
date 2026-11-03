# Case: pgjdbc#4466 under merge commits that copy the description

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one merges with a merge commit whose message is the pull request title and description, as ghostty-org/ghostty
does for most pull requests (checked on 2026-10-20). Two rules apply at once: every branch commit lands behind the
merge commit and stands alone (§4 rule 1), and the description is the body that `git log --first-parent` shows
(rule 5). Neither the squash cases nor the rebase case combine them.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, reviewer-only content), §4,
  §5 (links in a commit body)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
2. **Every commit stands alone** (`every_commit_full_with_issue`), as in
   [`pgjdbc-4466-squash-or-rebase`](../pgjdbc-4466-squash-or-rebase/README.md).
3. **Fix-ups folded** (`fixups_folded`).
4. **The title is a subject** (`title_is_subject`).
5. **The description is a commit body** (`description_as_commit_body`), as in
   [`pgjdbc-4466-squash-title-description`](../pgjdbc-4466-squash-title-description/README.md).

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | Every commit (2) | Fix-ups (3) | Title (4) | Body shape (5) | Verification in one sentence (5, read) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1 | passes | passes | passes | passes | passes | passes |
| Opus r2 | passes | passes | passes | passes | passes | fails: two sentences |
| Haiku r1 | passes | fails: a separate test commit with no `#2404` | passes | passes | passes | passes: one sentence, with the server precondition after a semicolon |
| Haiku r2 | passes | passes | passes | passes | passes | passes |
| Opus baseline | fails | passes | passes | passes | fails | fails |
| Haiku baseline | fails | fails: the test commit has no `#2404` | passes | passes | fails | fails |
| `controls/as-pushed.md` | fails | fails | fails | fails | passes | passes |
