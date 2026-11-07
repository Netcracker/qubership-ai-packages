# Case: pgjdbc#4392, a fix with no break aimed at a patch release

The input is the author's description of [pgjdbc/pgjdbc#4392](https://github.com/pgjdbc/pgjdbc/pull/4392): a JDBC
escape followed by a tab or a newline used to reach the server verbatim and fail, and now works. Nothing that worked
before fails or returns a different result. The target is the same `master` as in `pgjdbc-4367-breaks`, so the case is
the negative control for the rule in `SKILL.md` §2,
"A break leads the description" (until 1.7.0, only where the next release was not a major).

## Skill parts

- `SKILL.md`: §1, §2, §3, §4, §5, §7, §7a
- `english-developer-style`: `SKILL.md` §5

## Checks

1. **No lead.** The description opens with the problem, not with a compatibility statement.
2. **No empty section.** No `Breaking changes` heading or `**Breaking changes.**` lead-in, and no sentence saying that
   nothing breaks or that the change is compatible.
3. **Literals kept.** `{d\t'1999-01-09'}` and the server's `syntax error at or near "{"` appear as in the draft.
4. **No outcome lead-in in the description** (`no_outcome_lead_ins_in_description`), as in
   [`pgjdbc-4367-breaks`](../pgjdbc-4367-breaks/README.md).

## Running it

As in [`pgjdbc-4367-breaks`](../pgjdbc-4367-breaks/README.md). `check.py` marks all three checks.
`controls/empty-break-section.md` is `opus/result.md` as committed before 2026-10-28 (see the git history) with a
`Breaking changes` heading that says nothing breaks, and the server's message retyped.
`controls/empty-break-lead-in.md` is `opus/result.md` opened with `**Breaking changes.** None.`, and fails checks 1 and
2 through the lead-in alone.

## Results

Tree `340d167d` adds the `Implements:` and `Defers:` lines to §2 (Scope), the §5 trailer table, and the §8
checklist, for a repository whose decision records number their rules. This input has no decision records, so the
change does not reach this case, and the results below stand for `340d167d` as they stand for the tree before it.

Opus r1 and r2 were re-run on 2026-11-01 on tree `c99e1c77`, graded by reading. That tree differs from this change's in
places this case does not reach: a widening of the §2 translation rule to a comment the diff removes or rewrites, left
out because it changed no output on a description of pgjdbc/pgjdbc#4412; two example template headings since dropped
from one sentence; and where the break lead-in and a Scope lead-in under a template go, which needs a break or a
template with headings, and this case has neither. Both pass all three checks, with no `**Breaking changes.**` label, at
144 and 124 words. The other rows stand for the trees they ran on.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. All four
results pass all three checks: they open with the problem, carry no `Breaking changes` heading and no sentence about
compatibility, and keep both literals. Opus wrote 157 and 175 words, Haiku 192 and 172; the draft has 209. The
baselines (run 2026-10-20 with `english-developer-style` alone, not re-run) pass too: without a break, neither model
adds a lead. The control fails all three checks.

Tree `9fe02a7c` (2026-11-06) marks the outcome block with `**User-visible changes.**` and `**Not changed.**`, keeps each
outcome on one line that is not wrapped, says a lead-in opens its paragraph, and says what a description that becomes a
commit body keeps. This case was not re-run on it: its Opus results carry no outcome block, any `**Scope.**` lead-in in
them already opens its paragraph, and no check reads either. Check 4, added with it, passes every committed result. The
rows stand for the trees they ran on.
