# qubership-repo-essentials

Umbrella APM package with the baseline agent setup for new Netcracker/Qubership
repository installations. Depend on this one package and the agent picks up the
shared conventions through transitive APM dependencies — there is no content
of its own here, only the dependency list.

The deprecated [`qubership-essentials`](../qubership-essentials/) package
remains available with its original dependency set for existing consumers.
This package states the repository installation scope explicitly and excludes
`codex-review`; depend on [`codex-review`](../codex-review/) directly if your
repository wants agent-run Codex reviews.

## What it pulls in

- [`apm-authoring`](../apm-authoring/) — guidelines for authoring APM packages
  (instructions, skills, prompts, agents, hooks).
- [`english-us-developer-style`](../english-us-developer-style/) —
  American-English style for developer-facing text.
- [`markdown-line-length-120`](../markdown-line-length-120/) — Markdown drafting
  rules for repositories that pin markdownlint `MD013.line_length` to 120.
- [`qubership-workflow-hub-usage`](https://github.com/Netcracker/qubership-workflow-hub/tree/main/agent-packages/qubership-workflow-hub-usage)
  — conventions for GitHub Actions workflows built on qubership-workflow-hub.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new
member on their next `apm update`.
