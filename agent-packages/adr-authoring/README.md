# adr-authoring

An APM package that helps agents write Architecture Decision Records that a person or
an agent can check code against: one decision per record, a defined vocabulary, numbered
rules that name the layer holding them, a `Proposed | Accepted | Rejected | Superseded`
status, ISO 8601 dates, and immutable accepted records superseded by new ones. A record
stays in the repository's existing directory, or in `docs/adr/` with a
`NNNN-kebab-slug.md` filename where there is none.

## Contents

- `.apm/instructions/adr-authoring.instructions.md` — the trigger merged into
  `AGENTS.md` / `CLAUDE.md` by `apm compile`.
- `.apm/skills/adr-authoring/SKILL.md` — the on-demand how-to: the record template,
  the rules for writing a record, and the reading guide a repository keeps beside
  its records.

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
