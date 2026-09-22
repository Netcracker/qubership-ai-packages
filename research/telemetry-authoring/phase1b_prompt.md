# Pass 1b — discovery brief, per-ecosystem mechanics and conventions

## Research title

Find the primary sources that fix **what a library and a service may emit in Go, Python and on the JVM** — the logging
API contract, the metric client contract, the tracing API, and context propagation — for a skill that writes and
reviews instrumentation, and establish where the three ecosystems differ **in kind** rather than in API.

## Goal

The consumer of the resulting skill is a coding agent writing or reviewing instrumentation in one of three ecosystems,
at the moment a logger call, a counter, or a span enters a diff. The skill will state its binding rules once, in
language-neutral form, and carry the mechanics in reference files, one per role per ecosystem, in the shape
`references/<ecosystem>/<library>.md`. **This pass supplies what those reference files must contain, and — more
important — tells the skill writer which rules cannot be stated language-neutrally because an ecosystem genuinely
differs.**

Missing today, in the consumer's terms:

- what a **library** may do in each ecosystem: which dependency it may take, whether it may configure anything, what
  it must do so a silent host stays silent;
- how the host's context reaches the library's own concurrency, and what loses it;
- whether a library may export a metric at all, and through what;
- what each ecosystem's own maintainers say about logging inside library code, as opposed to what a blog post says;
- what the formatter or handler does to the message and its arguments that the author did not ask for.

This is Pass 1 only. The goal is discovery and classification, not final ranking. A companion brief (Pass 1a) covers
the cross-cutting question — which signal an event owes, what a line must carry, severity, rate, the empirical
literature. **Do not spend this pass's budget on those.**

## Important framing

The baseline at the end of this brief is a starting point, not the target. Sources that contradict it are preferred,
and a contradiction is a finding. The baseline's per-ecosystem mechanics were **asserted from memory by a model** and
are exactly what this pass exists to confirm or correct. Do not report agreement with them as support; check each
against the ecosystem's primary source and say confirmed, corrected, or unreachable.

Concluding that an ecosystem has no authoritative position on a question is an acceptable answer, and a useful one.

The consumer is an agent, so prefer a source that states a rule and its rationale over a snippet. Three properties
matter more than usual:

- **Detectability.** Can a reviewer tell from the diff alone that the rule was violated — an import of a logging
  implementation in a library's build file, a `basicConfig` call in a package, a goroutine started without the
  context, a global handler installed at import time? Sources that name the observable form of the defect are worth
  most.
- **Mechanical checkability.** Which of these has a linter, a vet check, an import-control rule, or a test: name the
  tool and what its verdict does and does not establish.
- **Resistance to a writer who optimizes for the check.** Name the shapes that satisfy the letter: taking the facade
  dependency and then configuring it anyway; accepting a logger parameter and ignoring it; passing a context and not
  using it; a counter registered on a global default registry from library code.

## Readers

Fixed for this pass. Report a row that is wrong or missing rather than replacing it.

| Reader | Situation | Holds |
| --- | --- | --- |
| R1 Library author | Adding or changing a logger call, or a counter, inside a library that ships to hosts it will never see | The diff, the library's conventions, no control over how the host configures output |
| R2 Service author | Has just written a branch that ends in a failure, a retry, a fallback, or a silently clamped value | The diff, the instruments the service already exports |
| R3 On-call engineer | An alert or a user report, no source access, deciding whether to wait or intervene | Logs, a dashboard, the deploy history, the literal text of one message |
| R4 Reviewer | Holds a diff in which a signal appeared, changed, or is conspicuously absent | The diff, the repository's conventions, no access to the author |

R1 and R4 are this pass's primary readers.

## Out of scope

Companion skills that own neighbouring ground; do not restate or re-derive:

- **`english-developer-style` §7** owns the wording of a message. Wording is settled.
- **`docs-page-authoring` §7** owns the documentation entry a user-visible message owes.
- **`deep-review`'s observability axis** owns the repository-wide review.

Subject matter that is not this skill's: vendor and backend products; log shipping, storage, retention, cost; dashboard
design; alerting rule syntax; benchmark shootouts between logging libraries; migration guides from one library to
another; anything whose content is a JSON-versus-text argument.

**Treat wording as settled. If a source's only contribution is wording, classify it as a reject and say so in one
line.**

## Questions the pass should answer

You do not have to answer these. You have to find the sources that can.

