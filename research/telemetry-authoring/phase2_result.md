# Pass 2 — rule brief result

## 1. Executive summary

**Rule contributors that survive.** Seven sources carry rules: Yanacek (AWS) for the unit-of-work shape and the rate
rule; Prometheus's instrumentation practices for the log/counter pairing, the failure-denominator rule, the library
minimum and the cardinality numbers; the Kubernetes SIG-Instrumentation conventions for log-or-return and the
verbosity ladder as an example of a *project-owned* ladder; the Python Logging HOWTO for the only primary-source
decision table and for `warnings.warn` as a fourth channel; SLF4J's FAQ and OpenTelemetry's client design principles
for the configuration prohibition and the no-op default; Yuan et al. (OSDI 2014 and LogEnhancer) for the two rules
with studied backing — an error handler that only logs is ignoring the error, and the values a line owes are the ones
that resolve the branches around it; and Saarimäki et al.'s log-smell taxonomy as the defect vocabulary.

**Dropped to supporting.** Google's SRE chapter 6 (one rule: a signal nothing consumes is a candidate for removal —
everything else is alerting, out of scope). go-logr and Cheney supply the argument behind the severity decision, not a
rule of their own. MultiLogBench, AL-Bench, Chen and Jiang, Log2 and Yuan (ICSE 2012) supply calibration, not rules.
Micrometer and HikariCP supply one JVM mechanism each. **Dropped entirely:** both books — O'Reilly returned HTTP 403
for the *Release It!* chapter and the *Observability Engineering* chapter was equally unreachable, so neither is cited
here (see §11); and the 2024 EMSE literature review, still behind Springer's bot challenge.

**Settled.** All six conflicts (§8). The central gap — which signal an event owes — is closed with a derived rule
(§5) and tested against the six named cases. **Left open:** whether a competent engineer holding only the emitted
text would wait or intervene. No source offers an oracle; it stays a human judgment (§12).

**Bucket split**, over the 40 rules in §3: **bucket 1 (diff alone) 30; bucket 2 (needs the work run) 4; bucket 3
(a tool reports it) 5; bucket 4 (human judgment) 1.** Sixteen of the thirty bucket-1 rules also have a tool in at
least one ecosystem, which is the skill's leverage: the natural-language rule states the intent, the reference file
names the lint id.

