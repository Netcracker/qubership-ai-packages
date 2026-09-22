# Pass 1B — discovery: the request genre, the colleague message, and machine-written reports

Arm B of a split discovery pass. Scope: search-scope categories 6 and 7 in full, plus the parts of categories 1–5 that
speak to a *request* rather than a defect report, to the short colleague message, or to reports produced by a machine.
Questions 8, 9 and 12 are the focus; 1, 6, 10 and 11 are covered only as they apply to a request. All fetches were made
on 2026-09-07 unless another date is given.

## Executive summary

- **No single source covers the domain; synthesis is required, and the seam is genre.** Nothing found writes rules for
  all three genres. The request genre is served by a cluster of enhancement-proposal templates (Rust RFC, KEP, Go
  proposal, PEP 1) plus one strong studied source on request text quality (QUS/AQUSA). The colleague message is served
  only by four short practitioner pages (ESR, xyproblem, nohello, dontasktoask) and one blog post (Evans). Machine-written
  reports are served by project policy and one industry guide, almost no measurement.
- **Strongest category: 6 (enhancement proposals and backlog practice).** It has both current primary templates and a
  studied, mechanically-checkable quality framework. **Weakest and most polluted: 7.** The short-form half is thin but
  clean; the agent-skill half is dominated by anonymous "awesome-*" lists and SEO listicles with no examples and no
  rationale. Backlog/agile material (also category 6) is the most polluted sub-area: certification courseware and
  consultancy blogs outnumber sourced work by a wide margin.
