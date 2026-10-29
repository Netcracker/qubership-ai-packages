# Pass 1b — per-ecosystem mechanics and conventions, discovery result

## Executive summary

**Is there an authoritative statement of the library contract?** Yes in all three ecosystems, and in all three it comes
from the ecosystem's own maintainers rather than from a third party — but the three statements are not the same
statement.

- **JVM.** SLF4J's FAQ is explicit and quotable: "Embedded components such as libraries not only do not need to
  configure the underlying logging framework, they really should not do so," and the manual adds that a library
  "should not declare a dependency on any SLF4J binding/provider but only depend on slf4j-api," because a transitive
  binding "is imposed on the end-user negating the purpose of SLF4J." The JDK restates the same shape in JEP 264
  (`System.Logger` as a façade in `java.base`), and Log4j 2 restates it as `log4j-api` versus `log4j-core`.
- **Python.** The stdlib Logging HOWTO is normative in tone and covers the same ground: use `getLogger(__name__)`;
  "It is strongly advised that you do not log to the root logger in your library"; "It is strongly advised that you do
  not add any handlers other than NullHandler to your library's loggers ... the configuration of handlers is the
  prerogative of the application developer."
- **Go.** There is **no** standard-library statement. `log/slog`'s docs and the accepted proposal describe mechanics
  and say nothing about libraries. The Go position exists, but it lives in project conventions and in a linter:
  Kubernetes' logging conventions, the contextual-logging work behind KEP-1602, `go-logr`, Google's Go style guide,
  and `sloglint`'s `no-global` option. **Concluding that Go's authoritative sources are silent on the library contract
  is itself a finding.**

**Baseline mechanics — confirmed, corrected, unreachable.**

- **S4, JVM half: confirmed** verbatim (facade only, and do not configure).
- **S4, Python half: confirmed but mis-motivated.** `getLogger(__name__)`, no `basicConfig`, no root logger, and
  `NullHandler` are all in the HOWTO. But the HOWTO says that with no application configuration, `WARNING` and above
  go to `sys.stderr` and "This is regarded as the best default behaviour"; `NullHandler` is offered only "If for some
  reason you *don't* want these messages printed." The seed's framing — attach `NullHandler` so a silent host stays
  silent — inverts the stdlib's own default.
- **S4, Go half: corrected.** "Accept a logger, install no global handler" matches practice, but there is no
  authoritative source for it, and the second clause understates the problem: a Go library that calls `slog.Default()`
  is not quiet on an unconfigured host. `pkg.go.dev/log/slog` states the default handler "formats the log record's
  message, time, level, and attributes as a string and passes it to the log package" — i.e. stderr at `Info` and
  above. Go has no silent default the way SLF4J does; `slog.DiscardHandler` exists (Go 1.24) but only the host can
  choose it.
- **S4, metrics clause: contradicted.** Prometheus's own instrumentation practices say "Libraries should provide
  instrumentation with no additional configuration required by users," and the client-library specification requires a
  default registry "and standard metrics must by default implicitly register into it with no special work required by
  the user." This is the opposite of "a library does not export metrics itself."
- **S5: confirmed in Go and Python, unsourced on the JVM.** Kubernetes: "Shared libraries, such as client-go, should
  not log errors themselves but just return error." `go-logr`: use error logs when "logging that error *and not
  returning it*." Google's Go style guide: return rather than log. Python's HOWTO table routes "Report an error
  regarding a particular runtime event" to "Raise an exception" and reserves `logger.error` for "suppression of an
  error without raising an exception." On the JVM the rule exists only as a static-analysis rule (Sonar S2139), not
  as a statement by a logging maintainer.
