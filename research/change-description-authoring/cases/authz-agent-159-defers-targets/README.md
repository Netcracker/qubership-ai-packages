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
7. **No squash request.** The repository rebases, so nothing asks whoever merges to copy the trailers into a squash
   message.

## Running it

As in [`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md). `check.py` marks all seven checks; check
2 is a marker, so read the sentence it quotes. `controls/as-pushed.md` is the title and description of #159 as pushed,
written before this rule: its lines sit in a fenced block under a `## Rules` heading with ADR-0094 R1 deferred "to the
wiring change", and it fails checks 1 and 3 to 6. It passes check 2, because its Scope names ADR-0094 R1 and the wiring
change in prose. `controls/squash-request.md` is `authz-agent-159-squash-title/opus/result.md` as run on tree
`2ed608e6`, which asks for the trailers in the squash commit; it fails check 7, which a repository that rebases never
owes.

## Results

Runs of 2026-11-09 on tree `e0a0d8f7`, graded by reading; both models at the default effort. All four results pass all
seven checks: the description and the commit end with both trailers, `Defers:` names ADR-0094 R20 to #175 and ADR-0092
R7 to #203 and nothing else, the `**Scope.**` paragraph says that ADR-0094 R1 waits for the wiring change, which has no
pull request or issue yet, and nothing mentions a squash. Some list the deferrals in the other order. The descriptions
run 298 to 368 words, the as-pushed one 1518. Three earlier rounds, on `5207d695`, `27b2445d`, and `2ed608e6`, passed
the same way.

The baselines ran on 2026-11-07 with `english-developer-style` alone. Opus ends its commit with five trailers, two
`Implements:` and three `Defers:`, one of them "to the change that wires the token packages into the service", and its
description with no trailers and three headings; it passes checks 2 and 7 and fails checks 1 and 3 to 6. Sonnet ends its
description with a `Defers:` trailer that sends ADR-0094 R1 to that change in prose, and its commit with no trailers; it
passes check 7 and fails checks 1 to 6.
