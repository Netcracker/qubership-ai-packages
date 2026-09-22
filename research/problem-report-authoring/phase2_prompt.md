# Pass 2 — rule brief: turning the Pass 1 shortlist into rules for a problem-report skill

## Research title

Evaluate the Pass 1 shortlist and extract applicable rules for a skill that drafts and reviews problem reports — bug
reports filed in other people's projects, short problem messages sent to a colleague, and feature or change requests.

## Goal

Pass 1 ran in two arms and established four things. First, no single source covers the domain: practitioner essays own
the epistemic rules (facts before theory), project contribution guides own the slot lists and the pre-conditions,
empirical work owns which slots are load-bearing, and one requirements-engineering framework (QUS/AQUSA) is the only
source that pairs each rule with a detector. Second, the maintainer's ordering rule survives only in its weaker form —
the user-facing symptom precedes the mechanism — while "actual behavior precedes expected behavior" does not survive
at all: it is scoped by genre and by project, and the same project (`gradle/gradle`) orders its bug form and its
feature form oppositely. Third, the obvious oracle fails: across 1.9 million GitHub issues, a *project* having a
template predicts faster resolution, but an individual issue's *conformance* to that template predicts nothing.
Fourth, three of the maintainer's rules (expected behavior stated in observable values; checking that a proposed
expected form actually works; a workaround not becoming the frame) have no source in either arm.

Pass 2 does not repeat that survey. Its job is to turn the shortlist into rules an agent can apply, and to settle the
questions Pass 1 left open.

The unit of the deliverable is not a source summary; it is a rule, stated once, with a rationale, a source, the reader
it serves, the situation it applies to, and the way a reviewer detects a violation of it.

## Target domain

The consumer is a coding agent (Claude Opus or Sonnet) that has just finished a session — it reproduced something,
read code across one or more projects, and formed a theory — and is now asked to write the problem up. Three facts
about that consumer change what counts as a usable rule.

**It works without the author.** When it reviews a draft, it holds the draft, the repository it is in, and whatever it
can run. It has nobody to ask what the reporter meant. A rule that depends on knowing the intent behind the text
cannot be applied, however sound the rule is.

**It produced the thing it is now judging, and it is rewarded when the thing passes.** This is not hypothetical here:
the recorded failure includes an agent asserting an expected form it had never executed, and stating a confident cause
for a project that had already shipped the fix. Every rule must therefore say what a reviewer checks, so that
satisfying the letter of the rule is worth something. Where the only available check is the text's own claim, say so
and mark the rule weak.

**Some defects have an oracle.** Every rule lands in exactly one bucket, and the report says which:

1. applied while writing or reviewing, from the report text and the repository alone;
2. violation needs something run — say precisely which run (the reproducer, the reduced example, the proposed
   expected form, the failure on a clean environment, the failure on the currently supported version);
