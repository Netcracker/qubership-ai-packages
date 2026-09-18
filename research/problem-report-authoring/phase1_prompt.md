# Pass 1 — discovery brief: how a problem is reported so that someone else can act on it

## Research title

Find proven rules for what a problem report must say, in what order, and what its author must establish before writing
it, for a skill that drafts and reviews bug reports filed in other people's projects, short problem messages sent to a
colleague, and feature or change requests filed in a backlog.

## Goal

The consumer of the skill is a coding agent (Claude Opus or Sonnet, running in a terminal inside a checkout) at the
moment a human says "write this up as an issue", "tell the team about this", or "file a request for this". The agent
holds what it just did: a session in which it reproduced something, read the code of one or more projects, and formed a
theory about the cause. It does **not** hold the reader. The artifact it produces is read by people who were not in
that session and who will spend far less time on it than the agent spent producing it.

What is missing today, in the consumer's terms:

- The agent has no form for a problem report, so it reaches for the nearest form it does have — the pull request
  description — and applies it. That form starts from the mechanism, because a reviewer already knows what is broken.
  A triager does not.
- The agent has no rule about what must be established **before** the first sentence is written: which project actually
  owns the defect, whether the symptom still occurs on a supported version, whether the report already exists.
- The agent has no rule about the status of its own causal analysis, which is often the largest and most confident part
  of what it wrote and is sometimes wrong.
- The agent has no rule about what "expected behavior" must contain to be usable, or about checking that a form it
  proposes as the expected one would actually work.
- The agent has no notion of how the three genres differ in length and in what may be left unsaid.

This is Pass 1 only. The goal is discovery and classification, not final ranking. Do not extract rules; find and
classify the sources from which rules can be extracted.

## Important framing

The baseline at the end of this brief is a starting point, **not** the target. Sources that improve on it, contradict
it, or take a different approach are preferred to sources that agree with it. Agreement with an unsourced baseline
establishes nothing, and a source that contradicts the baseline is a finding worth reporting prominently.

Concluding that no single source covers the domain is an acceptable answer. In that case, name the strongest reusable
sources and say how they combine, and which part of the domain remains unsourced.

The consumer is an agent, not a person with a mentor. A source that states a rule **and its rationale** is worth more
than a checklist, and a rule nobody can apply without the author present is not useful. Prefer sources with
before-and-after examples of actual reports.

Three properties matter more than usual here.

- **Detectability.** Can a reviewer tell the rule was violated from the report text alone — without the target
  project's code, without running anything? Sources that describe how a bad report is spotted are worth more than
  sources that describe the ideal report.
- **Mechanical checkability.** Which defects have an oracle (a template's required fields, a reproducer that a script
  can run, a version string that can be compared against the project's supported list, an identifier that either
  resolves or does not), what that oracle catches, and what it misses.
- **Resistance to an author who optimizes for the check.** The agent both writes the report and decides it is
  complete, and it is rewarded for producing something that looks thorough. Name the failure shapes where sources
  discuss them: a fabricated log line or version number, a reproducer asserted but never run, an expected behavior
  hedged until nothing can contradict it, padding with the target project's internals to look diligent, a confident
  cause that was never checked against the project's history. Sources that name these are worth more than sources that
  assume a good-faith human reporter.

## Readers

Fixed for this pass. Report a row as wrong or missing if the evidence says so; do not replace the table on your own
judgment.

| Reader | Situation | Holds |
| --- | --- | --- |
| **R1 Triager on a project the reporter does not maintain** | Working down a queue of newly filed issues, about a minute per item | The report text and the project's own templates, labels, and supported-version policy. Knows nothing about the reporter's code or setup |
| **R2 Maintainer deciding whether to act** | Has accepted the report as real and is deciding whether, and in which direction, to change the project | The whole report plus the project's design constraints and compatibility obligations |
| **R3 Whoever picks the work up months later** | Often the reporter, often a first-time contributor. Starts from a fresh checkout | The report and the current code. Nothing of the original session survives |
| **R4 A user who found the report by searching the symptom** | Hit the same error and is looking for whether it is theirs | The same error string in their own project, and a version number |
| **R5 A colleague the reporter messaged** | Interrupted mid-task. Shares the codebase and the jargon, not the last hour of the reporter's session | A few lines of chat. Decides whether this is theirs and what is being asked |

