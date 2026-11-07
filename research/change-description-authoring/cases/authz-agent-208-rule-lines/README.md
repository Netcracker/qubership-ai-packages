# Case: authz-agent#208, rule lines in a repository that numbers its rules

The input is the author's notes for
[Netcracker/qubership-authz-agent#208](https://github.com/Netcracker/qubership-authz-agent/pull/208): a token whose key
source could not be loaded gets a reason code of its own. The repository's decision records number their rules, and
its reading guide asks every pull request to name them in `Implements:` and `Defers:` lines. The change brings four
rules and defers three to a change that has no pull request yet. The repository rebases, so the description never
reaches the history.

[`authz-agent-208-prose-records`](../authz-agent-208-prose-records/README.md) is the same change in a repository whose
records are prose: the negative control for every check below.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Scope, the rule lines; headings and lead-in labels), §4 (rebase and
  merge), §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Implements line.** A plain line of the description, outside any fenced block, starts with `Implements:` and names
   ADR-0091 R23, R37, R38, and R39, and no other rule.
2. **Defers line with a placeholder.** A plain `Defers:` line of the description names exactly ADR-0092 R2, ADR-0095
   R2, and ADR-0095 R16, and gives the target as a visible placeholder (`[PR #NNNN]`, `#NNNN`, `TBD`), not as a number
   and not as a phrase such as "the wiring change".
3. **Placeholder flagged.** The description says that the placeholder is filled in before the merge.
4. **Scope lead-in.** The rule lines come after a `**Scope.**` lead-in, because a deferred rule is a deliberate gap.
5. **No headings.** The repository has no template, so the description has no headings, and the rule lines have no
   heading of their own.
6. **Commit trailers.** The commit message ends with `Implements:` and `Defers:` trailers that name the same rules and
   the same placeholder target as checks 1 and 2, because rebase and merge drops the description.

## Running it

From the repository root, as in [`cases/README.md`](../README.md):

```bash
research/change-description-authoring/cases/run-case.sh research/change-description-authoring/cases/authz-agent-208-rule-lines opus result
python3 research/change-description-authoring/cases/check.py research/change-description-authoring/cases/authz-agent-208-rule-lines
```

`check.py` marks all six checks; check 3 is a marker, so read the sentence it quotes. `controls/as-pushed.md` is the
commit message, title, and description of #208 as pushed on 2026-11-06, written before this rule. It fails all six
checks: its rule lines sit in a fenced block under a `## Rules` heading, the target is "the wiring change", and the
commit has no rule trailers. `controls/implements-claims-deferred.md` is a passing result with ADR-0092 R2 added to both
`Implements:` lines, and fails checks 1 and 6.

No case covers a merge model that keeps the description, an `Implements:` line with nothing deferred, or a deferred rule
whose target already has a number. Under a squash with "title and description", the description becomes the commit body
and its last lines are the trailers, so that model would test only that the lines are not written twice.

## Results

Runs of 2026-11-07 on tree `340d167d`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. All four results pass all six checks: the `**Scope.**` paragraph says why the rules wait
and that `[PR #NNNN]` is filled in before the merge, the two lines close it, and the commit ends with the same two
trailers. The descriptions run 310 to 340 words, the as-pushed one 622.

Two earlier rounds ran the same day, and their results are not committed. On tree `32d8cc58`, Opus r1 ended its commit
with an `Implements:` trailer and no `Defers:` trailer, because the §5 row said "each commit lists the rules it
brings"; the row now names `Defers:` too. On tree `b47b5b6e`, all four passed, but the example in §2 still used this case's rule
numbers and #208; the example now uses numbers of no case, and the final round ran after that change.

The baselines ran the same day with `english-developer-style` alone. Both pass check 1, because the prompt names the
lines, and fail checks 2 to 6: no placeholder for the wiring change, no word on it, no `**Scope.**` lead-in, three and
five headings, and trailers without a placeholder (Sonnet) or a sentence in place of trailers (Opus).