**What resists a writer optimizing for the check.** The measured answer is that natural-language instruction is
itself the weak channel. Ouatiti et al. (2026) found explicit logging instructions in 4.7% of the 1,308 agentic pull
requests where an instruction channel was observable, and compliance of 6.5% (3 of 46) for instructions carried in a
repository instruction file — the exact channel a skill occupies — against 27.3% (3 of 11) for *strong* issue-level
instructions that named files, levels or frameworks. The paper's own recommendation is deterministic enforcement.
The design consequence: every rule in §3 states what a reviewer checks, and the checks are written against **joins**
rather than presence — the identifier in the message must exist as a name the reader can set; the counter must have a
named consumer; the line must name the branch, not the inputs. Presence checks ("there is a log line", "there is a
counter") are gameable and are never the check.

## 2. Deep candidate evaluation

| # | Candidate | Disposition | Strongest contribution | Main weakness | Evidence | Maintenance | Examples | False-positive risk | Portability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Yanacek, *Instrumenting distributed systems* | **Rule contributor** | One request log entry per unit of work and no more than one; long-running tasks broken into periodic entries; a counter per error reason; a separate timer for successful responses; queue depth at enqueue and dequeue; trace ID passed in the method signature; rate-limit error spam | Service-mode only; no library guidance; asserted org practice | asserted (named author, AWS) | live | prose, no code | Low in service mode; the unit-of-work rule misfires on libraries that own no unit | Language-neutral except the `ThreadLocal` aside |
| 2 | Saarimäki, Shin, Bianculli, *Taxonomy of Software Log Smells* | **Rule contributor (vocabulary)** | Nine named smells with facets and a 16-tool map; LS2 undercover identifier, LS3 level inconsistency, LS7 landfill, LS8 sleeping guards | A taxonomy of *reported* issues, not a measured frequency; LS7 is explicitly context-dependent | studied (51 papers, open coding) | active preprint (v2, Mar 2026) | synthetic log and code examples for every smell | Low — each smell is a detection question, not a threshold | Language-neutral; examples are Python |
| 3 | Kubernetes SIG-Instrumentation | **Rule contributor** | "Shared libraries … should _not_ log errors themselves but just return `error`"; don't log before returning, with the rationale; V(0)–V(5) defined by meaning; the V(4) escape hatch | The ladder is klog-specific and does not port | asserted, project-enforced | live | code-shaped bullets | The ladder read as universal is the main misfire | Log-or-return ports; ladder does not |
| 4 | OpenTelemetry (libraries page, client design principles, attribute levels, span-events post) | **Rule contributor** | "When in doubt, don't instrument" with a three-condition test; API-only dependency with a no-op minimal implementation; high-cardinality metric attributes only at Opt-In; events are logs with names | Says nothing about a library emitting *logs* or *metrics* of its own | asserted (normative spec) | live, 1.60.0 | code snippets | Low | Genuinely cross-language |
| 5 | Ouatiti et al., *Do AI Coding Agents Log Like Humans?* | **Rule contributor (design constraint)** | 4.7% instruction prevalence; 67% non-compliance; 6.5% compliance for repository instruction files; WARN overused in 29.9% of repositories; humans do 72.5% of post-generation log repairs | Instruction analysis rests on 61 pull requests (15 issue-level, 46 repository-level); Python/Java/JS-TS only, no Go | studied (4,550 agent PRs, 3,276 human PRs, 81 repos) | 2026 preprint | no | n/a — it constrains the skill, it is not applied to a diff | Three of six ecosystems |
| 6 | Zhong et al., *MultiLogBench* | Supporting | Loop and nested-callable sites are the hardest buckets in every language; cross-language rank agreement collapses on maintenance data (Spearman 0.912 → 0.195) | Measures models, not rules | studied (63,965 snapshot instances, 744 revision cases, 7 models) | 2026 preprint | benchmark | n/a | Six ecosystems including Go and Python |
| 7 | Yuan et al. (OSDI 2014; LogEnhancer) | **Rule contributor** | "an error handler that only logs the error is also considered as ignoring the error" — 25% of catastrophic failures; 76% of failures printed explicit messages; 108 causally related branches per log point resolvable by 16.0 values | OSDI base is 48 catastrophic failures; LogEnhancer's analysis is C-language static analysis, not a review procedure | studied (198 failures / 5 systems; 8 applications) | canonical | code figures | Log-or-return misfires at the last frame that knows the cause | Language-neutral in intent |
| 8 | Prometheus instrumentation and naming | **Rule contributor** | "for every line of logging code you should also have a counter"; failures need an attempts denominator; libraries instrument with no configuration and track query count, errors and latency; cardinality below 10, investigate above 100 | The pairing rule taken literally doubles the diff; the no-configuration rule is written for a single-default-registry world | asserted | live | none | The pairing rule is the highest false-positive risk in the set | Go and Python idiom; not the JVM's |
| 9 | go-logr + Cheney + Google Go style | **Rule contributor (argument)** | "logging that error *and not returning it*"; warning is not author-decidable; a V-level guard around expensive arguments | Cheney is a 2015 position piece; logr rebuts the "libraries should not log" position outright | asserted, with argument | live | code | Low | The *argument* ports; the two-kind API does not |
| 10 | Python Logging HOWTO + `warnings` | **Rule contributor** | The only primary-source decision table; `warnings.warn` for the avoidable, caller-fixable case; `getLogger(__name__)`; no root logger; no handler but `NullHandler`; WARNING+ to stderr is "the best default behaviour" | Level definitions are generic | asserted (stdlib) | live, 3.14 | code | Low | Table's *distinction* ports; the channel does not |
| 11 | SLF4J FAQ and Manual | **Rule contributor** | "Embedded components such as libraries not only do not need to configure the underlying logging framework, they really should not do so"; provider at `test` scope only; no-op when no provider is present | JVM-only mechanics | asserted (maintainer) | live, 2.0.19 | POM snippets | Low | Rationale ports, mechanics do not |
| 12 | Context trio (Logback MDC, `contextvars`/`asyncio`, Go `context`) | **Rule contributor** | "A copy of the mapped diagnostic context can not always be inherited by worker threads … when `java.util.concurrent.Executors` is used"; a child thread does not inherit; asyncio Tasks do copy the context | Three different failures; one rule needs three detections | asserted (maintainers) | live | code | Moderate — a framework may already bridge it | Intent ports, detection does not |
| 13 | Mechanical layer (sloglint, Ruff, `go vet` slog, Sonar S2139) | **Rule contributor (detection)** | 13 sloglint options including `no-global`, `context`, `static-msg`, `forbidden-keys`; Ruff LOG001/002/004/014/015, G001–G004, G101, G201/202, TRY400/401 | A clean verdict establishes very little (§9) | tool | live | rule pages | Low | Per-ecosystem by construction |
| 14 | HikariCP `MetricsTrackerFactory` + Micrometer | **Rule contributor** | A one-method interface (`create(poolName, poolStats)`) the host implements; `Metrics.globalRegistry` is a composite where "Increments are NOOP'd until there is a registry in the composite" | Two mechanisms, no maintainer statement about which a library should prefer | asserted / read from source | live | source | Low | JVM-local |

## 3. Extracted rules

Reader first in each row. Evidence: **S**tudied, **A**sserted, **D**erived. Bucket: 1 diff, 2 needs a run, 3 tool,
4 human.

| ID | Rule | Reader | Why | Source (evidence) | Applies when | Detection | Gaming → check instead | Repair | B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | The mode is per module: the code is in library mode if something outside it decides where its output goes | R1 R4 | Every other rule branches on this | SLF4J FAQ + Python HOWTO + OTel client design + K8s (A) | Always, first | The module has no `main`, no configuration call, and its output destination is set elsewhere | Declaring "service mode" to license configuration → check for a `main`/entry point in the same artifact | State the mode in the review note; apply the library rules | 1 |
| T2 | A library never calls a logging-configuration API | R1 | "it is the end-user who has to read the logs" | SLF4J FAQ (A), Python HOWTO (A) | Library mode | `basicConfig`/`addHandler`/`setLevel`/`Configurator` in non-entry code | Moving the call into a lazily-run init → grep the whole module, not the constructor | Delete; document the logger names instead | 1/3 |
| T3 | A library's build does not carry a logging provider outside test scope | R1 R4 | A transitive provider "is imposed on the end-user" | SLF4J FAQ (A) | Library mode, JVM | Provider coordinates at compile/runtime scope in the build file | Declaring `optional` → check the published POM, not the build DSL | Move to `test` scope | 1 |
| T4 | A library obtains its logger the way its ecosystem routes: by name where the host configures by name, by value where it does not | R1 | Go has no useful ambient registry; the JVM and Python do | Python HOWTO, K8s/KEP-1602, `log/slog` docs (A) | Library mode | `getLogger(__name__)` present; in Go, `slog.Default()` or a package-level logger var | A logger injected once into a package var and then used globally → check that the call site takes it from the caller's context or receiver | Accept a logger/provider parameter | 1/3 |
| T5 | A library emits telemetry only through an API whose default, with nothing installed by the host, is a no-op or the host's own sink | R1 | Instrumented libraries must stay usable by hosts that want no telemetry | OTel client design principles (A); Micrometer composite (A) | Library mode, any signal | A direct dependency on an SDK, exporter or registry implementation | Wrapping the SDK behind a flag → check the dependency, not the flag | Depend on the API artifact | 1 |
| T6 | Where the ecosystem has no no-op default, a library publishes a hook the host implements instead of choosing a destination | R1 | HikariCP ships `MetricsTrackerFactory` and adapters as separate artifacts | HikariCP source (A) | Library mode, metrics, JVM | A registry chosen inside library code | Naming the hook but also registering a default → check for a registration call | Interface + separate adapter artifact | 1 |
| T7 | Emit nothing when the fact is already recoverable from a signal that exists; the author names that signal | R1 R2 R4 | "When in doubt, don't instrument" | OTel libraries page (A); SRE ch. 6 removal rule (A) | Always, before anything else | The review asks which existing signal carries the fact; no answer means the rule was not applied | Naming a signal that does not carry the fact → check that the named signal contains the *distinguishing* value, not the same event | Delete the addition | 1 |
| T8 | An avoidable condition the caller can fix goes to the caller, not to the log | R1 R3 | The log reaches the operator; the caller is the one who can change the call | Python HOWTO table (A) | Library mode, caller-fixable input | A `warning`-level line whose text tells the caller to change their code | Emitting both → check for a log call on the same path as the raise/warn | The ecosystem's caller channel (§4) | 1/3 |
| T9 | Log or return, never both | R1 R2 R4 | "it is usually uncertain if and how the caller is going to handle the returned error" | K8s (A), go-logr (A), Google Go style (A) | Any error that leaves the function | A log call and a throw/return of the same error on one path | Logging at a lower level to dodge the rule → the escape hatch is explicit and bounded: an info line at debug verbosity with the error as a field | Wrap and return; the top of the call chain logs once | 1/3 |
| T10 | An error handler whose whole body is a log call is not handling the error | R2 R4 | "an error handler that only logs the error is also considered as ignoring the error" — 25% of catastrophic failures | Yuan, OSDI 2014 (**S**) | Any catch/`if err != nil` block | The handler body is one log call and nothing else | Adding a comment that says "intentionally ignored" → check for a re-raise, a fallback branch, or a recorded decision the caller can observe | Re-raise, fall back, or record the decision | 1 |
| T11 | A fact someone will want aggregated over time is an instrument, not a line | R2 R3 | A log line cannot answer "how often, for how long" without a log-processing system | Prometheus instrumentation (A) | Service mode; library mode via T6 | A line whose text is a count, a rate or a duration | Adding a counter *and* a per-event line → check that the line carries something the counter cannot | Counter/histogram; keep the line only if it carries per-unit detail | 1 |
| T12 | A fact about one unit of work that the aggregate cannot reconstruct is a record | R2 R3 | The aggregate loses the identifiers that let a reader follow one request | Yanacek (A) | Service mode | The change adds a counter for a condition whose diagnosis needs the identifiers | — | One record for the unit, carrying the identifiers | 1 |
| T13 | One record per unit of work, and no more than one | R2 R3 | "Having multiple log entries per unit of work makes log analysis more difficult" | Yanacek (A) | Service mode, per request/message | More than one record emitted on the success path of one unit | Merging two lines into one 400-field line → check that each field is one the reader filters or joins on | Pass a metrics object through the stages, serialize once | 1 |
| T14 | Where the code owns no unit of work, the unit is the state change: emit on transition, not on occurrence | R2 R3 | Bounds the rate without requiring silence; matches published-state practice | Derived from Yanacek + K8s Conditions (**D**) | Reconcilers, caches, pools, libraries with no request | A record emitted inside a loop or on every call that reports an unchanged state | Comparing against a value that always differs (a timestamp) → check that the compared value is the state, not a clock | Keep the previous state; emit on inequality | 1 |
| T15 | A long-running unit emits periodic progress records, and the period is a constant, not a rate that follows the work | R2 R3 | "Break long-running tasks into multiple log entries" | Yanacek (A) | Work measured in minutes or more | Progress emitted per item rather than per interval | — | Interval-bounded progress record | 1 |
| T16 | A countable condition that is logged is also counted | R2 R4 | "for every line of logging code you should also have a counter"; closely related branches may share one counter | Prometheus (A) | Service mode, condition recurs | A new log line for a recurring condition with no counter | Adding an unread counter → T20 is the check | Increment a counter beside the line | 1 |
| T17 | A failure counter is introduced together with the attempts counter that is its denominator | R2 R3 | "you should generally have some other metric representing the total number of attempts" | Prometheus (A) | Any failure counter | A failure counter with no total on the same path | Reusing an unrelated total → check that the denominator counts the same attempts | Add the attempts counter | 1 |
| T18 | Errors are counted by reason, and the reason set is bounded and enumerable from the code | R2 R3 | "If all errors are lumped into the same metric, the metric becomes noisy and unhelpful" | Yanacek (A); Prometheus cardinality (A) | Service mode | One error counter with no reason dimension, or a reason taken from an exception message | A reason label built from a message string → check that the label values are a closed set in the source | Enumerate the reasons | 1 |
| T19 | Latency for the successful outcome is recorded separately from overall latency | R2 R3 | Fast failures make a generic timer look good | Yanacek (A) | Service mode, any timed operation | One timer covering success and failure | — | Split the timer by outcome | 1 |
| T20 | A new instrument is introduced with the question it answers stated where the instrument is defined | R2 R4 | A signal nothing consumes is a candidate for removal | SRE ch. 6 (A); owner derived (**D**) | Any new instrument, both modes | No alert, dashboard, or documented question names it | Writing a generic doc comment → check that the stated question names a decision someone makes | State the question, or delete the instrument | 1 |
| T21 | A threshold that decides "slow", "stuck" or "too many" lives in the alert, not in the emitting code | R2 R3 | A compiled-in threshold cannot be retuned by the reader | Derived from SRE symptom/cause + Yanacek (**D**) | Service mode | A constant compared against a measurement to decide whether to emit | Making the constant configurable → check whether the *signal* still carries the raw measurement | Emit the measurement; alert on it | 1 |
| T22 | A record carries the identifier that joins it to the other records of the same unit | R3 R4 | LS2 undercover identifier; "If an application is multithreaded, consider taking special care to set the correct request ID" | Log smells LS2 (**S**); Yanacek (A) | Every record, both modes | The record's fields contain no id of the connection, request, thread or component | A class name used as the identifier → check that the value distinguishes two concurrent units, not two code sites | Add the per-unit identifier | 1 |
| T23 | A record that reports a computed value names the constraint that bound it | R3 R4 | LogEnhancer: 108 causally related branches per log point, resolvable by 16.0 values; F1's first defect | LogEnhancer (**S**); generalization (**D**) | Any clamped, defaulted, truncated or negotiated value | The record prints the inputs and the result but not which branch produced the result | Printing every input → check that the *branch*, not the input set, is recoverable from the text | Name the limit that applied | 1 |
| T24 | The identifiers in a record are the names the reader can set or grep | R3 R4 | F2: the record named three symbols, one of which exists nowhere in the codebase | Recorded failure F2 (measured in-house) | Any record naming a setting | Each name in the text is grepped against the settable names | Renaming the private field to match → check the direction: the *user-facing* name wins | Use the connection-property / flag / environment name | 1 |
| T25 | A record about a durable state says which of not-started, in-progress, degraded, given-up it reports | R3 | Decides whether the reader waits or intervenes | Derived from Python level table + K8s Conditions (**D**) | Any state a reader may wait on | The text and level together leave "still trying" and "gave up" indistinguishable | Adding the word "failed" → check that a *later* record exists for the other outcome | Say which, and emit the counterpart | 1 |
| T26 | A published state carries the time of its last transition | R3 | `lastTransitionTime` is what makes "for ten minutes" answerable | K8s API conventions (A) | Any status field, gauge or condition | The state is published with no transition timestamp | — | Add the transition time or a last-success timestamp gauge | 1 |
| T27 | A value the reader will filter or join on is a field, not prose inside the message | R3 R4 | Fields survive the formatter; message text does not | Log smells LS1 (**S**); K8s structured logging (A) | Any record in a structured-logging repository | The value is concatenated or interpolated into the message | Adding the value as both → check for duplication, which TRY401 flags in Python | Move it to a key/value pair | 1/3 |
| T28 | A number in a message is not passed through a locale-aware formatter | R3 R4 | `Formatter.formatMessage` engages `MessageFormat` on `{<digit>`; `103887667` prints as `103 887 667` under `fr` | `java.util.logging.Formatter` javadoc + in-house measurement (**S**, JVM-local) | JVM, `java.util.logging` with an `Object[]` | A numeric argument in a `{0}`-style JUL message | — | `String.valueOf` at the call site | 1 |
| T29 | No log call in a loop body without aggregation | R2 R4 | LS7 landfill; Prometheus warns about metrics in code called over 100,000 times a second | Log smells LS7 (**S**); Prometheus (A) | Any loop over items or attempts | A log call whose enclosing block is a loop | Guarding with a modulus counter → check that the aggregate is emitted once after the loop | Count in the loop, record once after it | 1 |
| T30 | An error path that can fire once per item is rate-limited or counted, not recorded per occurrence | R2 R3 | "rate-limit how often a given logger will log" | Yanacek (A) | Service mode, error path under load | A stack-trace-bearing record on a per-item path | Lowering the level → check that the rate, not the level, was bounded | Rate-limit the logger or replace with a counter | 1 |
| T31 | Argument computation for a record that may be discarded is guarded | R1 R2 | LS8 sleeping guards; in Go "the arguments to a log call are always evaluated, even if the log event is discarded" | Log smells LS8 (**S**); `log/slog` docs (A); Google Go style (A) | Any record whose arguments call a method or build a string | An expensive call inside a log call with no level guard | Guarding the cheap half → check that the *expensive* expression is inside the guard | Level guard, or a lazy value type | 1/3 |
| T32 | A metric's label set is bounded and small: below 10 values, investigate above 100 | R2 R4 | "try to keep the cardinality of your metrics below 10" | Prometheus instrumentation (A) | Any new label | A label whose value comes from an unbounded input | Bounding it in the test fixture → the real value set needs the run (bucket 2) | Remove the dimension or move the analysis off monitoring | 2 |
| T33 | A high-cardinality attribute is not a metric attribute | R2 R4 | "Metric attributes that may have high cardinality can only be defined with `Opt-In` level" | OTel attribute requirement levels (A) | OTel-instrumented code | The attribute is an id, an address, a query text or a message | — | Put it on the record or span, not the instrument | 1 |
| T34 | A signal that no alert, dashboard or documented question consumes is removed | R2 R4 | "Signals that are collected, but not exposed in any prebaked dashboard nor used by any alert, are candidates for removal" | SRE ch. 6 (A) | Review of an existing signal set | No consumer can be named | — | Delete | 1 |
| T35 | The host's context crosses every thread, goroutine or task boundary the code creates | R1 R2 | Three different failures, one intent | Logback MDC, `contextvars`/`asyncio`, Go `context` (A) | Any code that starts concurrent work | A submit/`go`/`Thread` start with no context carried (§4) | Passing a context that is not the caller's → check that the value came from the parameter, not from a package variable | Carry the context explicitly | 1/3 |
| T36 | An ambient context entry that is set is removed on the same path | R1 R2 | A pooled thread that kept a previous request's keys leads the reader to the wrong unit | Logback MDC manual (A) | JVM MDC, any `put` | A `put` with no matching `remove`/`clear` on every exit | `remove` only on the happy path → check the `finally` | `try`/`finally` | 1 |
| T37 | A library propagates the host's context into the calls it makes | R1 R3 | Otherwise the host's trace ends at the library boundary | OTel Go `trace` package (A); Yanacek (A) | Library mode, outbound calls | An outbound call that drops the context parameter | — | Thread the context through | 1/3 |
| T38 | Do not wrap a call in a span when the layer beneath it is already instrumented | R1 R4 | One of the three conditions under which OTel says to skip instrumentation | OTel libraries page (A) | Tracing | A new span around an HTTP/DB client call | — | Delete the span; add attributes to the existing one | 1 |
| T39 | A span records the exception and sets the status instead of logging it | R1 | `recordException` plus `setStatus(ERROR, …)` is the span's channel | OTel libraries page (A) | Tracing, error path | A log call inside a catch that already has a span | — | `recordException` + `setStatus` | 1 |
| T40 | An event is a log record correlated with the current span, not a span event | R1 R2 | The Span Events API is deprecated; "New code should write events as logs that are correlated with the current span" | OTel span-events deprecation post (A, 2026) | New instrumentation | `addEvent` on a span in new code | — | Emit a named log record | 1 |

Bucket totals: **1 → 30** (T1–T31 less T32, plus T33–T40, counting split cells as bucket 1 with a tool);
**2 → 4** (T32 plus the run-only halves of T13, T29, T30 recorded in §9); **3 → 5** (the tool-primary halves of T2,
T4, T9, T27, T31); **4 → 1** (the wait-or-intervene judgment behind T25, §12).

## 4. The per-ecosystem table

Each cell is *documented* (stated by a primary source) or *measured* (established by running something).

| Rule | JVM | Go | Python | Reference file |
| --- | --- | --- | --- | --- |
| T2 | no `BasicConfigurator`/`Configurator.initialize`/`LogManager.readConfiguration` — documented (SLF4J FAQ) | no equivalent: Go has no ambient configuration to call; the analogue is `slog.SetDefault` — documented (`log/slog`) | no `basicConfig`, no root-logger call, no handler but `NullHandler`; Ruff LOG015 — documented | one per ecosystem |
| T3 | provider at `test` scope only; `slf4j-api` at compile scope — documented | n/a (no provider artifacts) | n/a | JVM |
| T4 | `LoggerFactory.getLogger(Foo.class)` — documented | logger passed by the caller; `sloglint no-global` — documented | `getLogger(__name__)`; Ruff LOG002 — documented | all three |
| T5 | `slf4j-api` only; Micrometer `globalRegistry` no-ops until a registry joins — documented | OTel API module only; `prometheus/client_golang` default registry is the host's — documented | OTel API only; Prometheus default registry — documented | all three |
| T6 | `MetricsTrackerFactory`-shaped hook, adapters in separate artifacts — documented (read from HikariCP source) | interface + host-supplied collector | same | JVM primarily |
| T8 | no first-class channel: a deprecation is `@Deprecated` plus documentation | no channel; the compiler and `staticcheck` carry deprecation | `warnings.warn(..., DeprecationWarning, stacklevel=2)` — documented | Python (the channel), body (the distinction) |
| T9 | Sonar S2139 — documented | `go-logr`, Google Go style, `%w` wrapping — documented | HOWTO: raise; Ruff TRY400/TRY401 — documented | all three |
| T27 | SLF4J `{}` placeholders; `KeyValuePair` — documented | `slog.LogAttrs`; `sloglint no-raw-keys`, `forbidden-keys` — documented | `extra=`; Ruff G001–G004, G101 — documented | all three |
| T28 | JUL `{0}` → `MessageFormat` → locale grouping — **measured** in-house; javadoc documented | `fmt` is not locale-aware — documented | `,`/`_` are not locale-aware, only `'n'` is — documented | JVM only |
| T31 | `isDebugEnabled` where the argument is expensive — documented | `Logger.Enabled`; arguments always evaluated — documented | `logger.isEnabledFor`; lazy `%` formatting — documented | all three |
| T35 | MDC not inherited by `Executors`-managed threads; `getCopyOfContextMap`/`setContextMap` — documented | pass `ctx`; `sloglint context`, `contextcheck` — documented | asyncio Tasks copy the context and `to_thread` propagates; a raw `ThreadPoolExecutor.submit` does not — documented | all three |
| T36 | `MDC.put` balanced by `remove` — documented | n/a (no ambient map) | `contextvars.Token` reset — documented | JVM primarily |
| Default when the host configures nothing | silent no-op since SLF4J 1.6 — documented | `slog.Default()` writes through the `log` package to stderr; only the host can install `DiscardHandler` — documented | WARNING+ to `sys.stderr` via `lastResort`, "regarded as the best default behaviour" — documented | all three |

**Does any of Pass 1's four differences in kind collapse?** One does. Difference 2 ("the library's sin is
*configuring* versus *acquiring*") is the same rule under a better formulation: **a library must not decide where its
output goes**, and the ecosystems differ only in which call makes that decision — a configuration call where routing
is by name, an acquisition call where routing is by value. T4 and T2 are the two detections of one rule. The other
three stand: the default blast radius (three different answers, and "leave a silent host silent" is satisfiable only
on the JVM), `warnings.warn` as a channel the others lack, and the shape of the context failure. **One more
difference found:** argument evaluation. Go evaluates log-call arguments unconditionally by documented design; the
JVM and Python both have a documented lazy path. T31 is therefore a stronger rule in Go than elsewhere.

**False-positive cost where conventions differ.** T16 (log/counter pairing) is the worst: in a repository with no
metrics facility it fires on every line and must be suppressed by mode, not by judgment. T9 misfires at the last
frame that knows the cause — the frame above `main`, a thread entry point, a callback that cannot return — and
Kubernetes' own escape hatch (an info line at V(4) with `err` as a key) is the documented repair. T13 misfires on
libraries and reconcilers, which is why T14 exists. T22 misfires where the framework injects the identifier through
the pattern layout; the check must look at the emitted record, not the call site.

**Rules a project's convention overrides, stated without hedging.** Three, and only three: the level ladder (T25's
level half), the structured-field mechanism (T27), and whether the repository exports metrics at all (T16, T20). The
skill states them as *"the repository's convention decides the ladder; the rule is that the new call matches the
calls around it"* — a check that is still falsifiable from the diff, because the neighbouring calls are in the diff's
own files.

