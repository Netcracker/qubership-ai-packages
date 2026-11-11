# adr-authoring

An APM package that helps agents write Architecture Decision Records that an agent can
write code under and a person or an agent can check code against: one decision per record,
a defined vocabulary, numbered behavior or structural rules that name the code they
constrain and the check that confirms them, a `Proposed | Accepted | Rejected | Superseded`
status, ISO 8601 dates, and accepted records that a new record supersedes rather than an
edit, apart from their confirming checks and implementation notes. Only a
decision becomes a rule: a defect in the code goes to the user as a proposed
issue, and a dependency's own guarantee is at most a fact in **Context**. A record
stays in the repository's existing directory, or in `docs/adr/` with a
`NNNN-kebab-slug.md` filename where there is none.

## Contents

- `.apm/instructions/adr-authoring.instructions.md` — the trigger merged into
  `AGENTS.md` / `CLAUDE.md` by `apm compile`.
- `.apm/skills/adr-authoring/SKILL.md` — the on-demand how-to: local conventions,
  the ADR template, how to write terms and numbered rules, the trailers a change
  carries, the reading guide a repository keeps, and how to check a change, with
  the verdicts of a check.
- `.apm/skills/adr-authoring/references/structural-invariant.md` — a whole record
  with structural rules, as an example of the template.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/adr-authoring
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/adr-authoring@v2.1.0
```

Then run `apm install` and `apm compile` to merge the trigger into your local
`AGENTS.md` / `CLAUDE.md`.
