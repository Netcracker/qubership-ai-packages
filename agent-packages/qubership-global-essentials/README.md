# qubership-global-essentials

Umbrella APM package with Qubership agent skills and instructions that are useful in a global user workspace. Install
it once per developer machine so your agent can use the same baseline across repositories.

This package has no content of its own. It pulls in transitive APM dependencies and deliberately does not include
repository-local telemetry hooks or `qubership-workflow-hub-usage`.

## Install

Register the marketplace first:

```sh
apm marketplace add Netcracker/qubership-ai-packages
```

Then choose the agent harnesses you use and install the package globally. This example uses the default Qubership
targets; replace `--target` with the harnesses you use:

```sh
apm install qubership-global-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

Use a different `--target` list if your local agent setup uses different harnesses.

`apm install -g` does not write user-scope root context files. Run `apm compile -g` after installing this package so
global instructions reach targets that read files such as `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`. See the
[APM compile guide](https://microsoft.github.io/apm/producer/compile/) and the placement discussion in
[microsoft/apm#1807](https://github.com/microsoft/apm/issues/1807).

## What it pulls in

- [`apm-authoring`](../apm-authoring/) — guidelines for authoring APM packages.
- [`codex-review`](../codex-review/) — Codex CLI code review with auto-fix, repeated until the review is clean.
- [`english-us-developer-style`](../english-us-developer-style/) — American-English style for developer-facing text.
- [`markdown-line-length-120`](../markdown-line-length-120/) — Markdown drafting rules for repositories that pin
  markdownlint `MD013.line_length` to 120.
- [`qubership-agent-support-pr`](../qubership-agent-support-pr/) — create a PR that adds Qubership baseline agent
  support to a repository.
- [`triage-dependency-prs`](../triage-dependency-prs/) — triage failing checks on Renovate and Dependabot PRs.
- [`enable-renovate-automerge`](../enable-renovate-automerge/) — enable Renovate automerge behind a real required
  check.
- [`adr-authoring`](../adr-authoring/) — write Architecture Decision Records that follow the Qubership ADR contract.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new member on their next `apm update`.
