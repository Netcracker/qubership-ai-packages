# qubership-user-essentials

Umbrella APM package with the Qubership agent setup for a global user workspace. Install it once per developer machine
so your agent uses the same baseline across repositories.

This package replaces [`qubership-global-essentials`](../qubership-global-essentials/). The name pairs with
[`qubership-repo-essentials`](../qubership-repo-essentials/): `repo` is the per-repository baseline, `user` is the
per-developer superset. This package has no content of its own — it pulls in the repository baseline plus the packages
that only make sense user-wide. Through the repository baseline it now also carries `qubership-workflow-hub-usage`,
which `qubership-global-essentials` used to leave out.

## Install

Register the marketplace first:

```sh
apm marketplace add Netcracker/qubership-ai-packages
```

Then choose the agent harnesses you use and install the package globally. This example uses the default Qubership
targets; replace `--target` with the harnesses you use:

```sh
apm install qubership-user-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

`apm install -g` does not write user-scope root context files. Run `apm compile -g` after installing this package so
global instructions reach targets that read files such as `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`. See the
[APM compile guide](https://microsoft.github.io/apm/producer/compile/) and the placement discussion in
[microsoft/apm#1807](https://github.com/microsoft/apm/issues/1807).

## What it pulls in

- [`qubership-repo-essentials`](../qubership-repo-essentials/) — the per-repository baseline: `apm-authoring`,
  `english-us-developer-style`, `markdown-line-length-120`, and `qubership-workflow-hub-usage`.
- [`codex-review`](../codex-review/) — Codex CLI code review with auto-fix, repeated until the review is clean.
- [`qubership-agent-support-pr`](../qubership-agent-support-pr/) — create a PR that adds Qubership baseline agent
  support to a repository.
- [`triage-dependency-prs`](../triage-dependency-prs/) — triage failing checks on Renovate and Dependabot PRs.
- [`enable-renovate-automerge`](../enable-renovate-automerge/) — enable Renovate automerge behind a real required
  check.
- [`adr-authoring`](../adr-authoring/) — write Architecture Decision Records that follow the Qubership ADR contract.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new member on their next `apm update`.
