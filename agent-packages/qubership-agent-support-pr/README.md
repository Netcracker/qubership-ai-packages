# qubership-agent-support-pr

A skill that prepares a repository PR for Qubership baseline agent support. It
adds `qubership-essentials`, installs generated APM assets for the selected
agent harnesses, and configures generated-file handling for review and
Super-Linter.

The skill is `qubership-agent-support-pr`. The user invokes it by asking the
agent to add Qubership agent support to a repository or to create the onboarding
PR.

## What it does

1. Reads the target repository layout, workflows, linters, APM files, and
   existing generated agent assets.
1. Creates or updates `apm.yml`, including `apm init -y --target <targets>` for
   repositories that do not have APM metadata yet.
1. Installs `qubership-essentials` with `apm install`, relying on
   `apm.lock.yaml` for the resolved revision.
1. Keeps generated assets for the selected harnesses and marks them as
   generated in `.gitattributes`.
1. Adds Super-Linter exclusions for generated APM install assets without
   excluding source files, docs, workflows, or `.apm/**`.
1. Runs focused validation and prepares the PR without hiding unrelated user
   changes.

## Install

Install this skill in the agent workspace that will prepare onboarding PRs:

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/qubership-agent-support-pr
```

Then run `apm install` for the configured targets. The skill deploys to the
location your agent reads, such as `.agents/skills/`, `.claude/skills/`, or
another target-specific skills directory.

## Usage

Ask the agent to apply the skill in the target repository:

```text
Use qubership-agent-support-pr to create a PR that adds Qubership agent support
to this repository.
```

Or just:

```text
Prepare a PR for APM agent support
```

Default targets are `claude`, `codex`, and `cursor`. Name other targets only
when the repository intentionally supports them.

## Requirements

- The `apm` CLI on `PATH`.
- The `gh` CLI authenticated for creating or updating the target repository PR.
- A clean understanding of the target repository's local checks, especially
  `.github/workflows/`, `.github/linters/`, `.github/super-linter.env`, and
  `.pre-commit-config.yaml` when present.
