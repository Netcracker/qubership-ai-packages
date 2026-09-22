---
name: telemetry-authoring
description: >-
  Load when a diff adds, removes, or changes a call to a logger, a metric, or a span, and when a
  change adds a branch that ends in a failure, a retry, a fallback, a clamped value, or a state a
  reader may wait on: load it before the first logger call is written, not when the pull request is
  due. Also load to decide whether an event deserves a signal at all, which signal it owes, what the
  record must carry, what a library may emit into a host it will never see, whether a new instrument
  is worth its cardinality, and how to review instrumentation somebody else wrote. Governs the choice
  between a record, an instrument, a span, the caller's channel, and nothing; what each carries; the
  rate at which it may be emitted; and which decisions belong to the host rather than to the code
  emitting. The wording of the message is the developer-style skill's, for the language the
  message is written in, and the documentation a user-visible message owes is
  docs-page-authoring's; load those too.
---

# Authoring telemetry

This skill governs **which signal an event owes, what that signal carries, and who decides where it goes**. Wording,
tense, sentence length, and dialect of the message belong to the developer-style skill of the language the message is
written in (`english-developer-style` for English); load it too. The documentation entry a user-visible message owes
belongs to `docs-page-authoring` §7. Alerting rules, dashboards, retention, and vendor choice are outside it.

Every rule states its detection next to its prescription: the detection is what a reviewer checks, and a rule with no
detection is not applied. Where a linter reports a rule, the ecosystem file in `references/` names the rule id.

The reader every rule serves holds an alert, no source access, and one decision: wait, or intervene.

## 0. Which reference to open

The rules below hold in every ecosystem. What a host sees when it configures nothing, how a logger is obtained, how
fields attach, whether formatting is deferred when the call is discarded, and which linter reports what, are in
`references/`, one file per ecosystem. **Before writing the first call, read the file for the repository's
ecosystem**: `jvm.md`, `go.md`, `python.md`. Open no other.

Which file, in this order:

