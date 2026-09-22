# Pass 1a — discovery result, cross-cutting

## Executive summary

**No single source covers the domain.** The nearest thing to a whole-domain source is the AWS Builders' Library
article *Instrumenting distributed systems for operational visibility* (David Yanacek), which states, with rationale
and in one place, what a unit of work owes, what its record must carry, how to bound the rate, and how correlation
crosses threads. It is an organizational practice statement, not a study, and it assumes a service. Everything else
covers a slice: the empirical corpus tells us what goes wrong and how often; the OpenTelemetry specification tells a
library author what to depend on and when not to instrument at all; Prometheus tells a metric author what a label
costs; Kubernetes' SIG-Instrumentation conventions are the only project-scale document that states a level ladder, a
library rule, and a log-or-return rule together. Synthesis is required, and the skill's value is mostly in the joins.

**Strongest category: 2 (empirical research).** It is the only category that supplies falsifiable numbers, and one
2024/2026 paper — Saarimäki, Shin and Bianculli's *Towards a Taxonomy of Software Log Smells* — is a near-complete
defect vocabulary derived from 51 articles by open coding, with a tool map attached. Category 4 (metric design) is
small but unusually crisp. Category 5 (project conventions) is strong where a project has written one down and absent
otherwise. **Weakest and most polluted: category 6 (agent skills and rule files) and, secondarily, the practitioner
web around category 1.** Searching for "when to use a span versus a log" returns vendor explainers of the three
pillars with no decision rule; searching for "metric answers a question" returns marketing-dashboard advice. Both
searches produced nothing citable.

