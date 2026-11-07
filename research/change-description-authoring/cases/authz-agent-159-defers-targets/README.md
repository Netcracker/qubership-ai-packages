# Case: authz-agent#159, rule trailers with existing targets

The input is the author's notes for
[Netcracker/qubership-authz-agent#159](https://github.com/Netcracker/qubership-authz-agent/pull/159): the token packages
mark a provider as the API server of a Kubernetes cluster and check the `sub` of its tokens. The repository's decision
records number their rules, and its reading guide asks every pull request to name them. The change brings twenty rules,
leaves two to open pull requests (#175 and #203), and leaves one to a change that has no pull request and no issue yet.
The repository rebases, so the description never reaches the history. The notes are a short form of the description
as pushed, with the branch's seven commits taken as one.

[`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md) has no existing target at all.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Scope, the rule trailers and the condition that leaves them out; headings
  and lead-in labels), §4 (rebase and merge), §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Description trailers.** The description, outside any fenced block, ends with a paragraph of trailers. Its
   `Implements:` names ADR-0091 R6, R8, and R10 and the seventeen ADR-0094 rules of the notes, and no other rule. Its
   `Defers:` defers ADR-0094 R20 to #175 and ADR-0092 R7 to #203, and nothing else: ADR-0094 R1 has no target.
2. **Waiting rule named.** The prose of the description names ADR-0094 R1 and says that the change that brings it has
   no issue or pull request yet.
3. **No placeholder.** Nothing in the result stands in for a number: no `[PR #NNNN]`, `#NNNN`, `TBD`, or "to the
   wiring change".
4. **Scope lead-in.** A `**Scope.**` paragraph comes before the trailers.
5. **No headings.** The repository has no template, so the description has no headings.
6. **Commit trailers.** The commit message ends with the same two trailers.

## Running it

As in [`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md). `check.py` marks all six checks; check
2 is a marker, so read the sentence it quotes. `controls/as-pushed.md` is the title and description of #159 as pushed,
written before this rule: its lines sit in a fenced block under a `## Rules` heading with ADR-0094 R1 deferred "to the
wiring change", and it fails checks 1 and 3 to 6. It passes check 2, because its Scope names ADR-0094 R1 and the
wiring change in prose.

## Results

Runs of 2026-11-07 on tree `27b2445d`, graded by reading; both models at the default effort. All four results pass all
six checks: the description and the commit end with both trailers, `Defers:` names ADR-0094 R20 to #175 and ADR-0092 R7
to #203 and nothing else, and the `**Scope.**` paragraph says that ADR-0094 R1 waits for the wiring change, which has no
pull request or issue yet. Some list the deferrals in the other order. Opus r1 nests a `text` fence inside its
`markdown` fence with the same three backticks, so `check.py` reads only the part above it and marks checks 1, 2, and 4
failed; read as text, that description passes them. The other three descriptions run 298 to 316 words, the as-pushed
one 1518. An earlier round on `5207d695`, before `Implements` was limited to rules brought in every case, passed the
same way.

The baselines ran the same day with `english-developer-style` alone. Opus ends its commit with five trailers, two
`Implements:` and three `Defers:`, one of them "to the change that wires the token packages into the service", and its
description with no trailers and three headings; it passes check 2 and fails checks 1 and 3 to 6. Sonnet ends its
description with a `Defers:` trailer that sends ADR-0094 R1 to that change in prose, and its commit with no trailers;
it fails all six checks.
