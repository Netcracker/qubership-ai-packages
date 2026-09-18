# Pass 2 — rule brief

## Research title

Evaluate the Pass 1 shortlists and extract applicable rules for a `telemetry-authoring` skill: which signal an event
owes, what each signal must carry, and what a library may emit, across the JVM, Go and Python.

## Goal

Pass 1 ran as two discovery passes and established the following. **No single source covers the domain**; the closest,
AWS's *Instrumenting distributed systems for operational visibility*, is asserted org practice and assumes a service.
The empirical research is the strongest category and supplies a ready-made defect vocabulary; the agent-skill category
is empty on the author side — every published observability skill is backend-side, so the ground is unoccupied. The
library contract is stated authoritatively on the JVM (SLF4J) and in Python (the stdlib Logging HOWTO), and **not at
all by Go's standard library**, where it exists only in project conventions and a linter. The three ecosystems differ
in kind, not only in API, on four points: what silence costs a library that logs into an unconfigured host; whether the
library's sin is *configuring* (name-routed ecosystems) or *acquiring* (value-routed Go); Python's `warnings.warn` as a
fourth channel the others lack; and the shape of the context-propagation failure.

Pass 2 does not repeat that survey. Its job is to turn the shortlist into rules an agent can apply, and to settle the
questions Pass 1 left open.

The unit of the deliverable is not a source summary; it is a rule, stated once, with a rationale, a source, the reader
it serves, the situation it applies to, and the way a reviewer detects a violation of it.

## Target domain

Three facts about the consumer, each of which changes what counts as a usable rule.

**It works without the author.** It reads the artifact, the diff, and the source, and has nobody to ask. A rule that
depends on knowing the intent behind the instrumentation cannot be applied, however sound it is. "Log what is
interesting" is not a rule; "a line that reports a computed value names which constraint bound it" is.

**It produced the thing it is now judging, and it is rewarded when the thing passes.** Every rule has to say what a
reviewer checks, so that satisfying the letter of it is worth something. This is not hypothetical here: Pass 1 found a
study of 4,550 agent-authored pull requests reporting WARN overuse in 29.9% of repositories, under-logging in loops and
conditionals relative to humans, and instruction non-compliance about two-thirds of the time **even when the level or
the framework was specified in the instruction**. Natural-language rules alone under-perform in this domain, and that
is a design constraint on the skill, not a footnote.

**Some defects have an oracle.** Every rule lands in one of four buckets, and the report says which:

1. applied while writing or reviewing, from the artifact and the diff alone;
2. violation needs the work run, and the brief says which run;
3. reported by a tool, with what the tool's verdict does and does not establish;
4. a human judgment the agent may raise but not decide.

The proportion in bucket 1 is how usable the skill will be. Report the counts.

## Readers

Fixed; Pass 1 confirmed the table and confirmed that R3 is a beneficiary rather than a consumer. **Every rule names the
reader whose need it exists for, listed first.**

| Reader | Situation | Holds |
| --- | --- | --- |
| R1 Library author | Adding or changing a logger call, or a counter, inside a library that ships to hosts it will never see | The diff, the library's conventions, no control over how the host configures output |
| R2 Service author | Has just written a branch that ends in a failure, a retry, a fallback, or a silently clamped value | The diff, the instruments the service already exports |
| R3 On-call engineer — **beneficiary, not consumer** | An alert or a user report, no source access, deciding whether to wait or intervene | Logs, a dashboard, the deploy history, the literal text of one message |
| R4 Reviewer | Holds a diff in which a signal appeared, changed, or is conspicuously absent | The diff, the repository's conventions, no access to the author |

## What Pass 1 settled, and this pass does not reopen

- **The rule sources** are categories 1 (practitioner guidance), 2 (empirical research), 3 (OpenTelemetry
  cross-cutting), 5 (project conventions) and the ecosystems' own primary documentation. The **evidence labels** come
  from category 2 and from the tool documentation; the practitioner sources are asserted org practice and are labeled
  as such.
- **Settled as rejects:** vendor and backend material, logging-library benchmarks, format arguments, tutorials,
  backend-side observability agent skills, migration guides.
- **Readers:** the four-row table holds; R3 stays a beneficiary.
- **Out of scope and to whom it belongs:** message wording → `english-developer-style` §7; the documentation entry a
  user-visible message owes → `docs-page-authoring` §7; the repository-wide review → `deep-review`'s observability
  axis; commit messages and changelogs → `change-description-authoring`; alerting rule syntax, dashboards, SLO
  documents, log shipping, retention, vendor choice → out of the skill entirely.
