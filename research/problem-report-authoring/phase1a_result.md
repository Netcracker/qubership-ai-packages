# Pass 1A — discovery: essays, project guides, tracker standards, mechanical oracles, empirical research

Arm A of a split discovery pass. Covers search-scope categories 1–5 exhaustively; concentrates on questions 1–7, 10
and 11; touches 8, 9 and 12 only where a source in these categories speaks to them. Categories 6 and 7 belong to arm
B and were not searched.

All fetches were made on 2026-09-07 unless a commit date is given. Every inventory row has a URL I fetched directly
(curl, `gh api`, `pdftotext`, or WebFetch) except where the row says otherwise.

## 1. Executive summary

- **No single source covers the domain; synthesis is required, and the seams are clean.** Three bodies of work each
  own a different part and do not overlap much. The practitioner essays (Tatham, Raymond, PostgreSQL) own the
  *epistemic* rules — facts before theory, symptoms before diagnosis, what a claim of "this is a bug" costs. The
  project guides own the *slot list and the pre-conditions* — which fields, which version, which project. The
  empirical work owns *which slots are actually load-bearing* and *which defects a machine can see*. Nothing in
  categories 1–5 addresses the colleague message at all, and only obliquely addresses the feature request.
- **Strongest category: 2 (project contribution guides and issue forms), closely followed by 5 (empirical
  research).** Category 2 is strong because the artifacts are machine-readable, current, and enforced: a required
  field is a rule with a date and a commit. Category 5 supplies the only *measured* claims in the whole domain, and
  several of them contradict what the essays assert.
- **Weakest and most polluted: category 3 (tracker documentation and standards).** Atlassian/Jira "how to write a
  bug report" material is content marketing on top of Spolsky's three items, with no rationale and no source.
  ISO/IEC/IEEE 29119-3's Incident Report outline is dominated by document control and transfers almost nothing.
  ISTQB restates 29119-3. Bugzilla's own `filing.html` is UI instructions. Only the GitHub issue-forms schema doc
  earns its place, and as an *oracle spec*, not as writing advice.
- **Does an agent skill for this already exist?** Not searched here — that is category 7, arm B. I found no
  agent-authored-report policy inside categories 1–5 except one, and it is a required checkbox rather than a skill:
  Homebrew's bug form (commit `fa00594af`, 2026-07-29, "Enforce responsible AI contribution policy") makes the
  reporter affirm *"I did not use AI/LLM to create this issue, or I disclosed the tool and model used; I will answer
  maintainer questions myself without AI/LLM."*
- **The reader table holds, with one correction and one addition.** The correction: R4 (the searcher) is served
  almost entirely by *verbatim error text and version strings*, not by prose, and no source in categories 1–5 states
  a rule for R4 beyond "quote the message exactly, including the numbers" (Tatham). The addition Pass 2 should
  consider is not the backlog owner but a **sixth reader absent from the table: the reporter's future self at the
  moment the maintainer asks a follow-up question.** curl, Angular and Vite all close reports for non-response, on
  stated clocks. On the backlog owner, my categories are suggestive but not decisive: Gradle's *feature* form
  inverts the bug form's order (Expected Behavior required and first, Current Behavior optional) and makes Context
  required with "What are you trying to accomplish? What other alternatives have you considered?" — questions R2 as
  defined does not ask. That is one project, not a finding. Defer to arm B.
- **Well served by what I found:** Q1 (order), Q2 (load-bearing fields), Q3 (the reproducer), Q4 (attribution across
  a stack), Q5 (duplicates and currency), Q6 (expected behavior), Q10 (solution instead of problem), Q11
  (detection). **Under-served:** Q7 (workarounds) — I found no source in categories 1–5 that states a rule, only
  commercial templates with a "Workaround (fine if N/A)" box; Q8 and Q9 are arm B's; Q12 is thin here by design.
