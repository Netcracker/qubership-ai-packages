# Research: problem-report-authoring

Why a report of an unfixed problem is a different artifact from a description of a change, what its
rules are, and which of them anyone can check. The pipeline ran on 2026-09-07 and produced
[`agent-packages/problem-report-authoring`](../../agent-packages/problem-report-authoring/README.md).

## Why the research was run

An agent was asked to draft issues for `gradle/gradle` and `junit-team/junit-framework` after a
session in which it had reproduced a test-reporting defect. It wrote them in the only form it had, the
form of a pull request description: mechanism first, symptom second. It also proposed filing against a
project that had already shipped the fix, asserted an expected form it had never executed, framed the
request around an available configuration setting, merged two independent symptoms, and used bare
argument values where the reader needs parameter names. Six rounds of correction followed. Nothing
installed covered the ground: `change-description-authoring` mentions an issue only as a link and a
number a description carries, never as an artifact to write, and `english-developer-style` treats a
bug report only as provenance to be verified.

## The readers

Fixed before the first search and not reopened by a pass. Pass 1 ruled that a backlog owner needs no
row of its own: its questions belong to R2 in a request mode.

| Reader | Situation | Holds |
| --- | --- | --- |
| R1 Triager on a project the reporter does not maintain | A queue of new issues, about a minute per item | The report, the project's templates and support policy |
| R2 Maintainer deciding whether to act | Has accepted the report as real | The whole report and the project's design constraints |
| R3 Whoever picks the work up months later | A fresh checkout | The report and the current code |
| R4 A searcher | Hit the same error, or has the same use case | An error string and a version, or their own case |
| R5 A colleague | Interrupted mid-task | A few lines of chat |

## Method

| Pass | Model | Brief | Result | What it produced |
| --- | --- | --- | --- | --- |
| 1A Discovery: essays, project guides, tracker standards, oracles, empirical work | Opus 5 | `phase1_prompt.md` | `phase1a_result.md` | 20 candidates, 8 shortlisted |
| 1B Discovery: requests, backlog practice, short form, machine-written reports | Opus 5 | `phase1_prompt.md` | `phase1b_result.md` | 20 candidates, 9 shortlisted |
| 2 Rules and verification | Opus 5 | `phase2_prompt.md` | `phase2_result.md` | 45 rules with detections, five of six conflicts settled, the baseline audited, every figure checked |

Discovery was split in two because the domain spans three genres; the two arms shared one brief and
were given different halves of the search scope. Verification ran inside pass 2 rather than as a
separate pass.

## Findings

- **The ordering rule is two rules, and only one survives.** Symptom before mechanism holds
  everywhere. Actual before expected does not: projects order those fields both ways, one project
  orders its bug form and its feature form oppositely, and one contradicts itself between its template
  and its worked example. The skill states the first and defers the second to the project's form
  (pass 1A, pass 2 conflict 1).
- **A request inverts the opening.** Every enhancement-proposal process found puts motivation first,
  and one project's feature form makes expected behavior the required first field while leaving
  current behavior optional (pass 1B).
- **Filling the template buys admission, not resolution.** Across a large corpus of GitHub issues, a
  project having a template predicts faster resolution while an individual issue's conformance to it
  predicts nothing. The rule survives with a different justification: projects close reports that skip
  the checklist, and component fields route them (pass 1A, pass 2 conflict 6).
- **Expected behavior is the weak point, three times over.** It is the field reporters omit most
  often; its grounding predicts whether a report is fixed or closed as invalid; and three of the
  maintainer's four unsourced rules were about it. The skill's center is a six-question test for one
  expected block (pass 1A, pass 2 §5).
- **Attribution across a stack is a procedure, not an exhortation.** Four projects converge on the
  same shape: re-run the failure with one layer removed, and report the innermost layer that still
  fails (pass 1A).
- **Machine authorship is now project policy with consequences.** Disclosure requirements, brevity
  stated as a rule about machine-written reports, a ban on speculative impact, and a requirement that
  a human be able to defend the report without the tool. These policies also turned out to be the only
  sources that state two of the maintainer's rules directly (pass 1B, pass 2).
