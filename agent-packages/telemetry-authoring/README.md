# telemetry-authoring

An APM package that decides **which signal an event owes, what that signal carries, and who decides where it goes**,
for libraries and services on the JVM, in Go, and in Python. It loads when a diff adds, removes, or changes a logger
call, a metric, or a span, and when a change adds a branch that fails, retries, falls back, or clamps a value.

## What it governs

- The mode: whether the module is a library, whose host decides where output goes, or a service.
- The signal: a record, an instrument, a span, the caller's channel, or nothing, chosen by a rule with five branches
  that tests first whether an existing signal already carries the fact.
- The record: one per unit of work, or one per state transition where the code owns no unit of work; the joining
  identifier, the branch that produced a value, the names a reader can set, and which state it reports.
- The instrument: the question it answers, the attempts counter beside a failure counter, bounded reasons and
  labels, and thresholds that live in the alert.
- The span: no span around an already-instrumented call, and events as log records correlated with the span.
- What a library may emit: it does not decide where its output goes, it returns an error instead of also logging
  it, and it carries the host's context across the concurrency it creates.
- Severity: no ladder of its own; the repository's convention, checked against the neighboring calls.

Every rule carries its detection, and the reference files name the linter rule id where one exists.

## Contents

- `.apm/instructions/telemetry-authoring.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/telemetry-authoring/SKILL.md`: the rules and the review checklist.
- `.apm/skills/telemetry-authoring/references/`: `jvm.md`, `go.md`, `python.md`, one per ecosystem, each carrying
  what that ecosystem answers differently.

The research the skill was written from is in [`research/telemetry-authoring/`](../../research/telemetry-authoring/).

## Pairs with

- The developer-style skill of the language the message is written in (`english-developer-style` for English) owns
  the wording of a message.
- [`docs-page-authoring`](../docs-page-authoring/) owns the documentation entry a user-visible message owes.
- [`final-review`](../final-review/) runs a fixed checklist over a finished change.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/telemetry-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/telemetry-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.3.0`.

Then run `apm install` and `apm compile`.
