# qubership-ai-packages

This repository is an APM marketplace of Qubership agent packages. Use it to install shared skills, instructions, and
umbrella packages for agents such as Claude Code, Codex, Cursor, and GitHub Copilot.

## Contents

- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [About APM](#about-apm)
- [APM installation](#apm-installation)
- [Repository onboarding](#repository-onboarding)
- [Qubership user essentials](#qubership-user-essentials)
- [Guides](#guides)

## Prerequisites

Microsoft APM is used to manage packages. Install APM as described in the
[APM installation section](#apm-installation), or update it to the latest version by running:

```shell
apm self-update
```

## Quick start

### Register the marketplace

```shell
apm marketplace add Netcracker/qubership-ai-packages
```

### Install the recommended package set

Install it in the global user scope, then compile it.
The `--target` value is your local harness list. The example uses the default Qubership targets.

```shell
apm install qubership-user-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

### Optional: pin the marketplace version

The default marketplace registration tracks the `main` branch.
To pin the marketplace for reproducible installs, pass `--ref` with a release tag, branch, or commit SHA:

```shell
apm marketplace add Netcracker/qubership-ai-packages --ref <tag-or-sha>
```

## About APM

[Agent Package Manager (APM)](https://github.com/microsoft/apm) installs and deploys AI-agent primitives:
instructions, skills, prompts, agents, hooks, plugins, and MCP servers.

Use the official Microsoft APM docs for the full workflow:

- [APM quick start](https://microsoft.github.io/apm/quickstart/)
- [APM installation guide](https://microsoft.github.io/apm/getting-started/installation/)
- [APM CLI reference](https://microsoft.github.io/apm/reference/cli/install/)
- [APM package anatomy](https://microsoft.github.io/apm/concepts/package-anatomy/)
- [Primitives and targets](https://microsoft.github.io/apm/concepts/primitives-and-targets/)
- [`apm.yml` manifest schema](https://microsoft.github.io/apm/reference/manifest-schema/)

See the [package-manager evaluation](research/apm-research/) for a comparison with other open-source managers for
skills, MCP servers, and agent context.

### When to run `apm compile`

For project installs, `apm install` deploys primitives and runs `apm compile` internally during the integrate phase. Run
`apm compile` directly when you are iterating on local `.apm/instructions/*.instructions.md`, need flags such as
`--dry-run`, `--validate`, or `--clean`, or need to refresh generated root context files without changing
dependencies.

For global installs, run `apm compile -g` after `apm install -g` when the installed packages include instructions.
A global install fetches and deploys the package, but global compilation is explicit and writes user-scoped root
context files such as `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`.

See the official [APM compile guide](https://microsoft.github.io/apm/producer/compile/). The Claude-specific
discussion in [microsoft/apm#1807](https://github.com/microsoft/apm/issues/1807) explains why always-on or
read-only-session guidance may need native context-file placement instead of only path-scoped rules.

## APM installation

Install APM with the package manager for your platform when one is available.
Follow the [official APM installation guide](https://microsoft.github.io/apm/getting-started/installation/).

## Repository onboarding

- [Qubership repository onboarding skill](agent-packages/qubership-agent-support-pr/) — create an onboarding PR for a
  repository.

To add the Qubership repository baseline, install the marketplace and the onboarding skill globally:

```shell
apm marketplace add Netcracker/qubership-ai-packages
apm install qubership-agent-support-pr@qubership-ai-packages --target codex,claude -g
```

Then ask your agent to prepare the PR from inside the target Git repository:

```text
Use qubership-agent-support-pr to create a PR that adds Qubership agent support
to this repository.
```

The skill installs [`qubership-essentials`](agent-packages/qubership-essentials/) in the repository and prepares the
generated agent assets for the selected harnesses.

## Qubership user essentials

Recommended package to be used when working with any Qubership repository. It must be installed once, globally,
into the user space.

- [Qubership user essentials](agent-packages/qubership-user-essentials/) — the global baseline package.

Choose the agent harnesses you use and install the package globally. This example uses the default Qubership
targets; replace `--target` with the harnesses you use:

```shell
apm marketplace add Netcracker/qubership-ai-packages
apm install qubership-user-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

## Guides

- [Consuming packages](docs/consuming-packages.md) — register the marketplace, then install, update, and remove
  packages.
- [Publishing packages](docs/publishing-packages.md) — add a package and release a new marketplace version.
- [Renovate APM dependency updates](docs/renovate-apm-dependencies.md) — understand Renovate APM PRs and the manual
  marketplace index refresh.