- **Where Pass 2 should concentrate:** the four sources that convert into mechanical checks (Chaparro's discourse
  patterns, LLVM's isolation procedure, the Gradle CI-run reproducer, Stack Overflow's "double-check that your
  example reproduces"), and the three measured results that *contradict* received practice (duplicates are cheap;
  template conformance predicts nothing; expected behavior is ranked low by developers yet is the field most often
  missing).

## 2. Candidate inventory

| # | Name | URL | Cat | Author / org | Questions | Readers | Best use | Evidence | Maintenance | Why worth considering |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | How to Report Bugs Effectively | https://www.chiark.greenend.org.uk/~sgtatham/bugs.html | 1 | Simon Tatham (1999) | 1, 2, 3, 10, 11 | R1, R3, R4 | The aim-of-the-report frame; fact/speculation separation; verbatim error text | Asserted | Stable canonical, unchanged | States the goal ("let the programmer see the program fail") from which the ordering rule can be derived rather than asserted |
| 2 | How To Ask Questions The Smart Way, rev 3.10 (21 May 2014) | http://www.catb.org/~esr/faqs/smart-questions.html | 1 | Eric S. Raymond, Rick Moen | 1, 4, 7, 10 | R1, R5 | "Symptoms not guesses", chronological order, "describe the goal, not the step", the bar for claiming a bug | Asserted, with paired bad/good examples | Frozen since 2014 | The only category-1 source with before/after examples of the exact failure the baseline names; HTTPS cert is broken, fetched over HTTP |
| 3 | How to create a Minimal, Reproducible Example | https://stackoverflow.com/help/minimal-reproducible-example | 1 | Stack Overflow | 3, 6, 11 | R1, R3 | Minimal/Complete/Reproducible triad; two reduction procedures; the "test it again" rule | Asserted | Live (page rev 2026.9.3) | Contains the single best anti-gaming rule found anywhere: re-run the reduced example before posting it |
| 4 | Bug Writing Guidelines | https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html | 1, 2 | Mozilla | 1, 2, 5, 6 | R1, R4 | Summary shape; steps/expected/actual; one bug per report; clean-profile and current-build pre-checks | Asserted | Live | The canonical statement of "separate facts (observations) from speculations" as a *form* rule, not a tone rule |
| 5 | PostgreSQL 18 §5 Bug Reporting Guidelines | https://www.postgresql.org/docs/current/bug-reporting.html | 2 | PostgreSQL Global Development Group | 1, 3, 5, 6, 10 | R1, R2 | The strongest primary statement of "state all the facts and only facts"; self-contained reproducer; version currency | Asserted | Versioned with each release (read at 18.6) | Simultaneously the strongest support for baseline B1/B2 and a direct contradiction of the "always minimize" rule |
| 6 | curl `docs/BUGS.md` (commit `cc85cdf3c`, 2026-03-03) | https://github.com/curl/curl/blob/master/docs/BUGS.md | 2 | Daniel Stenberg et al. | 3, 4, 5, 11 | R1, R2 | Layer attribution (bindings → their project; "convert your program over to plain C"); old-version policy; the needs-info clock | Asserted | Actively maintained | Says explicitly what happens to a misfiled or stale report, with the inactivity window ("not shorter than two weeks") |
| 7 | gradle/gradle bug, regression and feature forms (bug form commit `326b193d1`, 2024-09-09) | https://github.com/gradle/gradle/tree/master/.github/ISSUE_TEMPLATE | 2 | Gradle | 1, 3, 4, 5, 8 | R1, R2 | The baseline's own reference form; genre-dependent field order; explicit off-ramps to other trackers | Asserted | Live | The feature form *inverts* the bug form's order, which is direct evidence that the ordering rule is genre-scoped |
| 8 | gradle-issue-reproducer template + `run-reproducer.yml` | https://github.com/gradle/gradle-issue-reproducer | 4 | Gradle | 3, 11 | R1, R3 | A reproducer whose CI run is the evidence: "Verify that the reproducer exhibits the problem on the GitHub Action page" | Asserted (a working oracle) | Live | Turns "the reproducer was asserted but never run" from a judgment call into a URL |
| 9 | junit-team/junit-framework `bug_report.md`, `feature_request.md` (commit `032f09e15`, 2025-05-13) | https://github.com/junit-team/junit-framework/tree/main/.github/ISSUE_TEMPLATE | 2 | JUnit team | 3, 8, 10 | R1, R2 | The other project in the recorded failure; the feature form states the XY rule as policy | Asserted | Live | "Start by telling us what problem you're trying to solve. Often a solution already exists!" is Raymond's rule as a required prompt |
| 10 | nodejs/node `1-bug-report.yml` (commit `d5dc540f1`, 2024-08-23) | https://github.com/nodejs/node/blob/main/.github/ISSUE_TEMPLATE/1-bug-report.yml | 2 | Node.js | 3, 5, 6 | R1, R2 | Required field: *"What is the expected behavior? **Why is that the expected behavior?**"*; supported-version check; reproducer form constraints | Asserted | Live | The only form found that requires the *justification* of the expectation, not just the expectation |
| 11 | Homebrew/homebrew-core `bug.yml` (commit `fa00594af`, 2026-07-29) + Responsible AI Usage | https://github.com/Homebrew/homebrew-core/blob/master/.github/ISSUE_TEMPLATE/bug.yml , https://docs.brew.sh/Responsible-AI-Usage | 2, 4, 7 | Homebrew | 5, 10, 12 | R1 | Required pre-condition checkboxes (updated, doctor clean, searched for duplicates) and a required AI-disclosure checkbox | Asserted (enforced) | Live, changed 2026 | The only source in these categories that treats the reporter as a party who may be gaming the form, and the only 2026 AI-disclosure requirement found |
| 12 | angular/angular `CONTRIBUTING.md` (commit `4739bde9f`, 2026-04-08) | https://github.com/angular/angular/blob/main/CONTRIBUTING.md | 2 | Angular team | 3 | R1, R3 | The rationale for demanding a reduction, stated as four reasons, plus the close-for-no-repro policy | Asserted | Live | "Often, developers find coding problems themselves while preparing a minimal reproduction" — reduction as a self-check before filing |
| 13 | renovatebot `docs/development/minimal-reproductions.md` (commit `3c49e8527`, 2024-06-16) | https://github.com/renovatebot/renovate/blob/main/docs/development/minimal-reproductions.md | 2, 4 | Renovate maintainers | 3, 4 | R1, R3 | Two named reduction methods (build up from a template vs fork and delete); what the reproduction proves | Asserted | Live | States the attribution purpose explicitly: "confirm the problem is with Renovate, and *not* with your environment, or your configuration settings" |
| 14 | LLVM, How to submit an LLVM bug report | https://llvm.org/docs/HowToSubmitABug.html | 2, 4 | LLVM project | 3, 4, 11 | R1, R2 | A deterministic procedure for deciding which layer owns a defect (frontend / middle-end / backend), by flags | Asserted (mechanically executable) | Live | The only source found that turns "establish which project owns the defect" into commands rather than an exhortation |
| 15 | Apache Infra bug-writing guide + Apache Arrow bug reports page | https://infra.apache.org/bug-writing-guide.html , https://arrow.apache.org/docs/dev/developers/bug_reports.html | 2 | Apache Software Foundation | 1, 4, 5 | R1, R2 | "One bug per report"; component prefixes; "as few non-Arrow dependencies as possible"; avoid speculation presented as fact | Asserted | Live (Infra page undated) | Component tagging is attribution made cheap: the reporter names the layer in the title |
| 16 | Bettenburg et al. — *What Makes a Good Bug Report?* (2007 TR) and *Duplicate Bug Reports Considered Harmful … Really?* (ICSM 2008) | https://www.st.cs.uni-saarland.de/publications/files/bettenburg-tr-2007.pdf , https://people.csail.mit.edu/hunkim/images/b/b2/Papers_Bettenburg2008icsm.pdf | 5 | Saarland Univ. / Univ. of Calgary / MIT | 1, 2, 3, 5, 6 | R1, R2 | Field importance and problem-delay rankings; duplicate prevalence and cost | **Studied** (156 developers, Apache/Eclipse/Mozilla; 1,248 quality votes on 289 reports; duplicate rates ~30% Mozilla, ~20% Eclipse) | 2007–2008; extended to TSE 2010 | Measures what the essays assert, and the numbers do not line up with them; the duplicate paper contradicts the near-universal "search first or you waste our time" framing |
| 17 | Chaparro, Lu, Zampetti, Moreno, Di Penta, Marcus, Bavota, Ng — *Detecting Missing Information in Bug Descriptions* | https://ojcchar.github.io/files/8-fse17.pdf | 5, 4 | ESEC/FSE 2017 | 2, 6, 11 | R1 | Measured presence of OB/EB/S2R; 154 discourse patterns; a detector for missing EB and S2R | **Studied** (≈3,000 reports manually analysed) | 2017, tool line continues (Euler, FSE 2019) | The single best source for "can a reviewer tell from the text alone" — it answers with precision/recall numbers |
| 18 | Chilana, Ko, Wobbrock — *Understanding Expressions of Unwanted Behaviors in Open Bug Reporting* | https://faculty.washington.edu/ajko/papers/Chilana2010ExpectationViolation.pdf | 5 | VL/HCC 2010 | 1, 6, 10 | R2 | Seven sources of violated expectation, and which ones predict FIXED vs INVALID | **Studied** (1,000 Mozilla reports) | 2010 | Turns "state the expected behavior" into "state *whose* expectation, and ground it in the project's own commitments" |
| 19 | Rahman, Khomh, Castelluccio — *Works for Me! Cannot Reproduce* | https://web.cs.dal.ca/~masud/papers/masud-EMSE2022.pdf | 5 | EMSE 2022 (incl. Mozilla) | 3, 4, 5, 11 | R1, R2 | 11 factors behind non-reproducibility, incl. false-positive (already fixed), missing information, ambiguous specification, third-party defects | **Studied** (576 non-reproducible reports; 13 developers) | 2022 | Names "already fixed in a recent release" and "third-party defect" as *measured* causes of wasted triage, which is the recorded failure |
| 20 | Sülün / Tüzün et al. — *An Empirical Analysis of Issue Templates Usage in Large-Scale Projects on GitHub* (thesis version read in full) | https://repository.bilkent.edu.tr/bitstreams/6f3affd5-571e-42e0-a6c2-952cf35c1bf2/download | 5, 4 | Bilkent Univ. / TOSEM 2024 | 2, 11 | R1 | Effect of templates and of *conformance* on time-to-resolution, reopens, comments | **Studied** (350 templates, 100 projects, 1,916,057 issues) | 2024 | Measures the oracle itself: having a template helps; a given report's conformance to it does **not** (p = 1.00, d = 0.03) |