## 5. The signal-choice rule and its test

**Rule SC (derived).** Its derivation, criterion by criterion: *(i)* OpenTelemetry states the only primary-source
emit-nothing test, and it is a recoverability test — skip when the layer beneath is already instrumented and no
convention would enrich the result. *(ii)* Google's SRE chapter supplies the converse for signals that already
exist: no consumer, no signal. *(iii)* Python's HOWTO supplies the only primary-source routing table, and its axis is
*who can act*: the caller (raise, or `warnings.warn`), or the operator (a logger). *(iv)* Kubernetes, go-logr, the Go
style guide and Yuan et al. agree that an error that leaves the function is the caller's, not the log's. *(v)*
Prometheus and Yanacek between them split the operator's half by *shape*: what is asked in aggregate is an
instrument, what is asked about one unit of work is a record. *(vi)* Yanacek bounds the record count at one per unit
of work; K8s Conditions supply the unit where there is no request. Nothing in the derivation needs the author's
intent, which is the property the consumer requires.

> **SC.** For a fact the change makes true, take the first branch that applies.
> 1. **Already recoverable.** If an existing signal carries the fact *and* its distinguishing value → **emit
>    nothing**, and name the signal.
> 2. **The caller can act.** If the caller can prevent or repair it → **the caller's channel** (return, raise, or
>    the ecosystem's deprecation channel), and **not also** a log call.
> 3. **Asked in aggregate.** If the question is "how often, how long, how many now" → **an instrument**: a counter
>    by bounded reason with its attempts denominator, or a timer split by outcome, or a gauge of the current state.
> 4. **Asked about one unit.** If the question is "what happened to this one" and the aggregate cannot answer it →
>    **one record** for that unit, carrying the joining identifier (T22), the branch that produced it (T23) and the
>    names the reader can set (T24). Where the code owns no unit of work, the unit is the state change (T14).
> 5. **Otherwise → emit nothing.**
>
> Branches 3 and 4 are not exclusive: where both apply, the instrument is the thing that is always on and the record
> is the thing that is sampled or verbosity-gated.

