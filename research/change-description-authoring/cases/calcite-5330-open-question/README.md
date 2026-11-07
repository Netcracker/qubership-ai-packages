# Case: apache/calcite#5330, a question only a maintainer can settle

The input is [apache/calcite#5330](https://github.com/apache/calcite/pull/5330) as of 2026-10-15 09:20 UTC: the
description, the diff, and the discussion so far. The change makes `ARG_MIN`, `ARG_MAX`, `MIN_BY`, and `MAX_BY` reject
a key whose type reports comparability `NONE`. A committer wrote that it "would be a breaking change for us"; the
author answered with the code (no built-in type reports `NONE`) and offered to close the pull request or to reject only
`VECTOR` keys in #5331; the committer had not replied. The task is to rewrite the description to reflect the
discussion. The case tests the rule #130 added: a question only a maintainer can settle stays in the Scope slot with
the decision it needs and its evidence, and a question the evidence answers is not asked again. It also tests the break
lead of #169 in a repository other than pgjdbc: `main` ships 1.43.0, a minor release.

## Skill parts

- `SKILL.md`: §2 (Pull request description: slot 3 and the break lead; Scope, open questions; template headings)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **The break leads** (`break_leads_5330`). The description opens with the break: a key whose type reports `NONE`
   validated in 1.42.0 and now fails. A paragraph opening with `**Breaking changes.**` ahead of every heading passes.
   So do the shapes of earlier skills, after the template's Jira link or above it: a heading that names the break, or
   one short paragraph on which code breaks and then that heading.
2. **The maintainer's question is kept** (`maintainer_question_kept`). A sentence asks the maintainer to decide
   whether these functions reject a `NONE` key or stay permissive (with `VECTOR` rejected in #5331 instead): a
   question, or a sentence with "decide", "decision", or "choose". Question
   for the reader: does it carry the evidence, that built-in types report `ALL` and that `MIN` and `MAX` already reject
   a `NONE` type?
3. **Compatibility is not settled by the writer** (`compatibility_not_settled`). No "not a breaking change",
   "backward compatible", or "does not break".
4. **The answered question is not asked again** (`answered_question_not_reopened`). Whether all types are comparable
   at run time was answered with the `ARRAY` case; no sentence asks it.
5. **The template stays** (`calcite_template_kept`). `## Jira Link` and `## Changes Proposed`.
6. **Scope by lead-in under the template** (`scope_lead_in_under_template`). The template has no Scope heading, so the
   maintainer's question sits in a paragraph that opens with `**Scope.**`, and the description adds no heading that
   names Scope. The Haiku results, both baselines, and the control fail it; the Opus results pass it.
7. **Break lead-in ahead of the template** (`break_lead_in_before_headings`). The description opens with a paragraph
   that starts with `**Breaking changes.**`, ahead of `## Jira Link`, and adds no heading that names the break. The
   Haiku results, both baselines, and both controls fail it; the Opus results pass it.
8. **No outcome lead-in in the description** (`no_outcome_lead_ins_in_description`), as in
   [`pgjdbc-4367-breaks`](../pgjdbc-4367-breaks/README.md).

## Running it

As in [the cases README](../README.md). `controls/settled-and-reopened.md` is `opus/result-2.md` as committed before
2026-10-28 (see the git history) with the Jira Link heading removed, "so this is not a breaking change for them" added,
and the run-time question asked as open. `controls/break-heading.md` is `opus/result.md` as run on tree `044c6057`
(2026-11-02), which put the breaks under a `## Breaking changes` heading above the template's.

## Results

Tree `27b2445d` adds the `Implements:` and `Defers:` trailers to §2 (Scope), the §5 trailer table, and the §8
checklist, for a repository whose decision records number their rules. This input has no decision records, so the
change does not reach this case, and the results below stand for `27b2445d` as they stand for the tree before it.

Opus r1 and r2 were re-run on 2026-11-02 on tree `6efc3a3a`, graded by reading; both pass all seven checks. Both open
with a `**Breaking changes.**` paragraph ahead of `## Jira Link`, keep the template's headings, and put the
maintainer's question in a paragraph that opens with `**Scope.**` under `## Changes Proposed`. r2 asks it as "A
maintainer needs to choose between two options", which check 2 matched only once `choose` joined its words. They wrote
466 and 520 words; the two runs on `044c6057` (`controls/break-heading.md` is r1) wrote 500 and 475 under a
`## Breaking changes` heading. The case has no word limit. The other rows stand for the trees they ran on.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Break leads (1) | Question kept (2) | Not settled (3) | Not reopened (4) | Template (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 (`9fe02a7c`) | passes | passes, with both pieces of evidence | passes | passes | passes |
| Opus r1, r2 | passes | passes, with both pieces of evidence | passes | passes | passes |
| Haiku r1, r2 | passes | passes, with both pieces of evidence | passes | passes | passes |
| Opus baseline | fails | fails: an "Alternative" section, no question | passes | passes | passes |
| Haiku baseline | fails | passes | passes | passes | passes |
| `controls/settled-and-reopened.md` | passes | passes | fails | fails | fails |

Both Opus runs put their "Breaking changes" section above the template's `## Jira Link`; both Haiku runs put it
under `## Changes Proposed`.

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c` (the first row), graded by reading, and pass every check. r1
asks the maintainer whether a type that reports `NONE` but is comparable at run time should stay valid as a key; that is
the question check 2 asks for, and check 4's snippet now skips a question that asks what should be done, where it used
to fail r1. An earlier re-run on `0d0fa5fa` put `**Breaking changes.**` on a paragraph of its own in both results, so
the break sentence no longer opened the description and both failed check 1; r2 also stated the maintainer's two options
without asking for the decision and failed check 2. Check 8 passes every committed result. The other rows stand for the
trees they ran on.
