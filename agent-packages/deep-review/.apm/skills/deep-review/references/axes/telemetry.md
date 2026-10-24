# Axis: telemetry

Finding prefix: `TEL`.

Call site by call site, does each fact the code makes true leave through the right signal, carrying what its reader
needs, at a rate the host can afford, and into a destination the right party chose? For every fact you inspect, ask
one question first: does it owe a record, an instrument, a span, the caller's channel, or nothing? The rest of the
axis follows from the answer. A fact that emits nothing where it owes a signal is as much a finding as a signal that
is wrong.

The rules come from the `telemetry-authoring` skill, at the path your prompt gives. Read it in full before you start,
then the one file under its `references/` that its §0 selects for each component's ecosystem (`go.md`, `jvm.md`,
`python.md`). Apply §1–§8 and use §10 as the per-call-site checklist. Do not report §9's question (holding only the
text, would an engineer wait or intervene?) as a finding: name it under *Open questions* and leave the drill to
`observability-operability`. Judge the wording of log messages and span or event text by the `english-developer-style`
skill, section "Error and log messages", plus its §5 rules on digits a reader greps and on the `MessageFormat`
apostrophe.

**JavaScript and TypeScript have no reference file.** Judge them by the skill's language-independent rules and the
platform's own conventions, and say so in coverage. In Node, `console.*` in library code is the ambient acquisition
of §6. A library takes a logger from its caller or a named channel the host enables (the `debug` convention).
`@opentelemetry/api` is a no-op until the host registers an SDK. Context is ambient through `AsyncLocalStorage` and
is lost across hand-rolled callback queues. In the browser, the questions are whether unhandled errors and rejections
reach a reporter at all, and whether outbound `fetch` carries the trace header the backend joins on.

**A `focus` note narrows which call sites you walk, never the question.** An agent focused on records still
classifies every fact it reads by §2, so a log line that should have been a counter is its finding. Every slice fills
the inventory for its own paths.

## What counts as a finding

- **Wrong signal for the fact (§2).** A path that logs an error and also returns or rethrows it; a handler whose
  whole body is a log call; a log line whose text is a count, a rate, or a duration (§4); a second signal for a fact
  an existing one already carries with its distinguishing value (branch 1).
- **A silent branch.** A failure, retry, fallback, clamped value, or given-up state whose §2 branch is 3 or 4 and that
  emits nothing, with no existing signal carrying the distinguishing value. In service mode, a whole component that
  emits nothing on its failure paths counts as well. Name the branch and the question nobody can answer because of it.
- **A record its reader cannot use (§3).** No joining identifier where units run concurrently; the clamped and the
  unclamped case print the same text; a private field name where the reader holds a property, a flag, or an
  environment variable; "still retrying" and "gave up" sharing text and level; a published state with no transition
  time; a filter value interpolated into prose in a repository that logs structurally.
- **Rate (§3).** A record per item, per row, per message, or per attempt inside a retry loop; a library or reconciler
  that reports an unchanged state on every pass instead of on transition; an expensive argument outside a guard (in Go
  the arguments are always evaluated). State the rate in records per unit of input.
- **An instrument that cannot answer its question (§4).** A label carrying an id, a path, a query, an address, or an
  error message, with the value count quantified; a failure counter with no attempts counter on the same path; error
  reasons built from exception text; one timer for success and failure together; a compiled-in threshold deciding
  whether to emit.
- **Span misuse (§5).** A manual span around an already-instrumented HTTP or database client; an exception logged
  under an active span instead of recorded on it; `addEvent` in new code.
- **The library contract (§1, §6).** A configuration call or an ambient-logger acquisition in library-mode code; a
  logging provider, telemetry SDK, exporter, or concrete registry in the published compile or runtime scope; a hook
  that also registers a default; a warning that tells the caller to change their code.
- **Lost or stale context (§8, §6).** A goroutine or task started without the caller's context; `context.Background()`
  on a request path; an executor that drops MDC; an MDC `put` or a context variable set with no removal on the failure
  path; an outbound call that does not propagate the trace header.
- **Severity that misleads (§7).** A level that disagrees with neighboring calls for the same kind of event; a
  warning or error for a condition the code handled and the reader cannot act on; a recoverable retry logged as error.
- **A message that cannot be grepped or acted on.** No offending identifier or value; a message that only restates
  the exception type; locale-grouped digits from a JVM formatter; an apostrophe in a `MessageFormat` pattern that
  silences the placeholders after it.

## What is not a finding

- A level ladder you would have chosen differently, where the call agrees with its neighbors (§7, §9).
- A library that logs. §6 permits it; only the rate and the routing are in scope.
- No metrics in a repository that exports none. §4's "recurring and logged is also counted" rule is suppressed by
  mode, so record it once in the inventory and leave the operational consequence to `observability-operability`.
