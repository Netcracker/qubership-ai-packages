# Case: pgjdbc#4466 under a squash with the default message

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one is a squash merge with GitHub's default message: the classifier prints `merge 0 squash 40 plain 0`, and the
squash bodies are `* subject` bullets. The description is never copied, and the first commit carries the reason into
`git log`. The case is the negative control for `pgjdbc-4466-squash-title-description`: a writer that shapes every
description as a commit body drops the pull request template here, where it belongs.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description, the break lead, template
  headings and the Scope lead-in under them), §4
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`). The output carries a `User-visible:`
   label, a `**User-visible changes.**` lead-in, or a "User-visible changes" heading, and a line under it or under
   "Breaking changes" names the new default value and the condition (`ApplicationName` unset). No such line carries a
   SQLState, an exception class, or another error code: the outcome emits none. Question: does a line give the value,
   and does any line carry an identifier the outcome does not emit?
2. **The first commit carries the why** (`first_commit_full_with_issue`). The first surviving commit has a body that
   states the problem (which driver version a connection uses cannot be seen in `pg_stat_activity`) and references
   `#2404`. Under the default message the body of a multi-commit squash is the list of commit messages, so this body
   is what `git log` keeps.
3. **The title is a subject** (`title_is_subject`). `feat:` or another prefix, then a lowercase imperative verb, no
   trailing period.
4. **The template stays** (`template_headings_kept`). The description uses at least one of the template's headings.
   The description is not copied under this setting, so nothing argues for stripping the template, and §2 says a
   repository's template supplies the headings.
5. **Scope by lead-in under the template** (`scope_lead_in_under_template`). The template has no Scope heading, so
   the deliberate gap (the git sha and the JDK version left out of the default) sits in a paragraph that opens with
   `**Scope.**`, and the description adds no heading that names Scope.
6. **Break lead-in ahead of the template** (`break_lead_in_before_headings`). The new default breaks code that
   matches the old `application_name`, so the description opens with a paragraph that starts with
   `**Breaking changes.**`, ahead of the template's first heading, and adds no heading that names the break.
7. **One line per outcome** (`outcome_lines_unwrapped`). Each outcome is one line, however long, in the commit body and
   in the description wherever a lead-in introduces them, and no line under the lead-in continues the one above it: no
   indented continuation, no line that starts lowercase, and no line after one that ends mid-sentence. The body may wrap
   its other slots at 72 columns; an outcome wrapped there reads as two outcomes to the reader who greps for one.
8. **No outcome lead-in in the description** (`no_outcome_lead_ins_in_description`), as in
   [`pgjdbc-4367-breaks`](../pgjdbc-4367-breaks/README.md).

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it, with the real
pull request title and description. `controls/break-heading.md` is `opus/result.md` as run on tree `044c6057`
(2026-11-02), which put the breaks under a `### Breaking changes` heading the template lacks.

## Results

Tree `27b2445d` adds the `Implements:` and `Defers:` trailers to §2 (Scope), the §5 trailer table, and the §8
checklist, for a repository whose decision records number their rules. This input has no decision records, so the
change does not reach this case, and the results below stand for `27b2445d` as they stand for the tree before it.

Opus r1 and r2 were re-run on 2026-11-02 on tree `6efc3a3a`, graded by reading; both pass every check. Each opens the
description with a `**Breaking changes.**` paragraph ahead of the template's first heading, puts the gap in a
`**Scope.**` paragraph of its own before the template's checklist, and keeps all three template headings. The two runs
on `044c6057` (`controls/break-heading.md` is r1) passed checks 1 to 5 and added a `### Breaking changes` heading the
template lacks, which fails check 6, as do the Haiku results, both baselines, and `controls/as-pushed.md`. The earlier
Opus runs (the `f03479c0` row below) added a `Scope` heading of their own and fail check 5, as do the Haiku results, the
baselines, and the control: no lead-in, or a heading that names Scope.

The rows below the first are runs of 2026-10-28 on tree `f03479c0` (branch `vs/cda-concise`), graded by reading; Haiku
at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. The Opus results of those runs
are in the git history; the committed `opus/result*.md` are the `6efc3a3a` re-runs.

| Run | Outcome (1) | First commit (2) | Title (3) | Template (4) | Scope (5) | Break lead-in (6) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1, r2 (`9fe02a7c`) | passes | passes | passes | passes | passes | passes |
| Opus r1, r2 (`6efc3a3a`) | passes | passes | passes | passes | passes | passes |
| Opus r1, r2 (`f03479c0`) | passes | passes | passes | passes | fails: a `Scope` heading | fails: a `Breaking changes` heading |
| Haiku r1, r2 | passes | passes | passes | passes | fails: r1 a `### Scope` heading, r2 no lead-in | fails: a `### Breaking changes` heading |
| Opus baseline | fails: outcomes under "Behavior change", no label | passes | passes | passes | fails | fails |
| Haiku baseline | fails: no label | passes | passes | passes | fails | fails |
| `controls/as-pushed.md` | fails | fails: no `#2404`, no reason | fails: `Include` | fails | fails | fails |

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first row), graded by reading, and pass every check,
check 7 included. Check 7 fails both Haiku results and `controls/break-heading.md`, which wrap their outcome lines; the
baselines and `controls/as-pushed.md` carry no outcome label for it to read. A re-run on `0d0fa5fa` put r2's
`**Breaking changes.**` on a paragraph of its own. Check 8 passes every committed result. The other rows stand for the
trees they ran on.
