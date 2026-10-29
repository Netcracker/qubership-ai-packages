# Seed for `telemetry-authoring`

This file is the three-part seed required by `skill-research` §1. It is **context, not the target**. Part 2 is stated
from practice and sourced nowhere. A source that contradicts any of it is a finding worth reporting.

## Part 1 — what practice already produced

House text that already covers a slice of this ground. It is unsourced house convention, not literature.

| Where | What it says | What it does not say |
| --- | --- | --- |
| `deep-review/references/axes/observability-operability.md` | Two review modes. **Mode A (library):** does the library impose a logging implementation; can the host turn it off, route it, set its level; are metrics optional hooks; does it propagate the host's trace context through its calls and into its threads; does it swallow information the host needs; is anything logged at a level the host will not expect. **Mode B (service):** two readers without source access, an on-call engineer and an automated triage agent; run a drill over six realistic failure modes and answer from the emitted strings alone; is state observable ("not started", "in progress", "waiting on something external", "failed and retrying", "failed and given up", "diverged from the external truth"); steady-state line rate; does one line carry the object, the operation, the correlation id and the upstream status; are levels honest; correlation id propagated to every external call and back; three SRE questions a metric set must answer; label cardinality; alerting rules; does readiness reflect anything real. Rating: a signal that leads a competent engineer to the **wrong action** is HIGH; a signal that is merely thin is MEDIUM. | It is a **review** axis, invoked only by `/deep-review` over a whole repository, and explicitly "Not for reviewing a single pull request or diff". It never fires while the code is being written. It says nothing about which signal an event owes. |
| `english-developer-style` §7 "Error and log messages" | Wording only: reason + action + consequence; no `please`, no `sorry`; name the offending input; include identifiers a developer can grep; logs add structured fields rather than padding the message; the message is bound to the vocabulary of the code it reports on; a warning describes a situation the program is handling, an error one it is not. Plus the `java.text.MessageFormat` traps: an apostrophe opens a quoted literal and kills the placeholders; a locale-aware formatter groups digits, so pass numbers as text. | Whether the event deserves a line at all, at which level, where the call goes, and what else must be in it. |
| `docs-page-authoring` §7 | One table row: a new or changed error, exception, or log line a user can see owes D5 the literal text in the reference entry or the troubleshooting page, naming the cause and the action. | Anything about the design of the signal. |
| `pgjdbc/AGENTS.md` | "Use the word the code uses" for error messages; wrap user-facing text in `GT.tr`. | House-specific. |
| `pgjdbc` `docs/content/documentation/logging.md` | The driver uses `java.util.logging` deliberately, to add no logging dependency; the root logger is `org.postgresql`; logging exists "mainly to debug the driver itself". | A decided question for that repository, recorded here so a pass does not report it as a defect. |

## Part 2 — positions stated from practice, sourced nowhere

These are the maintainer's and the assistant's positions from the design conversation of 2026-09-12. **None is
sourced.** The ones marked *weakest* are where the research should push hardest.

| # | Position | Note |
| --- | --- | --- |
| S1 | The choice between a log line, a metric, a span, and emitting nothing is **one decision with four outcomes**, so it cannot be split across three skills; whichever skill does not own it will state a partial version and the versions will drift. | Structural. Supported by a house audit that found 18 duplications and 10 contradictions between two skills describing one predicate. |
| S2 | The primary split inside the skill is **library versus service**, not language. Language decides mechanics only. The mode boundary is per module, not per repository, and the test is: *does something outside this code configure the output?* | *weakest* — needs external evidence that the library/application distinction is a real fault line in practice and not a house idea. |
| S3 | The most common correct outcome is **emit nothing**: the state is already observable through a signal that exists. | *weakest* — no source known; plausible but untested. |
| S4 | A library does not choose the logging backend and does not export metrics itself. JVM: depend on a facade, never an implementation. Python: `getLogger(__name__)` plus `NullHandler`, never `basicConfig`, never touch the root logger. Go: accept a logger, do not install a global handler. | Mechanics asserted from memory; each ecosystem's primary source must confirm or correct. |
| S5 | **Log or return, never both.** A library that logs and rethrows duplicates the record and takes a decision that belongs to the host. | Believed idiomatic in Go; needs checking for JVM and Python, and for the case where the library is the last frame that knows the cause. |
| S6 | Do not drop the host's context across a thread, goroutine, or task boundary. The rule is the same in every ecosystem; the failure differs (a thread pool loses the ambient context; a goroutine started without the context propagates nothing). | Mechanics asserted; primary sources must confirm per ecosystem. |
| S7 | A signal must let the reader distinguish **still working / degraded / given up**. Getting this wrong is the most common defect, because it decides whether the reader waits or intervenes. | House text (Mode B) states it; no external source known. |
| S8 | For a monotonic state, log **on change, not on occurrence**, so the steady state is silent and the line rate is bounded. | *weakest* — stated from one example. |
| S9 | A metric is authored under a **named question**. A metric added without the question it answers cannot be alerted on and usually cannot be read. | No source known. |
| S10 | A line carries the identifier that joins it to its neighbours: the connection, the request, the query. Without it, N concurrent workers produce N interleaved streams that cannot be separated. | Believed standard; the research should return the accepted vocabulary for this. |
| S11 | Numbers in a message are not passed through a locale-aware formatter. | Measured in the session against pgjdbc: `Logger.log` with an `Object[]` renders `103887667` as `103,887,667` in `en-US` and `103 887 667` in `fr`, and the same repository already works around it with `String.valueOf` in `PGStream.increaseByteCounter`. This one is measured, not asserted. |
| S12 | A log line that reports a computed value must say **which constraint bound it**, not only the inputs of the computation. | Derived from failure F2 below; generalisation untested. |

## Part 3 — the recorded failures

### F1 — model failure, 2026-09-12, this session's transcript

Asked to review pgjdbc PR #2837, which adds a single FINE log statement to the adaptive-fetch path, the first review
covered the wording of the message and the documentation the change owed, and **never asked whether the line answers
the operator's question**. The question surfaced only when the maintainer asked whether any skill covers "SRE,
production monitoring, debugging". Two defects went unfound in the first pass and were found only after the question:

- the line prints the inputs of the fetch-size computation but never says which limit bound the result, so the reader
  cannot tell "still adapting" from "clamped at `adaptiveFetchMaximum` and will now overrun the buffer forever" —
  which is the exact failure the PR author was debugging;
- the line carries no connection identifier, though the cache that produces it is one per connection, so a pooled
  application produces N interleaved streams that cannot be separated.

The skills that were loaded (`docs-page-authoring`, `english-developer-style`) both fired correctly and neither has a
place for either defect.

### F2 — human failure, pgjdbc PR #2837 (open since 2023-03-04)

The log statement prints `maximumResultBufferSizeBytes`, `minimumAdaptiveFetchSize`, `maximumAdaptiveFetchSize` —
the first of which exists nowhere in the codebase, and the other two are private fields. The connection properties the
reader sets are `maxResultBuffer`, `adaptiveFetchMinimum`, `adaptiveFetchMaximum`. A reader holding a connection string
cannot grep the log for the property they set.

### F3 — the gap, recorded as a gap

**No Go or Python failure has been recorded yet.** Both failures above are JVM. The reader table and every rule in
part 2 therefore risk a JVM shape, with the Go and Python reference files bolted on afterwards. Pass 1 is asked to
report where the ecosystems differ **in kind** rather than in API, and whether the library/service split (S2) is the
right primary axis in ecosystems whose idiom differs from the JVM's.