- **S11 is settled as JVM-local** and demoted from a language-neutral rule to a reference-file entry: the
  `java.util.logging.Formatter` javadoc confirms the `MessageFormat` route, Go's `fmt` is not locale-aware, and
  Python's `,`/`_` are explicitly not locale-aware. Do not re-litigate.
- **S2 is settled as confirmed**: the library/application split is stated as a fault line by SLF4J, the Python HOWTO,
  OpenTelemetry's client design principles, and Kubernetes' shared-library rule. What is **not** settled is the test
  for the boundary and what the library side may emit — see the conflicts.

## Shortlisted candidates from Pass 1

Group members count as one candidate. Read the specific part named; where a candidate is a book chapter, **read the
chapter before quoting it** — Pass 1 characterized two books from publisher pages and flagged that as a limit.

1. **Yanacek, *Instrumenting distributed systems for operational visibility* (AWS Builders' Library).** The
   unit-of-work record; one entry per unit of work and no more; a separate timer for successful responses; a counter
   per error *reason*; queue depth at every enqueue and dequeue; "keep the application log free of spam"; rate-limiting
   a logger that starts emitting stack traces; propagating the trace id in the method signature rather than through
   framework magic.
2. **Saarimäki, Shin and Bianculli, *Towards a Taxonomy of Software Log Smells*.** Nine smells with facets,
   implications, and a map to 16 repair tools. LS2 (undercover identifier), LS3 (the retry-versus-timeout worked
   example), LS7 (landfill logs / logging in a tight loop).
3. **Kubernetes SIG-Instrumentation** as a group: the logging conventions, KEP-1602 (structured logging) for the
   written rationale, the klog V-level ladder with per-level meanings, the shared-library rule with its rationale and
   its escape hatch, and the API `Conditions` vocabulary (Available / Progressing / Degraded with
   `lastTransitionTime`) as published on-change state.
4. **OpenTelemetry** as a group: the library instrumentation guidance including "when in doubt, don't instrument" and
   its three-part test; the client design principles ("the developers of the final application normally decide how to
   configure the SDK"); the API-not-SDK rule and the no-op default; the general attribute and metric naming rules with
   their stability ladder; and the current position of events relative to spans and logs.
5. **Ouatiti et al., *Do AI Coding Agents Log Like Humans?*** 4,550 agent pull requests over 81 repositories: WARN
   overuse in 29.9% of repositories, under-logging in loops and conditionals, ~67% instruction non-compliance, 72.5%
   of post-generation repairs done by humans. Plus **AL-Bench** as the runtime oracle, where the best tool still fails
   to compile 20.1% of the time.
6. **Zhong et al., *MultiLogBench*.** Six ecosystems, 63,965 instances; absolute performance language-sensitive,
   model ordering largely preserved (Spearman 0.912); loop and nested-callable sites hardest in every language.
7. **Yuan et al.** as a group: OSDI 2014 (*Simple testing can prevent most critical failures*) — an error handler that
   only logs is counted as ignoring the error, and such handlers account for 25% of catastrophic failures; 76% of
   failures did print explicit failure messages, so the usual gap is comprehension rather than absence. And
   **LogEnhancer** — which values a line must carry, derived from the causally related branches around the log point.
8. **Prometheus** as a group: the instrumentation practices ("libraries should provide instrumentation with no
   additional configuration required by users"; "for every line of logging code you should also have a counter";
   the warning about metrics in inner loops), the naming practices, the cardinality budget (below 10; investigate
   above 100), and the client-library specification's default-registry requirement.
9. **go-logr and Dave Cheney's *Let's talk about logging*** as a pair: the argument that warning and error are not
   author-decidable, implemented as a two-kind API with numeric verbosity; plus Google's Go style guide on returning
   rather than logging, and the rule that a verbosity guard must wrap expensive argument computation.
10. **Python `logging` HOWTO** as a group with the stdlib `warnings` documentation: the decision table
    (`print` / `logger.info` / `logger.debug` / `warnings.warn` / raise / `logger.error` / `logger.exception`), the
    library section (`getLogger(__name__)`, no root logger, `NullHandler` as opt-out), and the stated default that
    `WARNING`+ goes to stderr and that this is "the best default behaviour".
11. **SLF4J FAQ and Manual**, with JEP 264 (`System.Logger`) and the Log4j `api`/`core` split as corroboration: the
    library depends on the API only; a transitive provider "is imposed on the end-user"; embedded components "really
    should not" configure the underlying framework; the no-op default when no provider is present.
12. **The context-propagation trio:** the Logback MDC manual (not inherited by `Executors`-managed threads; a `put()`
    balanced by a `remove()`; the stale-context failure), Python's `contextvars` and `asyncio` documentation (a Task
    copies the current context; `asyncio.to_thread` propagates; a hand-rolled `ThreadPoolExecutor.submit` does not),
    and Go's `context` documentation and blog.
13. **The mechanical layer** as a group: `sloglint` (`no-global`, `context`, `forbidden-keys`, static message, constant
    keys, balanced key/value pairs), `loggercheck`, Ruff's `LOG`/`G`/`TRY` families, Sonar S2139, and the
    `java.util.logging.Formatter` javadoc. For each, the rule id and what a clean verdict does **not** establish.
14. **HikariCP's `MetricsTrackerFactory` and Micrometer's `MeterBinder`:** a widely deployed library that exports no
    metrics itself and publishes an interface the host implements, with adapters shipped as separate artifacts.

## Measured data, supplied

Use these rather than re-measuring.

- **The `MessageFormat` measurement** (seed S11): on the JVM, `java.util.logging.Logger.log` with an `Object[]` renders
  through `java.text.MessageFormat`, so `103887667` prints as `103,887,667` under `en-US` and `103 887 667` under
  `fr`; the same repository already works around it with `String.valueOf` in `PGStream.increaseByteCounter`. Settled
  as a JVM reference-file entry.
- **The two recorded failures** in `seed_baseline.md` part 3 (F1, F2), and the Go and Python defects Pass 1b recovered: the
  CPython `fork` logging deadlock (bpo-6721 / bpo-36533, with its regression test), boto3 #3403 (three libraries each
  defining a private `NullHandler`, so a host cannot detect them by `isinstance`), and the Go global-logger cases.