Not in the inventory because I could not obtain them in primary form: Zeller, *Why Programs Fail* §2.2 "Reporting
Problems" and *The Debugging Book* reduction chapter (the chapter URL I tried returned 404; the book is paywalled),
and Agans, *Debugging* (print only). Located but not read — treat no claim about them as verified.

## 3. Promising shortlist for Pass 2

**1. PostgreSQL §5 Bug Reporting Guidelines.** The most quotable statement of the baseline's B1/B2 anywhere: *"state
all the facts and only facts. Do not speculate what you think went wrong … or which part of the program has a fault.
If you are not familiar with the implementation you would probably guess wrong."* Crucially it does not ban analysis
— it demotes it: *"educated explanations are a great supplement to but no substitute for facts."* That is a
compact rule an agent can apply alone: analysis is allowed, is never the opening, and is never the only content.
Serves R1 and R2. It also supplies the *expected-behavior* rule in operational form: writing "this is not what I
expected" is a defect, because the reader may scan the output and think it looks fine.

**2. Chaparro et al., *Detecting Missing Information in Bug Descriptions* (FSE 2017).** Measured: 93.5% of reports
contain observed behavior, 51.4% steps to reproduce, and only **35.2%** expected behavior. Their detector finds
missing EB at 85.9% precision / 93.2% recall and missing S2R at 69.2% / 83%, using 154 recurring discourse patterns.
For the skill this converts twice over: the patterns are a checklist the agent can run over its own draft ("does any
sentence in this text realise an EB pattern?"), and the asymmetry — EB is the field reporters most often omit while
OB is nearly always present — tells the skill which slot to defend hardest. Serves R1 and R3.

**3. Chilana, Ko & Wobbrock, *Understanding Expressions of Unwanted Behaviors* (VL/HCC 2010).** Classified 1,000
Mozilla reports by *which* expectation the reporter said was violated: reporter's personal expectation (n=337, the
largest group), runtime logic (195), specification (177), community expectation (85), genre convention i.e. "a
competing product does it this way" (71), prior behavior (69), standards (41). Reports grounded in specification,
runtime logic or community expectation were more likely to end FIXED; reports grounded in personal expectation or
genre convention achieved "little success", and standards, genre conventions and prior behavior were more likely to
be closed INVALID. That is a rule with a detection: read the expected-behavior block and name its source; if the
source is "what I wanted" or "how tool X does it", the block is not yet usable. Serves R2 directly.