1. **The repository's instructions name the stack.** A line such as `Logging: SLF4J API, Micrometer for metrics,
   OpenTelemetry API for traces` selects the file and settles the mechanics. Where the line is missing, propose it in
   the pull request that adds the instrumentation.
1. **Otherwise the imports of the nearest existing call decide**, then the build file.

## 1. The mode

**The mode is per deployable artifact.** Code is in **service mode** when it is built into an artifact that contains
its own entry point, and the entry point configures where output goes. Code is in **library mode** when it is published
for hosts its author never sees, and a host decides where its output goes.

Inside a service, the configuration calls of §6 belong to the entry-point module and to nothing else. A package of a
microservice is part of the service: it does not configure output, and it does not need a hook or a no-op API either,
because the artifact it ships in configures both.

Detection of library mode: the artifact has no entry point and is published under its own coordinates. A change that
calls a configuration API and defends it as service mode is checked against the same artifact for an entry point.

The mode changes three things: whether a configuration call is permitted at all (§6), whether the build may carry a
provider, an SDK, or an exporter (§6), and whether an instrument is registered with a destination or only defined
through a no-op API or a hook (§6). What the unit of work is (§3) does not depend on the mode.

## 2. Which signal the fact owes

For a fact the change makes true, run the steps in order. Steps 1 and 2 end the procedure. Steps 3 and 4 are
independent: check both, and emit both where both apply. Step 5 applies when neither does.

| # | Step | Condition | Outcome |
| --- | --- | --- | --- |
| 1 | **Already recoverable** | An existing signal of the kind the question needs carries the fact *and* the value that distinguishes this case | **Nothing.** Name the existing signal in the review note |
| 2 | **The caller can act** | The caller can prevent or repair it | **The caller's channel**: return, raise, or the ecosystem's warning channel, and **not also** a log call |
| 3 | **Asked in aggregate** | The question is "how often, how long, how many right now" | **An instrument** (§4) |
| 4 | **Asked about one unit** | The question is "what happened to this one", and the aggregate cannot reconstruct it | **One record** (§3) |
| 5 | Neither 3 nor 4 | — | **Nothing**, and the review note says so |

**Step 1 is first because the common failure is a second signal for a fact already carried.** The kind matters: a
sampled trace or a debug record does not answer an aggregate question, and a counter does not answer "what happened
to this request", so neither suppresses the other. The check is that the named signal carries the distinguishing
value: a line that reports "a value was computed" does not cover "the value hit its limit".

**Step 2 is the rule a reviewer checks mechanically.** An error that leaves the function goes to the caller. An error
handler whose whole body is a log call has not handled the error. Detection: a log call and a throw or return of the
same error on one path; the JVM file names a linter rule for it, and in Go and Python the reviewer reads the path.
Two exceptions, and only these: at the frame that handles the error, and nowhere above it, the error is recorded once
under the rules of §5 where a span is active, or as an informational record at debug verbosity carrying the error as
a field where none is.

## 3. The record

A record is one entry about one unit of work.

**The unit of work is the operation the code completes for a caller**: a request, a message, a job, a reconciliation
attempt, a database operation. A library owns a unit of work when it completes an operation for its caller. Where the
code completes no operation for a caller, as in a cache, a pool, or a background maintenance loop, **the unit is the
state change**: emit on transition into a state and on transition out of it, not on each occurrence. Detection: a
record inside a loop, or on every call, that reports an unchanged state. A record that compares against a value that
always differs, such as a clock, reports no state; check that the compared value is the state.

**Rate.** One completion record per unit of work, plus these and nothing else:

- **Progress on an interval** for a unit that runs for minutes or longer. The interval is a duration constant, not a
  count of items. Detection: progress emitted per item.
- **Transition records** where the unit is the state change, one per transition.
- **Diagnostic records at debug verbosity**, under the same rate rule as info records. Detection: a debug record
  for a fact the reader needs in production, or a debug line at a verbosity the repository's default configuration
  never enables.

A service that emits one entry per request is in rule at any traffic level, because the rate follows the traffic.
Detection: more than one record on the success path of one unit, other than the three shapes above.

What every record carries:

| Carries | Why the reader needs it | Detection |
| --- | --- | --- |
| **The joining identifier** | Concurrent workers produce interleaved streams that cannot be separated without it | The record is emitted outside any active trace context the logging bridge attaches, and its fields carry no id of the request, connection, or unit. A class name is not an identifier: the value has to distinguish two concurrent units, not two code sites |
| **The branch that produced the value** | A record that prints its inputs and its result leaves the reader to re-derive which case fired | The clamped and the unclamped case produce the same text. Printing every input does not repair it: the *branch* has to be recoverable from the text |
| **Names the reader can set or grep** | A private field name sends a reader holding a configuration file to a search that returns nothing | Grep each name in the message against the settable names: the property, the flag, the environment variable. The user-facing spelling wins; renaming the private field to match is the wrong direction |
| **Which state it reports**, where a reader may wait on it | The reader's decision is wait or intervene, and "still retrying" and "gave up" must not share a text | The text and the level together leave the two indistinguishable. Adding the word "failed" is not enough: a counterpart record for the other outcome has to exist |
| **The transition time**, for a published state | "It has been stuck for ten minutes" is unanswerable without it | A status field, gauge, or condition published with no transition timestamp or last-success timestamp |

**A value the reader will filter or join on is a field, not prose inside the message.** Detection: the value is
interpolated into the message text in a repository that logs structurally. Adding it in both places duplicates it.

**Cost.** A log call inside a loop emits per item unless it is interval progress or a transition record: count in the
loop and record once after it. Detection: the enclosing block of a log call is a loop, and the call is neither interval
progress nor a transition record. A modulus guard is not aggregation; check that an aggregate is emitted after the loop.
An error path that can fire once per item is rate-limited or counted rather than recorded per occurrence, and lowering
the level does not repair it, because the rate rather than the level was unbounded. Where a record's arguments call a
method or build a string, guard the computation: every ecosystem evaluates the arguments of a discarded call, and only
the formatting is deferred, and only in some of them. Check that the expensive half is inside the guard.

## 4. The instrument

A fact someone will want aggregated over time is an instrument. Detection: a log line whose text is a count, a rate,
or a duration.

- **A new instrument is introduced with the question it answers, stated where the instrument is defined.** Whoever
  defines it states the question, because the host wiring it up cannot infer it; whoever registers it owns where it
  goes. Detection: no alert, dashboard, or stated question names it. A generic doc comment does not satisfy this;
  the stated question names a decision somebody makes.
- **The failure rate is computable from one label set.** Either one instrument carries an outcome attribute
  (`error.type` in the OpenTelemetry conventions), or the failure counter and the attempts counter share a label set
  on the same path. Detection: a failure counter with no attempts counter and no outcome attribute; or a denominator
  that counts different attempts.
- **Errors are counted by a low-cardinality reason.** The reason is the exception class, or an identifier from a
  closed set the code names; the convention's attribute is `error.type`. Detection: one error counter with no reason
  dimension, or a reason built from an exception message.
- **Latency for the successful outcome is separable from overall latency**, because fast failures make a combined
  timer look healthy. One histogram with an outcome attribute satisfies this. Detection: one timer around the call
  with no outcome dimension and no separate success timer.
- **A condition that is both recurring and logged is also counted**, where the repository exports metrics at all.
  Detection: a new log line for a recurring condition and no counter beside it.
- **A threshold that decides "slow", "stuck", or "too many" lives in the alert, and the emitting code exports the
  raw measurement.** A threshold in the code is in rule only beside a histogram of the same measurement, because
  then the reader can retune it. Detection: a constant compared against a measurement to decide whether to emit,
  with no instrument carrying the measurement. Making the constant configurable does not add the instrument.
- **A label set is bounded and small.** Keep the value count in single digits; a value count in the hundreds needs a
  reason. Detection of the bound needs the run, not the diff: a label bounded only by a test fixture passes review
  and fails in production.
- **A high-cardinality attribute is not a metric attribute.** An id, a query text, a message, or a client address
  belongs on the record or the span. An attribute a semantic convention defines for the instrument, such as
  `server.address` over a small configured set of backends, follows the convention, and the reviewer then checks the
  actual value set. Detection: a metric attribute whose value is unbounded.
- **In a service, a signal no alert, dashboard, or stated question consumes is a candidate for removal.** Detection:
  nothing in the repository's alerts, dashboards, or documentation names the signal. A failed search in the
  repository is a question for the owners, not a deletion: consumers may live outside it, and removing a published
  signal is a compatibility change. A library's consumers are its hosts, so for a library the check is the stated
  question above.

## 5. The span

- **One span per operation.** A new span for an operation that is already instrumented duplicates it; a span for a
  distinct logical operation, such as a retry loop over an instrumented HTTP call or a database operation over an
  instrumented transport, is a parent span and in rule. Detection: a new span whose only content is one
  already-instrumented call and which adds no attribute a convention names. The repair is attributes on the existing
  span, set before it ends.
- **The span status reports the final outcome of the operation the span represents.** A failed attempt that a retry
  or a fallback recovered does not set the status to error. Detection: `setStatus(ERROR)` or the equivalent inside a
  retry loop, or on a path the operation recovers from.
- **An exception is recorded once, at the frame that handles it, correlated with the active span.** New code emits it
  as a log record with the exception attributes (`exception.type`, `exception.message`, `exception.stacktrace`)
  through the repository's logging API, which the OpenTelemetry logs bridge correlates with the span; where the
  repository's OpenTelemetry version offers no logs bridge, `recordException` on the active span is the same record.
  Intermediate frames that rethrow record nothing. This is one of the two records §2 step 2 admits. Detection: a
  `recordException` or an exception log on a frame that rethrows, or the same exception recorded on more than one
  frame.
- **A new event is a log record correlated with the current span.** The span-event API (`addEvent` and
  `recordException`) is being deprecated in favor of the logs API. Existing span events are not rewritten by this
  skill. Detection: an `addEvent` call in new code.

## 6. What a library may emit

**A library does not decide where its output goes.** The ecosystems differ in which call makes that decision, so the
detection differs and the rule does not.

- Where the host routes **by name**, the deciding call is a **configuration** call: installing a handler, setting a
  level, reading a configuration file, or attaching anything but a null sink. Detection: that call anywhere
  outside the entry-point module, in a library or in a service.
- Where the host routes **by value**, the deciding call is an **acquisition**: reaching for the ambient default
  logger, or holding one in a package-level variable, instead of taking the logger the caller supplied. Detection:
  the ambient-default call, or a package-level logger variable, including one injected once and then used globally.

The rest of the library contract:

- **The build does not carry a logging provider outside test scope**, because a transitive provider is imposed on
  every host. Detection: provider coordinates at compile or runtime scope in the **published** metadata, since an
  optional declaration in the build script does not always reach the published artifact.
- **Telemetry leaves through an API whose default, with nothing installed by the host, is a no-op or the host's own
  sink.** The OpenTelemetry API and Micrometer's global composite registry are such APIs. Detection: a dependency on
  an SDK, an exporter, or a registry that writes somewhere by default, at compile or runtime scope. A flag around it
  does not repair it.
- **Where the ecosystem offers no no-op default, publish a hook the host implements** rather than choosing a
  destination, and ship the adapters as separate artifacts. Detection: a registry chosen inside library code, or a
  hook published beside a default registration.
- **A library may log.** No ecosystem requires silence. What a library owes is the rate (§3) and the host's ability
  to route by name or by value. What a host sees when it configures nothing differs by ecosystem, and the ecosystem
  file states it.
- **A library propagates the host's context into the calls it makes**, or the host's trace ends at the library
  boundary. Detection: an outbound call that takes a context and is passed a fresh one, or none.
- **An avoidable condition the caller can fix goes to the caller, not to the log.** Detection: a warning-level line
  in library code whose text tells the caller to change their code. Python has a first-class channel for this, and
  the Python file names it.

## 7. Severity

**The axis is who must act and whether they can.** The software still works as expected, and the reader need do
nothing: informational. The reader may have to act: warning. The operation did not happen and the code did not handle
it: error.

**The repository's existing convention owns the ladder**, and the reviewer's check is agreement with the neighboring
calls in the same package. Where the repository exports logs through OpenTelemetry, the level maps to a severity
number the alerts filter on, so a level that disagrees with its neighbors breaks an alert and not only a reader.

Where the convention is generic, three questions decide:

1. Does the level put the record in the default production output for a condition the reader cannot act on? Warning
   is the level agent-written code overuses, and this is the shape it takes.
1. Did the code continue normally afterwards? Then the record is informational, whatever the text suggests.
1. Does the same kind of event carry a different level elsewhere in the file?

## 8. Concurrency and context

**The host's context crosses every thread, goroutine, or task boundary the code creates**, and a scope that changes
the context restores it on exit. The ecosystem file has the detection:

- where context is an explicit parameter, the failure is a concurrent call started without it, visible in the diff as
  a missing argument and reported by a linter;
- where context is ambient and copied into tasks automatically, only a hand-rolled thread pool loses it;
- where context is ambient and **not** inherited by pooled threads, there are two failures: a task that starts without
  the context, and a pooled thread that kept the previous unit's keys and leads the reader to the wrong request. A
  scope that sets an entry restores the previous value on the same path, including the failure path; removing the
  entry is correct only where no outer scope set it. Detection: a set with no restore in a `finally`, or a removal
  inside a nested scope.

A context that is not the caller's does not satisfy this; check that the value came from the parameter rather than
from a package variable.

## 9. Review checklist

Run this over a diff that touches instrumentation. Every item gets an answer; an item with nothing to report says
`none` and one line on what was checked. Where an item turns on whether an engineer holding only the emitted text
would wait or intervene, raise it for a person and say so.

- **Mode** (§1, §6): does the change contain a configuration or acquisition call outside the entry-point module;
  is the artifact in library mode, and does it then carry a provider, an SDK, an exporter, or a default registry?
- **Signal** (§2): which existing signal of the right kind was checked for the fact; does any path both log an error
  and return or throw it; is any handler body a single log call; was a decision to emit nothing recorded?
- **Rate** (§3): can the new call fire per item, per row, or per message outside the three permitted shapes; where
  the unit is the state change, does it emit on transition; is a debug record carrying a fact the reader needs in
  production, or sitting at a verbosity nobody enables?
- **Contents** (§3): joining identifier or trace context, the branch that produced the value, settable names, which
  state, transition time; is a filterable value interpolated into the text; is an expensive argument guarded?
- **Instrument** (§4): does a log line carry a count, a rate, or a duration; is the question stated where the
  instrument is defined; is the failure rate computable from one label set; is the reason low-cardinality; is the
  label set bounded; is success latency separable; is an unbounded value a metric attribute; does a constant decide
  whether to emit with no instrument carrying the measurement; is an existing signal in the diff consumed by
  nothing?
- **Span** (§5): does a new span duplicate an instrumented operation; does a recovered attempt set the error status;
  is an exception recorded on a rethrowing frame or on more than one frame; does new code add a span event?
- **Library** (§6): does a warning-level line tell the caller to change their code; does an outbound call drop the
  host's context?
- **Level** (§7): does it agree with the neighboring calls, and did the code continue normally afterwards?
- **Context** (§8): does every concurrent call the change starts carry the caller's context; does every scope
  restore what it set, on every path?
