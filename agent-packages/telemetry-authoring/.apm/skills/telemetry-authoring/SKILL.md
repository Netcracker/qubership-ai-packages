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

Every rule below carries its detection in the same sentence as its prescription. That is deliberate. The channel this
skill occupies is the weakest enforcement channel there is: a repository instruction file is complied with far less
often than a check that fails, so a rule stated without the evidence a reviewer looks for is a rule that does not
arrive. Where a linter already reports a rule, its file in `references/` names the rule id, and routing the reviewer
to the linter is worth more than restating the rule.

The reader the whole skill serves never loads it. That reader holds an alert, no source access, and one decision:
wait, or intervene. Every rule here is enforced through the author or the reviewer on that reader's behalf.

## 0. Which reference to open

The rules below hold in every ecosystem. What a host sees when it configures nothing, how a logger is obtained, how
fields attach, whether arguments are evaluated when the call is discarded, and which linter reports what, are in
`references/`, one file per ecosystem. **Before writing the first call, read the file for the repository's
ecosystem**: `jvm.md`, `go.md`, `python.md`. Open no other.

Which file, in this order:

1. **The repository's instructions name the stack.** A line such as `Logging: SLF4J API, Micrometer for metrics,
   OpenTelemetry API for traces` selects the file and settles the mechanics. Where the line is missing, propose it in
   the first pull request that adds instrumentation under this skill, and not in the later ones.
1. **Otherwise the imports of the nearest existing call decide**, then the build file.

Three rules the ecosystems answer differently, and the reference file is the authority for each: what reaches the
host's console when the host has configured nothing; which call constitutes deciding where output goes; and whether
the arguments of a discarded call are evaluated anyway.

## 1. The mode, which decides everything else

**The mode is per module, not per repository.** The code is in **library mode** when something outside it decides
where its output goes; in **service mode** when the artifact containing it also contains the entry point that
configures output. A microservice's internal packages are in library mode.

Detection: the module has no entry point of its own and no configuration call, and its output destination is set in
another artifact. A change that calls a configuration API and defends it as service mode is checked against the same
artifact for an entry point.

The mode changes four things: whether a configuration call is permitted at all (§6), whether a metric may be
registered or only defined (§4), whether the code owns a unit of work (§3), and whether §4's rule that a recurring
logged condition is also counted applies at all.

## 2. Which signal the fact owes

This is the skill's spine, and it is **derived**: no source states it. It is built from the emit-nothing test of the
tracing specifications, from the removal rule of operational practice, from the one routing table a standard library
publishes, from the agreement of three ecosystems that an error leaving a function belongs to the caller, and from
the split between what is asked in aggregate and what is asked about one unit of work. It needs nothing from the
author's intent, which is what makes it applicable by a reviewer.

For a fact the change makes true, take the **first** branch that applies.

| # | Branch | Condition | Outcome |
| --- | --- | --- | --- |
| 1 | **Already recoverable** | An existing signal carries the fact *and* the value that distinguishes this case | **Nothing.** Name the existing signal in the review note |
| 2 | **The caller can act** | The caller can prevent or repair it | **The caller's channel**: return, raise, or the ecosystem's deprecation channel, and **not also** a log call |
| 3 | **Asked in aggregate** | The question is "how often, how long, how many right now" | **An instrument** (§4) |
| 4 | **Asked about one unit** | The question is "what happened to this one", and the aggregate cannot reconstruct it | **One record** (§3) |
| 5 | Otherwise | — | **Nothing** |

Branches 3 and 4 are not exclusive. Where both apply, the instrument is the thing that is always on and the record is
the thing that is sampled or verbosity-gated.

**Branch 1 is first on purpose.** The common failure is not a missing signal; it is a second signal for a fact
already carried. The check is not that the author named *a* signal, but that the named signal carries the
distinguishing value: a line that reports "a value was computed" does not cover "the value hit its limit".

**Branch 2 is the rule a reviewer can check mechanically.** An error that leaves the function goes to the caller. An
error handler whose whole body is a log call has not handled the error, and handlers of that shape are a measured cause
of catastrophic failures, not a style preference. Detection: a log call and a throw or return of the same error on one
path, which the JVM file names a linter rule for; in Go and Python the reviewer finds it by reading the path. The escape
hatch is explicit and bounded: at the last frame that knows the cause, and nowhere else, an informational record at
debug verbosity carrying the error as a field.

**What branch 5 costs.** Nothing is a decision, and a review note that names it is what distinguishes it from an
oversight.

## 3. The record

A record is one entry about one unit of work.

**Rate.** One record per unit of work, and no more than one. A service that emits one entry per request is in rule at
any traffic level, because the rate follows the traffic rather than the code's chattiness. Detection: more than one
record on the success path of one unit.

**Where the code owns no unit of work — a library, a reconciler, a cache, a pool — the unit is the state change**
(derived). Emit on transition into a state and on transition out of it, not on each occurrence. This is what makes a
steady state quiet, and quiet is the consequence rather than the goal. Detection: a record inside a loop, or on every
call, that reports an unchanged state. A writer who compares against a value that always differs, such as a clock,
satisfies the letter; check that the compared value is the state.

**A long-running unit emits progress on an interval**, and the interval is a constant rather than a count of items.
Detection: progress emitted per item.

What every record carries:

| Carries | Why the reader needs it | Detection |
| --- | --- | --- |
| **The joining identifier** | Without it, concurrent workers produce interleaved streams that cannot be separated | The record's fields contain no id of the request, connection, thread, or component. A class name is not an identifier: check that the value distinguishes two concurrent units, not two code sites |
| **The branch that produced the value** | A record that prints its inputs and its result leaves the reader to re-derive which case fired | The clamped and the unclamped case produce the same text. Printing every input does not repair it: check that the *branch* is recoverable from the text |
| **Names the reader can set or grep** | A private field name sends a reader holding a configuration file to a search that returns nothing | Grep each name in the message against the settable names: the property, the flag, the environment variable. The user-facing spelling wins, and renaming the private field to match is the wrong direction |
| **Which state it reports**, where a reader may wait on it | The reader's decision is wait or intervene, and "still retrying" and "gave up" must not share a text | The text and the level together leave the two indistinguishable. Adding the word "failed" is not enough: check that a counterpart record exists for the other outcome |
| **The transition time**, for a published state | "It has been stuck for ten minutes" is unanswerable without it | A status field, gauge, or condition published with no transition timestamp or last-success timestamp |

**A value the reader will filter or join on is a field, not prose inside the message.** Detection: the value is
interpolated into the message text in a repository that logs structurally. A writer who adds it in both places
duplicates it, which one ecosystem's linter reports.

**Cost.** No log call in a loop body without aggregation: count in the loop and record once after it. Detection: the
enclosing block of a log call is a loop; a modulus guard satisfies the letter, so check that an aggregate is emitted
after the loop. An error path that can fire once per item is rate-limited or counted rather than recorded per
occurrence, and lowering the level does not repair it, because the rate rather than the level is what was
unbounded. Where a record's arguments call a method or build a string, guard the computation; check that the
expensive half is inside the guard, and read the ecosystem file, because one of the three evaluates the arguments of
a discarded call by design.

## 4. The instrument

A fact someone will want aggregated over time is an instrument. Detection: a log line whose text is a count, a rate,
or a duration.

- **A new instrument is introduced with the question it answers, stated where the instrument is defined** (derived
  ownership). Whoever defines it states the question, because the host wiring it up cannot infer it; whoever
  registers it owns where it goes. Detection: no alert, dashboard, or stated question names it. A generic doc comment
  satisfies the letter; check that the stated question names a decision somebody makes.
- **A failure counter arrives with the attempts counter that is its denominator.** Detection: a failure counter with
  no total on the same path. Reusing an unrelated total is the gaming shape; check that the denominator counts the
  same attempts.
- **Errors are counted by reason, and the reason set is closed and enumerable from the source.** Detection: one error
  counter with no reason dimension, or a reason built from an exception message.
- **Latency for the successful outcome is recorded separately from overall latency**, because fast failures make a
  combined timer look healthy. Detection: one timer around the call with no outcome dimension.
- **A condition that is both recurring and logged is also counted.** In a repository with no metrics facility this
  rule is suppressed by mode rather than by judgment.
- **A threshold that decides "slow", "stuck", or "too many" lives in the alert, not in the emitting code** (derived).
  The emitting code cannot know which wait is interesting, and a compiled-in constant cannot be retuned by the
  reader. Detection: a constant compared against a measurement to decide whether to emit. Making the constant
  configurable does not repair it; check whether the signal still carries the raw measurement.
- **A label set is bounded and small.** Keep the value count in single digits; a value count in the hundreds needs a
  reason. Detection of the bound needs the run, not the diff: a label bounded only by a test fixture passes review
  and fails in production.
- **A high-cardinality attribute is not a metric attribute.** An id, an address, a query text, or a message belongs
  on the record or the span. Detection: a metric attribute whose value is one of those.
- **A signal no alert, dashboard, or stated question consumes is removed.** This is the converse of the question
  rule and the only stated lifecycle rule for an existing signal. Detection: nothing in the repository's alerts,
  dashboards, or documentation names the signal.

## 5. The span

- **Do not wrap a call in a span when the layer beneath it is already instrumented.** Detection: a new span around an
  HTTP or database client call. The repair is attributes on the existing span.
- **On an error path that already has a span, record the exception and set the span status** rather than logging it.
  Detection: a log call inside a catch block, or an error branch, that runs under an active span.
- **An event is a log record correlated with the current span, not a span event** (the span-event API is being
  withdrawn on the ground that two APIs make library authors choose between two ways of emitting the same data).
  Detection: an `addEvent`-shaped call in new code.

## 6. What a library may emit

One rule survived every crossing of the three ecosystems: **a library does not decide where its output goes.** The
ecosystems differ only in which call makes that decision, so the detection differs and the rule does not.

- Where the host routes **by name**, the deciding call is a **configuration** call: installing a handler, setting a
  level, reading a configuration file, or attaching anything but a null sink. Detection: that call anywhere in
  non-entry-point code, not only in the constructor.
- Where the host routes **by value**, the deciding call is an **acquisition**: reaching for the ambient default
  logger, or holding one in a package-level variable, instead of taking the logger the caller supplied. Detection:
  the ambient-default call, or a package-level logger variable. A logger injected once into a package variable and
  then used globally satisfies the letter; check that the call site takes it from the caller.

The rest of the library contract:

- **The build does not carry a logging provider outside test scope**, because a transitive provider is imposed on
  every host. Detection: provider coordinates at compile or runtime scope. Declaring the dependency optional is the
  gaming shape; check the published metadata rather than the build script.
- **Telemetry leaves through an API whose default, with nothing installed by the host, is a no-op or the host's own
  sink.** Detection: a direct dependency on an SDK, an exporter, or a registry implementation. Wrapping it behind a
  flag does not repair it; the dependency is the evidence.
- **Where the ecosystem offers no no-op default, publish a hook the host implements** rather than choosing a
  destination, and ship the adapters as separate artifacts. Detection: a registry chosen inside library code.
  Naming a hook and also registering a default satisfies the letter; check for the registration call.
- **A library may log.** No ecosystem's primary sources require silence, and one standard library states the
  opposite. What a library owes instead is the rate (§3) and the host's ability to route by name or by value.
- **A library propagates the host's context into the calls it makes**, or the host's trace ends at the library
  boundary. Detection: an outbound call that takes a context and is passed a fresh one, or none.
- **What a library owes about its own silence differs by ecosystem and cannot be stated once.** With no host
  configuration, one ecosystem emits nothing, one emits warnings and above to the console and calls that its best
  default, and one writes to the console with no remedy available to the library at all. Read the ecosystem file
  before promising a host anything about silence.

**An avoidable condition the caller can fix goes to the caller, not to the log.** One ecosystem has a first-class
channel for this and the other two do not; the distinction it encodes holds everywhere. Detection: a warning-level
line in library code whose text tells the caller to change their code.

## 7. Severity

**This skill states no ladder, and a skill that stated one could not be checked against any particular commit**: a
project's own verbosity choices drift in both directions over its history, so a generic ladder is unfalsifiable. Two
things survive every convention.

**The axis.** Every source that defines levels by meaning rather than by adjective defines them by **who must act and
whether they can**. The software still works as expected, and the reader need do nothing: informational. The reader
may have to act: warning. The operation did not happen and the code did not handle it: error.

**The authority.** The repository's existing convention owns the ladder, and the reviewer's check is agreement with
the neighboring calls in the same package, which are in the diff's own files. Where the convention is generic, three
questions decide:

1. Does the level put the record in the default production output for a condition the reader cannot act on? Warning
   is the level agent-written code overuses, and this is the shape it takes.
1. Did the code continue normally afterwards? Then the record is informational, whatever the text suggests.
1. Does the same kind of event carry a different level elsewhere in the file?

## 8. Concurrency and context

**The host's context crosses every thread, goroutine, or task boundary the code creates.** One intent, three
different failures, so read the ecosystem file for the detection:

- where context is an explicit parameter, the failure is a concurrent call started without it, and it is visible in
  the diff as a missing argument and reported by a linter;
- where context is ambient and copied into tasks automatically, only a hand-rolled thread pool loses it;
- where context is ambient and **not** inherited by pooled threads, there are two failures, and the second is worse:
  a pooled thread that kept the previous unit's keys leads the reader to the wrong request. An entry that is set is
  removed on the same path, including the failure path. Detection: a set with no matching removal in a `finally`.

Passing a context that is not the caller's satisfies the letter; check that the value came from the parameter rather
than from a package variable.

## 9. What no check here settles

One question, and the skill does not pretend to answer it: **holding only the emitted text, would a competent
engineer wait or intervene?** No source offers an oracle. The state rule in §3 is a proxy, checkable and not the
thing itself. Where a change turns on that question, raise it for a person and say that is what you are doing.

Three more belong to the repository rather than to this skill, and the rule is that the new call agrees with the
calls around it: the level ladder, the mechanism for structured fields, and whether the repository exports metrics at
all.

## 10. Review checklist

Run this over a diff that touches instrumentation. An item with nothing to report says `none` and one line on what
was checked.

- Mode: is the module in library mode, and does the change contain a configuration or acquisition call that decides
  where output goes (§1, §6)?
- Branch 1: which existing signal was checked for the fact, and does it carry the distinguishing value (§2)?
- Branch 2: does any path both log an error and return or throw it, and is any handler body a single log call (§2)?
- Rate: can the new call fire per item, per row, or per message; and where the code owns no unit of work, does it
  emit on transition rather than on occurrence (§3)?
- Contents: joining identifier, the branch that produced the value, names the reader can set, which state it reports,
  transition time (§3)?
- Fields: is a value the reader will filter on interpolated into the message text (§3)?
- Progress: does a long-running unit report per item rather than on an interval (§3)?
- Guard: does the call build a string or call a method in its arguments, and does the ecosystem evaluate those
  anyway (§3, `references/`)?
- Instrument: does a log line carry a count, a rate, or a duration; is the question the instrument answers stated
  where it is defined; does a failure counter have its denominator; is the reason set closed; is the label set
  bounded; does success latency have its own timer; is an id, an address, a query, or a message a metric attribute
  (§4)?
- Threshold: is a constant deciding whether to emit, where the alert should decide (§4)?
- Span: does it wrap an already-instrumented call; is an exception logged instead of recorded on the active span; is
  an event added to a span instead of emitted as a correlated record (§5)?
- Library: does the build carry a logging provider outside test scope or an SDK, exporter, or registry
  implementation; does a published hook also register a default; does a warning-level line tell the caller to change
  their code; does an outbound call drop the host's context (§6)?
- Level: does it agree with the neighboring calls, and did the code continue normally afterwards (§7)?
- Context: does every concurrent call the change starts carry the caller's context, and is every ambient entry
  removed on every path (§8)?
- Vacuous: a counter nobody reads, a record at a verbosity nobody enables, a line that prints inputs and not the
  branch, a per-attempt line inside a retry loop, a state field with no transition time (§2–§5)?
- Nothing: is there a signal here that should not exist, and was the decision to emit nothing recorded (§2)?
