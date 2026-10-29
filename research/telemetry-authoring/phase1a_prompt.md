# Pass 1a — discovery brief, cross-cutting

## Research title

Find proven, checkable rules for deciding **which telemetry signal an event owes** — a log line, a metric, a span, or
nothing — and for what a log line must carry to be usable by someone without source access, for a skill that writes and
reviews instrumentation in libraries and services.

## Goal

The consumer of the resulting skill is a coding agent at one of two moments: it has just written a branch that ends in
a failure, a retry, a fallback, or a silently clamped value and is deciding what to emit there; or it is reviewing a
diff in which a logger call, a counter, or a span appeared, changed, or is conspicuously absent. It works without the
author, on the diff and the source, and it has nobody to ask. It also **produced the code it is now judging**, so a
rule it can satisfy by writing a line that looks instrumented is worth nothing.

Missing today, in the consumer's terms:

- no rule for **which** signal an event owes, so everything becomes a log line;
- no rule for what a line must carry so the reader can tell **still working** from **degraded** from **given up**;
- no rule for the cost of a signal — its rate in a healthy system, its cardinality, what it costs at scale;
- no rule for when the honest answer is **emit nothing**, because the state is already observable;
- no rule about severity that survives contact with a real project's conventions;
- nothing about what a **library** may emit, as opposed to a service.

This is Pass 1 only. The goal is discovery and classification, not final ranking. A companion brief (Pass 1b) covers
the per-ecosystem primary sources — Go `log/slog`, Python `logging`, JVM facades, OpenTelemetry APIs, metric clients —
and the project-specific conventions. **Do not spend this pass's budget on those**; this pass is for the cross-cutting,
language-independent question.

## Important framing

The baseline at the end of this brief is a starting point, not the target. Sources that improve on it, contradict it,
or take a different approach are **preferred**, and a contradiction is a finding worth reporting in its own right.
Agreement with an unsourced baseline establishes nothing, so do not report agreement as support.

Concluding that no single source covers the domain is an acceptable answer. Then name the strongest reusable sources
and say how they combine.

The consumer is an agent, so a source that states a rule **and its rationale** beats a checklist, and a rule nobody can
apply without the author present is not useful however sound it is.

Three properties matter more than usual here:

- **Detectability.** Can a reviewer tell the rule was violated from the artifact and the diff, without running
  anything? Sources that describe how a defect is *spotted* are worth more than sources that describe the ideal.
- **Mechanical checkability.** Which defects have an oracle — a linter, a log-analysis tool, a cardinality check, a
  static rule — what the oracle catches, and what it misses.
- **Resistance to a writer who optimizes for the check.** The agent writes the instrumentation and is rewarded when it
  passes review. Name the failure shapes: logging the obvious, adding a line with no identifier in it, a counter
  nobody can alert on, a span that wraps nothing, a level chosen so the line disappears. Sources that name these are
  worth more than sources that assume good faith.

## Readers

Fixed for this pass. Report a row that is wrong or missing rather than replacing it.

| Reader | Situation | Holds |
| --- | --- | --- |
| R1 Library author | Adding or changing a logger call, or a counter, inside a library that ships to hosts it will never see | The diff, the library's conventions, no control over how the host configures output |
| R2 Service author | Has just written a branch that ends in a failure, a retry, a fallback, or a silently clamped value | The diff, the instruments the service already exports |
| R3 On-call engineer | An alert or a user report, no source access, deciding whether to wait or intervene | Logs, a dashboard, the deploy history, the literal text of one message |
| R4 Reviewer | Holds a diff in which a signal appeared, changed, or is conspicuously absent | The diff, the repository's conventions, no access to the author |

R3 is treated as a **beneficiary, not a consumer**: R3 never loads the skill, and every rule serving R3 is enforced
through R1, R2, or R4. **Rule on whether that treatment is right**, and say what it costs.

## Out of scope

Companion skills that own neighbouring ground. Do not restate or re-derive their material; if a source's only
contribution falls in one of these, classify it as a reject in one line.

