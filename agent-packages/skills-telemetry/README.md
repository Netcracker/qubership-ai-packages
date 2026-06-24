# skills-telemetry

Hooks that call the `skills-telemetry` CLI after each skill invocation. Install the package
into a repository and every skill call is recorded — no code changes, no agent configuration.

Three harnesses are supported:

| Harness    | Hook event           | Trigger                                              |
|------------|----------------------|------------------------------------------------------|
| Claude Code | `PreToolUse`        | Fires when the `Skill` tool is invoked               |
| Codex      | `Stop`               | Fires at the end of a turn                           |
| Cursor     | `afterAgentResponse` | Fires after each agent response                      |

Each hook runs `skills-telemetry ingest --agent=<harness>`, which detects the skill, queues an
event to the local outbox, and flushes over OTLP/HTTPS. The command always exits 0 so a
delivery failure never blocks the agent.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/skills-telemetry
```

Or add it to `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/skills-telemetry
```

Then run `apm install` and `apm compile`.

## Prerequisites

The `skills-telemetry` binary must be on `PATH` (`~/.local/bin/skills-telemetry`) and
provisioned with an endpoint and token. Install the companion
`skills-telemetry-configure` package as a dev dependency to get the setup skill:

```sh
apm install --dev denifilatoff/skills-telemetry/agent-packages/skills-telemetry-configure
```

Run the `provision-skills-telemetry` skill inside your agent to complete the setup.
