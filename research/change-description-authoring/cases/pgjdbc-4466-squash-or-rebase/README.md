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

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, the break lead, template
  headings and the Scope lead-in under them), §4
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
2. **Every commit stands alone** (`every_commit_full_with_issue`). Every commit the output keeps has a body of at least
   30 words that references `#2404`. Under rebase each one lands in `git log` with nothing appended.
3. **Fix-ups folded** (`fixups_folded`). No commit with the subject `add tests` or `Apply suggestion …` remains.
4. **The title is a subject** (`title_is_subject`).
5. **The template stays** (`template_headings_kept`), as in the squash-default case.
6. **Scope by lead-in under the template** (`scope_lead_in_under_template`), as in the squash-default case.
7. **Break lead-in ahead of the template** (`break_lead_in_before_headings`), as in the squash-default case.
8. **One line per outcome** (`outcome_lines_unwrapped`), as in the squash-default case.
9. **No outcome lead-in in the description** (`no_outcome_lead_ins_in_description`), as in the squash-default case.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Opus r1 and r2 were re-run on 2026-11-02 on tree `6efc3a3a`, graded by reading; both pass every check. Each opens the
description with a `**Breaking changes.**` paragraph ahead of the template's first heading and puts the gap in a
`**Scope.**` paragraph of its own: r2 before the template's checklist, r1 after it, under `### Changes to Existing
Features`. r2 keeps two of the three template headings and drops `### New Feature Submissions`; check 5 needs one. The
two runs on `044c6057` (see the git history) passed checks 1 to 6 and added a `### Breaking changes` heading the
template lacks, which fails check 7, as do the Haiku results, both baselines, and the control. The earlier Opus runs
(the `f03479c0` row below) added a `Scope` heading of their own and fail check 6, as do the Haiku results, the
baselines, and the control: no lead-in, or a heading that names Scope.

The rows below the first are runs of 2026-10-28 on tree `f03479c0` (branch `vs/cda-concise`), graded by reading; Haiku
at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. The Opus results of those runs
are in the git history; the committed `opus/result*.md` are the `6efc3a3a` re-runs.

| Run | Outcome (1) | Every commit (2) | Fix-ups (3) | Title (4) | Template (5) | Scope (6) | Break lead-in (7) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus r1, r2 (`9fe02a7c`) | passes | passes | passes | passes | passes | passes | passes |
| Opus r1, r2 (`6efc3a3a`) | passes | passes | passes | passes | passes | passes | passes |
| Opus r1, r2 (`f03479c0`) | passes | passes | passes | passes | passes | fails: a `Scope` heading | fails: `### Breaking changes` |
| Haiku r1 | passes | passes | passes | passes | passes | fails: `### Scope` | fails: `### Breaking changes` |
| Haiku r2 | passes | fails: a separate test commit with a short body and no `#2404` | passes | passes | passes | fails: `### Scope` | fails: `### Breaking changes` |
| Opus baseline | fails | passes | passes | passes | fails: dropped | fails | fails |
| Haiku baseline | fails | passes | passes | passes | fails: dropped | fails | fails |
| `controls/as-pushed.md` | fails | fails | fails | fails | fails | fails | fails |

The Haiku baseline's commit body ends with a paragraph on the tests after the `Closes #2404` trailer, which lands in
`git log` under rebase.

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first row), graded by reading, and pass every check,
check 8 included. Check 8 fails Haiku r2, which wraps its outcome lines. The re-run on `23b838fc` wrapped r1's outcome
lines at 72 columns, which check 8 now catches, and the one on `0d0fa5fa` put a lead-in on a paragraph of its own in
both results. Check 9 passes every committed result. The other rows stand for the trees they ran on.
