# Case: authz-agent#208, rule trailers when the deferred rules have no issue

The input is the author's notes for
[Netcracker/qubership-authz-agent#208](https://github.com/Netcracker/qubership-authz-agent/pull/208): a token whose key
source could not be loaded gets a reason code of its own. The repository's decision records number their rules, and
its reading guide asks every pull request to name them in `Implements:` and `Defers:` lines. The change brings four
rules and leaves three to a change that has no pull request and no issue yet, so no `Defers` target exists. The
repository rebases, so the description never reaches the history.

[`authz-agent-159-defers-targets`](../authz-agent-159-defers-targets/README.md) is the path where the targets exist,
and [`authz-agent-208-prose-records`](../authz-agent-208-prose-records/README.md) is the same change in a repository
whose records are prose: the negative control for every check below.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Scope, the rule trailers and the condition that leaves them out; headings
  and lead-in labels), §4 (rebase and merge), §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Description trailers.** The description, outside any fenced block, ends with a paragraph of trailers whose
   `Implements:` names ADR-0091 R23, R37, R38, and R39 and no other rule, and which has no `Defers:` trailer, because no
   deferred rule has a target that exists.
2. **Waiting rules named.** The prose of the description names ADR-0092 R2, ADR-0095 R2, and ADR-0095 R16 and says
   that the change that brings them has no issue or pull request yet.
3. **No placeholder.** Nothing in the result stands in for a number: no `[PR #NNNN]`, `#NNNN`, `TBD`, or "to the
   wiring change".
4. **Scope lead-in.** A `**Scope.**` paragraph comes before the trailers, because the waiting rules are a deliberate
   gap.
5. **No headings.** The repository has no template, so the description has no headings, and the trailers have no
   heading of their own.
6. **Commit trailers.** The commit message ends with the same `Implements:` trailer and no `Defers:` trailer.
7. **No squash request.** The repository rebases, so nothing asks whoever merges to copy the trailers into a squash
   message.

## Running it

From the repository root, as in [`cases/README.md`](../README.md):

```bash
research/change-description-authoring/cases/run-case.sh research/change-description-authoring/cases/authz-agent-208-rule-lines opus result
python3 research/change-description-authoring/cases/check.py research/change-description-authoring/cases/authz-agent-208-rule-lines
```

`check.py` marks all seven checks; check 2 is a marker, so read the sentence it quotes. `controls/as-pushed.md` is the
commit message, title, and description of #208 as pushed on 2026-11-06, written before this rule. It fails all six
checks: its lines sit in a fenced block under a `## Rules` heading, the target is "the wiring change", and the commit
has no rule trailers. `controls/implements-claims-deferred.md` is a passing result with ADR-0092 R2 added to both
`Implements:` trailers, and fails checks 1 and 6. `controls/squash-request.md` is `sonnet/result-2.md` as run on tree
`2ed608e6`, with a sentence added to its Scope paragraph that asks for the trailer in the squash commit; it fails check
7, which a repository that rebases never owes.

No case covers a merge model that keeps the description, a pull request with several commits, or the request to open an
issue, which a `claude -p` run cannot make.

## Results

Runs of 2026-11-10 on tree `6eb5690b`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. All four results pass all seven checks: the description and the commit end with
`Implements: ADR-0091 R23, R37, R38, R39` and no `Defers:` trailer, the `**Scope.**` paragraph names the three waiting
rules and says that the wiring change has no pull request or issue yet, and nothing mentions a squash. The descriptions
run 286 to 322 words, the as-pushed one 622. Opus r1 puts its description in a `markdown` fence that holds a `text`
fence, so `check.py` sees the description end at the inner fence and fails checks 1, 2, and 4; read as written, the
description passes them.

Seven earlier rounds ran. Three on 2026-11-07, on trees `32d8cc58`, `b47b5b6e`, and `340d167d`, ran the first form of
this rule, which put the lines in the Scope slot with a `[PR #NNNN]` target, before #241 settled on trailers and
existing targets; only the `340d167d` results were committed, and they are in the history of this branch. Four, on
`5207d695`, `27b2445d`, `2ed608e6`, and `e0a0d8f7`, ran the trailer form before its last wording changes, and all their
results passed as here. A round on `4f93fd43`, which shortened the text before the final review changed it again, was
stopped part way, and its results are not committed.

The baselines ran on 2026-11-07 with `english-developer-style` alone, on the same prompt, and are graded by the current
checks. Both pass checks 2 and 7 and fail checks 1 and 3 to 6: neither description ends with trailers, both give the
deferred rules a `Defers:` line with no number, and they carry three and five headings.