**4. LLVM, *How to submit an LLVM bug report*.** The only source here that answers baseline B7 with a procedure
rather than an exhortation. Compile with `-emit-llvm -Xclang -disable-llvm-passes`: still crashes → the front end
owns it. `-emit-llvm` alone: crashes → the optimizer. Neither → the code generator. It generalises: "find the flag,
layer boundary, or interface at which you can re-run the same failure with one layer removed, and report the
innermost layer that still fails." curl states the same shape ("convert your program over to plain C"), PostgreSQL
("try to isolate the offending queries. We will probably not set up a web server"), Arrow ("as few non-Arrow
dependencies as possible"), Renovate its purpose. Four projects converging on one procedure is the strongest signal
in this pass.

**5. gradle-issue-reproducer plus the Gradle bug form.** The reproducer is a repository from a template that carries
a GitHub Action; the instructions end with *"Verify that the reproducer exhibits the problem on the GitHub Action
page"* and *"Link your reproducer to the issue."* This is the answer to "the agent asserts a reproducer it never
ran": the evidence is a run URL that the triager can open. Paired with the Gradle bug form (Current Behavior →
Expected Behavior → Context → Self-contained Reproducer Project → Gradle version) it gives the skill both a slot
order and an oracle for the slot that matters most. Serves R1, R3.