**Does an agent skill for this exist? Effectively no.** Published observability skills (Honeycomb's, Elastic's,
Datadog's, community collections) are *backend-side*: query the product, investigate an incident, define an SLO,
migrate to OTel. The closest author-side item found, `observability-designer` in a community skill collection, is an
SLO/dashboard/alerting design skill that states no rule for choosing between a log line, a metric, a span and nothing
at the moment the branch is written. The ground this skill claims is unoccupied.

**The reader table holds.** All four rows appear in the sources: OTel's library page is written to R1, Yanacek and
Prometheus to R2, the SRE monitoring chapter and the log-smell taxonomy's implications to R3, and Kubernetes'
conventions and the logging linters to R4. **R3-as-beneficiary is right, with one cost.** No source addresses an
on-call engineer as an author, so treating R3 as a consumer would be inventing a reader. The cost is that R3's
acceptance test — can the reader tell *still working* from *degraded* from *given up* — is unenforceable from the diff
without a proxy, and the pass found only one external proxy for it (below). Pass 2 must supply that proxy or the rule
will be satisfied by any line that merely looks informative.

**Answerable now:** Q3, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12 all have primary sources with rationale. **Under-served:**
Q1 (signal choice) has no single stated rule — the closest are Prometheus's "for every line of logging code you should
also have a counter" and OTel's negative rule for libraries; Q2 (emit nothing) is stated exactly once, as OTel's *when
in doubt, don't instrument*; Q4 (still-working / degraded / given-up) is named nowhere as a class, though the taxonomy
paper's LS3 worked example turns on precisely that distinction. **Pass 2 should concentrate on** Q1, Q2 and Q4 — the
three the house text is most confident about and the literature is quietest on — and on converting the taxonomy's nine
smells into diff-detectable checks.

**Contradictions with the seed, reported as findings.** S5 ("log or return, never both") survives, but `logr`'s own
documentation inverts the popular framing of S2/S4: "Many people assert that libraries should not be logging… Those
people are welcome to convince the authors of the tens-of-thousands of libraries that *do* write logs that they are
all wrong." Python's `logging` HOWTO likewise says the default *should* be that a library's WARNING reaches stderr,
and calls that "the best default behaviour" — `NullHandler` is an opt-out, not the rule S4 states. S3 ("the most
common correct outcome is emit nothing") is unsupported as a frequency claim; the only supporting source is OTel's
conditional advice for libraries. And Yanacek contradicts the reflex behind S8: DynamoDB "logs every request" at over
20 million requests per second, so a bounded steady-state rate is achieved by sampling and by structure, not
necessarily by silence.

## Candidate inventory

| # | Name | URL | Cat | Author / org | Questions | Readers | Best use | Evidence | Maintenance | Why worth considering |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Instrumenting distributed systems for operational visibility | https://d1.awsstatic.com/builderslibrary/pdfs/instrumenting-distributed-systems-for-operational-visibility.pdf | 1 | David Yanacek, AWS | 1,3,6,9 | R2,R3,R4 | The spine of the service-mode rules | asserted (org practice, named author) | live | Only source that states one-entry-per-unit-of-work, required fields, trace-ID propagation across threads, error-spam rate limiting, and sampling, together |
| 2 | Google SRE book, ch. 6 Monitoring Distributed Systems | https://sre.google/sre-book/monitoring-distributed-systems/ | 1 | Beyer et al., Google | 1,6,9 | R2,R3 | Four golden signals; "as simple as possible, no simpler"; delete signals no dashboard or alert uses | asserted | archival, stable | Supplies the "named question" backing for S9 and an explicit instruction to remove unused signals |
| 3 | Google SRE book, ch. 10 Practical Alerting | https://sre.google/sre-book/practical-alerting/ | 1 | Google | 9 | R2,R3 | Symptom-versus-cause rule for what a metric is for | asserted | archival | The distinction that makes a metric alertable; bounds what belongs in the skill (no PromQL) |
| 4 | Canonical log lines | https://stripe.com/blog/canonical-log-lines | 1 | Brandur Leach, Stripe | 3,6 | R2,R3 | One authoritative wide line per request | asserted | 2019, still referenced | Independent arrival at Yanacek's pattern; names the contract property that makes a line queryable |
| 5 | Observability Engineering | https://www.oreilly.com/library/view/observability-engineering/9781492076438/ | 1 | Majors, Fong-Jones, Miranda | 1,6 | R2,R3 | Why high-cardinality context belongs in events, not metrics | asserted | 2nd ed. 2025 | The clearest statement that pre-aggregation is the thing a metric gives up |
| 6 | Release It! 2nd ed., ch. 17 Transparency | https://www.oreilly.com/library/view/release-it-2nd/9781680504552/f_0081.xhtml | 1 | Michael Nygard | 1,7 | R1,R2 | "Transparency arises from deliberate design"; monitoring decisions belong outside the application | asserted | 2018 | States the library/host boundary as an architectural principle, not a language idiom |
| 7 | Prometheus — Instrumentation | https://prometheus.io/docs/practices/instrumentation/ | 4 | Prometheus project | 1,6,9 | R2,R4 | What to instrument per system kind; "for every line of logging code you should also have a counter" | asserted | live | The only explicit *pairing* rule between a log line and a metric found anywhere |
| 8 | Prometheus — Metric and label naming | https://prometheus.io/docs/practices/naming/ | 4 | Prometheus project | 6 | R2,R4 | Cardinality budget: keep below 10, investigate above 100 | asserted | live | A number a reviewer can check against a diff |
| 9 | The RED method | https://grafana.com/blog/the-red-method-how-to-instrument-your-services/ | 4 | Tom Wilkie, Grafana | 9 | R2 | Fixed metric set per request-driven service | asserted | live | Converts S9 into a default question set instead of a free-form prompt |
| 10 | OTel — Instrumenting libraries | https://opentelemetry.io/docs/concepts/instrumentation/libraries/ | 3 | OpenTelemetry | 1,2,7 | R1,R4 | "When in doubt, don't instrument"; never depend on the SDK | asserted | live | The only primary source that states *emit nothing* as an outcome, with a three-part test |
| 11 | OTel — Logs data model (SeverityNumber) | https://opentelemetry.io/docs/specs/otel/logs/data-model/ | 3 | OpenTelemetry | 5 | R1,R4 | Normative severity ladder and mapping rules | asserted (normative spec) | live | A level semantics that is version-pinned rather than folklore |
| 12 | OTel — Attribute requirement levels | https://github.com/open-telemetry/semantic-conventions/blob/v1.26.0/docs/general/attribute-requirement-level.md | 3 | OpenTelemetry | 6 | R1,R4 | "Metric attributes that may have high cardinality can only be defined with Opt-In level" | asserted (normative) | live | Turns cardinality from advice into a requirement level a reviewer can cite |
| 13 | OTel — Deprecating the Span Events API | https://opentelemetry.io/blog/2026/deprecating-span-events/ | 3 | OpenTelemetry | 1 | R1,R2 | Current model: events are named logs correlated by context | asserted | 2026 | Freshness: the signal-choice question as framed today has *three* outcomes plus nothing, not four |
| 14 | W3C Trace Context (Recommendation) | https://www.w3.org/TR/trace-context/ | 3 | W3C | 9 | R1,R2 | The accepted correlation vocabulary and mechanism | asserted (standard) | Recommendation | Answers S10's "what is this called" independently of any library |
| 15 | Kubernetes logging conventions | https://github.com/kubernetes/community/blob/master/contributors/devel/sig-instrumentation/logging.md | 5 | K8s SIG-Instrumentation | 3,5,7,8 | R1,R2,R4 | Per-level semantics; "don't emit an error log before returning an error"; "shared libraries… should not log errors themselves but just return error" | asserted, project-enforced | live | The single densest project convention; states S5 and S4 in one document |
| 16 | Kubernetes API conventions — Conditions | https://github.com/kubernetes/community/blob/main/contributors/devel/sig-architecture/api-conventions.md | 5 | K8s SIG-Architecture | 4 | R2,R3 | Available / Progressing / Degraded as a published state vocabulary | asserted | live | The nearest external analogue to S7, in status rather than in logs |
| 17 | go-logr/logr package documentation | https://pkg.go.dev/github.com/go-logr/logr | 5 | Tim Hockin et al. | 5,7,8 | R1,R4 | Two kinds only (info, error); numeric V-levels; logger passed in | asserted, with argument | live | Explicitly rebuts "libraries should not log"; a live conflict with S2/S4 |
| 18 | Let's talk about logging | https://dave.cheney.net/2015/11/05/lets-talk-about-logging | 5 | Dave Cheney | 5 | R1,R2 | Argument that warning and error levels are not decidable by the author | asserted | 2015, widely cited | The strongest stated case against a generic ladder; a counterweight to row 11 |
| 19 | Python `logging` HOWTO | https://docs.python.org/3/howto/logging.html | 5 | CPython | 1,5,7 | R1 | "When to use logging" table; library configuration section | asserted (primary docs) | live | Has a *decision table* mapping situations to logging, `warnings.warn`, raising, or `print` |
| 20 | SLF4J FAQ | https://www.slf4j.org/faq.html | 5 | QOS.ch | 7 | R1 | "Embedded components… should not [configure logging]… it is the end-user who has to read the logs" | asserted | live | The rationale behind S2, stated by the facade's own authors |
| 21 | Characterizing Logging Practices in Open-Source Software | http://petertsehsun.github.io/soen691/current/papers/log_icse12.pdf | 2 | Yuan, Park, Zhou (ICSE 2012) | 10 | R4 | Baseline rates for logging churn and level error | **studied** (4 systems, 1.1M LOC, 14,771 statements) | canonical | One log line per 30 LOC; logging churn 1.8× code; 26% of log improvements are level changes; 36% of messages modified as after-thoughts |
| 22 | Simple Testing Can Prevent Most Critical Failures | https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf | 2 | Yuan et al. (OSDI 2014) | 8,10 | R2,R4 | Evidence that log-and-swallow is a failure mode, not a style question | **studied** (198 failures, 5 systems) | canonical | "An error handler that only logs the error is also considered as ignoring the error" — 25% of catastrophic failures; 76% of failures printed explicit failure messages |
| 23 | Improving Software Diagnosability via Log Enhancement | https://www.eecg.toronto.edu/~yuan/papers/logenhancer-tocs.pdf | 2 | Yuan et al. (ASPLOS'11 / TOCS 2012) | 3 | R2,R4 | Which variables a line must carry, derived mechanically | **studied** (8 applications) | canonical | Defines "causally related" variables: ~108 branches per log point, resolvable by ~16 values |
| 24 | Characterizing and Detecting Anti-patterns in the Logging Code | http://www.cse.yorku.ca/~zmjiang/publications/icse2017_chen.pdf | 2 | Chen, Jiang (ICSE 2017) | 10,12 | R4 | Six anti-patterns with a static detector | **studied** (352 changes, 3 systems; LCAnalyzer recall 95%, precision 60%) | canonical | Shows exactly how far a static oracle gets, and where it stops |
| 25 | Towards a Taxonomy of Software Log Smells | https://arxiv.org/pdf/2412.09284 | 2 | Saarimäki, Shin, Bianculli (2024/2026) | 3,4,5,10,12 | R2,R4 | Nine named smells, each with facets, implications and a tool map | **studied** (51 articles, open coding, 16 tools mapped) | active preprint | LS2 "undercover identifier" is F1's second defect; LS3's worked example is the still-working/given-up distinction |
| 26 | Log2: A Cost-Aware Logging Mechanism | https://www.usenix.org/system/files/conference/atc15/atc15-paper-ding.pdf | 2 | Ding et al., MSR (USENIX ATC 2015) | 6 | R2 | What a signal costs at scale | **studied** (survey + production system) | 2015 | 99th-percentile latency +16.3%, throughput −1.48% under intensive logging; 80% of surveyed engineers had hit non-negligible overhead |
| 27 | The impact of concept drift and data leakage on log level prediction models | https://link.springer.com/article/10.1007/s10664-024-10518-9 | 2 | EMSE 2024 | 5 | R4 | Evidence that level conventions drift within one project | **studied** (OpenStack, 28 components) | 2024 | Components of one project move verbosity in opposite directions — fatal to any generic ladder |
| 28 | Do AI Coding Agents Log Like Humans? | https://arxiv.org/abs/2604.09409 | 6/2 | Ouatiti, Sayagh, Li, Hassan (2026) | 11 | R4 | The defect profile of agent-written instrumentation | **studied** (4,550 agent PRs, 3,276 human PRs, 81 repos) | 2026 preprint | Agents overuse WARN in 29.9% of repos, under-log in loops, comply with explicit logging instructions only ~33% of the time; humans perform 72.5% of post-generation log repairs |
| 29 | Automated Logging Is Language-Sensitive (MultiLogBench) | https://arxiv.org/pdf/2604.17529 | 2 | Zhong et al., CUHK (2026) | 10,11 | R4 | Whether rules port across ecosystems | **studied** (6 languages, 63,965 snapshot instances, 744 revision cases, 7 models) | 2026 preprint | Directly addresses F3: absolute performance is language-sensitive, model ranking is not (mean pairwise Spearman 0.912); loop and nested-callable sites hardest everywhere |
| 30 | AL-Bench | https://arxiv.org/html/2502.03160v2 | 2 | Tan, Xu, Zhu, He, CUHK-Shenzhen (2025) | 11,12 | R4 | A runtime oracle for generated logging | **studied** (5 tools; best compile-failure rate 20.1%) | 2025 | Shows that a generated log statement can look right and still not compile or not execute |

## Promising shortlist for Pass 2

**1. Yanacek, *Instrumenting distributed systems for operational visibility* (row 1).** The highest rule density per
page of anything found, and every rule comes with the reason it exists. It can contribute: one entry per unit of work
and no more than one; a separate timer for successful responses so throttling does not make latency look good; a
counter per error *reason* and errors grouped by cause; queue depth recorded at every enqueue and dequeue; "keep the
application log free of spam"; rate-limit a logger that starts emitting stack traces; propagate the trace ID in the
method signature because "in a multi-threaded environment, it is very difficult and error-prone for the framework to
do this propagation on our behalf". Serves R2 and, through R2, R3. Converts to compact rules directly — most are
already imperative and checkable against a diff.

**2. Saarimäki, Shin and Bianculli, *Towards a Taxonomy of Software Log Smells* (row 25).** Nine smells, each with
facets, implications and a mapping to the 16 tools that repair them. It is the closest thing to a defect vocabulary
the skill needs, and it is derived, not asserted. LS2 (*undercover identifier* — missing or wrong component/thread
identifier) is F1's second defect, externally named. LS3's worked example distinguishes a retry that should be WARN
from the timeout that should be ERROR — the only external text found that turns on the still-working / given-up
distinction. LS7 (*landfill logs*) names logging in a tight loop and failure to aggregate. Serves R4 primarily. Each
smell converts to a detection question; the facets are already written as failure shapes.

**3. Kubernetes SIG-Instrumentation logging conventions (row 15).** A convention that has survived a decade and a
full structured-logging migration in a project of Kubernetes' size is the strongest available evidence for Q5 and Q8.
It states a six-level ladder with per-level semantics, a library rule, and the log-or-return rule *with* its rationale
("it is usually uncertain if and how the caller is going to handle the returned error") and its escape hatch (an info
log at V(4) or higher). Serves R1, R2 and R4. Converts cleanly, but the skill must decide how a project-specific
ladder generalizes — see the conflict with row 18 below.

**4. OpenTelemetry library instrumentation guidance (row 10).** The only primary source that states *emit nothing* as
an outcome and gives a test for it: skip instrumentation when the library is a thin proxy over self-explanatory APIs,
when OTel already instruments the underlying network calls, and when no convention would enrich the telemetry — "when
in doubt, don't instrument". Also the API-not-SDK rule and the no-op guarantee that makes it safe. Serves R1 and R4
directly. Converts into the S3 rule with a real test attached, which S3 currently lacks.

**5. Ouatiti et al., *Do AI Coding Agents Log Like Humans?* (row 28).** The only study of agent-authored logging at
scale, and it names failure shapes the skill must resist: WARN overuse in 29.9% of repositories, under-logging in
loops and conditionals relative to humans, instruction non-compliance about two-thirds of the time even when the level
or framework is specified, and humans doing 72.5% of the repairs afterwards. Serves R4. It converts into the
"resistance to a writer who optimizes for the check" section, and it is the evidence that natural-language rules alone
under-perform — which is itself a design constraint on the skill.

**6. Zhong et al., *MultiLogBench* (row 29).** Six ecosystems, Java, Python, Go, C++, JavaScript and C#, with both
repository snapshots and real maintenance commits. Directly addresses F3. It reports that absolute performance is
language-sensitive but model ordering is largely preserved, and that loop and nested-callable sites are the hardest
buckets in every language. Serves R4. It converts into the answer to "do the cross-cutting rules port" — the finding
suggests the *hard cases* are shared and the *mechanics* differ, which is exactly S2's claim.

**7. Yuan et al., OSDI 2014 (row 22).** The one studied claim that turns S5 from a style preference into a defect
class: an error handler that only logs is counted as ignoring the error, and such handlers account for 25% of
catastrophic failures in the sample. It also bounds what logging can be blamed for: 76% of failures did print explicit
failure messages, so the gap is usually comprehension, not absence. Serves R2 and R4. Converts into the rationale
slot behind the log-or-return rule.

**8. Prometheus instrumentation and naming practices (rows 7 and 8).** Small, specific, enforced by a project with
enormous adoption. Contributes the pairing rule ("for every line of logging code you should also have a counter"), the
cardinality budget (below 10; investigate above 100), counter-versus-gauge, "timestamps not time since", and the
warning about metrics in inner loops. Serves R2 and R4. Every item is checkable from the diff; the cardinality rule is
the rare telemetry rule with a number in it.

**9. go-logr documentation and Dave Cheney's *Let's talk about logging* (rows 17 and 18) as a pair.** Read together
they are the live argument about severity: Cheney argues warning and error are not decidable by the author, logr
implements that argument as a two-kind API with numeric verbosity, and both are contradicted by rows 11 and 15, which
publish ladders. Serves R1 and R4. This pair is how the skill's severity section earns the right to say anything at
all: it must state the conflict and give a rule that survives either convention.

**10. Yuan et al., LogEnhancer (row 23).** The only source that derives *which values* a line must carry from the
code rather than from taste: the causally related branches around the log point, resolvable by a small variable set.
This is the mechanical form of S12 and of F2's defect. Serves R2 and R4. It converts into a diff-time question — "does
this line name the branch that produced it?" — which is precisely the check F1 and F2 both failed.

**11. Python `logging` HOWTO (row 19).** Holds the only *decision table* found in a primary source: for each
situation, which tool — `print`, a logger's `info`/`debug`, `warnings.warn`, raising, or `error`/`exception`. The
`warnings.warn`-versus-`logger.warning` split ("if the issue is avoidable and the client application should be
modified" versus "if there is nothing the client application can do") is a genuine cross-cutting rule wearing Python
clothes, and it is close to the distinction S7 is reaching for. Serves R1.

**12. Kubernetes API conventions, Conditions (row 16).** Published state vocabulary — Available, Progressing,
Degraded, with `lastTransitionTime` — where a controller reports on-change rather than on-occurrence. Serves R2 and
R3. It is the nearest external support for both S7 and S8, but it lives in an API status field rather than in a log,
so Pass 2 must decide whether the analogy is load-bearing or decorative.

## Obvious rejects

- **Vendor "logs vs metrics vs traces" explainers** (SigNoz, Dash0, Last9, Chronosphere, Better Stack). Restate the
  three pillars; none states a decision rule an author can apply to a branch.
- **"Prometheus best practices: 8 dos and don'ts" and similar listicles.** Derivative of rows 7 and 8 with the
  rationale removed; excluded by the brief.
- **Circuit-breaker pattern pages (Azure Architecture Center, AWS Prescriptive Guidance, Polly guides).** Resilience
  design, not instrumentation authoring; their logging advice is one line of "log state transitions".
- **Log rate-limiting libraries and syslog throttling docs** (`log-rate-limit`, syslog-ng, F5, Aruba). Operational
  mitigations downstream of the author; say nothing about which events deserve a line.
- **Dashboard-metric advice returned for "a metric answers a question"** (marketing and product-analytics blogs).
  Wrong domain entirely; the search term is polluted.
- **Backend-side agent skills** (Honeycomb, Elastic, Datadog LLM-observability, `observability-designer`). Query,
  investigate, define SLOs, migrate to OTel. None is author-side at the moment the branch is written.
- **SLF4J-versus-Log4j comparison posts and "effective Java logging" roundups.** Tool comparison; excluded. Row 20 is
  kept only for the FAQ's own rationale paragraph.
- **Sentry/Chronosphere "when to reach for what" posts.** Product-shaped signal taxonomies; the rule reduces to "use
  all four".
- **JSON-versus-text logging arguments.** Format only; excluded by the brief.
- **`english-developer-style` §7 territory** — anything whose contribution is message wording. Several
  practitioner posts found (error-message phrasing, "no please", naming the offending input) fall here and are settled.

## Gaps and questions for Pass 2

**Detectable from the diff alone.** Whether the line carries a correlation identifier (LS2, row 1's trace-ID rule);
whether an error is both logged and returned (row 15's rule, mechanised by `errcheck`-adjacent linters and by
LCAnalyzer's family); whether a logging call sits inside a loop with no aggregation (LS7; row 7's inner-loop warning);
whether a metric gains a label whose value set is unbounded (rows 8 and 12); whether a span wraps a call that is
already instrumented (row 10); whether the identifiers in the message exist in the codebase under the names a user
sets — F2's defect, and grep-checkable; whether a new metric appears with no alert, dashboard or documented question
(row 2's "eliminate collected signals unused in dashboards or alerts"). **Needs the work run:** the steady-state line
rate, the actual cardinality, whether the level is honest under a real failure, and whether an operator can answer
"wait or intervene". **Needs a tool:** cardinality measured against a live series database; AL-Bench-style runtime
comparison of emitted logs against expected ones; log-smell detectors beyond the static subset.

**Conflicts between sources, to be resolved and not smoothed over.** (a) *Severity*: OTel's normative ladder and
Kubernetes' six-level V-scale versus logr's two-kind API and Cheney's argument that warning and error are not
author-decidable; and, cutting across both, row 27's finding that components of a single project drift in opposite
directions. (b) *Library logging*: SLF4J and Python's HOWTO say a library must not configure output, but Python's
default *is* WARNING to stderr and calls that best; logr says the "libraries should not log" position has already lost.
(c) *Rate*: row 1 logs every request at 20M requests/second while S8 says the steady state is silent; the reconciliation
is probably that "silence" is the wrong variable and "one bounded record per unit of work" is the right one, and Pass 2
should test that. (d) *Where events live*: row 13 moves events out of spans and into logs, which changes the shape of
the signal-choice question the skill will state.

**Does any source treat instrumentation as something its own author may game?** Only one, and only indirectly: row 28
measures what agents actually do rather than what they claim, and finds compliance with explicit instructions at about
one in three. Rows 24 and 30 propose oracles rather than trust — a static detector with published precision, and a
benchmark that compiles and runs the result and compares emitted logs. Nothing in the practitioner literature assumes
bad faith. The skill will therefore have to invent its anti-gaming checks, and the shape suggested by the evidence is
to check the *joins* rather than the presence: does the identifier in the message exist as a settable name; does the
new counter appear in an alert or a question; does the message name the branch that produced it rather than only its
inputs.

**Does the signal-choice rule survive the baseline's concrete cases?** Partly. For F1's adaptive-fetch line, row 7's
pairing rule and row 23's causally-related-variables analysis both produce the missing element (which limit bound the
result, and a counter for the clamped case). For a library like pgjdbc, rows 10, 15, 19 and 20 agree that the library
emits through a facade and exports no metrics of its own, which leaves S9 with no owner in library mode — an unresolved
asymmetry in the skill's structure that Pass 2 must settle. And the pgjdbc position recorded in the seed (logging
exists "mainly to debug the driver itself") is in direct tension with row 3's symptom-versus-cause framing; that
tension should be stated in the skill, not resolved by fiat.

**Found but held out of the capped inventory**, and worth a row in Pass 2 if the cap is lifted: `sloglint`
(https://github.com/go-simpler/sloglint) and `loggercheck` (https://github.com/timonwong/loggercheck), which between
them enumerate what a linter can enforce today — static message, context passed, no global logger, constant keys,
balanced key/value pairs; Elastic Common Schema's guidelines (https://www.elastic.co/docs/reference/ecs/ecs-guidelines)
as a named field vocabulary for a record; KEP-1602 (https://github.com/kubernetes/enhancements/blob/master/keps/sig-instrumentation/1602-structured-logging/README.md),
which carries the written rationale behind row 15; Fu et al., *Where Do Developers Log?*
(https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/ICSE-2014-SEIP-Where-Do-Developers-Log-An-Empirical-Study-on-Logging-Practices-in-Industry.pdf),
studied over 2.5M and 10.4M LOC at Microsoft, for the empirical list of sites developers log at; Li, Shang and Hassan's
log-level model (https://link.springer.com/article/10.1007/s10664-016-9456-2), whose AUC of 0.75–0.81 is itself evidence
that level choice is underdetermined; Sridharan's *Distributed Systems Observability*
(https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/); and OTel's naming rules
(https://opentelemetry.io/docs/specs/semconv/general/naming/).

**Unreachable.** The 2024 EMSE literature review (`10.1007/s10664-024-10452-w`) is behind Springer's IdP redirect and
was not read; its figures are reported here only as they appeared in search results and must be re-verified or dropped.
Rows 5 and 6 are books; their chapters were characterized from publisher pages and secondary summaries, not read in
full, and Pass 2 must read the specific chapters before quoting them.

**What only a human can judge.** Whether a given event is *interesting* to this project's operators; whether the
project's existing level convention means what its documentation says; whether a log line's absence is a decision or an
oversight; and the one R3 question the whole skill exists to serve — whether, holding only the emitted text, a
competent engineer would wait or intervene. No source found offers an oracle for that, and the skill should say so
rather than pretend to one.
