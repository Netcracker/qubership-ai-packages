# adr-authoring

An APM package that helps agents write Architecture Decision Records following the
ADR contract used across Qubership repositories: one decision per record, stored
under `docs/adr/` with a `NNNN-kebab-slug.md` filename, a
`Proposed | Accepted | Rejected | Superseded` status, ISO 8601 dates, and
immutable accepted records superseded by new ones.

## Contents

- `.apm/instructions/adr-authoring.instructions.md` — the trigger merged into
  `AGENTS.md` / `CLAUDE.md` by `apm compile`.
- `.apm/skills/adr-authoring/SKILL.md` — the on-demand how-to: local conventions
  plus the ADR template.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/adr-authoring
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/adr-authoring@v1.1.0
```

Then run `apm install` and `apm compile` to merge the trigger into your local
`AGENTS.md` / `CLAUDE.md`.
