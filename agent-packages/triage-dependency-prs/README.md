# triage-dependency-prs

A skill that triages failing checks on dependency-update PRs from
Renovate (hosted and self-hosted, including fork mode) and Dependabot,
and drives them back to green: classify each failure, fix the clear ones,
and ask about the rest rather than guessing.

The skill is user-invoked: ask the agent to triage dependency PRs, or
invoke it by name. Name a PR number to triage one PR, or invoke it with
no number to sweep every open dependency-update PR that has a failing
check. It ships as a skill rather than a slash-command so it reaches
every target, including Codex, which does not deploy
[APM prompts](https://github.com/microsoft/apm/issues/1781).

## What it does

1. Finds the dependency-update PRs and their red checks (`gh pr list`,
   `gh pr checks`, `gh run view --log-failed`).
1. Classifies each failure: infrastructure flake, real regression from
   the bump, pre-existing tech debt the PR surfaces, flaky test, or a
   non-test gate.
1. Fixes the clear cases in an isolated worktree, verifies the fix under
   the CI toolchain, and commits it to the PR branch (a `@dependabot`
   comment when only a rebase is needed).
1. Reports a per-PR table and links any issues and PRs it opens.

The policy is deliberate: push a fix only when the cause is clear and
verified; otherwise ask. Flaky tests get an issue (or a small separate
PR), and a failure that also reproduces on the default branch is fixed
there, not on the bot branch.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/triage-dependency-prs
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/triage-dependency-prs@v2.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the
location your agent reads (`.claude/skills/`, `.cursor/`, ...).

## Requirements

- The `gh` CLI, authenticated against the repository.
- A local checkout where the agent can reproduce and verify a fix under
  the same toolchain as CI.