- **An agent skill for this already exists, twice, and neither is close to sufficient.** `github/awesome-copilot`
  ships `skills/github-issues/SKILL.md` (GitHub's own repo, fetched from `main`): it routes to bug/feature/task
  templates, caps titles at 72 characters, prefers issue *types* over labels, and carries one anti-fabrication line —
  "Ask for missing critical information rather than guessing." It has no ordering rule, no attribution rule, no
  currency check, and delegates duplicate handling to a reference file. A published `playwright-bug-reporter` skill
  (dev.to, author Aswani Kumar; the page's stated date of 2024-07-25 predates Claude Skills and should be treated as
  unverified) is stronger on exactly the axis the baseline cares about: "Never include a reproduction step you did not
  personally execute and observe during this session", and an instruction to say a field's evidence is missing rather
  than guess. Both are **asserted**, neither has before/after examples.
- **Reader table: the backlog owner does not need a row of its own.** See the ruling and its evidence below.
- **Well served:** Q8 (feature and change requests) — the best-served question in this arm; Q10 (solution instead of
  problem) — named as a rule by ESR, Tatham and QUS, and mechanically checkable in QUS; Q12 (machine-written reports) —
  well served on *policy*, thin on *measurement*. Partly served: Q5 (duplicates and currency, for requests), Q9 (short
  form), Q11 (detection). **Under-served:** Q1 (ordering) for the request genre — the one direct piece of evidence
  contradicts the baseline; Q6 (expected behavior) — only QUS's problem-oriented criterion touches it; Q7 (workarounds)
  — nothing found.
- **Pass 2 should concentrate on** (a) QUS's 13 criteria as the only mechanically-checkable rule set in this arm,
  (b) the Go/KEP/Gradle template *field orders*, which disagree with the baseline about the request genre, (c) the
  four short-form pages, which are the entire evidence base for R5, and (d) the Ghostty / Linux-kernel / OpenSSF
  triple, which is the only current, project-authored statement of what a machine-written report owes its reader.

## Candidate inventory

| # | Name | URL | Cat | Author / org | Questions | Readers | Best use | Evidence | Maintenance | Why worth considering |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Quality User Story framework + AQUSA (Lucassen et al., *Requirements Engineering* 21(3), 2016) | https://webspace.science.uu.nl/~dalpi001/papers/luca-dalp-werf-brin-16-rej.pdf | 6 | Lucassen, Dalpiaz, van der Werf, Brinkkemper (Utrecht) | 6, 8, 10, 11 | R2 | Rule set for request text with a tool that detects violations | Studied (13 criteria; tool evaluated on 1023 stories from 18 companies) | Canonical, tool archived | The only source in this arm whose rules come with a detector; "problem-oriented" is the baseline's B1 stated as a checkable criterion |
| 2 | Go proposal process + Go 2 language-change template | https://github.com/golang/proposal/blob/master/README.md and `go2-language-changes.md` | 6 | Go team | 1, 5, 8 | R2 | The question list a request must answer before it is worth filing | Asserted | Active | Asks cost ("Every language change has a cost"), "Who does this proposal help, and why?", and "Has this idea, or one like it, been proposed before?" |
| 3 | Kubernetes KEP template | https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md | 6 | Kubernetes SIG Architecture | 6, 8, 11 | R2, R3 | Slots for a large request: Motivation, Goals, Non-Goals, User Stories, Risks | Asserted | Active | "How will we know that this has succeeded?" is acceptance criteria stated as a required question; Non-Goals is a slot the baseline lacks |
| 4 | Kubernetes enhancement issue form | https://raw.githubusercontent.com/kubernetes/kubernetes/master/.github/ISSUE_TEMPLATE/enhancement.yaml | 2, 6 | Kubernetes | 4, 8 | R1, R2 | A two-field required minimum for a request | Asserted | Active (master) | Only two required fields — "What would you like to be added?" and "Why is this needed?" — plus a venue warning that requests filed as issues are unlikely to progress |
| 5 | Rust RFC template | https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md | 6 | Rust project | 1, 6, 8 | R2 | Slots: Motivation, Drawbacks, Rationale and alternatives, Prior art | Asserted | Active | "explain this problem in detail" precedes any design; Drawbacks is a required self-criticism slot |
| 6 | PEP 1 | https://peps.python.org/pep-0001/ | 6 | Python steering council | 5, 8 | R2 | What a proposal owes, and what to do *before* writing it | Asserted | Active | Requires vetting the idea on Discourse first, and a "Rejected Ideas" section — alternatives recorded, not just considered |
| 7 | Django, "Reporting bugs and requesting features" | https://docs.djangoproject.com/en/dev/internals/contributing/bugs-and-features/ | 2, 6 | Django | 4, 5, 8 | R1, R2 | Venue routing and the "why" requirement for a request | Asserted | Active (dev docs) | "Explain *why* you'd like the feature… a minimal use case"; requests go to the ideas project, not the tracker; asks the reporter to first judge whether the change belongs in core at all |
| 8 | Gradle contributor feature request form | https://github.com/gradle/gradle/blob/master/.github/ISSUE_TEMPLATE/20_contributor_feature_request.yml (blob `21c03981`) | 2, 6 | Gradle | 1, 6, 8 | R1 | Field order for a request in the baseline's own project | Asserted | Active (master) | **Expected Behavior is required and first; Current Behavior is optional and second; Context is required** — the inverse of the same project's bug form |
| 9 | JUnit feature request template | https://github.com/junit-team/junit-framework/blob/main/.github/ISSUE_TEMPLATE/feature_request.md (blob `6b6b2808`) | 2, 6 | JUnit team | 8, 10 | R1 | Minimal request template | Asserted | Active (main) | One instruction line only: "Start by telling us what problem you're trying to solve. Often a solution already exists!" — plus a Deliverables checklist |
| 10 | K C et al., "Towards Better Requirements from the Crowd" (CrowdRE'25) | https://arxiv.org/abs/2507.13553 | 5, 6 | UT San Antonio | 2, 5, 8, 9 | R2 | Measured base rates for what requests lack and why they are closed | Studied (50 annotated requests from 476; Signal, Mastodon) | 2025, single venue | 34/50 requests carried an NL defect; developers asked no clarifying question in 39/50; closure reasons counted (7 duplicate, 4 existing feature, 5 no reason); the 7 template-following requests needed least clarification |
| 11 | K C et al., "Demystifying Feature Requests" (2025) | https://arxiv.org/pdf/2507.13555 | 5, 6 | UT San Antonio | 8, 12 | R2 | Practitioner list of what is missing from requests | Studied (7 interviews) but small N | 2025 | Ranked missing items named by contributors: lack of details (5/7), missing information (5/7), unclear user intent and goals (2/7), misalignment with product mission (2/7) |
| 12 | Niu et al., "Feature Request Analysis and Processing: Tasks, Techniques, and Trends" | https://arxiv.org/html/2508.12436 | 5 | Nanjing Univ. / Zhejiang Univ. | 8 | — | Map of the request-side literature; source of further primaries | Studied (SLR over 140 primary studies) | v3, Feb 2026 | The only systematic map of this half of the literature; use it to find primaries Pass 2 has not seen |
| 13 | Scott, Tõemets, Pfahl, "User Story Quality and Its Impact on OSS Project Performance" (SWQD 2021) | https://link.springer.com/chapter/10.1007/978-3-030-65854-0_10 | 5, 6 | Univ. of Tartu | 2, 8 | R2 | Evidence that request-text quality has downstream cost | Studied (AQUSA scores vs. bugs, rework, delay) | 2021, paywalled — only the abstract and secondary summaries were read | Ties a mechanical quality score to later bugs, rework and delayed issues; the strongest "why bother" argument found for the request genre |
| 14 | Linux kernel, "Security bugs" (Documentation/process) | https://docs.kernel.org/process/security-bugs.html | 2, 7 | Linux kernel | 3, 5, 12 | R1, R2 | Project policy written specifically for machine-found reports | Asserted, current (page shows 7.3.0-rc2) | Active | "If you resorted to AI assistance to identify a bug, you must treat it as public" — with the reason (such bugs surface simultaneously across researchers); also four absolutely-required report elements, including "with no version indication, your report will not be processed" |
| 15 | OpenSSF, *Securing Open Source in the Age of AI* (May 2026) | https://openssf.org/wp-content/uploads/2026/05/Securing-Open-Source-in-the-Age-of-AI.pdf | 7 | OpenSSF / Linux Foundation | 3, 5, 12 | R1, R2 | Reporter-side obligations in the AI era, stated as a guide | Asserted, with one figure (1–8 h to review a report) | 2026 | Has a "Researchers' Guide" with named rules: respect the project's reporting format, provide a PoC, provide a proposed patch, provide regression tests, expect that someone already found it, and "Be Clear and Up-Front if and How AI Tools Were Used" |
| 16 | Stenberg, "Death by a thousand slops" | https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/ | 7 | Daniel Stenberg (curl) | 12 | R1 | The cost side of machine-written reports, with project numbers | Asserted, but the numbers are the project's own records | 2025-07-14, superseded by later curl decisions | 20% of 2025 submissions judged AI slop; ~5% validated genuine; 3–4 people per report at 30 min–3 h each. Later events (bounty closed 2026-01-31) were seen in search results only |
| 17 | Ghostty `AI_POLICY.md` | https://github.com/ghostty-org/ghostty/blob/main/AI_POLICY.md | 7 | Ghostty project | 12 | R1 | The only found project policy that governs *issues*, not just code | Asserted | Active (main) | "Issues and discussions can use AI assistance but must have a full human-in-the-loop"; disclosure of the tool and extent; the human must be able to explain the content without the tool; named consequence (public denouncement list, all future contributions blocked) |
| 18 | `github/awesome-copilot` — `skills/github-issues/SKILL.md` | https://github.com/github/awesome-copilot/blob/main/skills/github-issues/SKILL.md | 7 | GitHub | 8, 12 | R1 | The incumbent agent skill to beat | Asserted | Active (main) | GitHub's own published issue-writing skill; carries one relevant rule ("Ask for missing critical information rather than guessing") and no ordering, attribution or currency rule |
| 19 | Raymond & Moen, "How To Ask Questions The Smart Way" (rev. 3.10, 2014) | http://www.catb.org/~esr/faqs/smart-questions.html | 1, 7 | Eric S. Raymond, Rick Moen | 1, 9, 10 | R5 | The short-form genre's canonical rules, with worked good/bad pairs | Asserted | Stable canonical, last revised 2014 | "Describe the goal, not the step" and "Describe the problem's symptoms, not your guesses… If you feel it's important to state your guess, clearly label it as such"; "Volume is not precision"; each with a Stupid/Smart example pair |
| 20 | xyproblem.info; nohello.net; dontasktoask.com; Evans, "How to ask good questions" (2016-12-31) | https://xyproblem.info/ · https://nohello.net/en/ · https://dontasktoask.com/ · https://jvns.ca/blog/good-questions/ | 7 | Community pages; Julia Evans | 9, 10 | R5 | The whole practitioner base for the colleague message | Asserted | Live; xyproblem.info returned HTTP 403 to the fetch and is cited from search-result content only | Four rules an agent can apply in three lines: name the goal above the step; put the question in the first message; do not ask to ask; state your current understanding and ask "is that right?" |

Not covered by this arm, by design: category 3 (Bugzilla/Atlassian/ISTQB/IEEE 829/29119-3) and the defect-report halves
of categories 1, 2, 4 and 5, which are arm A's. Within my own scope, category 4 (mechanical oracles) was covered only
where an oracle applies to a request or to a machine-written report — AQUSA, CTQRS, GitHub issue-form `required`.

## Promising shortlist for Pass 2

**1. QUS + AQUSA (row 1).** The only source in this arm that pairs each rule with a detection. Three of its 13 criteria
map straight onto baseline rules: *problem-oriented* ("a user story only specifies the problem, not the solution") is
B1 and Q10; *atomic* ("exactly one feature") is B5, the independent-symptoms rule, in the request genre; *conceptually
sound* ("the means expresses a feature and the ends expresses a rationale") is the rule against a request whose
rationale is a pointer to another request. Every criterion in the paper comes with a real violating example and its
repair, which is what "before and after" means here. Serves R2. Converts to compact rules directly; the risk is that
the criteria are stated over the `As a … I want … so that …` sentence form, and Pass 2 must decide whether they survive
being lifted off it.

**2. The Go 2 language-change template (row 2).** The single best question list for the request genre, and the source
that decides the reader-table question. It makes the requester answer what the change costs, who it helps, whether it
has been proposed before, and asks for before-and-after example code. Serves R2. It converts cleanly into a checklist
an agent can run without the author present, and — unusually — the questions are answerable from the requester's own
session rather than from the target project's roadmap.

**3. The Gradle feature-request form against the Gradle bug form (row 8).** The most useful contradiction found. The
same project, in the same directory, orders the two genres oppositely: the bug form requires Current Behavior first,
the feature form requires **Expected Behavior first and makes Current Behavior optional**. Its Context field is
required and asks "What are you trying to accomplish? What other alternatives have you considered?" — the XY-problem
guard as a required field. Serves R1. Pass 2 should use it to state the ordering rule per genre rather than globally.

**4. The CrowdRE'25 study (row 10).** The only measured base rates in this arm. Two findings bear directly on the
skill: developers overwhelmingly do *not* ask for clarification (39/50) — they close instead, so a request that omits
something usually gets no second chance; and their clarification, when it happens, is about intent and feasibility,
not technique — which argues that a request's goal statement is load-bearing and its implementation sketch is not.
Serves R2. Small and two-project, so treat the direction as findable and the magnitudes as local.

**5. The KEP template (row 3).** Contributes two slots the baseline has no equivalent for: **Non-Goals** ("listing
non-goals helps to focus discussion") and Goals stated as "How will we know that this has succeeded?" — acceptance
criteria phrased as a question rather than as a Gherkin ritual. Serves R2 and R3. Converts to a rule of the form
"state one sentence that would be false if the change did not work"; the rest of the template (PRR questionnaire,
version skew) is Kubernetes-specific and should be left behind.

**6. ESR "Smart Questions", §"Describe the goal, not the step" and §"symptoms, not your guesses" (row 19).** The
colleague-message genre rests on this. It gives the rule, the rationale, and a paired Stupid/Smart example for each,
which is exactly the form the skill needs. It also supplies the escape hatch the baseline's B2 lacks: a guess may be
stated if it is *labelled* as a guess and accompanied by why it did not work. Serves R5. Old (rev. 3.10, 2014) and
written for mailing lists; the tone advice is `english-developer-style`'s and should be dropped.

**7. The Linux kernel security-bugs page (row 14).** The strongest *current* project policy aimed at machine-produced
reports, and it is written as content rules, not procedure: a version range without which the report is not processed,
a reproducer that is not a binary, the conditions under which the bug appears, and the AI clause with its stated
reason. Serves R1. Converts into two hard checks an agent can run on itself: is there a resolvable version identifier,
and was the reproducer actually executed. The security-procedure parts around it are out of scope.

**8. OpenSSF, *Securing Open Source in the Age of AI* (row 15).** The only source that addresses an author who is a
machine and writes obligations for it: disclose the tool and the extent, expect that the finding is duplicated, keep
it short because "AI reports tend to be overly verbose", and prefer a patch and a regression test over another report.
Serves R1 and R2. Its rules are stated for security research; Pass 2 must decide which generalize to an ordinary
defect or request. Current (May 2026) and organizationally accountable.

**9. Ghostty `AI_POLICY.md` (row 17).** The clearest statement anywhere found that an *issue* — not just a patch — has
an AI policy, and the only one that names a test the agent's human can fail: be able to explain the content without
the tool. Serves R1. It converts into a disclosure rule and a "would a human stand behind each claim" gate, and it
gives the skill a reason to keep the report short enough that a human can check it.

## Obvious rejects

- **Consultancy SCQA / "problem statement" pages** (managementconsulted.com, stratechi.com, slideworks.io) — generic
  storytelling frames with no software example and no accountable claim; the ordering advice they carry is
  `english-developer-style`'s.
- **Given-When-Then / Gherkin acceptance-criteria blog posts** (parallelhq, wazobia, agileambition, Substack posts) —
  listicles restating one template with no rationale and no source; where acceptance criteria matter, KEP and INVEST
  say it with an owner behind the claim.
- **Definition-of-Ready advocacy and its rebuttals** (scrum.org posts, Mountain Goat, Serious Scrum) — process
  advocacy, explicitly out of scope; the debate is about whether a gate should exist, not about what a request text
  must contain.
- **"Awesome Claude skills" lists** (karanb192, BehiSecc, travisvn, theneoai, awesomeskill.ai, blockchain-council
  "Top 50") — anonymous or aggregate collections with no examples and no accountable author; the brief excludes them.
- **Secondary news coverage of curl, Ghostty and the kernel** (The Register, Tom's Hardware, BleepingComputer,
  betanews, hackaday, techtimes, and the AI-written aggregator posts) — every claim in them traces to a primary that
  was fetched here; cite the primary.
- **"How to write a good issue" content-marketing pages** (opensauced, hoop.dev, dev.to newbie guides, LogRocket and
  Visual Paradigm INVEST explainers) — restate Tatham, Raymond or Wake with nothing added.
- **Wikipedia "XY problem" and the XY-problem commentary blogs** (thecoder.cafe, chengweihu, davelozinski,
  xyproblemproblem.com) — derivative of xyproblem.info; use the primary, which is the one to re-fetch.
- **`melissawm/open-source-ai-contribution-policies`** — useful as an index, but a reject as a *source*: fetched from
  `main`, its policy table covers code contributions and pull requests only, and says nothing about AI-generated
  issues, bug reports or feature requests. Worth recording as evidence that this category is thin.

## Gaps and questions for Pass 2

**Ruling on the reader table: the backlog owner does not need a row of its own.** The evidence says the cost, priority
and completion questions are asked by R2 rather than by a distinct person. The Go proposal template — the most
cost-conscious artifact found — is answered by the proposal *committee*, which is R2; the KEP's "How will we know that
this has succeeded?" is a required field of the maintainer's own template; Django routes requests to a steering-council
project, again R2; Kubernetes's enhancement form asks only "what" and "why", and defers everything else to a SIG. The
CrowdRE'25 closure taxonomy shows the same people deciding on project alignment, duplication and workload. What the
evidence *does* say is that R2 reads in two modes: when the artifact is a request, R2 additionally asks who is
blocked, what it costs, and how anyone will know it worked — and INVEST's *estimable* and *testable*, KEP's Goals and
Non-Goals, and Go's cost questions are the content that answers them. So: extend R2 with a request mode; do not add a
sixth row. One row that *does* need restating is **R4**: in the request genre the searcher is not matching an error
string but deciding whether an existing request already covers their case, and OpenTelemetry's issue-participation
page is the only source found that tells them what to add (their own environment and impact) rather than a "+1".

**Detectable from the report text alone.** Solution-instead-of-problem (QUS *problem-oriented*; ESR "describe the goal,
not the step"); two requests merged into one (QUS *atomic*); a request whose rationale is a cross-reference rather than
a reason (QUS *conceptually sound*); a missing "why" (Django, Kubernetes, JUnit); an unlabelled diagnosis (ESR — the
label is a text property); absence of a version identifier (kernel); a first chat message with no question in it
(nohello); verbosity as an AI tell (OpenSSF).

**Needs the reproducer run.** Whether the reproducer reproduces at all; whether a *proposed expected form* actually
works, which is baseline rule B4 and which **no source in this arm addresses** — the closest is the Playwright skill's
"never include a step you did not personally execute", which covers steps taken, not forms proposed. Flag this as
unsourced and push arm A or Pass 2 on it.

**Needs a tool or a lookup.** Duplicate search (PEP 1's prior-discussion check, Go's "has this been proposed before",
CrowdRE's 7/50 duplicate closures, the kernel's simultaneous-discovery argument); whether the venue is right (Django,
Kubernetes, rust-internals — a request filed in the tracker instead of the forum is a text-invisible defect);
whether the project's supported versions still carry the behavior; whether the project has an AI policy at all
(Ghostty, kernel, curl) — that lookup is now a precondition, not a courtesy.

**Human judgment.** Whether the stated goal is the real goal (the XY problem is defined by the asker not knowing);
whether a request is in the project's scope (Django asks the requester to judge this, CrowdRE shows maintainers
closing on it); whether the cost estimate is honest.

**Conflicts found.** (a) *Ordering, request genre.* Gradle's feature form requires Expected Behavior first and makes
Current Behavior optional; the baseline's B1 says start from the user-facing problem. Both cannot be stated as one
rule. Rust RFC, KEP, PEP 1, Django and JUnit all put motivation first, so Gradle looks like the outlier — but it is
the outlier in the baseline's own project, and it is a *required-field order*, which an agent filling a form cannot
ignore. (b) *Motivation-first vs. exploration.* On `internals.rust-lang.org` ("Guidelines on RFCs and feature
requests", July 2022) a commenter argues pre-RFCs already assume the pain point is agreed and should be filtered on
motivation first, while scottmcm and burntsushi defend a bias for action; this is the ordering debate, held by
maintainers, in public. (c) *Sketch or no sketch.* CrowdRE'25 finds requests carrying mock-ups or code snippets get
faster and more positive responses, while QUS's *problem-oriented* criterion counts a solution hint as a defect.

**Does any source treat the report as something its own author may game?** Three, all recent and all in category 7.
Ghostty: disclose the tool, and be able to explain the content without it — the check is a conversation, not a text
property. OpenSSF: disclose whether and how AI was used, expect duplication, prefer a patch and a test over another
report. The Playwright skill: never include a step you did not execute, and say a field's evidence is missing rather
than leave it blank. Nothing found proposes a check against a *fabricated version string or log line*; the kernel's
"no version indication, your report will not be processed" is the nearest, and it detects absence, not invention.

**Least-served genre: the colleague message.** Its entire base is four short community pages plus one blog post, all
asserted, none with an OSS-scale audience behind it, and one of them (xyproblem.info) returned HTTP 403 to the fetch
and is reported here from search-result content, not from the page. There is no measurement at all of what a
three-line message must carry. The request genre is second-best served and the filed issue best served (by arm A's
half). Pass 2 should decide whether the colleague-message rules are simply the request rules with an omission budget,
or whether R5's "is this mine" decision needs its own slot.

**Left over for a human.** Whether the diagnosis in hand is worth stating at all; whether the request is one the
project would want; and whether the reporter's confidence is proportionate to what they actually ran.