R5 is the reader of the short genre; R1 through R4 are the readers of a filed issue. For the feature or change request
genre, R2 doubles as the backlog owner. **Rule on that:** does the evidence say a backlog owner asks questions R2 does
not — cost, priority, who is blocked, how we will know it is done — and therefore needs a row of their own?

## Out of scope

**Companion skills that own neighboring ground. Do not restate or re-derive their material.**

- `english-developer-style` — wording, tense, mood, sentence length, punctuation, dialect, hedging, and the tells of
  machine-written prose. Treat wording as settled. If a source's only contribution is wording, classify it as a reject
  and say so in one line.
- `change-description-authoring` — commit messages, pull request titles and descriptions, changelog entries. Its
  readers already know that something was wrong. Sources about describing a *change* belong to it, not here.
- `docs-page-authoring` — documentation pages, including troubleshooting pages, where the problem and its cause are
  already established.
- `adr-authoring` — recording a decision that has been made.
- `test-authoring` — writing the regression test for a confirmed defect, and what a failing test prints.
- Triage skills that consume other people's issues, answer them, or label them.

**Subject matter that is not this skill's:** issue-tracker product comparisons; process advocacy (Scrum, SAFe, shape-up
and their relatives) except where a source states concretely what a written request must contain; incident postmortems
and on-call communication; customer-support ticket handling from the support agent's side; security vulnerability
disclosure procedure (embargo, CVE assignment, coordinated disclosure) — although what a *security* report must contain
is in scope if a source states it as content rules.

## Questions the pass should answer

You do not have to answer these. You have to find the sources that can, and say which questions are well served and
which are under-served.

1. **Order.** Does any source establish an ordering for a report — observable symptom before mechanism, or otherwise —
   and on what grounds? Is there evidence, studied or asserted, on what a diagnosis stated up front costs the reader
   when it turns out to be wrong?
2. **Which fields are load-bearing.** What does the empirical work find about which parts of a report predict that it
   gets acted on, and which parts developers rank as most useful versus what reporters most often omit? Distinguish
   what is measured from what is asserted.
3. **The reproducer.** What makes a reproducer acceptable to a project: a self-contained project, a minimal example, a
   failing test, an archive, a repository, a container image? What guidance exists on *reducing* an example, and on
   what a reporter should do when the failure will not reduce?
4. **Attribution across a stack.** How does a reporter establish which component owns a defect when the symptom is
   observed through several layers (application, library, framework, build tool, runtime)? What do projects say about
   filing at a boundary, what happens to a misfiled report, and what evidence is required before naming a layer?
5. **Duplicates and currency.** What do projects require before a report is filed — searching existing issues,
   reproducing on the latest or a supported version, checking release notes and recent fixes? Is there measured
   evidence on how common duplicates and already-fixed reports are, and what they cost a project?
6. **Expected behavior.** What makes a statement of expected behavior usable: precise enough that someone could write a
   test against it, distinct from a proposed implementation, stated in values a reader can observe? Does any source
   address stating one expectation per independent symptom, or the failure where "expected" silently becomes a design
   proposal?
7. **Workarounds and configuration.** How should a report present a known workaround or an available setting without
   undercutting the request? Does any source discuss the failure where the workaround becomes the frame, so the report
   reads as "I am already fine" while asking for a change?
8. **Feature and change requests.** What distinguishes an actionable request from a wish: the job to be done, what is
   impossible today, acceptance criteria, alternatives considered, who is affected? What do enhancement-proposal
   processes require of the initial request, and what does a backlog item owe (user story shape, INVEST, acceptance
   criteria, definition of done) that an issue in someone else's tracker does not?
