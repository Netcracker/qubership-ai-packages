# Axis: observability and operability

Finding prefix: `OPS`.

Two modes. Read the profile and pick the one that applies; running the wrong mode produces a report about a reader
who does not exist.

**When `telemetry` runs in the same review**, it judges each call site and you judge the outcome. You then run in the
`synthesis` phase, and your prompt is distilled from the evidence reports: start from the *Signal inventory* of the
`telemetry` report (one per slice when it was sliced), and cite its finding ids rather than re-reporting a call-site
defect it owns.

## Mode A — library

The question is whether the **host application** can see what this library is doing. When `telemetry` runs, it owns
the logging implementation, context propagation, and levels call site by call site; judge only whether the host can
see what it needs and turn off what it does not, and skip the first, third, and fifth questions below.

- Does the library impose a logging implementation, or does it use a facade the host already controls? Can the host
  turn its logging off, route it, and set its level?
- Are there metrics or instrumentation hooks, and are they optional? Is there a way to observe the things that matter
  (connections, retries, queue depth, latency) without patching?
- Does the library propagate the host's context — trace context, request id, cancellation — through its calls and
  into its threads? A thread pool that drops the context breaks the host's tracing, and the host cannot fix it.
- Does the library swallow information the host needs: exceptions logged and not rethrown, failures counted but not
  exposed, state reachable only through a private field?
- Is anything logged at a level the host will not expect — a retried transient failure at error level, or per-message
  logging at info?

## Mode B — service, operator, or CLI

Two readers matter, both without source access: an on-call engineer with `logs`, `describe`, and a dashboard; and an
automated triage agent whose entire input is status, events, logs, and metrics.

**Run the drill.** Pick at least six realistic failure modes from the profile and the other axes' reports. For each,
reproduce it if you can, otherwise trace the exact strings the code emits, then answer from those strings alone: what
does the reader see, does it say what happened and why, is the next action clear, and can the reader tell whether the
system is retrying or has given up? That last distinction decides whether they wait or intervene, and it is the most
common thing to get wrong.

Then judge the signals:

- **State.** Is the current state observable without the source? Can the reader distinguish "not started", "in
  progress", "waiting on something external", "failed and retrying", "failed and given up", and "diverged from the
  external truth"?
- **Logs.** In a healthy system at scale, what is the steady-state line rate — is there anything to notice? On
  failure, does one line carry the object, the operation, the correlation id, and the upstream status, or must the
  reader stitch five together? Are levels honest? Can the level be changed without a restart?
- **Correlation.** Is a request id propagated to every external call and back, so a line here can be joined to a line
  there? Is that documented where a person would look?
- **Metrics.** Take three questions an SRE will ask — how many things are stuck right now, is the dependency the
  problem or are we, did the last rollout make it worse — and establish whether the exported metrics answer them.
  Check naming against the ecosystem's conventions, and check label cardinality: any label carrying an object name, a
  namespace, or an error message is a risk — quantify it. When `telemetry` runs, naming and cardinality are its
  findings: cite its ids and its *Signal inventory*, and judge only whether the metrics answer the three questions.
- **Alerting.** Are there rules at all? If not, say what the four or five should be, as expressions.
- **Health.** Does readiness reflect anything real — dependencies, cache warm-up, leadership — or is it a constant?

## Rating

Rate by what the signal costs the reader, not by the size of the fix. A signal that leads a competent engineer to the
wrong action — restarting when they should fix configuration, waiting when the system has already given up — is
`HIGH`. A signal that is merely thin, so the reader digs further but is not misled, is `MEDIUM`.

Quote every string verbatim, including its defects, and say what a reasonable reader would wrongly conclude from it.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Signal choice, record contents and rate, levels, instrument cardinality, spans, and context propagation per call site | `telemetry` |
| Whether a reader can reconstruct a failure from all emitted signals; alerting; readiness and health; timeout ordering along a request chain | `observability-operability` |