1. **The library contract, per ecosystem.** What does each ecosystem's authoritative source say a library must and must
   not do about logging configuration? Specifically: the JVM facade position (SLF4J's own manual on why a library
   depends on the API and not an implementation, and the failure it names); Python's standard-library guidance on
   `logging.getLogger(__name__)`, `NullHandler`, and why a library must not call `basicConfig` or touch the root
   logger; the Go position — what `log/slog` and its design documents say about a library taking a logger, using
   `slog.Default()`, or installing a handler.
2. **Where these differ in kind.** Is the difference between the three only mechanical, or does an ecosystem take a
   genuinely different stance — for example on whether a library should log at all, on whether it should return an
   error instead, or on who owns the level?
3. **Context propagation.** What is the mechanism, the failure mode, and the stated rule in each: Go's
   `context.Context` as an explicit first parameter and what a goroutine started without it loses; the JVM's ambient
   MDC and what a thread pool does to it; Python's `contextvars`, what `asyncio` tasks inherit and what a thread pool
   executor does not. Name the primary source for each claim.
4. **Log or return.** What does each ecosystem's idiom say about logging an error and also returning or rethrowing it?
   Find the Go error-wrapping guidance, any JVM statement, and any Python statement, with rationale and stated
   exceptions.
5. **Metrics from a library.** May a library register instruments, and on which registry? What do
   `prometheus/client_golang`, `prometheus_client` (Python) and Micrometer say about a library registering on a global
   default, and what does OpenTelemetry's instrumentation-library guidance say instead?
6. **The tracing API contract.** What does each language's OpenTelemetry API say about a library creating a tracer,
   the no-op default when the host has not configured a provider, span lifetime and error recording? What is the
   stated rule for attributes versus span events?
7. **What the framework does to the message.** Per ecosystem: what does the formatter or handler do that the author
   did not ask for — locale-aware number formatting, a format-pattern character that swallows placeholders, lazy
   versus eager argument evaluation, a level guard that is or is not needed, what a structured attribute costs when
   the level is off.
8. **Structured fields.** What is each ecosystem's supported way of attaching key-value fields, and what does its own
   documentation say about choosing a key, reusing a key, and the stability of a key over time?
9. **Level semantics that a project actually states.** Find projects that define their levels concretely rather than
   generically — Kubernetes' klog verbosity levels and their stated meanings are one; find others, per ecosystem, and
   report what each level is defined to mean.
10. **The mechanical checks that exist.** Per ecosystem: linters and analyzers that catch instrumentation defects —
    an unused context, a `basicConfig` in a package, an implementation dependency in a library's build, a
    non-constant metric label, a missing level guard, a logged-and-returned error. Name the tool, the rule id, and
    what it does not catch.
11. **Ecosystem-specific anti-patterns named by maintainers**, in issue threads, style guides, or review comments,
    rather than in blog posts.
12. **What a library does instead of emitting.** Where an ecosystem's answer is a hook, a callback, an event
    interface, or a metrics interface the host implements, find the stated pattern and an example of a widely used
    library that follows it.

## Search scope

Seven categories. The named examples are starting points, not the limit. Run at least 25 distinct searches across all
seven, and fetch the primary source before citing it.

1. **Go primary sources.** The `log/slog` package documentation and its design proposal and discussion; the Go blog on
   structured logging; `context` documentation and the Go blog on context; Go's error-wrapping documentation and the
   `errors` package; the Go standard library's own policy on logging; `golang.org/x/exp/slog` history; the Go code
   review comments document.
2. **Python primary sources.** The standard library `logging` documentation, the Logging HOWTO, and the
   "Configuring Logging for a Library" section; `contextvars` documentation and the asyncio task-context rules;
   `structlog` documentation; guidance in widely used libraries (`urllib3`, `requests`, `boto3`, `django`) on their
   own logger and handler policy.
3. **JVM primary sources.** The SLF4J manual, including the section on why a library depends on the API; the
   `java.util.logging` documentation; Log4j 2 and Logback's own statements on library usage; Micrometer's
   documentation on registering meters from library code; the JDK's own `System.Logger`.
4. **OpenTelemetry, per language.** The Go, Python and Java API and SDK documentation; the instrumentation-library
   guidance ("libraries should depend on the API only"); the no-op default behaviour; the span status and error
   recording sections; the logs bridge API and what it means for a library.
5. **Metric clients.** `prometheus/client_golang`, `prometheus_client` for Python, Micrometer: registry ownership,
   what a library may register, label cardinality rules, naming and unit conventions as each client states them.
