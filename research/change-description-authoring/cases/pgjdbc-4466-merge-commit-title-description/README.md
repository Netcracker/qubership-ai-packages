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

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description: a break leads the description,
  reviewer-only content, the lead-in paragraph), §4, §5 (links in a commit body)
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
6. **Outcome lead-ins, not labels** (`no_plain_outcome_labels`). The description, which becomes the commit body, has no
   line that opens with `User-visible:` or `Not changed:`; its outcomes sit under `**User-visible changes.**`
   and `**Not changed.**`.
7. **Break lead-in first** (`break_lead_in_before_headings`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md): the new default breaks code that
   matches the old `application_name`, so the description opens with `**Breaking changes.**`.
8. **One line per outcome** (`outcome_lines_unwrapped`), as in the squash-default case.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | Every commit (2) | Fix-ups (3) | Title (4) | Body shape (5) | Verification in one sentence (5, read) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1 (`9fe02a7c`) | passes | passes | passes | passes | passes | passes: none |
| Opus r2 (`9fe02a7c`) | passes | passes | passes | passes | passes | passes: one sentence |
| Opus r1 (`f03479c0`) | passes | passes | passes | passes | passes | passes |
| Opus r2 (`f03479c0`) | passes | passes | passes | passes | passes | fails: two sentences |
| Haiku r1 | passes | fails: a separate test commit with no `#2404` | passes | passes | passes | passes: one sentence, with the server precondition after a semicolon |
| Haiku r2 | passes | passes | passes | passes | passes | passes |
| Opus baseline | fails | passes | passes | passes | fails | fails |
| Haiku baseline | fails | fails: the test commit has no `#2404` | passes | passes | fails | fails |
| `controls/as-pushed.md` | fails | fails | fails | fails | passes | passes |

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first two rows), graded by reading, and pass every
check, checks 6 to 8 included: both descriptions open with `**Breaking changes.**` and mark their outcomes with the bold
lead-ins, one line each. The re-run on `23b838fc` wrapped r1's outcome lines at 72 columns, which check 8 now catches.
The Opus results of `f03479c0` failed check 7, and r1 also failed check 6 with plain `User-visible:` and `Not changed:`
lines. Check 7 fails the Haiku results, both baselines, and the control; check 8 fails both Haiku results.