3. reported by a tool or a lookup — say what the verdict does and does not establish (a tracker search, a supported
   version matrix, an identifier that resolves, a CI run URL, a template's required fields);
4. a human judgment the agent may raise but not decide.

The skill must stay small and must work on Sonnet as well as Opus. So mark every rule **core** (belongs in a short
SKILL.md that is always read) or **reference** (belongs in a reference file the trigger names, opened only in the
situation that needs it). A skill body of roughly 200 to 250 lines is the target; the pass should propose the split,
not assume everything fits.

## Readers

Fixed. Pass 1 ruled that the backlog owner does not need a row: its questions are asked by R2 in a request mode. Every
rule names the reader whose need it exists for, listed first.

| Reader | Situation | Holds |
| --- | --- | --- |
| **R1 Triager on a project the reporter does not maintain** | Working down a queue of newly filed issues, about a minute per item | The report text and the project's templates, labels, and supported-version policy. Knows nothing about the reporter's code |
| **R2 Maintainer deciding whether to act** | Has accepted the report as real and decides whether, and in which direction, to change the project. In *request mode* also asks who is blocked, what it costs, and how anyone will know it worked | The whole report plus the project's design constraints and compatibility obligations |
| **R3 Whoever picks the work up months later** | Often the reporter, often a first-time contributor, from a fresh checkout | The report and the current code. Nothing of the original session survives |
| **R4 A user who found the report by searching** | For a defect: hit the same error and wants to know if it is theirs. For a request: deciding whether an existing request already covers their case and what to add beyond a "+1" | The same error string and a version, or their own use case |
| **R5 A colleague the reporter messaged** | Interrupted mid-task; shares the codebase and the jargon, not the last hour | A few lines of chat. Decides whether this is theirs and what is being asked |

## What Pass 1 settled, and this pass does not reopen

- **Rule sources versus evidence sources.** Project contribution guides and issue forms (Pass 1 category 2) and
  practitioner essays (category 1) are where the rules come from. Empirical work (category 5) supplies the evidence
  labels and the base rates; it rarely states a rule. Tracker standards (category 3 — Atlassian, ISTQB,
  ISO/IEC/IEEE 29119-3, Bugzilla UI docs) are settled as rejects: document control and UI steps, no transferable
  content rule that Mozilla does not already state with a rationale.
- **Settled rejects, not to be revisited.** Commercial bug-report-template listicles; "awesome-*" skill collections;
  Given-When-Then and Definition-of-Ready advocacy; consultancy problem-statement frames (SCQA and relatives);
  secondary news coverage of the curl, Ghostty and kernel AI policies; restatements of Tatham or Raymond; duplicate-
  detection research tooling (its verdict is advisory to triagers and tells a reporter nothing at writing time).
- **Readers.** Five rows, as above. No sixth row.
- **Out of scope, and to whom it belongs.** Wording, tone, sentence craft, hedging and the tells of machine prose →
  `english-developer-style`. Commit messages, PR titles and descriptions, changelog entries → `change-description-
  authoring`. Documentation and troubleshooting pages → `docs-page-authoring`. Recording a decision → `adr-authoring`.
  Writing the regression test for a confirmed defect → `test-authoring`. Triage from the maintainer's side, labelling,
  and answering other people's issues → the triage skills. If a source's only contribution is wording, it is a reject.
- **The ordering claim is two claims.** "Symptom before mechanism" and "actual before expected" must be treated
  separately throughout; Pass 1 found the first supported and the second contradicted.

## Shortlisted candidates from Pass 1

Group members count as one candidate.

1. **PostgreSQL, Bug Reporting Guidelines (Appendix §5).** *"State all the facts and only facts. Do not speculate what
   you think went wrong … or which part of the program has a fault"*; and *"educated explanations are a great
   supplement to but no substitute for facts."* Also its rule that writing "this is not what I expected" is itself a
   defect, because the reader may scan the output and think it looks fine. Also its dissent on reduction effort.
2. **Chaparro et al., *Detecting Missing Information in Bug Descriptions* (ESEC/FSE 2017).** Measured presence of
   observed behavior, steps to reproduce and expected behavior in bug descriptions, plus a detector built on recurring
   discourse patterns. The patterns are usable as a self-check over a draft.
3. **Chilana, Ko & Wobbrock, *Understanding Expressions of Unwanted Behaviors in Open Bug Reporting* (VL/HCC 2010).**
   Classified Mozilla reports by *which* expectation the reporter claimed was violated (personal expectation, runtime
   logic, specification, community expectation, genre convention, prior behavior, standards) and related the grounding
   to the FIXED or INVALID outcome.
4. **The layer-attribution procedure, four projects converging.** LLVM's flag-by-flag isolation (`-emit-llvm -Xclang
   -disable-llvm-passes` still crashes → front end; `-emit-llvm` alone → optimizer; neither → code generator); curl's
   "convert your program over to plain C"; PostgreSQL's "isolate the offending queries"; Apache Arrow's "as few
   non-Arrow dependencies as possible". Group members count as one candidate.
5. **`gradle-issue-reproducer` plus the Gradle bug form.** A reproducer repository from a template carrying a GitHub
   Action, with the instruction to verify the failure on the Action page and link the run to the issue: an oracle that
   produces evidence outside the report's prose. Paired with the bug form's slot order.
6. **Stack Overflow, *How to create a Minimal, Reproducible Example*.** Three named properties, two named reduction
   procedures, the instruction to state expected behavior rather than "it doesn't work", and the anti-gaming line:
   *"Double-check that your example reproduces the problem!"*
7. **Bettenburg et al., *What Makes a Good Bug Report?* (2007 technical report / FSE 2008 / TSE 2010), together with
   the ICSM 2008 duplicate paper.** The only measured ranking of report contents by developer-stated importance, the
   measured causes of delay, the finding that absent information costs more than wrong information, and the duplicate
   base rates. Group members count as one candidate.
8. **Homebrew `bug.yml` and its Responsible AI Usage policy.** Required pre-condition affirmations before the form
   submits (`brew doctor` clean and still reproduces, updated and still reproduces, tracker searched, not a source
   build), an AI-disclosure checkbox, and a stated consequence for not filling the checklist.
9. **QUS and AQUSA (Lucassen et al., 2016 and the *Requirements Engineering* journal version).** Thirteen quality
   criteria for a user story, each with a violating example and a repair, plus an automated detector. Its
   *problem-oriented*, *atomic* and *conceptually sound* criteria map onto the maintainer's rules. Decide whether the
   criteria survive being lifted off the `As a … I want … so that …` sentence form.
10. **The request-genre templates, five projects.** The Go 2 language-change template (what it costs, who it helps,
    has it been proposed before, before-and-after example code); the Kubernetes KEP template (**Non-Goals**, and Goals
    phrased as "How will we know that this has succeeded?"); PEP 1's prior-discussion requirement; the Rust RFC
    motivation-first order; Django's routing and its "is this in scope" question. Group members count as one
    candidate.
11. **The Gradle feature-request form set against the Gradle bug form.** Same project, same directory, opposite
    order: the bug form requires Current Behavior first; the feature form requires Expected Behavior first and makes
    Current Behavior optional, with a required Context field asking what the requester is trying to accomplish and
    which alternatives they considered.
12. **The CrowdRE'25 study of feature requests.** Measured defect rates in filed requests, how often maintainers ask a
    clarifying question versus close, what their clarifications are about, and the effect of mock-ups or code snippets
    on response speed and tone.
13. **The short-form cluster.** Raymond's *How To Ask Questions The Smart Way*, specifically "Describe the goal, not
    the step" and "Describe the symptoms, not your guesses", each with paired bad/good examples, and its escape hatch
    that a guess may be stated if it is *labelled* as a guess with what ruled it out; plus `nohello.net`,
    `dontasktoask.com`, and `xyproblem.info` (which returned HTTP 403 to Pass 1 — re-fetch it, and if it is still
    unreachable, say so rather than reconstructing it). Group members count as one candidate.
14. **The machine-author policy cluster.** Ghostty's `AI_POLICY.md` (disclose the tool; be able to explain the content
    without it); the Linux kernel's security-bugs page (a version range without which the report is not processed, a
    reproducer that is not a binary, and its AI clause with the stated reason); the OpenSSF guide for researchers
    (May 2026: disclose tool and extent, expect duplication, keep it short because machine reports run verbose,
    prefer a patch and a regression test over another report); Homebrew's AI-disclosure checkbox. Group members count
    as one candidate.
15. **The template-conformance null result** (the study of ~1.9 million GitHub issues): having a template predicts
    faster resolution, conformance of an individual issue to it does not.
16. **The prior art in agent skills.** `github/awesome-copilot`'s `skills/github-issues/SKILL.md` and the published
    `playwright-bug-reporter` skill ("never include a reproduction step you did not personally execute and observe
    during this session"; say a field's evidence is missing rather than guess). Evaluate what each already covers, so
    the new skill states only what they do not.
17. **Mozilla, Bug Writing Guidelines**, for one bug per report and for a summary that names the symptom rather than a
    solution; and **Rahman et al. on non-reproducible bug reports**, for the named causes that match the recorded
    failure (already fixed in a recent release; a legitimate feature characterized as a bug).

## Specific questions from Pass 1 to investigate

### Conflicts Pass 1 identified as live

Decide each, and say why. A conflict returned undecided becomes a hedge in the skill.

1. **Order.** Gradle, Mozilla, Kubernetes and Homebrew put current/actual first; Rust and Node put expected first;
   Gradle's own feature form inverts its bug form; Rust RFC, KEP, PEP 1, Django and JUnit put motivation first for
   requests. Decide what the skill states, per genre, and how an agent resolves the case where the target project's
   required field order disagrees with the skill.
2. **How hard to reduce.** Stack Overflow, Angular, Renovate, LLVM and Arrow demand reduction; PostgreSQL says *"Do
   not spend all your time to figure out which changes in the input make the problem go away"*; Node forbids the
   reproducer forms Gradle requires (no archive, no repository — versus a repository or an attached archive). Decide
   what the skill says about how far to reduce and in what form to ship it, given that the answer is project-scoped.
3. **Duplicates.** Every project requires a search before filing; the measured evidence says duplicates are a minor
   cause of delay and that duplicate reports often add information. Decide what the agent does: the compliance
   obligation and the cost model point different ways.
4. **Regression framing.** Gradle and Rust ship dedicated regression forms that make the last working version
   required; Chilana et al. found reports grounded in *prior behavior* more likely to be closed INVALID. Decide
   whether "it used to work in X" is a strong or a weak grounding, and under what condition each.
5. **Sketch or no sketch.** CrowdRE'25 finds requests carrying mock-ups or code snippets get faster and more positive
   responses; QUS's *problem-oriented* criterion counts a solution hint as a defect. Decide what a request may carry
   and where it goes.
6. **Template conformance.** The 1.9M-issue null result undercuts the outcome-based justification for filling every
   field. The maintainer's rule stands anyway. State the rule with the justification the evidence supports, and say
   plainly what filling the fields does and does not buy.

### The gaps Pass 1 could not close

Four of the maintainer's rules are unsourced after both arms. Source them elsewhere, or mark them **derived** and
build the derivation from sourced criteria — do not quietly drop them and do not restate them as if sourced.

- **Expected behavior stated in values a reader can observe and act on, not in positional artifacts.** The concrete
  case: a report asking that a test-report entry carry `value = "x"` rather than `[1]`, on the grounds that an index
  identifies nothing to a reader and shifts when the source data changes.
- **Checking that a form proposed as the expected one actually works.** The concrete case: the agent proposed an
  index-based name partly because it would let a reader re-run a single case; re-running by index does not work in
  that tool, and nobody had tried it. The nearest sourced line found is the Playwright skill's rule about steps
  executed, which covers steps taken and not forms proposed.
- **A known workaround must not become the frame of the request** when the request is that the default should work.
  The concrete case: a request framed around an available configuration setting, which reads as "configuration is
  enough for me" while asking for the default to change. Nothing was found on this in either arm.
- **One expectation per independent symptom.** Supported only indirectly, through "one bug per report". The concrete
  case: two independent symptoms of one reporting defect merged into a single expected-behavior block.

Work through each concrete case by name and show what the rule, as you state it, would have produced.

### The highest-value question in this pass

**What must the expected-behavior block contain, and how does a reviewer detect an unusable one from the text alone?**
Send the budget here. Three lines of evidence converge on it: expected behavior is the field reporters most often omit
while observed behavior is nearly always present; the *grounding* of the expectation predicts whether the report ends
FIXED or INVALID; and three of the four unsourced maintainer rules are all about this one block. The skill's single
most valuable rule is likely to be a test for an expected-behavior block, stated so that an agent can apply it to its
own draft.

### Applicability

- Which rules are universal and which are scoped by genre (filed issue, colleague message, request)? Produce the
  matrix; it is this domain's per-ecosystem table.
- Which rules does a target project's own convention override, and how does the agent detect that it must yield —
  which files does it read, in which order (`.github/ISSUE_TEMPLATE/*`, `CONTRIBUTING.md`, `SECURITY.md`, an
  `AI_POLICY.md`, the supported-version statement)?
- What does each rule cost in false positives? Name the rules whose detection fires on a legitimate report, and say
  what the agent does then.
- Which rules survive an author optimizing for the check, and which are satisfiable in letter alone? For each of the
  second kind, name what is checked instead.

## Required output

Under **5000 words excluding tables**. Twelve sections, in this order, with these headings. Rules must not overlap: if
two rows say the same thing for two readers, merge them and name both readers.

1. **Executive summary.** Which candidates survive as rule contributors and which drop to supporting; which conflicts
   were settled and which stayed open; the bucket split with counts; the core/reference split with counts; what
   resists a writer who optimizes for the check.
2. **Deep candidate evaluation.** One row per candidate from the seventeen above: disposition, strongest
   contribution, main weakness, evidence label, maintenance status, whether it ships before/after examples,
   false-positive risk, portability across the three genres.
3. **Extracted rules**, 30 to 45 rows, columns: the rule as one imperative sentence; its rationale; the reader served;
   the source; the evidence label (studied / asserted / derived); the genre or situation it applies to; how a reviewer
   detects a violation without the author present; whether a writer can game it and what is checked instead; the
   repair; the bucket (1–4); core or reference.
4. **The genre matrix**: rule family against the three genres, each cell marked required, optional, or not applicable,
   with the source that decides the cell.
5. **The expected-behavior test**, worked against the concrete cases named above, including the `value = "x"` versus
   `[1]` case and the two-symptom case.
6. **The shapes that fail vacuously** — a report that satisfies every rule's letter and is still useless — each with
   its detection. Include at minimum: the fully-filled template with nothing in it; the expected block that says only
   "it should work"; the reproducer that was never run; the confident cause for a project that already fixed it; the
   request framed around its own workaround.
7. **Worked examples**, before and after, one per rule family, drawn from real reports where you can fetch them.
8. **Conflicts and how they were decided**, with the reason for each of the six above.
9. **The detectability matrix**: rule against bucket, with the source per cell, and the run named for every bucket-2
   rule.
10. **Baseline audit.** Rule by rule through the maintainer's eight rules (B1–B8, restated in the appendix below):
    survives / survives with a changed rationale / needs restating / contradicted. Then what the baseline misses
    entirely, in descending order of cost, with the recorded failure's own misses first.
11. **Evidence map and verification.** Every figure that will reach the skill or its research README, with its sample,
    its source, and a verdict of confirmed / corrected / unreachable after checking against the source text itself —
    not a summary, not an abstract, not a citation in another paper. Name every correction to Pass 1 as a correction.
    Verify at minimum: the observed/steps/expected presence rates and the detector's precision and recall; the
    developer-importance ranking and the delay-cause percentages; the duplicate base rates and the share of developers
    naming duplicates as a delay cause; the expectation-grounding group sizes and which groupings predicted FIXED or
    INVALID; the issue-count, p-values and effect sizes of the template-conformance study; the CrowdRE'25 counts; the
    number of QUS criteria and AQUSA's reported performance. An unreachable source is reported as unreachable.
12. **What the skill-writing session should be told.** The handover: what the skill states, in which order, at what
    length; the proposed core/reference split with the reference files named; what stays in the research directory and
    never reaches the skill; what stays a human judgment; and what the trigger must say so the skill is loaded at the
    right moment.

## Constraints

Label every rule **studied**, **asserted**, or **derived**. Do not promote asserted to studied, and do not label a
rule derived without showing the sourced criteria it was built from.

Every figure is checked against the source text rather than a summary. Corrections are carried and named. A source you
cannot reach is reported as unreachable, not confirmed from memory. Fetch the primary before citing it; where a paper
is paywalled, say so and say what you used instead.

## Appendix: the maintainer's baseline rules, for the audit in section 10

Stated from practice, sourced nowhere at the time they were written.

- **B1.** Start from the user-facing problem — "I do X, Y breaks" — before any statement about the target project's
  internals.
- **B2.** Causal analysis and links into the target project's source go at the end, if at all: the analysis may be
  wrong, and a wrong diagnosis stated first costs the reader more than a correct one saves.
- **B3.** Expected behavior is stated in values a reader can observe and act on, not in positional artifacts.
- **B4.** Any form proposed as the expected one must have been checked to actually work.
- **B5.** Independent symptoms get separate expected-behavior blocks rather than one merged block.
- **B6.** A known workaround must not become the frame of the request when the request is that the default should
  work.
- **B7.** Establish which project owns the defect before filing; a symptom observed through a stack is not evidence
  about any one layer.
- **B8.** Fill the target project's own template fields, by their names, so the text drops into the form unchanged.

The recorded failure that produced them: an agent drafted issues for `gradle/gradle` and `junit-team/junit-framework`
after a session in which it reproduced a test-reporting defect. It led with the mechanism (which internal class
produces the reporting name, which one writes the XML attribute), proposed filing against a project that had already
shipped the fix, asserted an expected form it had never executed, framed the request around an available configuration
setting, merged two independent symptoms, and used bare argument values where the reader needs parameter names. Six
rounds of correction followed. The accepted end states are public as
[gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
[junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041), and may be fetched as
examples; the rejected drafts are not public.
