# codex-review

A skill that runs a code review through the [Codex CLI](https://github.com/openai/codex) as a
second reviewer, then applies the fixes — without leaving your agent. Codex reports findings, the
agent classifies each one (real issue vs false positive), fixes the real ones, and re-reviews until
the review comes back clean.

The skill is `codex-review`. The user invokes it by name; it does not fire on its own.

## What it does

1. Picks the review target: a branch diff, the uncommitted changes, or a specific commit.
1. Picks a mode — **automatic** (the agent classifies every finding, then shows what it will fix
   and skip before editing) or **interactive** (you decide per finding: fix, skip, or fix
   differently).
1. Runs `codex exec review` and reads the findings from its JSONL output, keeping the Codex
   `session_id` so later passes resume the same session.
1. Applies the fixes, then re-reviews with `codex exec resume` so Codex judges the changes in
   context. The cycle repeats up to three iterations, or until the review is clean.
1. Reports each finding next to its resolution — the concrete change, or the reason it was skipped.

Intermediate files live in a scratch directory outside the repository, so the review never appears
in the diff it is reviewing.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/codex-review
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/codex-review@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the location your agent reads
(`.claude/skills/`, `.cursor/`, ...).

## Requirements

- The [Codex CLI](https://github.com/openai/codex) installed and authenticated, with `codex` on the
  `PATH`.