**6. Stack Overflow, *How to create a Minimal, Reproducible Example*.** Three named properties, two named reduction
procedures (restart from scratch and add until it fails; or divide-and-conquer by deleting until it stops failing,
then restore the last deletion), and the anti-gaming rule stated outright: *"Double-check that your example
reproduces the problem! If you inadvertently fixed the problem while composing the example but didn't test it again,
you'd want to know that before asking someone else to help."* Also *"tell other readers what the expected behavior
should be"* rather than "it doesn't work". Converts to compact rules with no author present; the reduction
procedures are exactly what an agent in a checkout can execute.

**7. Bettenburg et al., *What Makes a Good Bug Report?* (2007 TR / FSE 2008 / TSE 2010).** The only ranking of report
contents by measured developer importance: steps to reproduce 78%, stack traces 57%, test cases 53%, observed
behavior 32%, screenshots 24%, expected behavior 19%, code examples 17%, version 12%, summary 10%. And the problems
that cost most delay: errors in steps to reproduce 82%, incomplete information 77%, wrong observed behavior 48%,
wrong hardware 44%, bad stack traces 40%, bad test cases 35%, over-long text 26%, wrong version 25%, wrong expected
behavior 22%, duplicates 10%. A developer quote makes the shape of the finding: *"The biggest causes of delay are not
wrong information, but absent information."* Note the era and tracker (Bugzilla/JIRA free-text, three projects,
2007) before transferring any figure.

