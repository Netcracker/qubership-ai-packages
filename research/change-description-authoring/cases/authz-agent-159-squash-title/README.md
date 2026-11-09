# Case: authz-agent#159 under a squash that keeps only the title

The input is [`authz-agent-159-defers-targets`](../authz-agent-159-defers-targets/README.md) with one fact changed: the
repository squashes every pull request, and the squash message is the pull request title alone, GitHub's "pull request
title" setting. Neither the branch commit nor the description reaches the history, so the rule trailers survive only if
whoever merges puts them into the squash commit message. The case tests the exception in `SKILL.md` §2 (Scope) and §4
for that setting.

## Skill parts

- `SKILL.md`: §2 (Pull request description: Scope, the rule trailers and the title-only squash; headings and lead-in
  labels), §4 (the squash row and rule 1), §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Description trailers.** As check 1 of `authz-agent-159-defers-targets`: the description ends with `Implements:`
   and `Defers:` trailers that name exactly the rules and the targets of the notes.
2. **Squash message asked for.** A sentence of the description, outside its trailers, asks whoever merges to add the
   trailers to the squash commit message.
3. **Waiting rule named.** The prose of the description names ADR-0094 R1 and says that the change that brings it has
   no issue or pull request yet.
4. **No placeholder.** Nothing in the result stands in for a number.
5. **Scope lead-in.** A `**Scope.**` paragraph comes before the trailers.
6. **No headings.** The repository has no template, so the description has no headings.

## Running it

As in [`authz-agent-208-rule-lines`](../authz-agent-208-rule-lines/README.md). `check.py` marks all six checks; checks 2
and 3 are markers, so read the sentences they quote. `controls/as-pushed.md` is the as-pushed text of #159, which fails
every check but 3. `controls/rebase-shape.md` is `authz-agent-159-defers-targets/sonnet/result.md` as run on tree
`27b2445d` for the rebase input: it passes every check but 2, which shows that check 2 needs the sentence this case is
about. `controls/no-ask.md` is `opus/result.md` as run on tree `2ed608e6`, with its request replaced by "The squash
keeps only the title, so the two trailers below never reach the history.": it fails check 2 alone, because a sentence
that mentions the squash and the trailers but asks for nothing does not count.

## Results

Runs of 2026-11-09 on tree `e0a0d8f7`, graded by reading; both models at the default effort. All four results pass all
six checks. Each ends its description with the same two trailers as `authz-agent-159-defers-targets`, and asks, in its
`**Scope.**` paragraph or in a sentence of its own after it, that whoever merges paste those trailers into the body of
the squash commit, because the squash message is the title alone. The descriptions run 321 to 336 words. An earlier
round on `2ed608e6`, before the shapes table and the GitLab template entered the rule, passed the same way.

The baselines ran on 2026-11-09 with `english-developer-style` alone. Both pass check 3 and fail checks 1, 2, and 4 to
6: neither description ends with trailers or asks for them in the squash message (Sonnet states the setting but asks
nothing), both send ADR-0094 R1 to the wiring change in prose inside a `Defers:` line, and they carry two and three
headings.
