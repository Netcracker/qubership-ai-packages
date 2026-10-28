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

1. **The break leads** (`break_leads_5330`). The description opens with the break, after the template's Jira link or
   above it: a key whose type reports `NONE` validated in 1.42.0 and now fails. A heading that names it, or one short
   paragraph on which code breaks and then that heading, passes.
2. **The maintainer's question is kept** (`maintainer_question_kept`). A sentence asks the maintainer to decide
   whether these functions reject a `NONE` key or stay permissive (with `VECTOR` rejected in #5331 instead). Question
   for the reader: does it carry the evidence, that built-in types report `ALL` and that `MIN` and `MAX` already reject
   a `NONE` type?
3. **Compatibility is not settled by the writer** (`compatibility_not_settled`). No "not a breaking change",
   "backward compatible", or "does not break".
4. **The answered question is not asked again** (`answered_question_not_reopened`). Whether all types are comparable
   at run time was answered with the `ARRAY` case; no sentence asks it.
5. **The template stays** (`calcite_template_kept`). `## Jira Link` and `## Changes Proposed`.

## Running it

As in [the cases README](../README.md). `controls/settled-and-reopened.md` is `opus/result-2.md` as committed before
2026-10-28 (see the git history) with the Jira Link heading removed, "so this is not a breaking change for them" added,
and the run-time question asked as open.

## Results

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`.

| Run | Break leads (1) | Question kept (2) | Not settled (3) | Not reopened (4) | Template (5) |
| --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes, with both pieces of evidence | passes | passes | passes |
| Haiku r1, r2 | passes | passes, with both pieces of evidence | passes | passes | passes |
| Opus baseline | fails | fails: an "Alternative" section, no question | passes | passes | passes |
| Haiku baseline | fails | passes | passes | passes | passes |
| `controls/settled-and-reopened.md` | passes | passes | fails | fails | fails |

Both Opus runs put their "Breaking changes" section above the template's `## Jira Link`; both Haiku runs put it
under `## Changes Proposed`.