**8. Homebrew's `bug.yml` and Responsible AI Usage.** A required pre-condition block the reporter must tick before
the form will submit: `brew doctor` clean and the bug still reproduces; `brew update` run and it still reproduces;
all doctor warnings resolved; the tracker searched and no duplicate found; not a source build; and AI use either
absent or disclosed with tool and model, with a commitment to answer maintainer questions personally. This is the
only artifact in categories 1–5 written by people who assume the reporter may be optimising for the check, and the
introductory text says what happens otherwise: *"we will close your issue without comment if you do not fill out the
issue checklist"*. Converts directly into a pre-flight block for the skill.

## 4. Obvious rejects

- **Atlassian / Jira "how to write a bug report" pages and the Community template articles** — content marketing
  around Spolsky's three items; no rationale, no source, no examples; several are vendor app listings.
- **ISO/IEC/IEEE 29119-3:2013 Incident Report (§7.12, Annex A.2.15)** — the recognition-state outline is dominated by
  document control (unique document identifier, issuing organization, approval authority, change history); the one
  transferable rule ("one incident report for each unique incident") is already in Mozilla's guidelines with a
  rationale attached.
- **ISTQB Foundation §5.5/5.6 defect-management material and its derivative sites** — certification cram; restates
  29119-3 field lists; the exclusion on courseware applies.
- **Bugzilla `using/filing.html`** — UI instructions ("click the New link", "click Submit Bug"); the content rules
  live in Mozilla's Bug Writing Guidelines instead.
- **Mirrors and restatements of Tatham** (stevengould.org, squarepenguin.co.uk, parkermoore.de, the DEV/Medium
  summaries) — cite the original.
- **Commercial bug-report-template listicles** (featurebase, usersnap, crosscheck, jam.dev, teamgantt) — the only
  place a "Workaround" field appears, but with no rationale and no source; not usable evidence for Q7.
- **Generic stale-bot debate posts** (drewdevault.com and the HN thread) — about maintainer process, not about what
  the report must carry.
- **Duplicate-detection research tooling** (Advaita, deep-learning DBRD papers) — the verdict is advisory to
  triagers, tells the reporter nothing checkable at writing time, and the harm premise it optimises is the one
  Bettenburg's ICSM 2008 paper undercuts.

## 5. Gaps and questions for Pass 2

**Detectable from the report text alone.** Missing expected behavior and missing steps to reproduce (Chaparro:
measured, with a detector). "It doesn't work" / "this is not what I expected" as the whole of the expected-behavior
block (PostgreSQL, Stack Overflow). Diagnosis stated as fact rather than labelled as a guess (Tatham, Raymond,
PostgreSQL all state the rule as a *labelling* requirement, which is what a text check can verify). The source of the
violated expectation — personal vs specification vs community (Chilana et al.). Two independent symptoms merged into
one report (Mozilla, Arrow, 29119-3). Missing version string. A summary that names a solution instead of a symptom
(Mozilla). Whether the report leads with a mechanism — the recorded failure — is detectable by position: does the
first paragraph mention any identifier internal to the target project?