9. **The short form.** What does the evidence or the practitioner literature say about asking a colleague: how much
   context, what to state first, what the recipient needs in order to decide "is this mine", what may be omitted
   because it is shared, and what must never be omitted even in three lines?
10. **Reporting the solution instead of the problem.** Which sources name the failure where the reporter describes
    their attempted fix or their theory rather than the outcome they cannot reach, and what check catches it from the
    text?
11. **Detection.** For the defects the sources name, which are detectable from the report text alone; which need the
    reproducer to be run; which need a tool or a lookup (an identifier that resolves, a version against a support
    matrix, a search of the tracker); and which stay a human judgment.
12. **Machine-written reports.** Is there empirical work, project policy, or maintainer-published guidance on reports
    produced by an LLM or an agent: hallucinated identifiers and log lines, unverified reproducers, volume effects on
    maintainers, projects that ban or gate AI-assisted issues, disclosure requirements? Also: does an agent skill or
    rule file for writing issues already exist, and what does it say? Report honestly if this category is thin.

## Search scope

Search every category. A category not searched is a gap in the report, and you must say so if you could not cover one.
Run at least 25 distinct searches spread across all seven.

1. **Practitioner essays and books.** Simon Tatham, "How to Report Bugs Effectively"; Eric S. Raymond, "How To Ask
   Questions The Smart Way"; Stack Overflow, "How to create a Minimal, Reproducible Example" and its help-center pages
   on asking; Mozilla, "Bug writing guidelines"; David Agans, *Debugging*; Andreas Zeller, *Why Programs Fail* and *The
   Debugging Book* on reducing an input; Joel Spolsky on bug tracking; *The Pragmatic Programmer* on reporting.