- **S6: confirmed, but "the rule is the same everywhere" is too strong** — see below.
- **S11: JVM-local, not language-neutral.** The JVM trap is documented: `java.util.logging.Formatter.formatMessage`
  says "if the string contains `{<digit>` where `<digit>` is in [0-9], `java.text.MessageFormat` is used to format the
  string," which is where the locale grouping enters. Go's `fmt` is not locale-aware; localization is opt-in through
  `golang.org/x/text/message`. Python's logging uses `%`-formatting, and in the format mini-language `,` and `_` are
  explicitly *not* locale-aware — only `'n'` is ("it uses the current locale setting to insert the appropriate digit
  group separators"), and `'n'` is not reachable by accident through a logging call. **Neither Go nor Python has an
  equivalent trap.**
- **S2: holds, in all three, as an explicitly stated fault line** — SLF4J FAQ, Python HOWTO, OpenTelemetry's client
  design principles ("The developers of the final application normally decide how to configure OpenTelemetry SDK"),
  Kubernetes' shared-library rule. It is not a JVM-shaped idea. But the *test* differs, and the metrics answer
  inverts it.

**Where the ecosystems differ in kind — the pass's highest-value answer.**

1. **What silence costs.** On the JVM, a library that logs into a host with no provider produces nothing: SLF4J
   "will default to a no-operation implementation," emitting one warning and discarding all requests. In Python, a
   library that logs produces `WARNING`+ on the host's stderr unless the library itself opted out with `NullHandler`.
   In Go, a library that reaches for `slog.Default()` writes to the host's stderr, and nothing the library can do
   makes that silent. **The same code has three different default blast radii.** A language-neutral rule of the form
   "a library must leave a silent host silent" is only satisfiable on the JVM.
2. **How the logger is obtained.** JVM and Python route by *name* through an ambient registry, and the host
   configures by name — so the library's sin is *configuring*. Go routes by *value*, and there is no useful ambient
   registry — so the library's sin is *acquiring* a logger it was not handed. Kubernetes states the Go form
   directly: libraries "are passed a logger instance by their caller and use that for logging instead of accessing a
   global logger." A reviewer therefore looks for different evidence in the diff: a `basicConfig`/`addHandler`/binding
   dependency on the JVM and in Python, a `slog.Default()` or package-level `var logger` in Go.
3. **The fourth outcome Python has and the others do not.** Python's HOWTO routes an avoidable, caller-fixable
   condition to `warnings.warn` "in library code if the issue is avoidable and the client application should be
   modified," and reserves `logger.warning` for when "there is nothing the client application can do about the
   situation." Neither Go nor the JVM has a first-class channel for this. The seed's S1 four-outcome set (log,
   metric, span, nothing) is missing it.
