# qubership-essentials

Umbrella APM package with the baseline agent setup every Netcracker/Qubership
repository gets by default. Depend on this one package and the agent picks up
the shared conventions through transitive APM dependencies — there is no content
of its own here, only the dependency list.

## What it pulls in

- [`apm-authoring`](../apm-authoring/) — guidelines for authoring APM packages
  (instructions, skills, prompts, agents, hooks).
- [`codex-review`](../codex-review/) — Codex CLI code review with auto-fix,
  repeated until the review is clean.
- [`english-us-developer-style`](../english-us-developer-style/) —
  American-English style for developer-facing text.
- [`markdown-line-length-120`](../markdown-line-length-120/) — Markdown drafting
  rules for repositories that pin markdownlint `MD013.line_length` to 120.
- [`qubership-workflow-hub-usage`](https://github.com/Netcracker/qubership-workflow-hub/tree/main/agent-packages/qubership-workflow-hub-usage)
  — conventions for GitHub Actions workflows built on qubership-workflow-hub.
- [`ai-agent-telemetry`](https://github.com/Netcracker/qubership-ai-agent-telemetry/tree/main/agent-packages/ai-agent-telemetry)
  — hooks that report skill-usage telemetry after each skill invocation.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new
member on their next `apm update`.