## Specific questions from Pass 1 to investigate

### Conflicts Pass 1 identified as live

Decide each and say why. A conflict returned undecided becomes a hedge in the skill.

- **(a) Severity.** OpenTelemetry's normative ladder and Kubernetes' six-level V-scale publish ladders; Cheney argues
  warning and error are not decidable by the author, and go-logr implements that as a two-kind API. Cutting across
  both, Pass 1 found components of a single project drifting in opposite directions. Decide what the skill states
  about levels **so that it survives either convention**, and say what a reviewer checks when the repository's
  convention is generic.
- **(b) What a library may emit.** SLF4J and the Python HOWTO say a library must not configure output; Python's own
  default *is* `WARNING` to stderr and the HOWTO calls that the best default; go-logr states that the "libraries
  should not log" position has already lost; Kubernetes states that shared libraries should not log errors but return
  them. These are not the same position. Decide what the skill tells R1, and whether the answer differs by signal
  (a log line, an error return, a counter).
- **(c) Rate.** Yanacek's service logs one record per request at 20 million requests per second, while seed S8 says the
  steady state should be silent. Pass 1's hypothesis is that "silence" is the wrong variable and "one bounded record
  per unit of work" is the right one. **Test that hypothesis** against both cases and against the library mode, where
  there is no unit of work the library owns.
- **(d) Metrics from a library.** Prometheus requires instrumentation with no configuration and a default registry;
  OpenTelemetry says API only with a no-op default; Micrometer's global registry is a composite that does nothing
  until the host binds one; HikariCP publishes an interface instead. Four answers. Decide what the skill states, and
  whether seed S4's metrics clause survives, is bounded, or is withdrawn.
- **(e) Where events live.** The movement of events out of spans and into logs changes the shape of the signal-choice
  question. State the current position and what it means for a rule written today.
- **(f) S9's owner in library mode.** If a library exports no metrics of its own, who owns "a metric is authored under
  a named question"? Pass 1 calls this an unresolved asymmetry in the skill's structure. Settle it.

### The gap Pass 1 could not close

**Which signal does an event owe?** No source states a rule. The only pairing rule found is Prometheus's "for every
line of logging code you should also have a counter", and the only *emit-nothing* rule is OpenTelemetry's "when in
doubt, don't instrument" with its three-part test. This is the central rule the skill exists to state, so **build it,
label it derived, and show the derivation from sourced criteria.**

