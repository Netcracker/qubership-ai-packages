# Case: pgjdbc#4367, a fix with breaks aimed at a patch release

The input is the author's description of [pgjdbc/pgjdbc#4367](https://github.com/pgjdbc/pgjdbc/pull/4367) as posted on
2026-08-23, which a maintainer [rewrote](https://github.com/pgjdbc/pgjdbc/pull/4367#issuecomment-6079358908) with the
breaking changes first, because `master` ships 42.7.x patch releases. The draft lists two `**Breaks:**` lines and one
result-shape change under "What the caller sees", after Why and What, and keeps the `grant insert` case in Scope. The
case tests the rule in `SKILL.md` §2,
"A break leads the description unless the next release from the target branch is a major".

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

Checks 1 to 3 are the rule under test; 4 to 6 are the guard against the rule costing other facts. `check.py` marks
checks 1 and 6 and prints the question for check 5; checks 2 to 4 are graded by reading.

## Running it

As in [the cases README](../README.md): `run-case.sh` copies the skill at `<rev>` and `english-developer-style` from
`agent-packages/english-us-developer-style` out of the checkout. The drafting agent reads them as files; it does not
invoke the Skill tool, which would load an installed copy. `<model>/result*.md` is a run on the skill whose tree id is
in `<model>/skill-tree`; `<model>/baseline/` is the same on `origin/main` before the rule, run through subagents
when #169 added the case. Unlike the other cases' baselines, these ran with the skill as it was before the rule, not
without it. Haiku ran at effort `high`; Opus at the session's default. `controls/retyped-and-repeated.md` is
`opus/result.md` with `0100E` and the final period of its message retyped, and the `getMoreResults()` break line
repeated under "User-visible changes"; it fails checks 5 and 6, which no result fails.

## Results

Runs of 2026-10-20: the baselines when #169 added the case, the results again after 41fe345 on the skill whose tree
id is in `<model>/skill-tree`. Graded by reading.

| Run | Lead (1) | Result shape (2) | `grant insert` (3) | Fix out (4) | Once (5) | Literals (6) | Words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opus/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 756 |
| `opus/result.md` | passes | passes | passes | passes | passes | passes | 807 |
| `opus/result-2.md` | passes | passes | passes | passes | passes | passes | 868 |
| `haiku/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 758 |
| `haiku/result.md` | passes | passes | passes | fails: the `begin atomic` fix in the break list | passes | passes | 745 |
| `haiku/result-2.md` | passes | passes | passes | passes | passes | passes | 779 |
| `controls/retyped-and-repeated.md` | passes | passes | passes | passes | fails: repeated | fails: retyped | 864 |

Three versions of the rule were run on Opus when #169 added it. The first, without the sentence on a failure extended
to inputs that worked before, left `grant insert` in Scope in both runs; the draft framed it as a known limitation the
change extends. The second, with that sentence, put it in the lead in both runs. The version #169 merged, reworded
after review, did in one of two Opus runs and in both Haiku runs; after 41fe345 it did in all four.

The growth over the baseline is the lead sentence, the `grant insert` line, and in one Opus result one sentence per
break on what the caller does. A review asked whether the sentence "the outcomes above were checked against
PostgreSQL 17" widens to the `grant insert` line once that line moves up. In three of the four results after 41fe345
(both Haiku, `opus/result-2.md`) the sentence that says what was checked covers it; `opus/result.md` keeps the line out
of it. No check covers this yet.

Cost, from `<model>/result*.run.txt`: an Opus run costs about $0.50 and a Haiku run about $0.02, nearly all of it the
two skill files read as input.
