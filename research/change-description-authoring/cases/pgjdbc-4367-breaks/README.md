# Case: pgjdbc#4367, a fix with breaks aimed at a patch release

The input is the author's description of [pgjdbc/pgjdbc#4367](https://github.com/pgjdbc/pgjdbc/pull/4367) as posted on
2026-08-23, which a maintainer [rewrote](https://github.com/pgjdbc/pgjdbc/pull/4367#issuecomment-6079358908) with the
breaking changes first, because `master` ships 42.7.x patch releases. The draft lists two `**Breaks:**` lines and one
result-shape change under "What the caller sees", after Why and What, and keeps the `grant insert` case in Scope. The
case tests the rule in `SKILL.md` §2,
"A break leads the description" (until 1.7.0, only where the next release was not a major).

## Skill parts

- `SKILL.md`: §1, §2, §3, §4, §5, §7, §7a
- `english-developer-style`: `SKILL.md` §5

## Checks

1. **Lead.** The description opens, before the Why slot, with the break lines, after at most a short paragraph that says
   which code breaks.
2. **Result shape is a break.** The line on `getMoreResults()` returning the keys as a result set, with
   `getUpdateCount()` at `-1`, is among the break lines: code that loops over `getUpdateCount()` sees different
   results.
3. **Later-statement failure is a break.** `grant insert on t to bob` after a `;` (success before, syntax error after) is
   a break line, not left in Scope.
4. **The fix is not a break.** `create table begin(atomic int); insert into t(a) values(?)` no longer failing stays out
   of the lead.
5. **Stated once.** No break line is repeated in the Why slot or in a later outcome list.
6. **Literals kept.** `42703`, `0100E`, `A result was returned when none was expected.`, and `42601` with `cannot insert
   multiple commands into a prepared statement` appear as in the draft.

7. **The break lead-in comes first** (`break_label_4367`). The description opens with `**Breaking changes.**` (or
   `**Breaking changes:**`), with nothing before it, and has no headings: the case has no template.
8. **No outcome lead-in in the description** (`no_outcome_lead_ins_in_description`). The description is never a commit
   body under this merge model, so §2 keeps its outcomes in prose: it carries no `**User-visible changes.**` or
   `**Not changed.**` lead-in, which the other slots may not carry (§2, §8 Headings).

Checks 1 to 3 and 7 are the rule under test; 4 to 6 are the guard against the rule costing other facts. `check.py`
marks checks 1, 6, and 7 and prints the question for check 5; checks 2 to 4 are graded by reading. Check 7 was added
with the lead-ins. The Haiku results, both baselines, and `controls/retyped-and-repeated.md` fail it: they carry
a `## Break…` heading or none, under the headings the skill they ran on wrote. `controls/breaking-lead-in.md` is
`opus/result.md` as committed before 2026-11-01 with its first heading replaced by the lead-in; it fails check 7 on the
five headings it keeps. `controls/paragraph-before-lead-in.md` is `opus/result.md` with one sentence of prose put
above the lead-in, and fails check 7 on that alone. The two Opus results pass it.

## Running it

As in [the cases README](../README.md): `run-case.sh` copies the skill at `<rev>` and `english-developer-style` from
`agent-packages/english-us-developer-style` out of the checkout. The drafting agent reads them as files; it does not
invoke the Skill tool, which would load an installed copy. `<model>/result*.md` is a run on the skill whose tree id
is in `<model>/skill-tree`; `<model>/baseline/` is the same on `origin/main` before the rule, run through subagents
when #169 added the case. Unlike the other cases' baselines, these ran with the skill as it was before the rule, not
without it. Haiku ran at effort `high`; Opus at the session's default. `controls/retyped-and-repeated.md` is
`opus/result.md` as committed before 2026-10-28 (see the git history) with `0100E` and the final period of its
message retyped, and the `getMoreResults()` break line repeated under "User-visible changes"; it fails checks 5 and
6, which no result fails.

## Results

Tree `e0a0d8f7` adds the `Implements:` and `Defers:` trailers to §2 (Scope), the "pull request title" row, the shapes
table, and rule 1 of §4, the §5 trailer table, and the §8 checklist, for a repository whose decision records number
their rules. This input has no decision records, so the change does not reach this case, and the results below stand
for `e0a0d8f7` as they stand for the tree before it.

Opus r1 and r2 were re-run on 2026-11-02 on tree `044c6057`, graded by reading. Both open the description with
`**Breaking changes.**`, which starts a short paragraph on which code breaks, and both pass check 7; both keep `grant
insert` among the break lines and repeat no break line. They wrote 764 and 769 words of prose, against 763 and 781 on
`c99e1c77`, where the skill did not yet say where the lead-in goes. Tree `6efc3a3a` differs from `044c6057` only in
where the break lead-in and the Scope paragraph go under a template, and this case has no template, so the runs were
not repeated. The other rows stand for the trees they ran on.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. The baseline
rows and the control are of 2026-10-20 and were not re-run.

| Run | Lead (1) | Result shape (2) | `grant insert` (3) | Fix out (4) | Once (5) | Literals (6) | Words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opus/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 756 |
| `opus/result.md` | passes | passes | passes | passes | passes | passes | 763 |
| `opus/result-2.md` | passes | passes | passes | passes | passes | passes | 781 |
| `opus/result.md` (`9fe02a7c`) | passes | passes | passes | passes | passes | passes | 729 |
| `opus/result-2.md` (`9fe02a7c`) | passes | passes | passes | passes | passes | passes | 770 |
| `haiku/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 758 |
| `haiku/result.md` | passes | passes | passes | passes | passes | passes | 799 |
| `haiku/result-2.md` | passes | passes | passes | passes | passes | passes | 785 |
| `controls/retyped-and-repeated.md` | passes | passes | passes | passes | fails: repeated | fails: retyped | 864 |

The Opus r1 of 2026-10-28 kept `grant insert` in Scope as a consequence of the rule the change extends, the miss that
the second version of the rule was written for; both re-runs keep it among the break lines.

Cost, from `<model>/result*.run.txt`: an Opus run costs about $0.50 and a Haiku run about $0.02, nearly all of it the
two skill files read as input.

Opus r1 and r2 were re-run on 2026-11-06 on tree `9fe02a7c`, which marks the outcome block with
`**User-visible changes.**` and `**Not changed.**`, keeps each outcome on one line, and says a lead-in opens its
paragraph; graded by reading, both pass checks 1 to 7 (the `9fe02a7c` rows). Both open the description with
`**Breaking changes.**` on the paragraph it introduces, keep `grant insert` among the break lines, and repeat no break
line. r1 fails check 8: it puts two non-changes under `**Not changed.**`, a lead-in §2 keeps for a description that
becomes a commit body, which this squash with the default message never copies. r2 states them in prose and passes it.
Of the other committed results, only the Haiku baseline fails check 8, with `**Not changed:**`. They wrote 729 and 770
words of prose. The other rows stand for the trees they ran on.