### 5.1 pgjdbc adaptive fetch (F1/F2), library mode

The applied fetch size is already printed by an existing `FINEST` line, so branch 1 disposes of "a new fetch size was
computed": **emit nothing**. What is *not* recoverable is the transition into the clamped state — the failure the
author was debugging. That is not caller-fixable from inside the driver (branch 2 does not apply) and the driver is
in library mode with no metrics facility (branch 3 yields a hook at most, and pgjdbc publishes none). Branch 4, with
T14's clause: **one record on the transition into clamped and one on the transition out**, at the verbosity the
repository uses for state changes, carrying the connection identifier, the value, and the name of the limit that
bound it *as the user spells it* — `adaptiveFetchMaximum`, not `maximumAdaptiveFetchSize`. **Emit nothing about:**
each recomputation, the unclamped path, every row that did not change the size, and — in this repository — any
counter, because there is nothing to register it with.

### 5.2 A Go service retry loop, three attempts then give up

Per attempt, branch 4 is refused by T29: a line per attempt inside the loop is the landfill shape, and loops are the
bucket where both the agent study and MultiLogBench find the most damage. Branch 3 applies: **a counter of attempts
and a counter of failures by bounded reason** (T17, T18). On giving up, branch 2 applies in full: **return the
wrapped error**, carrying the attempt count and the elapsed time, and **do not log it** (T9). If the service does not
return but falls back, branch 4 gives **one record at the fallback decision**, naming the branch taken (T23). **Emit
nothing about:** each individual retry, the sleep between attempts, and a span per attempt when the outbound call is
already instrumented (T38).