4. **The context failure is not the same failure.** Go: nothing is ambient, so a goroutine started without `ctx`
   silently loses cancellation and trace context — but the omission is *visible in the diff* as a missing parameter,
   and `contextcheck` and `sloglint`'s `context` option can see it. Python: `asyncio` tasks *do* inherit — "the Task
   copies the current context and later runs its coroutine in the copied context" — and `asyncio.to_thread`
   propagates explicitly, so only a hand-rolled `ThreadPoolExecutor.submit` loses it. JVM: the MDC is never inherited
   by `Executors`-managed threads ("A copy of the mapped diagnostic context can not always be inherited by worker
   threads from the initiating thread. This is the case when `java.util.concurrent.Executors` is used"), *and* it has
   a failure mode the other two lack — a pooled thread that kept a previous request's keys, which is why Logback
   insists "a `put()` operation should be balanced by the corresponding `remove()`". A stale MDC is worse than an
   empty one: it leads the reader to the wrong request.
5. **Metrics from a library have three different answers.** Prometheus (Go and Python): register on the default
   registry, no configuration. OpenTelemetry: API only, no-op without an SDK. Micrometer: `Metrics.globalRegistry` is
   a composite that does nothing until the host binds a registry, and the JVM idiom additionally offers the
   host-implements-the-interface shape (`MeterBinder`; HikariCP's `MetricsTrackerFactory`). One language-neutral rule
   is not available here.

**Which roles need a reference file.** Logging API (all three, and they diverge most), context propagation (all
three), metrics client (all three, because the guidance conflicts), mechanical checks (all three). **Which do not:**
tracing semantics and span/error recording (one OpenTelemetry file plus a page of per-language spellings), metric and
attribute naming (Prometheus naming and OTel semconv are already language-neutral), and message wording (owned by
`english-developer-style`).

**Under-served questions.** Q9 (levels defined concretely): only Kubernetes/klog and `go-logr` define levels by
meaning; Python's table and the JVM's are generic, and CockroachDB and Elasticsearch merely list severities. Q12
(what a library does instead of emitting): thin outside the JVM. Q11 for Python: maintainer-named anti-patterns are
scattered across bug reports rather than stated in a style guide.

**Recorded Go and Python defects (fills seed part 3's F3 gap).** Python: CPython gh-50970 / bpo-6721 and bpo-36533 —
`logging` handler locks held across `os.fork()` deadlock the child; fixed by reinitializing the locks via
`os.register_at_fork`, with a regression test. Python: boto3 #3403 — boto3, botocore and s3transfer each define their
*own* `NullHandler` class, so a host cannot detect them with `isinstance(h, logging.NullHandler)`. Go:
`grpclog.SetLoggerV2` is documented as not mutex-protected, must be called before any gRPC function, and panics if
handed a component logger — a global-logger design defect stated in the package's own docs. Go: golang/go#57396 —
`slog.SetDefault` has side effects on `log.Print` level handling.

## Candidate inventory

| # | Name | URL | Ecosystem | Role | Author/org | Questions | Evidence | Maintenance / version | Why worth considering |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SLF4J Manual | https://www.slf4j.org/manual.html | JVM | logging API | QOS.ch | 1, 3, 7 | asserted (maintainer) | current, 2.x | The facade argument in the maintainer's own words, plus MDC delegation and parameterized messages |
| 2 | SLF4J FAQ | https://www.slf4j.org/faq.html | JVM | logging API | QOS.ch | 1, 7 | asserted; 30× figure is vendor-measured | current | "libraries ... really should not [configure]"; no-op fallback since 1.6; why `isDebugEnabled` is usually unneeded |
| 3 | Python Logging HOWTO | https://docs.python.org/3/howto/logging.html | Python | logging API | CPython | 1, 4, 7, 9 | asserted (stdlib) | 3.14 | "Configuring Logging for a Library" verbatim; the log-vs-warn-vs-raise table; lazy `%` formatting |
| 4 | `log/slog` package docs | https://pkg.go.dev/log/slog | Go | logging API | Go team | 1, 3, 7, 8 | asserted | Go 1.21+; `DiscardHandler` 1.24 | Default handler writes to the `log` package; `LogAttrs`; args always evaluated; group keys |
| 5 | Proposal 56345, structured logging | https://go.googlesource.com/proposal/+/master/design/56345-structured-logging.md | Go | logging API | Go team | 1, 3, 7, 10 | asserted | accepted 2023-03 | Rationale for `ctx` in the API, `Enabled` before argument processing, and the vet check |
| 6 | Go blog "Structured Logging with slog" + slog handler guide | https://go.dev/blog/slog ; https://github.com/golang/example/blob/master/slog-handler-guide/README.md | Go | logging API | Go team | 3, 7 | asserted | Go 1.21+ | `Enabled` as the early drop before arguments are processed; `WithAttrs` pre-formatting; `LogValuer` |
| 7 | Go Wiki Code Review Comments + `context` package docs | https://go.dev/wiki/CodeReviewComments ; https://pkg.go.dev/context | Go | context propagation | Go team | 3 | asserted | current | "Don't add a Context member to a struct type"; ctx first and named `ctx`; derived-context cancellation |
| 8 | Go blog, Go 1.13 errors | https://go.dev/blog/go1.13-errors | Go | logging API | Go team | 4 | asserted | Go 1.13+ | `%w` wrapping as the alternative to logging; explicitly says nothing about log-and-return |
| 9 | Google Go Style Guide, best practices | https://google.github.io/styleguide/go/best-practices | Go | project convention | Google | 4, 7, 9 | asserted | current | "better not to log it yourself but rather let the caller handle it"; `if log.V(2)` guard against expensive args |
| 10 | `go-logr` README | https://github.com/go-logr/logr/blob/master/README.md | Go | logging API | go-logr | 1, 4, 9 | asserted | current | Error logs only when *not* returning; V-levels with V(0) as "always want to see this" |
| 11 | Kubernetes logging conventions | https://github.com/kubernetes/community/blob/main/contributors/devel/sig-instrumentation/logging.md | Go | project convention | Kubernetes SIG Instrumentation | 1, 4, 8, 9, 11 | asserted | current | V(0)–V(5) defined by meaning; "Shared libraries ... should not log errors themselves but just return error" |
| 12 | KEP-1602 + contextual-logging post | https://github.com/kubernetes/enhancements/blob/master/keps/sig-instrumentation/1602-structured-logging/README.md | Go | project convention | Kubernetes | 1, 3, 8 | asserted | 1.24+ | "libraries are passed a logger instance by their caller"; the Go answer to the ambient-logger question |
| 13 | `contextvars` docs | https://docs.python.org/3/library/contextvars.html | Python | context propagation | CPython | 3 | asserted | 3.7+ | Per-thread context stacks; `copy_context`/`Context.run` as the manual bridge |
| 14 | `asyncio` tasks docs | https://docs.python.org/3/library/asyncio-task.html | Python | context propagation | CPython | 3 | asserted | 3.11+ for `context=` | Tasks copy the current context; `to_thread` propagates — so only raw executors lose it |
| 15 | Logback MDC manual | https://logback.qos.ch/manual/mdc.html | JVM | context propagation | QOS.ch | 3 | asserted | current | The `Executors` caveat and the `getCopyOfContextMap`/`setContextMap` pattern; put/remove balance |
| 16 | OTel Client Design Principles | https://opentelemetry.io/docs/specs/otel/library-guidelines/ | all | tracing SDK | OpenTelemetry | 1, 5, 6 | asserted | current spec | API/SDK split; minimal no-op in the API; negligible overhead when no SDK |
| 17 | OTel "Libraries" concept page | https://opentelemetry.io/docs/concepts/instrumentation/libraries/ | all | tracing SDK | OpenTelemetry | 1, 6, 12 | asserted | current | What to instrument, record-exception-plus-set-status, expensive tracing behind an off-by-default option |
| 18 | OTel Logs (bridge) API + Metrics API specs | https://opentelemetry.io/docs/specs/otel/logs/api/ ; https://opentelemetry.io/docs/specs/otel/metrics/api/ | all | logging API, metrics client | OpenTelemetry | 1, 5 | asserted | Logs API Stable | The logs API is for appender authors, not for application logging — kills a likely agent mistake; Meter is obtained by instrumentation-scope name |
| 19 | OTel Go `trace` package | https://pkg.go.dev/go.opentelemetry.io/otel/trace | Go | tracing SDK | OpenTelemetry | 6 | asserted | current | "Instrumentation should be designed to accept a TracerProvider"; every span MUST be ended |
| 20 | OTel semconv naming | https://opentelemetry.io/docs/specs/semconv/general/naming/ | all | project convention | OpenTelemetry | 8 | asserted | 1.44 | Attribute key grammar, namespacing, and the Development/RC/Stable key-stability ladder |
| 21 | Prometheus instrumentation practices | https://prometheus.io/docs/practices/instrumentation/ | Go, Python | metrics client | Prometheus | 5, 12 | asserted | current | "Libraries should provide instrumentation with no additional configuration" and "for every line of logging code you should also have a counter" |
| 22 | Prometheus metric and label naming | https://prometheus.io/docs/practices/naming/ | Go, Python | metrics client | Prometheus | 5, 8 | asserted | current | Base units, `_total`, and the cardinality CAUTION in the project's own words |
| 23 | `prometheus/client_golang` #715 | https://github.com/prometheus/client_golang/issues/715 | Go | metrics client | Prometheus | 5, 11 | asserted (maintainer thread) | open | Maintainers on the default registry and `MustRegister`: "not a desirable state" |
| 24 | Micrometer registry + naming + high-cardinality detector | https://docs.micrometer.io/micrometer/reference/concepts/high-cardinality-tags-detector.html | JVM | metrics client | Micrometer | 5, 8, 10 | asserted | 1.17.x | `globalRegistry` is a composite; `withHighCardinalityTagsDetector()` is a runtime check, not a lint |
| 25 | `sloglint` | https://github.com/go-simpler/sloglint | Go | mechanical check | go-simpler | 10 | tool | current, in golangci-lint | `no-global`, `context`, `no-raw-keys`, `forbidden-keys`, `static-msg` — the closest thing to a codified Go library contract |
| 26 | `x/tools` slog vet analyzer + `contextcheck` | https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/slog | Go | mechanical check | Go team / community | 10 | tool | ships with `go vet` | Catches mismatched key/value pairs; `contextcheck` catches a non-inherited context |
| 27 | Ruff LOG/G/TRY rules + flake8-logging-format | https://docs.astral.sh/ruff/rules/root-logger-call/ | Python | mechanical check | Astral / globality | 10, 4 | tool | current | LOG002/LOG015 (root logger, `getLogger` argument), G004 (f-string), TRY400/TRY401 (error vs exception, redundant exception text) |
| 28 | Sonar S2139 + findbugs-slf4j / errorprone-slf4j | https://rules.sonarsource.com/java/rspec-2139/ | JVM | mechanical check | SonarSource / KengoTODA | 10, 4 | tool | current | The only mechanical form of "log or rethrow, not both", plus `SLF4J_FORMAT_SHOULD_BE_CONST` |
| 29 | `java.util.logging.Formatter` javadoc | https://docs.oracle.com/en/java/javase/21/docs/api/java.logging/java/util/logging/Formatter.html | JVM | logging API | Oracle/OpenJDK | 7 | documented + measured in-session | JDK 8+ | The primary source behind S11: `MessageFormat` engages on `{<digit>` |
| 30 | HikariCP `MetricsTrackerFactory` + Micrometer `MeterBinder` | https://javadoc.io/static/com.zaxxer/HikariCP/3.2.0/com/zaxxer/hikari/metrics/MetricsTrackerFactory.html | JVM | metrics client | HikariCP / Micrometer | 12 | asserted | current | The "library defines the interface, host supplies the implementation" pattern with a widely used example |

## Promising shortlist for Pass 2

1. **SLF4J FAQ + Manual (rows 1–2).** The only source in any ecosystem that states the library contract, its
   rationale, *and* the failure it prevents in one place, from the maintainer. Yields two rules with clean detection:
   a library's build file must not name a provider (detectable from the diff), and a library must not call a
   configuration API. Both are local to the JVM in mechanics but the *rationale* generalizes. Converts to a compact
   rule easily.
2. **Python Logging HOWTO, library section + the log/warn/raise table (row 3).** Does double duty: it settles S4's
   Python half and it supplies the answer to Q4 that Python's idiom actually has — raise, don't log. The `warnings.warn`
   row is the finding: it is a channel the skill's outcome set does not model. Rule is local to Python; the
   underlying distinction ("can the caller fix this?") is language-neutral and may deserve promotion into the body.
3. **Kubernetes logging conventions (row 11).** The single richest project convention found: levels defined by
   meaning rather than adjective, a structured-logging mandate, and the shared-library rule stated as a rule. Yields
   a language-neutral rule (a library returns the error rather than logging it) and a Go-local one (klog/logr
   V-levels). Its level table is the concrete answer Q9 asks for and the only one found outside `go-logr`.
4. **`sloglint` (row 25).** The only tool that mechanizes the Go library contract. `no-global` detects
   `slog.Default()`/package-level loggers; `context` detects the non-context call; `forbidden-keys` detects keys the
   handler will overwrite. Pass 2 should record for each option what a clean verdict does *not* establish — notably
   that `no-global` does not see a logger injected once at init and then treated as a global.
5. **OpenTelemetry Client Design Principles + Libraries page (rows 16–17).** The only genuinely cross-language
   statement of the contract, and it carries the property the JVM and Python contracts lack: a documented, cheap
   no-op when the host has configured nothing. Yields a language-neutral rule (a library depends on the API artifact,
   never the SDK) that can be stated once in the body with a one-line per-ecosystem artifact name in the reference.
6. **Prometheus instrumentation practices (row 21).** The highest-value contradiction in the pass. Its
   "libraries should instrument with no configuration" and "for every line of logging code you should also have a
   counter" both cut against seed positions (S4's metrics clause, S3's "emit nothing"). Pass 2 must decide whether
   the skill adopts, bounds, or rejects it — it cannot ignore it, because it is the metric client's own guidance for
   two of the three ecosystems.
7. **Logback MDC manual + `contextvars`/`asyncio` docs (rows 13–15).** Together they let S6 be stated correctly
   rather than uniformly: the JVM has the stale-context failure, Python has the executor-only failure with asyncio
   already handled, Go has the missing-parameter failure. Rule is language-neutral in intent, local in every
   detection and every repair — a textbook case for "state once, mechanize per reference file".
8. **`go-logr` README + Google Go style guide (rows 9–10).** Two independent Go sources that agree with S5 and give
   it a testable form ("log it only if you are not returning it"). Also the cleanest statement of why a V-level guard
   must wrap expensive argument computation. Compact, reviewable from a diff alone.
9. **Ruff's LOG/G/TRY rule families (row 27).** Python's mechanical layer, and unusually complete: root-logger use,
   `getLogger` argument, eager f-string formatting, `error` where `exception` belongs, and the exception object
   duplicated into the message. Each rule id is a ready-made detection clause. Rules are Python-local; several map
   one-to-one onto JVM rules from row 31, which makes them good evidence that a rule is real rather than idiomatic.
10. **`java.util.logging.Formatter` javadoc (row 29).** Confirms S11 from the primary source and, by contrast with
    the Go and Python formatting docs, proves S11 must be demoted from a language-neutral rule to a JVM reference-file
    entry. Small but decisive for the skill's structure.
11. **HikariCP `MetricsTrackerFactory` + Micrometer `MeterBinder` (row 30).** The best available answer to Q12: a
    widely deployed library that emits no metrics itself and instead publishes an interface the host implements, with
    adapters shipped as separate artifacts. Converts into a rule about what a library offers when it must not export.
12. **Prometheus naming + OTel semconv naming (rows 22, 20).** Between them they answer Q8 language-neutrally: key
    grammar, namespacing, units, and an explicit stability ladder for a key's name over time. One shared reference
    section rather than three.

## Obvious rejects

- **Blog "ultimate guide"/"complete guide" posts on slog (SigNoz, Better Stack, Dash0).** Derivative of the package
  docs; no rationale the primary source lacks.
- **The Hitchhiker's Guide to Python logging page.** Restates the HOWTO without attribution or added rationale.
- **Baeldung's Micrometer and SLF4J pages.** Tutorial restatement; the primary docs say the same in fewer words.
- **Vendor observability blogs on cardinality (Last9, SigNoz, Sawmills, OneUptime).** Marketing-adjacent; the
  Prometheus naming page carries the same rule as a first-party statement.
- **The anonymous cardinality "postmortem" recounted in a DEV.to article.** No incident report behind it; not
  citable as a recorded failure.
- **StackOverflow and forum threads on `DEBUG:urllib3.connectionpool`.** Symptom reports with no maintainer position.
- **"How to enable debug logging for requests" recipes.** Setup instructions, no rationale — explicitly excluded.
- **Wording-only sources.** Kubernetes' message-style rules (capital letter, no trailing period, past tense) are
  wording and belong to `english-developer-style` §7; keep the level table, drop the style table.
- **Migration guides between logging libraries** (log4j→slf4j, klog→logr mechanics): out of scope by the brief.
- **Micrometer "best practices" pages published by downstream projects.** Second-hand; use the Micrometer docs.

## Gaps and questions for Pass 2

**Which rules have a mechanical check and which do not.**

- *Go:* well covered. Global logger (`sloglint no-global`), missing context (`sloglint context`, `contextcheck`),
  malformed key/value pairs (`go vet` slog pass), dynamic message (`static-msg`), handler-reserved keys
  (`forbidden-keys`). **No check** for: a library that accepts a logger and then ignores it; a counter registered on
  `prometheus.DefaultRegisterer` from library code; a log line that does not say which limit bound a value.
- *Python:* partially covered. Root-logger calls (LOG015), `getLogger` argument (LOG002), eager f-strings (G004,
  W1203), `error` where `exception` belongs (TRY400), exception text duplicated (TRY401), `extra` clashing with
  `LogRecord` fields (G101). **No check** for: `basicConfig` called at import time in a package, a missing
  `NullHandler`, or a `ThreadPoolExecutor.submit` that dropped `copy_context`.
- *JVM:* thinnest. Log-or-rethrow (Sonar S2139), non-constant format (`SLF4J_FORMAT_SHOULD_BE_CONST`). A provider
  dependency in a library's build is checkable but only by a rule the project writes itself (ArchUnit, Maven enforcer
  banned-dependencies, Gradle `dependencies` constraints) — **Pass 2 should find whether any widely used project
  publishes such a rule**, because the claim "this is mechanically checkable on the JVM" currently rests on nothing I
  fetched. **No check** for: MDC not restored across a thread pool, or an unbalanced `MDC.put` without `remove`.

**Baseline part 2 claims I could not confirm from a primary source.**

- S3 ("the most common correct outcome is emit nothing") — no source found; Prometheus's "for every line of logging
  code you should also have a counter" pushes the other way, and nothing measures which is right.
- S7, S8, S9, S10, S12 — nothing found in this pass. These are Pass 1a's ground; I did not spend budget there, but I
  note that no per-ecosystem source I read states any of them either.
- The Go half of S4 — no authoritative Go statement exists at all; only conventions and a linter option.
- Micrometer's position for library authors — the registry docs do **not** say whether a library may use
  `Metrics.globalRegistry`. I could not confirm a Micrometer maintainer statement; treat "pass the registry in" as
  community practice, not documented guidance.
- Django's logging docs contain no guidance for third-party app authors on logger policy — the page I fetched has
  none. Reported as unreachable rather than confirmed from memory.

**Where two ecosystems' stated positions conflict, so one language-neutral rule is impossible.**

1. *Default output when the host configures nothing.* JVM: silent no-op. Python: `WARNING`+ on stderr, and the docs
   call that the best default. Go: everything at `Info`+ on stderr, with no library-side remedy.
2. *May a library export metrics?* Prometheus: yes, with no configuration. OpenTelemetry: only through the API, with
   a no-op default. JVM idiom: often neither — publish a hook.
3. *Who owns the level.* Kubernetes/klog and `go-logr` give the operator a numeric verbosity dial with project-defined
   meanings; SLF4J and Python give five named severities whose meanings the stdlib defines generically. A rule of the
   form "choose the level that means X" does not survive the crossing.
4. *Is the ambient context legitimate?* The JVM's MDC and Python's `contextvars` are the sanctioned mechanism; Go
   treats ambient state as the defect and the explicit parameter as the fix.

**What a reference file must carry that the body cannot.** The observable form of each defect in that ecosystem's
syntax (`basicConfig(` in a package `__init__`, `slog.Default()` in a non-`main` package, a `runtimeOnly` provider in
a library's build file); the exact default behaviour of an unconfigured host; the formatter's unrequested behaviour
(`MessageFormat` on `{0`, `%`-style laziness, always-evaluated slog arguments); the level-guard idiom and when it is
still needed; the context-carrying type and what loses it; the registry or provider the library may touch; the
linters, their rule ids, and what a clean verdict does not establish. The body can carry only the decision — which
signal, addressed to which reader, carrying which identifier — and the one rule that did survive every crossing: a
library does not configure the host's output, and does not both log an error and return it.
