# Axis: telemetry

Can someone who holds only what the change emits, a log record, a metric, a span, or the text of an error, tell what
happened and what to do, and can the host afford what the change emits? Load `telemetry-authoring` and the reference
file it names for the repository's ecosystem. Wording, tense, sentence length, and dialect of a message belong to the
developer-style skill of the language the message is written in (`english-developer-style` for English); load it too.

## Check

Run the skill's *Review checklist* over the diff. Beyond the calls the diff touches, it reaches these:

- Every branch the change adds that ends in a failure, a retry, a fallback, a clamped value, or a state a reader may
  wait on: name the signal it owes and does not emit. A branch that emits nothing is a finding only where the skill says
  the fact owes a signal.
- The text of every exception, error response, or failed build, CLI, or CI check the change adds or rewords, outside
  tests: whether a reader who holds only that text can tell what failed and what to do. The failure message of a test
  belongs to the tests axis.
- Every thread, task, or goroutine the change starts, and every outbound call that takes a context: whether the
  caller's context crosses it.
- A published signal the change removes or renames, in a service a metric or a record the default configuration emits:
  ask where a dashboard, an alert, or a parser reads it.

## Severity

A failure that the change makes silent, where an operator acted on the signal before, is `major`, and so is a metric
attribute with unbounded values on a path that runs per request. A log call beside a throw or return of the same error,
an error text that names neither the input nor the remedy, and a log level that disagrees with its neighbors where an
alert filters on it are `minor`. A log level that no alert reads and that keeps a per-unit record out of the default
output, where the neighbors use another, is a `nit`.
