# Case: pgjdbc#4367, a fix with breaks aimed at a patch release

The input is the author's description of [pgjdbc/pgjdbc#4367](https://github.com/pgjdbc/pgjdbc/pull/4367) as posted on
2026-08-23, which a maintainer [rewrote](https://github.com/pgjdbc/pgjdbc/pull/4367#issuecomment-6079358908) with the
breaking changes first, because `master` ships 42.7.x patch releases. The draft lists two `**Breaks:**` lines and one
result-shape change under "What the caller sees", after Why and What, and keeps the `grant insert` case in Scope. The
case tests the rule in SKILL.md §2, "A break leads the description where the next release from the target branch
promises compatibility".

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

Checks 1 to 3 are the rule under test; 4 to 6 are the guard against the rule costing other facts.

## Running it

The drafting agent gets `prompt.md` and the skill copied out of the checkout with `git archive <rev>
agent-packages/change-description-authoring/.apm/skills/change-description-authoring`, plus `english-developer-style`
from `agent-packages/english-us-developer-style`, as files to read; it does not invoke the Skill tool, which would load
an installed copy. `<model>/result*.md` is a run on the skill whose tree id is in `<model>/skill-tree`;
`<model>/baseline/` is the same on `origin/main` before the rule. Haiku ran at effort `high`; Opus at the session's
default.

## Results

Runs of 2026-10-20. "Fails" names the check; every result not listed under a check passes it.

| Run | Lead (1) | Result shape (2) | `grant insert` (3) | Fix out (4) | Once (5) | Literals (6) | Words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opus/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 756 |
| `opus/result.md` | passes | passes | passes | passes | passes | passes | 825 |
| `opus/result-2.md` | passes | passes | fails: in Scope | passes | passes | passes | 792 |
| `haiku/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 758 |
| `haiku/result.md` | passes | passes | passes | passes | passes | passes | 779 |
| `haiku/result-2.md` | passes | passes | passes | passes | passes | passes | 784 |

Three versions of the rule were run on Opus. The first, without the sentence on a failure extended to inputs that worked
before, left `grant insert` in Scope in both runs; the draft framed it as a known limitation the change extends. The
second, with that sentence, put it in the lead in both runs. The version committed here, reworded after review, did in
one of two Opus runs and in both Haiku runs, so the sentence moves the case most of the time and not always.

The growth over the baseline is the lead sentence, the `grant insert` line, and in `opus/result.md` one sentence per
break on what the caller does. All three Haiku results end with a `Generated with Claude Code` line that no input
asked for. A review asked whether the sentence "the outcomes above were checked against PostgreSQL 17" widens to
the `grant insert` line once it moves up; it does not, because in the draft that sentence already followed Scope.

Cost: each Opus run used about 110000 to 115000 tokens and each Haiku run about 120000 to 127000, nearly all of it
the two skill files read as input. At list prices (Opus 5.5 $4 per million input tokens, Haiku 5.5 $0.10) that is
under $0.50 an Opus run and about $0.01 a Haiku run, before cache discounts.
