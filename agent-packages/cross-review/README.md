# cross-review

A skill that reviews one change with two reviewers that never see each other's work: the
[Codex CLI](https://github.com/openai/codex) and a Claude subagent. A merge step scores where they
agree and where they contradict each other, the session that wrote the code decides what to fix, and
the next round starts with a record of what was fixed and what was rejected.

The skill is `cross-review`. The user invokes it by name; it does not fire on its own. For a
single-reviewer pass, use [`codex-review`](../codex-review/) instead — it costs less and needs no
subagents.

## What it does

1. Picks the review target: a branch diff, the uncommitted changes, or a specific commit.
1. Opens a round: pins the head commit and a snapshot of the working tree, and fences the tree's
   dirty state so a finding written against code that has since moved is marked stale.
1. Runs both reviewers concurrently. Codex writes to files; the Claude reviewer is a subagent whose
   transcript never enters the orchestrating session. What reaches the session is one merged file.
1. Merges the two reports: pairs findings by anchor, takes the highest severity across reviewers,
   marks agreement, and flags contradictions.
1. Records every decision in a ledger — fixed, rejected, or deferred, each with the evidence that
   settles it. A later round shows a refiled finding next to the evidence that retired it.
1. Loops until nothing blocks, the round limit is reached, or two rounds raise the same findings,
   then writes a report of what was fixed, what was rejected, and on what grounds.

`scripts/review_run.py` performs every step that needs no judgment: run directories, snapshots,
schema validation, merging, and the ledger. Run state lives outside the repository, so the review
never appears in the diff it reviews.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/cross-review
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/cross-review@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the location your agent reads
(`.claude/skills/`, `.cursor/`, ...).

## Requirements

- The [Codex CLI](https://github.com/openai/codex) installed and authenticated, with `codex` on the
  `PATH`.
- Python 3 on the `PATH`, for `scripts/review_run.py`. The script uses the standard library only.
- An agent that can spawn subagents, for the second reviewer and the merger.