Then work it through each of these concrete cases, by name, and say what the rule emits for each:

1. **pgjdbc adaptive fetch (F1/F2).** A per-connection cache recomputes a fetch size when it sees a larger row; the
   result is clamped by a configured minimum and maximum; the applied value is already printed by an existing
   `FINEST` line elsewhere; the failure the author was debugging is the clamp becoming permanent. Library mode.
2. **A retry loop in a Go service** that retries three times and then gives up.
3. **A Python library that receives a deprecated argument** — the `warnings.warn` case.
4. **A connection pool that hands out a connection after waiting three seconds.** Latency, not failure.
5. **A parser that rejects a protocol message exceeding a configured limit** and throws. Library mode.
6. **A background reconciler that has not converged for ten minutes.** Service mode, no error anywhere.

For each: which signal or signals, at what level or of what instrument type, carrying what, and **what the rule says
to emit nothing about**.

### The highest-value question in the pass

The one above. Spend the budget there. Second priority is conflict (b), because it decides half the skill's structure.

### Applicability

- Which rules port across the three ecosystems unchanged, which port in intent but need a per-ecosystem detection, and
  which are local to one ecosystem and belong only in its reference file. Pass 1 found four differences in kind; check
  whether there are more, and whether any of the four collapses under a better formulation.
- What each rule costs in false positives, in a repository whose conventions differ.
- Which rules a project's own convention overrides, and how the skill says so without becoming advisory.

## Required output

Under 5000 words excluding tables. The rules must not overlap: one fact, one rule. Twelve sections, in order.

1. **Executive summary.** Which sources survive as rule contributors and which drop to supporting; which questions were
   settled and which stayed open; the bucket split with counts; what resists a writer who optimizes for the check.
2. **Deep candidate evaluation.** One row per candidate: disposition, strongest contribution, main weakness, evidence,
   maintenance, whether it ships examples, false-positive risk, portability.
3. **Extracted rules.** The centerpiece, 30 to 45 rows: the rule, its rationale, the reader, the source, the evidence
   label, when it applies, how a reviewer detects a violation, whether a writer can game it and what is checked
   instead, the repair, and the bucket.
4. **The per-ecosystem table:** for each rule that is not language-neutral, the JVM, Go and Python forms, each cell
   marked measured or documented, and each naming the reference file it belongs in.
5. **The signal-choice rule and its test** against the six concrete cases named above, one subsection each.
6. **The list of shapes that fail vacuously** — instrumentation that satisfies the letter and carries nothing — each
   with its detection. Draw on the agent study and the log-smell taxonomy.
7. **Worked examples**, before and after, one per rule family, at least one in each of the three ecosystems.
8. **Conflicts and how they were decided**, (a) through (f), with the reason for each.
9. **The detectability matrix**: rule against bucket, with the source per cell.
10. **Baseline audit.** Rule by rule through `seed_baseline.md` part 2, S1 to S12: survives, survives with a changed rationale,
    needs restating, or is contradicted. Then what the seed misses entirely, in descending order of cost. S11 and S2
    are settled above and need one line each, not a re-argument.
11. **Evidence map.** Every figure with its sample and the source it was checked against, and every correction to
    Pass 1 named as a correction. Pass 1 flagged two limits you must clear or carry forward: the 2024 EMSE literature
    review behind Springer's IdP redirect was **not read**, and its figures must be verified or dropped; and the two
    books were characterized from publisher pages rather than read.
12. **What the skill-writing session should be told.** The handover: what to state in the body, what belongs in a
    reference file and which one, what stays in the research directory, and what stays a human judgment. Pass 1 named
    one item for the last category — whether, holding only the emitted text, a competent engineer would wait or
    intervene — and said no source offers an oracle for it.

## Constraints

**Label every rule studied, asserted, or derived. Do not promote asserted to studied.** A rule the pass builds from
sourced criteria is *derived*, and its derivation is stated.

Every figure is checked against the source text rather than a summary. Carry corrections and name them as corrections.
Report an unreachable source as unreachable rather than confirming it from memory.

Read `seed_baseline.md`, `phase1a_result.md` and `phase1b_result.md` in the same directory before starting; this brief is
self-contained on the shortlist, but the results carry the inventories, the rejects and the URLs.