- **Prior art exists and is thin.** One published agent skill for filing issues is `gh` mechanics with
  no content rules; a second could not be located at all (pass 1B, pass 2 §11).

## The baseline audit

All eight of the maintainer's starting rules survive. Two gained sources they did not have: checking a
proposed fix or form before reporting, and one report per independently fixable symptom, the second
with a merge test attached. Two are labeled derived in the skill, with the derivation kept here:
expected values stated by content rather than by position, and the workaround that must not become the
frame. One kept its rule and lost its rationale: filling the template's fields. The largest gaps the
baseline had were a supported-version check, a rule that an expectation must be grounded at all, and
any coverage of the request genre or the colleague message.

## Verification

Every figure in the results was checked against its primary source inside pass 2, and the corrections
are recorded in `phase2_result.md` §11. The load-bearing findings held. The misses were in
attribution and framing: a percentage set that is a conditional likelihood rather than a share of
respondents, duplicate base rates cited from another paper rather than measured, an author's name,
an effect size taken from a thesis rather than the published paper, a quoted developer comment
reported as a measurement, and an observation reported as a quantified effect. Two sources were
unreachable and are reported as unreachable rather than reconstructed.

Two corrections belong to the transcripts themselves and are recorded here rather than edited into
them. The genre matrix in `phase2_result.md` §4 marks the ownership rule not applicable to a request, and
its stated ground is that "a request is about a project you have already chosen". That is the sentence
to distrust: choosing an addressee is the decision, not a step already taken. A request that names the
wrong project in a stack is misfiled the same way a defect report is, and the accepted request the
research itself cites carries a section arguing why its addressee is the right one. What genuinely
lapses is the method, because there is no failing run to bisect. The skill keeps the obligation and
drops the method.

The second:
`phase2_result.md` §5 case 3 credits `junit-team/junit-framework#6041` with a `Workaround` section
placed last. That issue has no such section; the setting it discusses does not fix the problem and
appears under a heading saying so, between the symptom and the ask. The `Workaround` section belongs to
`gradle/gradle#39079`, where it sits after everything that states the problem, with the causal guess
and the attached reproducer below it. The rule the case supports is unaffected, and the skill now
states both placements.

## The trial

The skill was tried on the case that produced it, and the whole trial is in
[`trial/`](trial/README.md): the input both arms were given, the draft written without the skill, the
draft written with it, and the comparison.

What it established. The control arm already opened with the symptom and hedged its reading of the
source, so the worst framing defect does not need the skill. Four defects did need it: an expected
block with no literal in it, a project form that was never read, two pull requests named as possibly
related and left unverified, and an index-based name reported neutrally. The arm with the skill closed all
four and handed over three gaps it could not close: the tracker search with the terms to search for,
the reproducer re-run with the command, and the human sign-off as a question for the person filing. It also
found two ambiguities in the skill's own text, and both were fixed before the package was called done.

## Files

| File | What it is |
| --- | --- |
| `phase1_prompt.md` | The discovery brief, shared by both arms |
| `phase1a_result.md` | Arm A: essays, project guides, standards, oracles, empirical work |
| `phase1b_result.md` | Arm B: requests, short form, machine-written reports, prior art |
| `phase2_prompt.md` | The rule brief, with the shortlist inlined |
| `phase2_result.md` | The rules, the conflicts, the baseline audit, the evidence map |
| `trial/README.md` | The A/B trial: method, what each arm did, and what it changed in the skill |
| `trial/facts.md` | The investigation notes both arms were given |
| `trial/control.md` | The draft written without the skill |
| `trial/treatment.md` | The draft written with the skill |
| `versions/README.md` | What changed in the skill across four review rounds, rule by rule |
| `versions/v1..v5-*.md` | The skill and its reference files as they stood before review and after each round |
| `versions/decisions/` | The fix reports: every finding decided, with its evidence |

## Status

Complete. The skill ships at `agent-packages/problem-report-authoring`. Three follow-ups remain.

- Pin the package in the umbrella packages once it is on `main` and has a commit SHA.
- **The trial covered the bug-report genre only.** Both arms wrote a report for `gradle/gradle`; the
  feature request and the colleague message have no evidence behind them, and their rules rest on the
  sources alone.
- Repeat the trial on a second real report in another ecosystem.
