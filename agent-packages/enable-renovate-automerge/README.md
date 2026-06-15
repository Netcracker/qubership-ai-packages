# enable-renovate-automerge

A skill that enables Renovate automerge on a repository, gated on a real
test or style required check rather than a PR-title linter or a
Docker-build smoke test.

The skill is `enable-renovate-automerge`. It activates when you turn on
automerge for dependency PRs, choose which status checks to require, or
add a CI-gate job. Apply it per repository, whether you configure one or
sweep several.

## What it does

1. Confirms the prerequisites: the repository runs Renovate (not
   Dependabot), you have admin, and at least one `pull_request` workflow
   runs real tests or style checks.
1. Decides the required check(s). Several gating jobs in one workflow
   file collapse into a single `CI Gate` job; checks spread across
   separate files are each registered on their own, with long check
   names shortened first.
1. Registers those checks in the branch ruleset (`gh api`), avoiding the
   traps that silently break automerge: name mismatches, bot-excluded
   jobs that stay pending, and skipped checks that block the merge.
1. Enables automerge in `renovate.json` (scoped update types plus
   `platformAutomerge`) and the repository's `allow_auto_merge` setting,
   opened as a PR.
1. Pilots on one Renovate PR — green merges, red holds — and reports a
   per-repository table.

The policy is deliberate: automerge is only as safe as the check that
gates it, so the work is mostly about the gate, and flipping
`automerge: true` is the last and smallest step.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/enable-renovate-automerge
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/enable-renovate-automerge@v1.0.0
```

Then run `apm install` and `apm compile`. The skill deploys to the
location your agent reads (`.claude/skills/`, `.cursor/`, ...).

## Requirements

- The `gh` CLI, authenticated with admin on the target repository.
- A repository that runs Renovate and has a real test or style workflow
  on `pull_request`.
