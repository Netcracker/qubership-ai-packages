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

7. **The break block is labelled** (`break_label_4367`). One of the first three blocks opens with
   `**Breaking changes.**` (or `**Breaking changes:**`), and the description has no headings: the case has no template.

Checks 1 to 3 and 7 are the rule under test; 4 to 6 are the guard against the rule costing other facts. `check.py`
marks checks 1, 6, and 7 and prints the question for check 5; checks 2 to 4 are graded by reading. Check 7 was added
with the lead-in labels. The Haiku results, both baselines, and `controls/retyped-and-repeated.md` fail it: they carry
a `## Break…` heading or none, under the headings the skill they ran on wrote. `controls/breaking-lead-in.md` is
`opus/result.md` as committed before 2026-11-01 with its first heading replaced by the lead-in; it fails check 7 on the
five headings it keeps, and the two Opus results pass it.

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

Opus r1 and r2 were re-run on 2026-11-01 on tree `c99e1c77`, graded by reading. That tree differs from this change's in
two places the checks do not reach: a widening of the §2 translation rule to a comment the diff removes or rewrites,
left out because it changed no output on `pgjdbc-4412-comment-only`, and two example template headings since dropped
from one sentence; both open with `**Breaking changes.**` and pass check 7, and both keep `grant insert` among the break
lines. The other rows stand for the trees they ran on.

Runs of 2026-10-28 on the skill whose tree id is in `<model>/skill-tree` (`f03479c0`, branch `vs/cda-concise`), graded
by reading; Haiku at effort `high`, Opus at the default. "r1" and "r2" are `result.md` and `result-2.md`. The baseline
rows and the control are of 2026-10-20 and were not re-run.

| Run | Lead (1) | Result shape (2) | `grant insert` (3) | Fix out (4) | Once (5) | Literals (6) | Words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opus/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 756 |
| `opus/result.md` | passes | passes | passes | passes | passes | passes | 763 |
| `opus/result-2.md` | passes | passes | passes | passes | passes | passes | 781 |
| `haiku/baseline/result.md` | fails: Why first | fails: in slot 3 | fails: in Scope | passes | passes | passes | 758 |
| `haiku/result.md` | passes | passes | passes | passes | passes | passes | 799 |
| `haiku/result-2.md` | passes | passes | passes | passes | passes | passes | 785 |
| `controls/retyped-and-repeated.md` | passes | passes | passes | passes | fails: repeated | fails: retyped | 864 |

The Opus r1 of 2026-10-28 kept `grant insert` in Scope as a consequence of the rule the change extends, the miss that
the second version of the rule was written for; both re-runs keep it among the break lines.

Cost, from `<model>/result*.run.txt`: an Opus run costs about $0.50 and a Haiku run about $0.02, nearly all of it the
two skill files read as input.