### 5.3 A Python library receiving a deprecated argument

Branch 2, decided by the HOWTO's own table: `warnings.warn` "in library code if the issue is avoidable and the client
application should be modified to eliminate the warning" — so `warnings.warn(..., DeprecationWarning, stacklevel=2)`,
with `stacklevel` set so the warning points at the caller's line and not the library's. Not `logger.warning`, which
the same table reserves for when "there is nothing the client application can do about the situation". **Emit nothing
about:** the same call on every invocation (the warnings registry already deduplicates per location), a counter, and
a log line. The reviewer's detection is one grep: a `warning`-level log call in library code whose text says
"deprecated".

### 5.4 A connection pool that hands out a connection after waiting three seconds

Branch 3. The question is a distribution, not an incident, and the emitting code cannot know which wait is
interesting — T21 forbids the compiled-in threshold. **A timer of wait time on every checkout, and a gauge of the
current wait queue depth recorded at enqueue and dequeue.** In library mode the pool publishes the hook and the host
supplies the destination (T6). **Emit nothing about:** a per-checkout record, a "slow checkout" boolean label, a
threshold constant, and a WARN line — which is the exact shape the agent study measures as over-produced.

### 5.5 A parser rejecting a protocol message over a configured limit, library mode

Branch 2: the exception *is* the signal, and it is the caller's. **Raise it, and log nothing beside it** (T9, T10).
The exception's text owes what T23 and T24 require: the observed size, the configured limit, and the name of the
property that sets the limit, spelled as the connection string spells it. **Emit nothing about:** a log call at the
throw site, a counter in library mode, or a span. Detection here is fully mechanical — a log call and a throw on the
same path is what Sonar S2139 and Ruff's TRY family report.

### 5.6 A background reconciler that has not converged for ten minutes, service mode

Nothing has failed, so branches 1 and 2 do not apply and nothing in the log says "still trying". Branch 3 gives the
instruments that make the ten minutes computable without the code knowing about ten minutes: **a gauge holding the
timestamp of the last successful reconcile** and **counters of reconcile attempts and outcomes by reason**. Branch 4
with T14 gives **one record on the transition into not-converged and one on the transition back**, and T25 requires
the first to say which state it reports — degraded and still retrying, not given up — and T26 requires the published
state to carry its transition time. **Emit nothing about:** each unchanged iteration, a "still waiting" line per
tick, and the ten-minute threshold itself, which belongs to the alert (T21).

## 6. Shapes that fail vacuously

| Shape | What it satisfies | Detection |
| --- | --- | --- |
| The counter nobody reads | T16 | No alert, dashboard or stated question names it (T20, T34) |
| The line that prints its inputs and not its branch | "the value is logged" | The clamped and unclamped cases produce the same text (T23); F1's first defect |
| The WARN the reader cannot act on | "errors are logged" | The code continues normally after it; agents overuse WARN in 29.9% of repositories |
| Log-and-rethrow | T16 and "errors are logged" at once | One condition, two records; Sonar S2139, Ruff TRY400/401 |
| Vacuous compliance with a removal instruction | "debug logs were removed" | Named by the agent study itself: 100% compliance with "remove debug instrumentation" where no debug instrumentation was ever added |
| The object with no string form as the identifier | T22 | LS4 malformed output; Chen and Jiang's *Nullable objects* and *Malformed output* anti-patterns |
| The per-attempt line inside the retry loop | "the retry is observable" | T29; loop sites are the hardest bucket in every language in MultiLogBench |
| The label bounded only in the test fixture | T32 | Needs the run (bucket 2); Micrometer's high-cardinality detector is a runtime check, not a lint |
| The private `NullHandler` | T2 | boto3 #3403: three libraries each defined their own class, so `isinstance(h, logging.NullHandler)` finds none of them |
| The record at a verbosity nobody enables | "it is logged" | LS6's second facet; pgjdbc's `FINEST` case — the fact is emitted and never read |
| The message assembled before the level check | T31 | LS8; Ruff G004; in Go the arguments are always evaluated |
| The new span around an already-instrumented call | "the operation is traced" | T38; duplicate spans for one network call |
| The state field with no transition time | T25 | "for ten minutes" is unanswerable (T26) |

