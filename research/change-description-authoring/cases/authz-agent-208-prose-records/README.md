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

Runs of 2026-11-07 on tree `27b2445d`, graded by reading; both models at the default effort. All four results pass all
three checks. Each names ADR-0091 and ADR-0095 in a sentence, as the rule asks for a record without numbered rules,
says in its `**Scope.**` paragraph that the wiring change has no pull request yet, and writes no rule trailer and no
rule number. The descriptions run 286 to 297 words. Four earlier rounds the same day passed the same way, except that
one Sonnet result on `b47b5b6e`, under the first form of the rule, wrote the wiring change as `[PR #NNNN]`.