2. **Project contribution guides and issue templates, by name.** gradle/gradle; junit-team/junit-framework;
   kubernetes/kubernetes; rust-lang/rust; python/cpython; PostgreSQL (the bug reporting form and the pgsql-bugs
   guidance); curl (`docs/BUGS.md` and the project's writing on report quality); LLVM; Django; nodejs/node; Chromium;
   Homebrew; Apache projects filing into JIRA; Eclipse and Bugzilla-hosted projects. Look at both the prose guide and
   the machine-readable issue forms, and note which fields are marked required.
3. **Tracker documentation and standards.** Bugzilla documentation; Atlassian and JIRA guidance on writing a bug; the
   GitHub documentation on issue forms and templates; ISTQB syllabus material on defect reporting; IEEE 829 and
   ISO/IEC/IEEE 29119-3 incident-report content. Technique and content only, not process or certification.
4. **Mechanical oracles.** What a required template field enforces and what it does not; reproducer-checking bots and
   CI-run reproducers; stale-issue and needs-info automation; duplicate-detection tooling and what its verdict means;
   linters or bots that check a report for missing version or reproduction information.
5. **Empirical software engineering research.** "What Makes a Good Bug Report?" (Zimmermann, Premraj, Bettenburg et
   al.) and its follow-ups; work on duplicate bug reports; work on non-reproducible or irreproducible reports; studies
   of information needs of developers; studies of issue quality on GitHub; work on bug-report readability, on
   reproduction steps quality, and on what makes reports get closed as invalid.
6. **Requests, proposals, and backlog items.** Rust RFC, Python PEP, Kotlin KEEP and comparable processes — what the
   initial problem statement must contain; INVEST and user-story practice; acceptance-criteria guidance; "jobs to be
   done"; Amazon's working-backwards or PR-FAQ practice as a problem-first form; product-management guidance on
   writing a problem statement.
7. **Short-form asking, and agent-specific material.** The "no hello" and XY-problem literature (xyproblem.info and its
   sources); engineering-organization guidance on asking questions in chat; guidance on escalating to a colleague.
   Then: published agent skills, rule files, and prompt libraries for writing issues or bug reports, and any project
   policy on AI-generated reports. Report honestly if this last category is thin.

## Freshness

- The canonical essays (Tatham 1999, Raymond, Mozilla's guidelines) are old and remain the reference; do not discard
  them for their date. Say when a claim in them has been superseded.
- Empirical studies from the Bugzilla era are acceptable, but note the tracker and the era: findings about a
  free-text Bugzilla field may not transfer to a GitHub issue form with required fields.
- Project contribution guides, issue forms, and supported-version policies must be current — fetch the file from the
  default branch, and give the date or commit you saw.
- Anything about machine-written reports and project policy on them must be from 2023 onward, and is most useful from
  2025 onward.

## What counts as evidence

Signals, not filters. Weigh them; do not exclude a source for missing one.

- Adoption by a known organization, or by a large project that receives real traffic on its tracker.
- A named author who is accountable for the claim.
- Active maintenance, or a stable canonical status.
- Before-and-after examples of actual reports, or annotated real reports.
- A stated rationale rather than a bare rule.
- Independent evaluation, replication, or a public dataset.
- Public issue discussions where maintainers argue about what a report should have carried — these show the trade-off
  rather than the ideal.

Prefer a studied claim over a widely repeated one, and **say which is which for every central claim**. Do not promote
an asserted claim to studied because it is repeated often.

## Exclusions

- Marketing pages and tracker product comparisons.
- Courseware, certification cram material, and listicles with no rationale and no source.
- Anonymous prompt collections with no author and no examples.
- Blog posts that restate Tatham or Raymond with nothing added — cite the original instead.
- Anything whose only contribution is wording, tone, or politeness (owned by `english-developer-style`).
- Advice aimed at the maintainer's side of triage, unless it states what the report itself must carry.

## Required output for Pass 1

Write the report in English, as Markdown, with these exact section headings, under **3500 words excluding tables**.

1. **Executive summary.** Answer briefly, as a list: does a single source cover this domain or is synthesis required;
   which search-scope category is strongest and which is weakest or most polluted; does an agent skill for this already
   exist; does the reader table hold, and specifically does the backlog owner need a row; which of the twelve questions
   are answerable from what you found and which are under-served; where Pass 2 should concentrate.
2. **Candidate inventory**, 20 to 30 rows, columns: name; URL; category (1–7); author or organization; questions it
   speaks to (by number); readers it serves (by ID); best use; evidence strength (studied / asserted); maintenance
   status; one line on why it is worth considering.
3. **Promising shortlist for Pass 2**, 8 to 12 candidates, two to four sentences each: why it is promising, which rules
   it may contribute, which reader it serves, and whether it converts into a compact rule an agent can apply without
   the author present.
4. **Obvious rejects**, 5 to 10, one line of reason each.
5. **Gaps and questions for Pass 2.** Name at least: which rules look detectable from the report text alone, which need
   the reproducer run, and which need a tool or lookup; which sources conflict and on what; whether any source treats
   the report as something its own author may game, and what check it proposes; whether the ordering rule in the
   baseline survives contact with the sources; which of the three genres (issue, colleague message, request) is least
   served by the literature; and what is left that only a human can judge.

Every inventory row needs a URL you fetched or saw in a search result. Where a source is unreachable, say so rather
than reconstructing it from memory.

## Baseline

Use this as context and as a snapshot of what one practitioner's practice has produced. It is **not** the target.
Report any contradiction as a finding.

### A. What practice already produced

Two issue templates from the projects involved in the recorded failure below.

`gradle/gradle`, contributor bug report form, required fields in order: **Current Behavior** ("tell us what happens") →
**Expected Behavior** ("tell us what should happen") → Context (optional) → **Self-contained Reproducer Project**
(required) → **Gradle version** (required) → Build scan URL (optional) → Your Environment (optional).

`junit-team/junit-framework` ships a Markdown `bug_report.md`, a `feature_request.md`, and a `task.md`.

The repository this skill will ship from already has `change-description-authoring`, which fixes five readers for a
change description (reviewing maintainer, archaeologist, on-call engineer, upgrading user, backporter) and gives the
slots of a commit body and a pull request description. Applying that form to a problem report is the recorded failure
below. The skill under construction must state its boundary with it in both directions.

### B. Rules the maintainer states from experience

Stated from practice and **sourced nowhere**. Each needs external evidence, or an explicit note that none was found.

1. Start from the user-facing problem — "I do X, Y breaks" — before any statement about the target project's
   internals.
2. Causal analysis, and links into the target project's source, go at the end if they appear at all: the analysis may
   be wrong, and a wrong diagnosis stated first costs the reader more than a correct one saves.
3. Expected behavior is stated in values a reader can observe and act on, not in positional artifacts. A report asking
   for a test-report name should ask for `value = "x"`, not for `[1]`, because an index identifies nothing and shifts
   when the source data changes.
4. Any form proposed as the expected one must have been checked to actually work. (In the recorded failure, the agent
   proposed an index-based name partly on the grounds that it would let a reader re-run a single case; re-running by
   index does not work.)
5. Independent symptoms get separate expected-behavior blocks rather than one merged block.
6. A known workaround must not become the frame of the request when the request is that the default should work.
7. Establish which project owns the defect before filing. A symptom observed through a stack is not evidence about any
   one layer.
8. Fill the target project's own template fields, by their names, so the text drops into the form unchanged.

### C. The recorded failure

An agent (Opus) was asked to draft issues for `gradle/gradle` and `junit-team/junit-framework` after a session in which
it had reproduced a test-reporting defect. The maintainer's corrections, translated from Russian:

- On the first drafts: *"I understand expected behavior and current behavior, but the 'body' part is too hard to take
  in. It looks like this is not a description of the problem, it is already an investigation of its causes. I would
  start the issue with the user-facing problem: I do this, this breaks. The section with links into the code can go at
  the end — that analysis may turn out to be false, and it is not where to start."*
- The draft for JUnit led with the mechanism: which internal class produces the reporting name and which one writes the
  XML attribute. The agent later conceded it had written the report in the only form it had — the form of a pull
  request description — and that the resulting order (mechanism first, symptom second) is right for a change
  description and backwards for a problem report, because the reviewer of a change knows what is broken and a triager
  does not.
- The agent proposed filing against JUnit at all without establishing that JUnit still had the defect. The maintainer
  pushed back (*"From your description I do not understand what exactly the problem with JUnit is. It looks like the
  whole problem comes from Gradle. If it is only in Gradle, there is no point filing against JUnit."*). On a second
  look the agent found the project had already fixed two related reporting defects and shipped the fix in a maintenance
  release, and withdrew the framing.
- The agent put a proposed expected form in the report without checking it: re-running a single parameterized case by
  the index shown in the report does not work in that tool. The maintainer asked, *"How would the reader use the
  indices? To re-run? Are you sure that works? Check."* It did not.
- The agent framed the JUnit request around an available configuration setting ("one configuration parameter does it
  for a whole build"), which read as "configuration is enough for me" while the request was that the default should
  work.
- The agent merged two independent symptoms into one expected-behavior block, and used bare argument values (`x`,
  `true`) where the reader needs the parameter names (`value = "x"`, `flag = true`).

Both issues were eventually filed, after roughly six rounds of correction, as
[gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
[junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041). Both are public and may
be fetched as examples of the accepted end state; the rejected drafts are not public.

### Where this baseline is weakest

Push hardest here.

- **The ordering rule (B1, B2).** It is the whole point of the skill and rests on one maintainer's judgment. Find
  sources that back it, qualify it, or contradict it — including any source that argues a report *should* lead with a
  diagnosis when the reporter has one.
- **Attribution across a stack (B7).** The most expensive failure in the record, and the baseline says nothing about
  how to establish ownership beyond "establish it".
- **The colleague message.** The baseline has no rules for it at all beyond "the same, but shorter".
- **The feature or change request.** The baseline has no rules for it at all.
- **Detection.** The baseline states rules but not how anyone checks them without the author present.