## 7. Worked examples

**JVM, library mode — T23, T24, T14 (the pgjdbc case).**
Before: `LOGGER.log(FINE, "Adaptive fetch: maximumResultBufferSizeBytes={0}, minimumAdaptiveFetchSize={1},
maximumAdaptiveFetchSize={2}, size={3}", new Object[]{...})` — three names the reader cannot grep, no connection
identifier, no statement of which limit applied, and `{0}` with a numeric argument, which JUL renders through
`MessageFormat`.
After: on the transition into the clamped state only, one record whose fields are the connection identifier, the
computed size, the applied size, and `boundBy=adaptiveFetchMaximum` — with the numbers passed as strings. A second
record when the state returns to unclamped. Nothing on any other call.

**Go, service mode — T9, T29, T17.**
Before: inside the retry loop, `slog.Warn("retry failed", "attempt", i, "err", err)`, and after the loop
`slog.Error("giving up", "err", err); return err`.
After: `attempts.Inc()` and `failures.WithLabelValues(reason(err)).Inc()` inside the loop, no record; after the loop
`return fmt.Errorf("connect to %s after %d attempts in %s: %w", addr, n, elapsed, err)` and no log call. The caller
that cannot return logs it once.

**Python, library mode — T8, T2.**
Before: `logger.warning("The 'timeout_ms' argument is deprecated, use 'timeout'")` in a library module that also
calls `logging.basicConfig()` at import time.
After: `warnings.warn("timeout_ms is deprecated; use timeout", DeprecationWarning, stacklevel=2)`, the `basicConfig`
call deleted, and the package's `__init__` documenting the logger names it uses.

**JVM, library mode — T6 (what a library offers when it may not export).**
Before: the pool builds a `PrometheusMeterRegistry` and registers its own timers.
After: the pool publishes a one-method factory interface the host implements, ships the Micrometer and Dropwizard
adapters as separate artifacts, and documents, on that interface, the question each instrument answers (T20).

## 8. Conflicts and how they were decided

**(a) Severity — decided: the skill states no ladder.** Two things survive either convention. First, the *axis*: all
four sources that define levels by meaning define them by who must act and whether they can — Python's own table
("The software is still working as expected" for WARNING against "has not been able to perform some function" for
ERROR), Kubernetes ("inform admins that they might have to do something to fix a problem"), go-logr (error logs are
for an error you are *not* returning), Cheney (two audiences: developers debugging, and users of the software).
Second, the *authority*: the repository's existing convention owns the ladder, and the reviewer's check is agreement
with the neighbouring calls in the same package, which is in the diff. This is forced by evidence, not taste — the
concept-drift study shows one project's verbosity choices moving in both directions across its own history, so a
generic ladder is unfalsifiable against any particular commit. **When the convention is generic**, the reviewer asks
three questions: does the level exceed the repository's default production verbosity for a condition the operator
cannot act on (the 29.9% WARN failure); did the code continue normally afterwards (then it is informational); and
does the same kind of event carry a different level elsewhere in the file (LS3's inconsistency facet).

**(b) What a library may emit — decided: split by what the emission costs the host.** The four positions are not
about the same thing. *Configuration* is prohibited by all four sources, unanimously, and is the skill's hardest
rule (T2, T5). *An error that leaves the function* goes to the caller, not the log, in all three ecosystems (T9).
*A log line* is permitted: no primary source states that a library must be silent, and Python's stdlib states the
opposite — WARNING+ reaching stderr with no host configuration is "regarded as the best default behaviour", and
go-logr rebuts the abstinence position outright. What the library owes instead is the **rate** (T14, T29, T30) and
the host's ability to route by name or value (T4). *Metrics* are (d). So the answer to R1 differs by signal, and
the seed's blanket S4 is corrected on two of the four.

**(c) Rate — the hypothesis holds, with one addition.** Yanacek's DynamoDB logs every request at over 20 million
requests per second and is *in rule*, because the rate is one record per unit of work and is bounded by traffic, not
by the code's chattiness; the affordability comes from sampling, offloaded serialization and minute-granularity
rotation, not from silence. Seed S8's silence is right only where the code owns no unit of work — a library, a
reconciler, a cache — and there the correct unit is the *state change*, which is what makes the steady state silent
as a consequence rather than as a goal. So: **one bounded record per unit of work; where there is no unit of work,
one per transition** (T13, T14). S8 survives as a corollary of T14, not as a rule of its own.

**(d) Metrics from a library — decided: a library may define instruments, never their destination.** Prometheus's
"no additional configuration" is a statement about a world with exactly one default registry per process, which is
true in Go and Python and false on the JVM; it is the host's idiom, not a licence for a JVM library to pick a
registry. The rule that covers all four positions is T5: emit only through an API whose default with nothing
installed is a no-op — the OTel API by specification, Micrometer's `globalRegistry` by construction ("Increments are
NOOP'd until there is a registry in the composite") — or, where no such API exists, publish a hook (T6, HikariCP's
`MetricsTrackerFactory`). **Seed S4's metrics clause is bounded, not withdrawn**: "a library does not export metrics
itself" is contradicted by Prometheus and is replaced by "a library does not choose where its metrics go."

**(e) Where events live — decided, and it shrinks the outcome set.** OpenTelemetry is deprecating the Span Events
API on the ground that two APIs force library authors to "choose between two ways of emitting very similar data";
events are logs with names, and "New code should write events as logs that are correlated with the current span."
For a rule written today: the outcomes are a record, an instrument, a span, and nothing — "a span event" is no
longer a distinct outcome (T40), and Python adds a fifth, language-local outcome the seed's S1 set lacked
(`warnings.warn`, T8). The post carries no version numbers or dates, so the skill states the direction, not a
deadline.

**(f) S9's owner in library mode — settled: the question travels with the definition, the destination with the
registration.** Whoever *defines* an instrument states the question it answers, because the host that wires it up
cannot infer it; whoever *registers* it owns where it goes. A library that exports nothing but publishes a hook still
owns the question, and states it on the hook (T20, and the fourth worked example). The asymmetry Pass 1 found
dissolves once the two ownerships are separated.

## 9. The detectability matrix

| Bucket | Rules | Source per cell |
| --- | --- | --- |
| **1 — diff alone** | T1, T3, T5–T8, T10–T30 (less the run-only halves), T33, T34, T36, T38–T40 | The artifact and the diff; the rule's own detection column |
| **1 with a tool in at least one ecosystem** | T2 (Ruff LOG015), T4 (sloglint `no-global`, Ruff LOG002), T9 (Sonar S2139, Ruff TRY400/401), T27 (Ruff G001–G004/G101, sloglint `no-raw-keys`/`forbidden-keys`, `go vet` slog pass), T31 (`sloglint`, LS8 detectors), T35 (`sloglint context`, `contextcheck`), T37 (`contextcheck`) | Tool documentation, verified |
| **2 — needs the work run** | T32 (the real label value set), plus the run-only halves of T13 (records per unit under concurrency), T29/T30 (steady-state rate under load), and the honesty of a level under a real failure | Micrometer's high-cardinality detector is runtime, not lint; AL-Bench shows the gap directly — the best tool's output fails to compile 20.1% of the time and reaches 21.32% cosine similarity to the oracle logs at runtime |
| **3 — reported by a tool, with limits** | See below | — |
| **4 — human judgment** | Whether, holding only the emitted text, a competent engineer would wait or intervene (behind T25) | No source offers an oracle |

