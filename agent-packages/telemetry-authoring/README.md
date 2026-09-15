# telemetry-authoring

An APM package that decides **which signal an event owes, what that signal carries, and who decides where it goes**,
for libraries and services on the JVM, in Go, and in Python. It loads when a diff adds, removes, or changes a logger
call, a metric, or a span, and when a change adds a branch that fails, retries, falls back, or clamps a value.

## What it governs

- The mode: whether the artifact is a library, whose host decides where output goes, or a service with its own entry
  point.
- The signal: a record, an instrument, a span, the caller's channel, or nothing, chosen by a procedure that first
  tests whether an existing signal of the right kind already carries the fact.
- The record: one completion record per unit of work, plus interval progress, state transitions, and gated
  diagnostics; the joining identifier or trace context, the branch that produced a value, the names a reader can
  set, and which state it reports.
- The instrument: the question it answers, a failure rate computable from one label set, low-cardinality reasons
  and bounded labels, and a threshold that lives in the alert while the code exports the raw measurement.
- The span: one span per operation, status from the operation's final outcome, the exception recorded once at the
  frame that handles it and correlated with the span, and new events as log records.
- What a library may emit: it does not decide where its output goes, it returns an error instead of also logging
  it, and it carries the host's context across the concurrency it creates.
- Severity: the axis is who must act; the repository's convention owns the ladder, checked against the neighboring
  calls.

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
