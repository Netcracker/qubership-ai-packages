# qubership-essentials

> **Deprecated:** Use [`qubership-repo-essentials`](../qubership-repo-essentials/) for new repository installations.
> This package remains available for existing consumers. Version 2.0.0 drops `codex-review` from its dependencies.

Umbrella APM package with the baseline agent setup every Netcracker/Qubership
repository gets by default. Depend on this one package and the agent picks up
the shared conventions through transitive APM dependencies — there is no content
of its own here, only the dependency list.

## What it pulls in

- [`apm-authoring`](../apm-authoring/) — guidelines for authoring APM packages
  (instructions, skills, prompts, agents, hooks).
- [`english-us-developer-style`](../english-us-developer-style/) —
  American-English style for developer-facing text.
- [`markdown-line-length-120`](../markdown-line-length-120/) — Markdown drafting
  rules for repositories that pin markdownlint `MD013.line_length` to 120.
- [`qubership-workflow-hub-usage`](https://github.com/Netcracker/qubership-workflow-hub/tree/main/agent-packages/qubership-workflow-hub-usage)
  — conventions for GitHub Actions workflows built on qubership-workflow-hub.

## What it leaves out

The review skills, [`codex-review`](../codex-review/) and [`cross-review`](../cross-review/), are not part of the
bundle. Both run the Codex CLI, which needs a Codex account of its own, and for a contributor without one the skill
fails when it reaches the Codex step. Depend on them directly if your repository wants agent-run Codex reviews.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new
member on their next `apm update`.