- **`english-developer-style` §7** owns the *wording* of a message that already exists: reason + action + consequence,
  no `please`, naming the offending input, the vocabulary binding to the code, and formatter traps. Wording is settled.
- **`docs-page-authoring` §7** owns the documentation entry a user-visible message owes.
- **`deep-review`'s observability axis** owns the repository-wide *review*. This skill is the author-side counterpart.
- **`change-description-authoring`** owns commit messages and changelogs.

Subject matter that is not this skill's: vendor and backend comparisons; log shipping, storage, retention and cost
management; dashboard design; alerting rule syntax and SLO documents (the authoring consequence — that a metric is
added under a named question — **is** in scope, the PromQL is not); process advocacy; incident-management practice.

**Treat wording as settled. If a source's only contribution is wording, classify it as a reject and say so in one
line.**

## Questions the pass should answer

You do not have to answer these. You have to find the sources that can.

1. **Which signal does an event owe?** Does any source state a rule for choosing between a log line, a metric, a span,
   and nothing, that an author can apply at the moment of writing the branch — as opposed to describing the three
   signals and leaving the choice to taste?
2. **Is "emit nothing" ever stated as an outcome?** Which sources say that an event needs no signal because it is
   already observable, and what test do they give for "already observable"?
3. **What must a line carry?** Which sources state the required contents of a log record — the object, the operation,
   the correlation identifier, the upstream status, the decision taken — rather than the format it is serialized in?
4. **The still-working / degraded / given-up distinction.** Does any source name this class of distinction, or the
   defect of a message that cannot express it, and does any measure how often it is got wrong?
5. **Severity.** What evidence exists on how developers choose levels, how often they choose wrongly, and whether any
   project's stated level semantics (as opposed to a generic ladder) have been shown to work?
6. **Rate and cost.** What does the literature or practice say about the steady-state line rate of a healthy system,
   about logging inside a loop or per message, and about the "log on change, not on occurrence" pattern?
7. **Libraries versus applications.** Is the distinction a recognized fault line in instrumentation practice? What
   does a library owe its host that an application does not owe anyone, and who states it?
8. **Log-and-rethrow.** Is "log or return, never both" stated anywhere as a rule, with a rationale, and what are the
   stated exceptions?
9. **Correlation.** What is the accepted vocabulary and mechanism for joining one line to its neighbours across
   concurrency and process boundaries, stated independently of any one library?
10. **Empirical work on logging code.** What does the research find about how much logging code changes, its defect
    rates, anti-patterns, level mispredictions, and where developers actually log? Name the studies, their samples,
    and their findings.
11. **Agent-written instrumentation.** Is there any empirical work, benchmark, or evaluation of instrumentation
    produced by an LLM, and which defect shapes does it name?
12. **Existing rubrics.** Which review checklists, contribution guides, or agent skills already state instrumentation
    rules, and which of their items are mechanical?

## Search scope

Six categories. A category named abstractly gets searched abstractly, so the named examples are the starting points,
not the limit. Run at least 25 distinct searches across all six.

1. **Practitioner books and engineering-organization guidance.** Google's *Site Reliability Engineering* and *The Site
   Reliability Workbook* (the monitoring, alerting, and "four golden signals" chapters); Charity Majors, Liz
   Fong-Jones and George Miranda, *Observability Engineering*; Cindy Sridharan, *Distributed Systems Observability*;
   *Release It!*; the Google, Microsoft, and AWS Well-Architected operational-excellence material.
2. **Empirical software-engineering research on logging.** Yuan et al., "Characterizing logging practices in
   open-source software" and "Improving software diagnosability via log enhancement"; Yuan et al., "Simple testing can
   prevent most critical failures" (OSDI 2014); Fu et al., "Where do developers log?"; Chen and Jiang,
   "Characterizing and detecting anti-patterns in the logging code"; work on log-level prediction and on "which
   logging statement to add"; any systematic literature review of logging practice. Report samples and findings, and
   mark each claim studied or asserted.
