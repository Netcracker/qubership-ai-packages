# qubership-ai-packages

This repository is an APM marketplace of Qubership agent packages. Use it to install shared skills, instructions, and
umbrella packages for agents such as Claude Code, Codex, Cursor, and GitHub Copilot.

## Contents

- [Quick start](#quick-start)
- [APM quick start](#apm-quick-start)
- [APM CLI installation](#apm-cli-installation)
- [Repository onboarding](#repository-onboarding)
- [User workspace onboarding](#user-workspace-onboarding)
- [Guides](#guides)

## Quick start

Install the `apm` CLI first. See [APM CLI installation](#apm-cli-installation) below.

Register the marketplace and install the global Qubership baseline into the agent harnesses you use:

```bash
apm marketplace add Netcracker/qubership-ai-packages
apm marketplace browse qubership-ai-packages
apm install qubership-global-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

The `--target` value is your local harness list. The example uses the default Qubership targets.

The default marketplace registration tracks `main`. To pin the marketplace for reproducible installs, pass `--ref`
with a release tag, branch, or commit SHA:

```bash
apm marketplace add Netcracker/qubership-ai-packages --ref <tag-or-sha>
```

## APM quick start

[Agent Package Manager (APM)](https://github.com/microsoft/apm) installs and deploys AI-agent primitives:
instructions, skills, prompts, agents, hooks, plugins, and MCP servers.

Use the official Microsoft APM docs for the full workflow:

- [APM quick start](https://microsoft.github.io/apm/quickstart/)
- [APM installation guide](https://microsoft.github.io/apm/getting-started/installation/)
- [APM CLI reference](https://microsoft.github.io/apm/reference/cli/install/)
- [APM package anatomy](https://microsoft.github.io/apm/concepts/package-anatomy/)
- [Primitives and targets](https://microsoft.github.io/apm/concepts/primitives-and-targets/)
- [apm.yml Manifest Schema](https://microsoft.github.io/apm/reference/manifest-schema/)

See the [package-manager evaluation](research/apm-research/) for the comparison against other open-source skill, MCP,
and agent-context managers.

### When to run `apm compile`

For project installs, `apm install` deploys primitives and runs compile internally during its integrate phase. Run
`apm compile` directly when you are iterating on local `.apm/instructions/*.instructions.md`, need flags such as
`--dry-run`, `--validate`, or `--clean`, or need to refresh generated root context files without changing
dependencies.

For global installs, run `apm compile -g` after `apm install -g` when the installed packages include instructions.
Global install fetches and deploys the package, but global compilation is explicit and writes user-scope root context
files such as `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`.

See the official [APM compile guide](https://microsoft.github.io/apm/producer/compile/). The Claude-specific
discussion in [microsoft/apm#1807](https://github.com/microsoft/apm/issues/1807) explains why always-on or
read-only-session guidance may need native context-file placement instead of only path-scoped rules.

## APM CLI installation

Install APM with the package manager for your platform when one is available.

### Homebrew

```bash
brew install microsoft/apm/apm
```

### Scoop

```powershell
scoop bucket add apm https://github.com/microsoft/scoop-apm
scoop install apm
```

### pip

```bash
pip install apm-cli
```

### Arch Linux

APM is available from the Arch User Repository as the community-maintained `apm-bin` package:

```bash
yay -S apm-bin
```

### Install script

Use the official install script if your package manager is not listed above.

Linux and macOS:

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

Windows PowerShell:

```powershell
irm https://aka.ms/apm-windows | iex
```

### Verify the installation

```bash
apm --version
```

### Stay up to date

Use the latest available `apm` CLI for your installation method:

```bash
brew upgrade apm
pip install --upgrade apm-cli
apm self-update
```

For Scoop, run:

```powershell
scoop update apm
```

For Arch Linux AUR installs, update `apm-bin` through your AUR helper:

```bash
yay -Syu apm-bin
```

## Repository onboarding

- [Qubership repository onboarding skill](agent-packages/qubership-agent-support-pr/) — create an onboarding PR for a
  repository.

To add the Qubership repository baseline, install the marketplace and the onboarding skill globally, then ask your
agent to prepare the PR from inside the target Git repository:

```bash
apm marketplace add Netcracker/qubership-ai-packages
apm install qubership-agent-support-pr@qubership-ai-packages --target codex,claude -g
```

```text
Use qubership-agent-support-pr to create a PR that adds Qubership agent support
to this repository.
```

The skill installs [`qubership-essentials`](agent-packages/qubership-essentials/) in the repository and prepares the
generated agent assets for the selected harnesses.

## User workspace onboarding

- [Qubership global essentials](agent-packages/qubership-global-essentials/) — the global baseline package.

Choose the agent harnesses you use and install the package globally. This example uses the default Qubership
targets; replace `--target` with the harnesses you use:

```sh
apm marketplace add Netcracker/qubership-ai-packages
apm install qubership-global-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

## Guides

- [Consuming packages](docs/consuming-packages.md) — register the marketplace, then install, update, and remove
  packages.
- [Publishing packages](docs/publishing-packages.md) — add a package and release a new marketplace version.