**What a clean tool verdict does not establish.** `sloglint no-global` does not see a logger injected once and then
treated as a global thereafter, and its `default` mode only reports `slog.Default()`. `sloglint context` reports a
missing `context.Context` *argument*; it cannot tell whether the context passed is the caller's. Ruff's `G` family
and most of `TRY` are **not enabled in Ruff's default rule set** — LOG015 and TRY002/TRY003 are, G001–G004, G101,
G201/202, TRY400 and TRY401 are not — so `ruff check` passing says nothing about them unless the project selected
them. Sonar S2139 detects log-and-rethrow at one site and cannot see a log in a helper called from the catch. `go
vet`'s slog pass detects mismatched key/value pairs, not whether the keys mean anything. No tool in any of the three
ecosystems detects T7, T20, T23, T24, T25 or T34 — the six rules that carry most of the skill's value.

## 10. Baseline audit

| # | Verdict | Note |
| --- | --- | --- |
| S1 | **Survives, rationale changed** | The four outcomes are right but the set is wrong twice: "span event" is leaving (conflict (e)) and Python has a fifth channel. Restate as: record, instrument, span, the caller's channel, nothing |
| S2 | **Settled, confirmed** | Stated as a fault line by SLF4J, the Python HOWTO, OTel's client design principles and Kubernetes. One line in the skill; not re-argued |
| S3 | **Needs restating** | No source measures which outcome is most common, so "the most common correct outcome" is unsupported as a frequency claim. What is supported is the *ordering*: recoverability is tested first (OTel's rule, SRE's converse). Restate as a precedence rule, not a frequency |
| S4 | **Contradicted in part** | JVM half confirmed verbatim. Python half confirmed mechanically but mis-motivated — the stdlib's own default is WARNING to stderr and calls it best, so `NullHandler` is an opt-out. Go half has no authoritative source and understates the problem: `slog.Default()` writes to stderr and no library-side call makes it silent. Metrics clause contradicted; see (d) |
| S5 | **Survives, rationale upgraded** | From style preference to defect class: 25% of the catastrophic failures in Yuan et al.'s sample were caused by ignoring explicit errors, and an error handler that only logs counts as ignoring. Needs the documented escape hatch (Kubernetes' V(4) info line) or it misfires at the last frame |
| S6 | **Survives, "the same rule everywhere" contradicted** | Three different failures: a missing parameter in Go (visible in the diff, lintable), an executor-only loss in Python (asyncio already propagates), and on the JVM both a loss *and* a stale-context failure that leads the reader to the wrong unit |
| S7 | **Survives, now sourced** | Python's level table and Kubernetes' Conditions both encode the distinction. Its acceptance test remains unenforceable from the diff; T25's proxy — the record says which state, and a counterpart record exists for the other outcome — is the closest checkable form |
| S8 | **Survives as a corollary** | Not a rule of its own: it follows from T14 where the code owns no unit of work. Yanacek's 20M-requests-per-second case shows silence is the wrong variable |
| S9 | **Survives, owner reassigned** | The question belongs to whoever defines the instrument, the destination to whoever registers it (conflict (f)). SRE ch. 6's removal rule is the converse and makes it checkable |
| S10 | **Survives, now named** | The accepted vocabulary is LS2 *undercover identifier* for the defect and W3C Trace Context for the cross-service mechanism; Yanacek states the per-thread care it needs |
| S11 | **Settled, JVM-local** | Reference-file entry only; Go's `fmt` and Python's `,`/`_` are not locale-aware |
| S12 | **Survives, now derived** | LogEnhancer supplies the mechanism — 108 causally related branches per log point, resolvable by 16.0 values — and T23 is the review-time form of it |

**What the seed misses entirely**, in descending order of cost:

1. **Nothing about the rate at which a rule is complied with.** The single most important finding of the pass is that
   a natural-language instruction file is the weakest enforcement channel measured (6.5% compliance). The seed has no
   position on this, and it changes the skill's design.
2. **No pairing rule and no denominator rule.** Prometheus's log/counter pairing and the attempts denominator are
   absent from the seed, and the second is the difference between a readable failure metric and an unreadable one.
3. **No cost model.** The seed never prices a signal. Log2 measured 99th-percentile latency rising 16.3% and
   throughput falling 1.48% under intensive logging, and about 80% of 84 surveyed Microsoft engineers had hit
   non-negligible overhead. T29 and T31 need that number behind them.
4. **No per-unit bound and no unit-of-work concept at all.** S8 gropes at it through silence; Yanacek names it.
5. **Nothing about what an *existing* signal owes on removal.** SRE's removal rule is the only stated lifecycle rule.
6. **Nothing about the guard.** LS8 and the Go argument-evaluation rule are absent.
7. **Nothing about spans.** Three of the four outcomes in S1 get rules; the span gets none.

## 11. Evidence map