3. **The OpenTelemetry specification's cross-cutting parts**, not the per-language API: the data model for logs,
   metrics and traces; the guidance on what belongs in an attribute against an event against a metric; the
   instrumentation-library guidance; the semantic-convention *principles* (naming, stability, cardinality). Per-
   language APIs belong to the companion brief.
4. **Metric-design guidance independent of a client library:** Prometheus's own "instrumentation" and "naming" best
   practices, the RED and USE methods (Tom Wilkie, Brendan Gregg), guidance on label cardinality and what it costs.
5. **Project conventions that state cross-cutting rules**, named by project: Kubernetes' logging conventions and the
   structured-logging KEP; the Go project's own position on logging in the standard library; Elasticsearch, Envoy, and
   Rust's `tracing` ecosystem guidance; large OSS projects' CONTRIBUTING files that constrain logging.
6. **Agent skills, rule files, and LLM evaluations** covering instrumentation or observability. Report honestly if the
   category is thin.

## Freshness

Recent sources matter for: the signal-choice question as it is framed today (structured logging, OTel's unification of
the three signals), cardinality economics, and anything about agents. Age is irrelevant for: the empirical logging
studies (the 2012–2017 corpus is canonical and must not be discarded for its date), the SRE chapters, and the
library-versus-application distinction.

## What counts as evidence

Signals, not filters: adoption by a known organization or a large project; a named author; active maintenance; before
and after examples; a stated rationale rather than an assertion; independent evaluation; public issue discussions that
show the trade-off being argued. **Prefer a studied claim over a widely repeated one, and say which is which.**

## Exclusions

Vendor marketing and "top 10 logging best practices" listicles with no rationale and no source; tool comparisons;
observability-platform migration guides; courseware; anonymous prompt collections; anything whose only content is a
format (JSON versus text) argument.

## Required output for Pass 1a

Under 3500 words excluding tables. Write it to the path the launcher names, with these five sections and these counts.

1. **Executive summary.** Answer briefly: does a single source cover the domain or is synthesis required; which
   category is strongest and which is weakest or most polluted; does an agent skill for this already exist; does the
   reader table hold, and is R3-as-beneficiary right; which questions are answerable from what you found and which are
   under-served; where pass 2 should concentrate.
2. **Candidate inventory**, 20 to 30 rows: name, URL, category, author or organization, which of questions 1–12 it
   speaks to, which readers it serves, best use, evidence strength marked studied or asserted, maintenance status, and
   one line on why it is worth considering. A URL per row, fetched or seen in a search result.
3. **Promising shortlist for Pass 2**, 8 to 12 candidates, two to four sentences each: why it is promising, which
   rules it may contribute, which reader it serves, and whether it converts into a compact rule an agent can apply
   without the author present.
4. **Obvious rejects**, 5 to 10, one line of reason each.
5. **Gaps and questions for Pass 2.** Name at least: which rules are detectable from the diff alone, which need the
   work run, and which need a tool; which sources conflict and on what; whether any source treats instrumentation as
   something its own author may game, and what check it proposes; whether the signal-choice rule survives contact with
   the concrete cases in the baseline; what is left that only a human can judge.

## Baseline

Read `seed_baseline.md` in the same directory in full. It is **context and a snapshot of what house practice has produced, not
the target**. Report any contradiction as a finding.

Its part 2 lists twelve positions stated from practice and sourced nowhere. The weakest, where this pass should push
hardest:

- **S2** — that the primary split is library versus service, not language, and that the boundary is per module, tested
  by "does something outside this code configure the output";
- **S3** — that the most common correct outcome is to emit nothing;
- **S8** — that for a monotonic state one logs on change, not on occurrence, so the steady state is silent;
- **S9** — that a metric is authored under a named question, and one added without a question cannot be read;
- **S7** — the still-working / degraded / given-up distinction, which house text states and no known source does.

Part 3 carries two recorded failures, both on the JVM, and records the absence of a Go or Python failure as a gap. A
central question for this pass is therefore: **do the cross-cutting rules port, and where do the ecosystems differ in
kind rather than in API?**
