# Case: authz-agent#208 in a repository whose records are prose

The input is [`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md) with two facts changed: the
decision records are prose with no numbered statements, and nothing asks a pull request to cite them; the notes name
ADR-0091 and ADR-0095 without rule numbers. The rule lines are noise here, so this case is the negative control for the
rule in `SKILL.md` §2 (Scope) that adds them.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Scope, the rule lines and the condition that leaves them out; headings),
  §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **No rule lines.** Neither the commit message nor the description has an `Implements:` or a `Defers:` line.
2. **No rule numbers.** No `R` followed by a number appears anywhere: the notes carry none, so any would be invented.
3. **No headings.** The repository has no template, so the description has no headings.

## Running it

As in [`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md). `check.py` marks all three checks.
`controls/as-pushed.md` is the same as-pushed text of #208, which fails all three checks here: two rule lines, seven
rule numbers, and six headings.

## Results

Runs of 2026-11-07 on tree `340d167d`, graded by reading; both models at the default effort. All four results pass all
three checks. Each names ADR-0091 and ADR-0095 in a sentence, as the rule asks for a record without numbered rules,
says in its `**Scope.**` paragraph that the wiring change has no pull request yet, and writes no rule line and no rule
number. The descriptions run 289 to 307 words. The two earlier rounds, on trees `32d8cc58` and `b47b5b6e`, passed the
same way.

In the round on `b47b5b6e`, Sonnet r1 wrote the wiring change as `[PR #NNNN]`, "to be filled in before this merges",
without failing a check. The Scope slot asks to state what a follow-up without a number leaves out, and the §8
identifier item also allows a visible placeholder for a number that does not exist yet. No result of the final round
does it.
