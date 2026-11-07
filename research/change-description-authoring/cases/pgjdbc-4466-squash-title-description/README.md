# Case: pgjdbc#4466 under a squash that copies the description

The input is [pgjdbc/pgjdbc#4466](https://github.com/pgjdbc/pgjdbc/pull/4466), which makes the default
`ApplicationName` carry the driver version, with its review condensed into notes. The real pull
request has one commit; the case gives the branch two more, `add tests` and `Apply suggestion from @vlsi`, built from
what the review asked for, so that there are fix-up commits to fold. The five `pgjdbc-4466-*` cases share the input
below "Repository facts" and differ in the merge model only.

This one is a squash merge whose message is the pull request title and description, the setting uber/NullAway uses
(its last 40 first-parent commits are all squashes whose bodies are descriptions, template checklist included,
checked on 2026-10-20). §4 rule 5 makes the description the body of the one commit that lands: no headings, no
reviewer-only content, verification in one line, and no URL to this repository's code.

## Skill parts

- `SKILL.md`: §2 (Commit body, slot 4; Pull request title; Pull request description: a break leads the description,
  reviewer-only content, the lead-in paragraph), §4, §5 (links in a commit body)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Outcome line with no invented code** (`user_visible_without_invented_code`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md).
2. **The title is a subject** (`title_is_subject`). It becomes the subject of the squash commit.
3. **The description is a commit body** (`description_as_commit_body`). No Markdown heading, no checkbox, no URL to
   `github.com/pgjdbc/pgjdbc/blob/…`. Question for the reader: is verification at most one sentence naming what the
   tests establish?
4. **Outcome lead-ins, not labels** (`no_plain_outcome_labels`). The description, which becomes the commit body, has no
   line that opens with `User-visible:` or `Not changed:`; its outcomes sit under `**User-visible changes.**`
   and `**Not changed.**`.
5. **Break lead-in first** (`break_lead_in_before_headings`), as in
   [`pgjdbc-4466-squash-default`](../pgjdbc-4466-squash-default/README.md): the new default breaks code that
   matches the old `application_name`, so the description opens with `**Breaking changes.**`.
6. **One line per outcome** (`outcome_lines_unwrapped`), as in the squash-default case.

## Running it

As in [the cases README](../README.md). `controls/as-pushed.md` is the branch as the author pushed it.

## Results

Tree `27b2445d` adds the `Implements:` and `Defers:` trailers to §2 (Scope), the §5 trailer table, and the §8
checklist, for a repository whose decision records number their rules. This input has no decision records, so the
change does not reach this case, and the results below stand for `27b2445d` as they stand for the tree before it.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Outcome (1) | Title (2) | Body shape (3) | Verification in one sentence (3, read) |
| --- | --- | --- | --- | --- |
| Opus r1 (`9fe02a7c`) | passes | passes | passes | passes: none |
| Opus r2 (`9fe02a7c`) | passes | passes | passes | passes: one sentence, in the `**Not changed.**` paragraph |
| Opus r1 (`f03479c0`) | passes | passes | passes | passes: one sentence |
| Opus r2 (`f03479c0`) | passes | passes | passes | fails: two sentences |
| Haiku r1 | passes | passes | passes | fails: three sentences |
| Haiku r2 | passes | passes | fails: six headings | fails: a heading and two bullets |
| Opus baseline | fails | passes | fails: headings, checkboxes, a URL | fails |
| Haiku baseline | fails | passes | fails: headings, checkboxes, a URL | fails |
| `controls/as-pushed.md` | fails | fails | passes | passes: no verification at all |

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first two rows), graded by reading, and pass every
check, checks 4 to 6 included. Both descriptions open with `**Breaking changes.**`, put the remaining outcomes under
`**User-visible changes.**` and `**Not changed.**` with one line each, and close with a `**Scope.**` paragraph. r2 puts
its sentence on `explicitApplicationNameIsKept` in the `**Not changed.**` paragraph, which no check reads as a fault.
Check 4 fails both Haiku results, check 5 fails the Haiku results, both baselines, and the control, and check 6 passes
every committed result. The runs on `0d0fa5fa` passed every check registered then.