**Needs the reproducer actually run.** Whether the reduced example still fails (Stack Overflow's explicit warning;
Gradle's CI-run reproducer makes this observable to a third party). Whether the failure survives a clean
profile/environment (Mozilla, Homebrew's `brew doctor` gate). Whether any form proposed as the *expected* one works —
baseline B4 — has no source at all in categories 1–5; nobody writes about checking your own proposal. Flag this as an
unsourced rule.

**Needs a tool or a lookup.** Version against the project's supported list (Node: "verify that you are reproducing
the issue in a currently-supported version"; PostgreSQL: "if your version is older than 18.6 we will almost certainly
tell you to upgrade"; curl: an entire section on old versions). Whether the defect is already fixed — Rahman et al.
measure this as a named cause (F2, false-positive bug, "already fixed in the recent releases") of non-reproducible
reports, which is precisely the recorded failure. Layer ownership (LLVM's flags; curl's plain-C conversion;
PostgreSQL's query isolation). Duplicate search (every project asks; see the conflict below). Identifiers that
resolve — no source found; this stays an agent-specific rule.

**Stays human judgment.** Whether a stated expectation is *right* for the project's design (Rahman's F5: reporters
"might characterize a legitimate functionality as a bug"). Whether the request is worth doing. Severity and priority.

**Conflicts between sources, and they are real.**

1. *Order of expected vs actual.* Gradle, Mozilla, Kubernetes and Homebrew put current/actual first. Rust puts
   expected first ("I expected to see this happen … Instead, this happened"). Node puts expected first, with a
   required justification. The baseline's B1 (symptom first) survives contact only in the weaker form "the
   user-facing symptom precedes the mechanism"; it does **not** survive as "actual precedes expected". Pass 2 must
   separate the two claims.
2. *How hard to reduce.* Stack Overflow, Angular, Renovate, LLVM and Arrow all demand reduction. PostgreSQL says the
   opposite about the reporter's time: *"Do not spend all your time to figure out which changes in the input make the
   problem go away. This will probably not help solving it."* Node forbids the reproducer forms Gradle requires
   ("no ZIP archive, no GitHub repository" vs "as a GitHub repository or an attached archive"). The reproducer rule
   is therefore project-scoped, not universal — which itself is a rule the skill can state.
3. *Duplicates.* Every project requires a search; Bettenburg et al. (ICSM 2008) measured that only 10% of developers
   named duplicates as a delay cause, quote developers saying duplicates "often add useful information", and cite
   ~30% (Mozilla) / ~20% (Eclipse) duplicate rates as a fact of life. Received practice and measurement disagree, and
   the agent's cost model should follow the measurement while its compliance follows the project.
4. *Regression framing.* Gradle and Rust ship dedicated regression forms that make "the version it used to work on"
   required. Chilana et al. found reports grounded in *prior behavior* more likely to be closed INVALID. Worth
   probing in Pass 2 rather than resolving here.

**A report as something its own author may game.** Only Homebrew treats the reporter as a possibly-adversarial party
(required affirmations, AI disclosure, a stated threat to block repeat offenders). Stack Overflow's "double-check
that your example reproduces the problem" and Gradle's CI-run reproducer are the two checks that survive a motivated
author, because both produce evidence outside the report's prose. The most important negative result of this pass is
about the obvious oracle: the Bilkent/TOSEM study of 1.9 million issues found that whether a *project* has a template
predicts faster resolution (p = 0.00, Cohen's d = 0.59) and that YAML issue forms do better still, but that a given
issue's **conformance** to the template — the ratio of template components with a non-empty body that is not "No
response" or "N/A" — has no significant effect on time to resolution, reopens, or comments (p = 1.00, d = 0.03).
Filling every box is exactly the check an author optimising for appearance will pass, and it is measurably worth
nothing. Baseline rule B8 ("fill the target project's template fields by name") should be kept for a different reason
than outcome — it makes the text droppable into the form and readable by R1 — and Pass 2 should say so explicitly.

**Least-served genre.** By a wide margin, the colleague message. Categories 1–5 contain nothing about it: Raymond's
essay is about strangers in a public forum, every project guide is about a tracker, and no empirical study here
examines chat. The feature request is second — the only content rules I found are JUnit's "start by telling us what
problem you're trying to solve" and Gradle's inverted feature form, both single projects. Both gaps fall to arm B;
if arm B finds nothing either, those two genres will be derived, not sourced.

**Unsourced after this pass.** Baseline B3 (expected behavior in observable values rather than positional artifacts),
B4 (check that the proposed form works), and B6 (a workaround must not become the frame) have no support in
categories 1–5 — nothing found, not "found and weak". B5 (one expectation per independent symptom) is supported only
indirectly, through the widely stated "one bug per report" rule. Pass 2 should either source these elsewhere or mark
them as house rules.