6. **Project conventions, named by project.** Kubernetes logging conventions and the structured-logging KEP and klog
   levels; Envoy; Elasticsearch; CockroachDB; Django and Django REST framework; `kubectl`; `containerd`; any project
   whose CONTRIBUTING or style guide constrains logging in library code.
7. **Mechanical checks.** `go vet`, `staticcheck`, `errcheck`, `contextcheck`, `sloglint`, `ruff` and `pylint` logging
   rules, `flake8-logging`, `logging-format`, SpotBugs and Error Prone logging checks, ArchUnit or import-control
   rules that forbid an implementation dependency. Report the rule id and what the verdict establishes.

## Freshness

Recency matters for: Go `log/slog` (Go 1.21 and later — anything predating it describes a different world), the
OpenTelemetry logs signal and its stability status, `contextvars` and asyncio behaviour in current Python, and the
current state of the listed linters. **Say which version each claim is true of.** Age is irrelevant for the SLF4J
facade argument, the Python library-configuration guidance, and long-settled project conventions.

## What counts as evidence

Signals, not filters: the ecosystem's own documentation over a third party's; a maintainer's statement in an issue or
proposal over a blog post; a rule with a stated rationale over a snippet; adoption by a large project; a linter that
implements the rule. **Prefer a studied claim over a widely repeated one, and say which is which.** Where a claim is
the ecosystem's stated convention rather than a measured result, label it asserted and say by whom.

## Exclusions

Logging-library benchmark shootouts; vendor SDK marketing; "how to set up logging in X" tutorials with no rationale;
migration guides between libraries; courseware; anonymous prompt collections; StackOverflow answers with no primary
source behind them.

## Required output for Pass 1b

Under 3500 words excluding tables. Write it to the path the launcher names, with these five sections and these counts.

1. **Executive summary.** Answer briefly: for each of the three ecosystems, is there an authoritative statement of the
   library contract or only convention; which of the baseline's asserted mechanics are confirmed and which are
   corrected; **where do the ecosystems differ in kind rather than in API** — this is the highest-value answer in the
   pass; which roles need a reference file and which do not; which questions are under-served.
2. **Candidate inventory**, 20 to 30 rows: name, URL, ecosystem, role (logging API, metrics client, tracing SDK,
   context propagation, project convention, mechanical check), author or organization, which of questions 1–12 it
   speaks to, evidence strength marked studied or asserted, maintenance status and version applicability, and one line
   on why it is worth considering.
3. **Promising shortlist for Pass 2**, 8 to 12 candidates, two to four sentences each: why it is promising, which
   rules it may contribute, whether the rule it yields is language-neutral or local to its ecosystem, and whether it
   converts into a compact rule an agent can apply without the author present.
4. **Obvious rejects**, 5 to 10, one line of reason each.
5. **Gaps and questions for Pass 2.** Name at least: which per-ecosystem rules have a mechanical check and which do
   not; which claims in the baseline's part 2 you could not confirm from a primary source; where two ecosystems'
   stated positions conflict, so the skill cannot state one language-neutral rule; and what a reference file must
   carry that the body of the skill cannot.

## Baseline

Read `seed_baseline.md` in the same directory in full. It is **context and a snapshot of what house practice has produced, not
the target**. Report any contradiction as a finding.

The positions this pass must check against primary sources, all of them asserted from a model's memory and sourced
nowhere:

- **S4** — a library does not choose the logging backend and does not export metrics itself; the stated mechanics per
  ecosystem (facade on the JVM; `getLogger(__name__)` plus `NullHandler` and never `basicConfig` in Python; accept a
  logger and install no global handler in Go);
- **S5** — log or return, never both;
- **S6** — do not drop the host's context across a thread, goroutine, or task boundary, and the claim that the rule is
  the same everywhere while the failure differs;
- **S11** — that numbers must not pass through a locale-aware formatter. This one **is measured**: on the JVM,
  `java.util.logging.Logger.log` with an `Object[]` renders through `java.text.MessageFormat`, so `103887667` prints
  as `103,887,667` under `en-US`. Establish whether Go's and Python's formatters have an equivalent trap, and report
  honestly if they do not;
- **S2** — that the library/service split is the right primary axis. Report whether it holds in Go and Python or is a
  JVM-shaped idea.

Part 3 of the seed records that both observed failures are on the JVM and that no Go or Python failure has been
recorded. Where you find a documented, concrete Go or Python instrumentation defect — in an issue, a post-mortem, or a
maintainer's review comment — **report it**, because it fills a recorded gap in the research.