- A recorded decision to emit nothing (§2 branch 5).
- Wording taste beyond reason, action, consequence, and a greppable identifier.
- Telemetry in tests, examples, and generated code, unless it ships in the published artifact.
- Each instance of a shape a configured linter already reports. Where the linter (§0's reference file names it) is
  not configured, report its absence once, list the instances as evidence, and name the rule id.

## Method

1. **Inventory first.** For each component: the entry point and any configuration call (mode, §1); the logging API
   and provider from imports and the published dependency metadata; structured fields or not; every instrument with
   its label keys; tracer setup and auto-instrumentation; how context crosses its concurrency boundaries; which
   telemetry linter CI runs. `git grep` for logger acquisition, configuration calls, metric constructors, span
   starts, and MDC, `contextvars`, or `ctx` plumbing gives most of it.
2. **Run the linters** the reference file names (`sloglint`, `contextcheck`, `loggercheck`; Ruff `LOG`, `G`, `TRY4`;
   Sonar S2139 or the Error Prone equivalent) in the throwaway copy if CI does not run them. Triage the output and
   remember what a clean verdict does not establish (each reference file's last section).
3. **Sweep the failure branches.** In the components the profile marks as load-bearing, enumerate the catch blocks,
   `if err != nil` returns, `except` clauses, retry loops, fallbacks, and clamps. For each, write down the §2 branch
   that applies and the signal that exists. This table is the absence check; state how many branches you classified
   and in which files.
4. **Walk the record call sites** on those paths for rate, contents, level against the neighbors, and wording.
5. **Measure instruments and silence.** Execute where cheap: run a test or the binary and dump the registry or scrape
   `/metrics` to count label values; run a library entry point with no host configuration and capture what reaches
   stdout or stderr. A label bounded only by a fixture passes reading and fails in production (§4).
6. **Trace context** across every thread, goroutine, task, and outbound HTTP boundary the components create.

## Required section: Signal inventory

One row per component, written before the findings. `observability-operability` runs its drill from this table, so
fill every cell, and write `none` rather than leaving one blank.

| Component (path) | Mode, with evidence | Logging API / provider | Structured | Records: call sites, levels | Instruments: names, label keys | Spans: manual, auto | Context propagated: yes / no / partial, and the boundary that drops it | Linter in CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Under the table, list the components and paths you did not examine, and the ecosystems you judged without a reference
file.

## Severity

Rate by what the signal costs its reader, as `observability-operability` does. `HIGH`: the signal points the reader
at the wrong action or the wrong unit, as a stale MDC naming the previous request does, or "retrying" and "gave up"
sharing one text; a give-up or data-dropping branch that emits nothing; a label whose measured value count can
overload the metrics backend. `MEDIUM`: a missing joining identifier, log-and-rethrow duplication, per-item records
on a path whose rate follows the input, a library imposing a provider or writing into a host that configured nothing.
`LOW`: a message without its identifier, or a level that disagrees with its neighbors without misleading anyone.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Per call site: which signal a fact owes, record contents, rate, and level; instrument shape and cardinality; span use; telemetry context across boundaries; what a library emits and through what; log message wording; a component or branch that emits nothing | `telemetry` |
| Whether an operator can reconstruct a failure from all emitted signals; alerting rules, dashboards, readiness and health; steady-state log volume as the operator sees it. It reads this axis's inventory | `observability-operability` |
| The error value: classification, hierarchy, wrapping, cause preservation, the shape a caller receives, and an error that never reaches the caller. How the failure is recorded (logged and rethrown, a handler that only logs), and silence on a branch that handles the failure on purpose (a retry, a fallback, a give-up), are `telemetry` | `error-model` |
| Secrets, tokens, and personal data in records, span attributes, or metric labels; log injection from untrusted input. Note it in one cross-axis line and do not develop it | `security` |
| The measured throughput or allocation cost of logging on a hot path. This axis reports the rate and the missing guard; `performance` measures what they cost | `performance` |
| Version, advisory, and license of the logging and telemetry artifacts. Whether a provider or SDK belongs in a library's published scope at all is `telemetry` (§6) | `dependencies` |
| Cancellation, deadlines, executor ownership, and thread lifecycle. Trace context and MDC across those boundaries are `telemetry` | `concurrency-lifecycle` |
| Renaming or removing a metric, a label, or a log field that dashboards and alerts consume | `api-compatibility` |
| Browser platform concerns: source maps, the bundle cost of a reporting SDK, what the user sees on failure. Each browser emission call site, and an app that reports no unhandled errors at all, are `telemetry` | `frontend-web` |
| Kubernetes Events and status conditions | the owner the `kubernetes` surface pack names |
| Documentation of metrics and log fields; tests that assert telemetry; a running demonstration | `docs-pages`, `tests`, `runtime-verification` |