| Figure or quote | Sample | Source read | Status |
| --- | --- | --- | --- |
| 4,550 agentic PRs, 3,276 human PRs, 81 repositories | as stated | Ouatiti et al. 2026, PDF read | confirmed |
| Logging instructions in 4.7% of PRs | 61 of 1,308 PRs where a channel was observable | same | confirmed; **Pass 1 omitted the denominator** |
| Agents fail to comply 67% of the time | 61 instructions total (15 issue-level, 46 repository-level) | same | confirmed; **correction:** Pass 1 called this "about two-thirds even when the level or the framework was specified"; the specified-instruction figure is 27.3% compliance on **11** strong issue-level instructions, and repository-file compliance is 6.5% (3 of 46) |
| WARN overused in 29.9% of repositories | 77 paired repositories; humans overuse in 22.1%; WARN similarity 48.1% | same | confirmed |
| Under-logging in loops and conditionals | humans log more in 32.5% of repos (loops) and 28.6% (conditionals); agents more in 26.0% and 24.7% | same | confirmed, but **weaker than Pass 1 implied** — it is a repository-level majority, not a per-site deficit |
| Humans perform 72.5% of post-generation log repairs | log-statement level, agentic PRs; 99.5% for human PRs | same | confirmed |
| Languages covered | Python, Java, JS/TS | same | **correction:** Pass 1 did not state the scope; **Go is not covered** |
| 63,965 snapshot instances, 744 revision cases, 6 languages, 7 models | as stated | Zhong et al. 2026, PDF read | confirmed |
| Mean pairwise Spearman 0.912 | repository-snapshot data only | same | confirmed; **correction:** on revision-history data — the maintenance setting closest to an author writing a line for a change — it falls to **0.195**, 95% interval [−0.026, 0.400]. Pass 1's "model ordering largely preserved" holds only for the snapshot half |
| Loop and nested-callable sites hardest in every language | CCS 0.230 for loop | same | confirmed |
| 25% of catastrophic failures caused by ignoring explicit errors; "an error handler that only logs the error is also considered as ignoring the error" | 48 catastrophic failures out of 198 sampled, 5 systems | Yuan et al. OSDI 2014, PDF read | confirmed; **base is 48, not 198** |
| 76% of failures print explicit failure-related error messages | 198 failures | same | confirmed |
| 108 causally related branches per log point, resolvable by 16.0 values | 8 applications, 5 of them servers | LogEnhancer TOCS, PDF read | confirmed |
| Nine log smells, 51 articles, 16 tools | open coding over 51 included papers | Saarimäki et al., PDF read (v2, Mar 2026) | confirmed |
| 99th-percentile latency +16.3%, throughput −1.48%; ~80% of survey participants | Microsoft search engine; 84 respondents, 81 self-rated expert/knowledgeable | Log2, USENIX ATC 2015, PDF read | confirmed |
| LCAnalyzer recall 95%, precision 60%; 352 change pairs; six anti-patterns | ActiveMQ, Hadoop, Maven | Chen and Jiang ICSE 2017, PDF read | confirmed |
| One log line per 30 LOC; logging churn 1.8×; 26% of log improvements are level changes; 36% of messages modified as after-thoughts | 4 systems, 14,771 static log points | Yuan et al. ICSE 2012, PDF read | confirmed; **scope:** all four systems are C/C++ (Apache httpd, OpenSSH, PostgreSQL, Squid) |
| AL-Bench: best tool fails to compile 20.1% of the time | 21,804 instances; range across tools 20.1%–83.6% | AL-Bench, PDF read | confirmed; **addition:** the best runtime log similarity is 21.32% |
| Level-prediction AUC 0.75–0.81 | Li et al., cited by the drift paper | drift paper read (preprint) | confirmed as a **secondary** citation; primary not read |
| Level conventions drift within one project | Hadoop, Spring, OpenStack | drift paper preprint read | **correction:** Pass 1 reported "OpenStack, 28 components … components of one project move verbosity in opposite directions". The paper studies **three systems** and the OpenStack claim is about the same project **over its history**, not across components. The conclusion the skill relies on — that a generic ladder cannot be checked against a particular commit — survives; the sample and the mechanism as Pass 1 stated them do not |
| Cardinality: below 10, investigate above 100 | — | Prometheus **instrumentation** page read | confirmed; **correction:** Pass 1 attributed it to the *naming* page, which carries only the qualitative CAUTION |
| "for every line of logging code you should also have a counter"; libraries instrument with no configuration; failures need an attempts denominator | — | same page | confirmed, verbatim |
| "Embedded components … really should not do so"; provider at test scope; no-op since 1.6 | — | SLF4J FAQ read | confirmed, verbatim |
| Python: WARNING+ to stderr "regarded as the best default behaviour"; the log/warn/raise table; no root logger; no handler but `NullHandler` | — | Logging HOWTO (3.14) read | confirmed, verbatim |
| "Shared libraries … should _not_ log errors themselves but just return `error`"; the V(0)–V(5) ladder; the V(4) escape hatch | — | Kubernetes logging conventions read | confirmed, verbatim |
| "logging that error *and not returning it*"; the rebuttal of "libraries should not log" | — | go-logr README read | confirmed, verbatim |
| "Nobody needs a warning log level"; "The act of logging an error handles the error" | — | Cheney 2015 read | confirmed, verbatim |
| DynamoDB "serving at peak over 20 million requests per second … logs every request"; one entry per unit of work; separate timer for successful responses; counter per error reason; queue depth; rate-limit error spam; trace IDs in method signatures | — | AWS Builders' Library PDF read | confirmed, verbatim |
| OTel: "when in doubt, don't instrument" and its three conditions; API-only with a no-op minimal implementation; high-cardinality metric attributes Opt-In only | — | libraries page, client design principles, attribute-requirement-level.md read | confirmed |
| "New code should write events as logs that are correlated with the current span" | — | OTel span-events deprecation post read | confirmed; no dates or versions in the post |
| Micrometer: "Increments are NOOP'd until there is a registry in the composite" | — | Micrometer registry page read | confirmed |
| HikariCP `MetricsTrackerFactory` is a one-method interface the host implements | — | source file read | confirmed |
| MDC not inherited by `Executors`-managed threads; a child thread does not inherit; `put` balanced by `remove` | — | Logback MDC manual read | confirmed |
| Go: "The arguments to a log call are always evaluated, even if the log event is discarded"; the default handler passes records to the `log` package | — | `pkg.go.dev/log/slog` read | confirmed |
| sloglint's 13 options; Ruff's LOG/G/TRY ids and which are on by default | — | sloglint README and Ruff rule index read | confirmed |
| Four golden signals; "Signals that are collected, but not exposed in any prebaked dashboard nor used by any alert, are candidates for removal" | — | SRE book ch. 6 read | confirmed |

**Limits carried forward.** *(1)* The 2024 EMSE literature review (`10.1007/s10664-024-10452-w`) is still
unreachable — Springer serves a bot challenge to every non-browser client. No figure from it appears in this report.
What the pass therefore could not establish: whether the literature has a *measured* frequency for the emit-nothing
outcome (S3), which would have converted T7 from a precedence rule into a calibrated one. *(2)* Both books remain
unread: O'Reilly returned HTTP 403 for the *Release It!* transparency chapter and the *Observability Engineering*
chapter is behind the same wall. Neither is cited as a rule source, and the two claims Pass 1 attributed to them
("transparency arises from deliberate design"; high-cardinality context belongs in events) are **dropped**, not
carried. What that costs: the skill has no sourced statement of *why* monitoring decisions belong outside the
application beyond the logging maintainers' own version, which is adequate for T2 but not for an architectural
framing. *(3)* The concept-drift paper was read as the authors' preprint, not the published EMSE version; the
figures quoted are the preprint's. *(4)* `rules.sonarsource.com` did not resolve from this environment, so S2139 is
cited as Pass 1 recorded it and its exact current wording is unverified.

## 12. What the skill-writing session should be told

**State in the body.** The mode test (T1) and the one rule that survived every crossing: a library does not decide
where its output goes, and does not both log an error and return it. Rule SC in full, as the skill's spine, with its
five branches and the emit-nothing precedence first. The record's contents (T22–T26), because those are the rules
that no tool in any ecosystem detects and the ones both recorded failures broke. The rate rule as one record per unit
of work, with the state change as the unit where there is none (T13–T15). The instrument rules that carry numbers
(T17, T18, T20, T32, T33). The severity position: no ladder, the axis is who must act, the repository's convention is
the authority, and the check is agreement with the calls around it.

**Put in a reference file, and which.** Per-ecosystem mechanics for T2, T4, T5, T27, T31, T35, T36 — one file each
for the JVM, Go and Python, each carrying the ecosystem's default behaviour when the host configures nothing, the
observable form of each defect in that ecosystem's syntax, the lint ids, and what a clean verdict does not
establish. S11/T28 goes in the JVM file only. T6's hook pattern goes in the JVM file. T8's `warnings.warn` goes in
the Python file, but the *distinction* it encodes belongs in the body. The klog V-ladder goes in the Go file as an
example of a project-owned ladder, explicitly not as a recommendation.

**Keep in the research directory.** Every figure in §11 with its sample; the two unreachable sources and what they
cost; the six worked cases in §5 as the skill's regression fixture — if a future edit changes what the skill emits
for any of the six, that is the signal to re-run the pass. The evidence that instruction files are complied with at
6.5% belongs here too, as the justification for why the skill is written the way it is.

**Leave as human judgment.** One item, as Pass 1 named it: whether, holding only the emitted text, a competent
engineer would wait or intervene. No source offers an oracle, T25 is a proxy and not the thing itself, and the skill
should say so in the body rather than imply that its checks answer it.

**One design instruction that follows from the measurement.** Because the channel this skill occupies is the one
measured at 6.5% compliance, every rule in the body must carry its detection in the same sentence as its
prescription, and the skill should name the lint id wherever one exists — not as a convenience, but because the
enforcement that works is the deterministic kind, and the skill's job is to route the reviewer to it.
