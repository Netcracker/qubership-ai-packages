# Skill snapshot: v2-after-round1
after round 1 (15 findings) and the first final-review pass (4 findings)


<!-- ===== SKILL.md ===== -->

---
name: problem-report-authoring
description: >-
  Load before writing or reviewing a report of a problem someone else has to act on: a bug report or
  issue in a project you do not maintain, a feature or change request, or a short problem message to a
  colleague. A session that reproduced something in someone else's project reaches this point when it
  is asked to write it up, file an issue, or tell the team. Also load for "review this draft", "is
  this ready to file", and before `gh issue create`. Governs what the report establishes before its
  first sentence (which project owns the defect, whether the version is still supported, whether the
  report exists already), what each slot carries, the test an expected-behavior block must pass, and
  the reports that satisfy every rule and are still useless. Wording is english-developer-style's;
  load both. Not for a commit message or a pull request description (change-description-authoring), a
  documentation page (docs-page-authoring), or the regression test (test-authoring).
---

# Authoring a problem report

This skill governs **what a problem report establishes before it is written, what each part of it
carries, and how a reviewer detects a bad one without the author present**. Wording, tense, sentence
length, and dialect belong to `english-developer-style`; load it too.

Three artifacts fall under it, and they share a spine: a bug report filed in a project you do not
maintain, a feature or change request in that project or in your own team's backlog, and a short
problem message to a colleague. An issue in a repository you do maintain is in scope too: the reader
who picks it up months from now knows no more than a stranger would. What differs is
length, what may be left unsaid, and one ordering rule (§3).

**The form you already know is the wrong one.** A change description is written for a reader who holds
the diff and already knows something was wrong; it opens on the problem the change solves, inside the
project both of you work on. A triager knows neither the defect nor your code, so the same shape
produces a report that opens inside the target project's internals. Writing a report in the shape of a
pull request description is the failure this skill exists to prevent.

## 1. The readers

Every rule below names the reader it exists for. A sentence that answers none of their questions
belongs somewhere else.

| Reader | Holds | Asks |
| --- | --- | --- |
| **R1 Triager** | Your text, the project's templates and support policy, about a minute | Is this a defect in our project? Does it reproduce? On a version we support? Is it a duplicate? |
| **R2 Maintainer** | The whole report, plus the project's design constraints | Which behavior is correct here? Whom does this affect? What breaks if we change it? For a request: who is blocked, what does it cost, how will we know it worked? |
| **R3 Whoever picks it up** | The report and a fresh checkout, months later | How do I reproduce this? Is the expectation precise enough to write a test against? |
| **R4 A searcher** | The same error string, or their own use case | Is this my problem? On which versions? What do I do until it is fixed? |
| **R5 A colleague** | Three lines of chat, mid-task | Is this mine? What do you need from me? What did you already rule out? |

## 2. Five steps, in this order

The expensive work happens before any prose exists. Steps 1 and 2 can invalidate the whole report.

1. **Read the target project.** Its issue forms and `config.yml`, `CONTRIBUTING.md`, an `AI_POLICY.md`
   or the AI section of `CONTRIBUTING.md`, `SECURITY.md`, and its support-window statement. Record the
   required field names and their order before writing a sentence. Details and the known
   contradictions between projects: `references/project-conventions.md`. Where the target has no such
   files, which is the usual case for a team's own backlog, read what stands in for them: the tracker's
   own required fields, the last few items other people filed, and whatever the team treats as ready to
   pick up.
2. **Establish ownership and currency.** Which project owns the defect, whether it survives on a
   supported version, whether it is already reported, and how many reports this is (§4).
3. **Write into the form's fields, in the form's order,** with §3 governing what goes in each.
4. **Apply the expected-behavior test** to every expected block (§5). This is the center of the
   skill.
5. **Run your own checks and paste the transcripts** (§6), answer what the project asks of a report
   written with a tool (§7), then fill or mark every required field (§8).

## 3. Framing

- **Open with the user-facing symptom, in the project's vocabulary.** "I do X, Y breaks", before any
  statement about the project's internals. R1, R4, R5. *Test:* read the first paragraph. If its
  subject is a class, a function, a file, or a commit inside the target project rather than an action
  you took, it fails.
- **The title names the symptom, not the fix you have in mind.** R1, R4. *Test:* a defect title
  containing `add`, `make`, or `change` aimed at the project is naming a solution.
- **Put causal analysis at the very end, and label it a theory.** R1, R2. Even a correct analysis is no
  substitute: the project has to see the failure happen before it fixes anything, and an analysis
  stated first is read as the report. A guess is welcome once it is marked as a guess and says what
  ruled the alternatives out. *Test:* no sentence asserting a mechanism inside the target project
  appears before the symptom, and each one carries its own hedge. Where the form has a context or
  additional-information field, the analysis belongs there. Where it has none, put the analysis after
  the reproducer, and keep the field the form opens with free of it.
- **State the goal, not only the step you got stuck on.** R2, R5. *Test:* a sentence exists whose
  subject is you and whose verb is the task, independent of the project's API.
- **Describe what you did and what the machine did, in order.** R1, R3. Each step has an observable
  result.
- **Where the target form's field order disagrees with this skill, the form wins.** R1. Projects order
  actual and expected behavior differently, and one project can order its bug form and its feature
  form oppositely. Only the symptom-before-mechanism rule is universal. *Test:* compare your headings
  against the form's field labels, in sequence.
- **A message to a colleague is the same spine, shortened.** R5. What may be dropped is the context you
  share; what may never be dropped is the ask itself. `references/colleague-message.md`.
- **A request leads with the problem, not with the API you want.** R2. The first section names a task
  you could not complete, not a construct the project lacks. The rest of the request genre is
  `references/request-genre.md`.
- **A known workaround goes after everything that states the problem, and before the causal analysis;
  the expected behavior must not depend on it.** R2. A report
  framed around its own workaround reads as "configuration is enough for me" while asking for the
  default to change. *Test (the deletion test):* delete every sentence that mentions the workaround.
  If what remains no longer states a requirement, the workaround was the frame.
- **A setting you tried that does not solve the problem is neither a workaround nor an alternative.**
  R2. It is a negative result, and it belongs right after the symptom, under a heading that says it
  does not fix the problem. Putting it last with the alternatives hides the strongest argument that
  configuration cannot answer the request.

## 4. Before you file: ownership, currency, duplicates, count

- **Isolate which project owns the defect, and put the commands and their outputs in the report.**
  R1, R2. A symptom seen through a stack is not evidence about any layer in it. Ecosystems publish
  the procedure: rebuild with the front end only, convert the reproducer to plain C, isolate the
  offending queries, remove every dependency outside the project. Where none is published, remove one
  layer at a time and record each result. *Test:* the report contains a command sequence a
  reviewer can re-run, whose last step uses only the target project. Where the defect only appears
  through a dependency, the last step is the shortest chain that still fails, and the report names the
  dependency that could not be removed and what happened when it was. Report the elimination, not the conclusion.
- **Reproduce on a version the project still supports, and say which.** R1, R2. A defect already fixed in a
  release you did not test is a common reason a report comes back as not reproducible. *Test:* the
  stated version falls inside the published support window and appears in the pasted output.
- **Search the tracker, and write the query and the nearest hit into the report.** R1, R4. Do not
  suppress a report because something similar exists; a second report of a live defect is cheap and
  usually adds information. A null result establishes nothing on its own, so record what you searched.
  Where you cannot reach the tracker, say so and write the queries the person filing should run, in the
  report or in a note to them. An unreachable tracker is a gap to hand over, not a step to drop.
- **File one report per independently fixable symptom.** R1, R2, R3. *Test:* count the distinct expected
  outcomes, then ask what is observable about them. Could a maintainer accept one and refuse the
  other? Do they live under different owners or in different repositories? Either answer makes two
  reports. Merge only where you can see that the same maintainers would fix both in one change, such
  as two symptoms of one function. Where neither question settles it, file separately and link the two
  reports: a maintainer can merge two reports and cannot split one.
- **Obey the project's routing.** R1. Contact links, "ask here instead" lines, and component questions
  decide where this belongs. A correct report in the wrong queue is closed regardless of its quality.

## 5. The expected-behavior test

Expected behavior is the field reporters omit most often, and its grounding is what separates the
reports maintainers act on from the ones they close as invalid. Send every expected block through six
questions in order. The first "no" is the finding.

1. **Is there a literal?** At least one string, number, exit status, or emitted artifact that a
   machine could compare against. An expected block built from adjectives, such as correct,
   consistent, or works, states nothing.
2. **Is the literal sufficient?** Could two materially different outputs both satisfy it? Hand the
   block to a reviewer and ask them to write the assertion from it alone. If they cannot, it fails.
3. **Does every identifier resolve by content?** Name the thing; do not index it. An ordinal, an
   offset, or a position identifies nothing to a reader who holds only your text, and it moves when
   the underlying data changes, so a report archived last week names a different case today. Where the
   artifact's own vocabulary is positional, such as a byte offset or a line number, keep the ordinal
   and put the content beside it.
4. **Is the grounding named, and how strong?** State what the expectation rests on, in a
   because-clause naming something fetchable. Strongest first: the project's own documentation or
   specification; runtime logic, meaning a crash, an assertion, or an error the project itself raises;
   the expectation of its user community. Weaker: an industry standard the project does not claim to
   implement, another product's behavior, what the project used to do, and your own preference. The
   order is not taste: the first three are the groundings maintainers act on, and a standard the
   project does not claim, another product's behavior, and what the project used to do are the ones
   most often closed as invalid. A personal preference is weak for a different reason: nothing outside
   you supports it. Use a weak grounding where it is all you have, and say that it is weak. Prior
   behavior becomes strong only where the project ships a regression form that makes the last working
   version a required field.
5. **Was every claim about today's behavior executed?** The behavior you are asking for does not exist
   yet, so it cannot be run. Everything you say around it can: that a form works in an existing tool,
   that a reader could re-run one case from it, that another consumer of the same data already renders
   it, that the setting does not help. Each of those is a claim about a tool you have, and each needs a
   pasted transcript. Proposing a shape because it would let a reader do something, without having
   tried it, is how a report acquires a claim that is simply false. Mark the proposed rendering as one
   possible shape; make the claims around it verifiable. *Test:* every sentence about what a tool does
   today has a pasted command or output behind it.
6. **One block per symptom, and is the requirement separated from the rendering?** Say which part you
   need and which part is the project's to choose. A maintainer must be able to accept the requirement
   and reject the shape.

Do not ground an expectation only in another system's behavior, and never without stating the value
you expect. Worked repairs, including the ones this skill was built from:
`references/worked-cases.md`.

## 6. The reproducer

- **Everything needed to reproduce is in the report.** R1, R3. Every file, version, and command it
  references is present or publicly fetchable.
- **Run what you ship, after your last edit to it.** R1, R2. Reduction silently fixes the defect often
  enough that this is the check with the highest yield. *Test:* the pasted output carries incidental
  detail nobody invents, such as paths, timestamps, and the tool's exact punctuation, and it matches the shipped
  reproducer's own identifiers.
- **Reduce until nothing outside the target project is needed, then stop.** R1, R2. Reduction earns
  its keep by eliminating suspect layers, not by being small. Where the defect only appears through a
  dependency, say so and ship the shortest chain.
- **Ship it in the form the project accepts.** R1. Projects disagree: one requires a repository or an
  archive, another forbids both. The form's own field text decides.
- **Paste the failing output verbatim, as text.** R1, R4. Not a screenshot, not a paraphrase. R4
  arrives by searching for that string. *Test:* the report contains a fenced block whose content is
  the tool's own output, punctuation included.
- **Give the version of the target project and of every layer between it and the symptom.** R1, R4.
  *Test:* every tool named in the reproduction chain has a version string somewhere in the report.
- **Where the project provides an external oracle, run it and link the run.** R1, R2. A linked CI run
  is evidence a triager can open, which no sentence in your report is. *Test:* the report carries a run
  URL whose conclusion is the failure being reported.
- **Never write a step you did not execute.** R1, R2. Where evidence is missing, say what is missing
  and what would establish it.

## 7. Reports written by an agent

Projects now write policy for this case specifically, with stated consequences.

- **Put the summary and the critical details first.** R1. Do not make a triager scan pages. Each
  section must carry at least one fact absent from every earlier one.
- **Do not enumerate speculative consequences.** R1, R2. "This could allow" with no observed instance
  is the tell triagers name. Keep an impact you actually observed, and paste the observation.
- **Disclose the tool where the project asks, in the form it asks for.** Read the policy first; some
  projects also constrain who may answer follow-up questions. `references/machine-authorship.md`.

## 8. Filling the form

- **Fill the project's required fields, by their names, so the text drops in unchanged.** R1. This
  buys admission and routing: projects close reports that skip the checklist, and component fields
  decide who sees it. It buys nothing else: a filled form is the condition for
  being read, not a finished report.
- **A field you have no evidence for says what is missing, not a plausible guess.** R1, R2. "Not
  established: I could not test on Windows" is usable. An invented environment is worse than a blank.

## 9. Reports that pass every rule and are still useless

| Shape | Detection |
| --- | --- |
| Every field filled, nothing said | Cross-field consistency: the version in the environment field appears in the pasted output, and the identifiers in the expected block appear in the reproducer. A form whose fields do not reference each other is filled, not written |
| "It should work" | Question 2 of §5: ask whether a reviewer could write the assertion from the block alone |
| A reproducer that was never run | Re-run it. Composed output lacks incidental detail; this is why the check is a run and not a reading |
| A confident cause for a project that already shipped the fix | The version check and the tracker search of §4, against closed issues and release notes as well as open ones |
| A report framed around its own workaround | The deletion test in §3 |
| The same fact in four sections | Each section must contain a literal absent from every earlier section |
| A grounding that names a document which does not say it | Fetch the named artifact and read the sentence claimed for it |

## 10. What is not yours to decide

Raise these and let the human answer:

- Whether the person filing can explain and defend the report without the tool that wrote it. Several
  projects make this a condition of filing.
- Whether to file at all when personal preference is the only grounding available.
- Whether a project's AI policy permits an agent-authored report.
- Whether the request is one the project would want, and what it is worth.

## 11. Review checklist

Run it over a draft, yours or someone else's. Every item gets an answer, "none" included.

- First paragraph: an action you took and what broke, or a class inside the project?
- Ownership: is the isolation in the report as commands and outputs, or only as a conclusion?
- Currency: is the version inside the support window, and does it appear in the pasted output?
- Duplicates: is the search recorded, with its query and nearest hit?
- Count: how many independently fixable symptoms are here, and how many reports?
- Expected behavior: run the six questions of §5 over every block, and name which question failed.
- Grounding: which of the seven sources is it, and is a weak one marked weak?
- Execution: does every claim about what a tool does today carry a pasted transcript, and is a
  proposed rendering marked as one possible shape?
- Analysis: is it last, hedged, and does the report stand without it?
- Reproducer: is it complete, was it re-run in the shipped form, is the failing output pasted as text,
  and does every layer in the chain carry a version?
- Disclosure: does the project ask anything of a report written with a tool, and is it answered?
- Form: does every required field carry an observation or an explicit "not established"?
- Vacuous shapes: run §9.


<!-- ===== references/project-conventions.md ===== -->

# Reading the target project before you write

Open this at step 1 of the skill. Everything here is a lookup, and every answer changes the report
you are about to write.

## The files, in this order

1. **`.github/ISSUE_TEMPLATE/*.yml` and `*.md`.** The field labels, their order, and which carry
   `validations: required: true`. Write into those labels verbatim, in that order. A project often
   ships several forms (a bug form, a feature form, a regression form, a documentation form) and they
   disagree with each other on purpose. Pick the one that matches your artifact and read that
   one.
2. **`.github/ISSUE_TEMPLATE/config.yml`.** Contact links and `blank_issues_enabled`. A project that
   routes questions to a forum and security to an email will close a report filed in the tracker
   instead, whatever it contains.
3. **`CONTRIBUTING.md`.** Reproducer form, supported versions, what the project refuses to accept, and
   often the sentence that says what happens to a report that skips the checklist.
4. **`AI_POLICY.md`, or the AI section of `CONTRIBUTING.md`.** Disclosure, and sometimes a condition
   on who may reply. See `machine-authorship.md`.
5. **`SECURITY.md`.** Where security reports go, and in which format. A project whose security channel
   is email wants plain text, not Markdown decoration.
6. **The support window.** A release schedule, a `SUPPORT.md`, or the newest release. This decides
   whether the version you reproduced on is worth reporting at all.

## What the lookups establish, and what they do not

| Lookup | Establishes | Does not establish |
| --- | --- | --- |
| Form field labels | The required order and the admissible fields | That a filled form is a good report |
| `config.yml` routing | Where the project wants this | That the redirect target will take it |
| Tracker search | That one query returned nothing | Absence. Trackers match titles and labels, and duplicate detection is an open research problem |
| Support window | Whether the version is in scope | That the defect is absent from the development branch |
| Reproducer field text | The accepted form | That your reproducer reproduces |

## Where projects contradict each other

Do not carry a convention from one project to another. Three real disagreements, each settled only by
reading the target:

- **Reproducer form.** One large project requires a self-contained project as a repository or an
  attached archive. Another forbids both and wants the smallest possible inline snippet. A third
  requires a link to a running reproduction.
- **Actual versus expected.** Several projects put current behavior first in the bug form. Others put
  expected first, and one of those makes the reporter justify why it is expected. At least one project
  orders its own bug form and its own feature form oppositely, and at least one contradicts itself
  between its template and its worked example.
- **Reduction.** Some projects demand a minimal example. At least one tells reporters not to spend
  their time shrinking one, on the grounds that a reproducible defect will be found either way. The
  stop condition in the skill, no dependency outside the target project, satisfies both, because it
  is about eliminating suspect layers rather than about size.

## The one rule that overrides the skill

The form wins. Where the project's required field order disagrees with any ordering preference here,
write into the project's order. The only rule that survives the override is that the user-facing
symptom precedes the mechanism, because that is about which sentence opens a field, not about which
field comes first.


<!-- ===== references/request-genre.md ===== -->

# The request genre

Open this when the artifact is a feature or change request rather than a defect report. Most of the
skill still applies. What changes is the opening, five slots that a defect report does not have, and
two rules that lapse: there is no layer to isolate and no reproducer to ship, because the
behavior you are asking for does not exist. What replaces them is the prior-proposal
question in the slots below: confirm the project does not already do this, and that nobody has asked
for it before.

## The opening is inverted

A defect report opens with what broke. A request opens with what you could not do. Every
enhancement-proposal process converges on motivation first, and at least one project makes expected
behavior the required first field of its feature form while leaving current behavior optional. State
the task you could not complete before naming any construct the project lacks.

The test is the same deletion test as the workaround rule: remove every sentence that names your
proposed API. If the remaining text no longer states a problem, you have written a patch request with
a preamble.

## The slots

- **The problem.** A task you could not complete, in your own vocabulary. Not "the API lacks X".
- **Who else is blocked, and what it costs.** Both directions: the cost of doing it and the cost of
  leaving it undone. Name a party other than yourself, or say explicitly that you are the only known
  case. A maintainer's first question is how far the problem extends.
- **How anyone will know it worked.** One sentence that could become a test or a measurement. This is
  the acceptance criterion, and phrasing it as a question the project can answer later beats any
  ritual template.
- **What is out of scope.** A non-goals sentence keeps the discussion from expanding into the change
  you did not ask for. Maintainers use it to bound the review.
- **Whether it has been proposed before, and how yours differs.** A link to the prior discussion, or an
  explicit statement of what you searched. Some processes make this a required field.
- **Alternatives, including your workaround.** Last, subordinate, and stated with why each was ruled
  out. Ruling something out is information about your requirements; leading with it is a frame that
  undercuts the request. One kind moves: a setting you tried that does **not** solve the problem is
  a negative result rather than an alternative, and it belongs right after the problem statement,
  under a heading that says it does not fix it.
- **A sketch, optional and labeled.** A mock-up, a snippet, or before-and-after code helps a
  maintainer see the shape you mean. It sits below the problem statement and is marked as one possible
  shape, not as the requirement. Separate the requirement from the rendering explicitly:
  say which part you need and which part is the project's to choose.

## Grounding, for a request

The grounding order in the skill applies here too, and bites harder. A request grounded in "another
product does it this way" or in personal preference is the shape maintainers close. Ground it in a
task the project's own documentation says it supports, in an error the project itself raises, or in
users who hit the same wall.

## A backlog with no forms

An internal tracker rarely ships an issue form, a contribution guide, or a support window, so step 1 of
the skill has nothing to read. What stands in for those files: the tracker's own required fields, the
last few items other people filed and were picked up, and whatever the team treats as ready to work
on. Read those before writing, the same way and for the same reason.

Two things change beyond that. The reader is a colleague who can ask you, so the report can be shorter
and can leave shared context unsaid; and the prior-proposal question becomes a search of the backlog
itself, including whatever was closed as not now. What does not change is the problem-first opening,
the success test, and the non-goals, which is what a backlog item is most often missing.

## What the request does not owe

Priority, severity, a milestone, an estimate, or a design. Those are the project's, and offering them
reads as scope you have already claimed.


<!-- ===== references/colleague-message.md ===== -->

# The short form: telling a colleague

Open this when the artifact is a chat message to someone who shares the codebase, not a filed issue.
The symptom-first rule, the goal-not-the-step rule, and the expected-behavior test apply unchanged,
and so does the rule against writing a step you did not execute. Putting the analysis last is
optional here: a colleague who shares the code often wants your theory, as long as it is marked as
one. The reproducer applies as the command and its output, without packaging it as a project or
reducing it. What lapses is everything that presupposes a tracker or a form: the
tracker search, the routing lookup, the issue-form lookup, and the project's external reproducer
oracle. Shared context may be assumed, and the message is a few lines long.

## The four rules

- **Put the ask in the first message.** A greeting alone buys a round trip and a wait. Send the
  question, the symptom, and what you need in one message.
- **Say what you already ruled out, and how.** This is the half that makes a short message useful. It
  tells the reader where not to look and shows what your evidence actually covers. It is also the
  antidote to the trap where you describe your attempted fix instead of the outcome you cannot reach:
  the ruled-out list is where an attempt belongs.
- **Name shared artifacts by identifiers that resolve.** A branch, a commit, a file, a symbol, a test
  name, and the ref they exist at. A colleague reads your message inside the repository; anything they
  cannot grep costs them a question.
- **Say what you want back.** A decision, a pointer, or a review. A message that describes a situation
  and stops has asked for nothing, and the reader has to guess whether it is theirs.

## What may be dropped, and what may not

| Drop | Keep |
| --- | --- |
| The project's vocabulary explained | The exact error text |
| The full environment | The version or branch, when it is not the obvious one |
| The template's field names | The literal you expect and the literal you got |
| Background you both lived through | What you already ruled out |

## The escalation

Where the answer turns out to matter beyond the conversation, the message becomes the first draft of a
filed report, and everything in the skill applies to it: the ownership check, the currency check, the
expected-behavior test, and a reproducer someone can run.


<!-- ===== references/machine-authorship.md ===== -->

# Reports written with a tool

Open this when the target project has an `AI_POLICY.md`, an AI clause in `CONTRIBUTING.md`, or an
AI-disclosure checkbox in its issue form. Several projects now write rules for this case specifically,
and an AI policy can carry a consequence of its own: a reporter blocked from filing again. Being
closed unread is the separate consequence of skipping a project's checklist.

## What the policies require

- **Disclosure, in the form the project asks for.** A checkbox, a sentence naming the tool and the
  extent of its use, or a statement that no tool was involved. Where a project asks, answer; do not
  volunteer a paragraph where a checkbox is asked for.
- **A human who can defend the report.** More than one project states that the person filing must be
  able to explain the content without the tool, and answer follow-up questions themselves. This is not
  yours to certify. Raise it before filing.
- **Brevity, stated as a rule about machine-written reports.** They run long, and a triager should not
  have to scan pages to reach the point. Summary and critical details first; every section carries a
  fact absent from the earlier ones.
- **No speculative impact.** "This could allow" and "this might lead to", with nothing observed behind
  them, are the tell that gets a report dismissed. State an impact you saw, and paste what you saw.
- **A reproducer that was tested, and a proposed fix that was run.** One project states it plainly: if
  you had a tool propose a fix, test it before reporting; if the reproducer does not work, the whole
  report is in question.
- **The channel's format.** Where reports travel by email, send plain text. Markdown decoration in an
  email report is noise to the person reading it in a mail client.

## What this does not settle

A policy tells you what disclosure is demanded. It does not tell you whether an agent-authored report
is welcome at all. Some projects restrict more than disclosure, including replies written with a
tool and generated images. Read the policy, and where it is ambiguous, ask the human before filing.


<!-- ===== references/worked-cases.md ===== -->

# Worked cases

Open this when an expected block failed the test in the skill and you need the repair, or when you
want to see the rules applied end to end. Each case pairs a draft that failed a rule with the report
that was accepted. Two accepted reports are the source of the repairs, and both are public and worth
opening: [gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
[junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041).

## Case 1: an index where the reader needs a value

The draft asked for a test-report entry named `methodInParameterizedClass(String)[2][1]`. Question 1
of the expected-behavior test passes: there is a literal. Question 2 passes: it is unique. **Question
3 fails.** The two ordinals index the argument source, and a reader who holds only the report cannot
tell what ran.

The repair is to name the thing and keep the index only as a tiebreak. The accepted report asks for
`firstParameterizedMethod(String) [1] value = ""` and states the reason in one line: an index does not
say what ran, and it moves when a row is added to the argument source, so a report archived last week
names a different case today.

It also separates the requirement from the rendering, in the report's own words: the exact rendering
is the project's to choose, and what the reporter needs is the method name and the arguments.

## Case 2: a proposed form nobody ran

The same draft argued for the index form partly on the grounds that a reader could re-run a single
case with it. **Question 5 fails:** no transcript, and the claim was never tested.

Running it produced the strongest section of the accepted report. Two invocations fail with
the tool's own message, a third form works, and the report says which one and why it is unavailable
from the report file. A rejected assertion became evidence.

The rule is about the claims around the proposal, not the proposal. The behavior you are asking for
does not exist, so nothing can run it. What can run is every claim you make about a tool you have, and
the argument for a shape is usually one of those.

## Case 3: a setting in the wrong role

The draft for JUnit opened around a configuration setting, so it read as "configuration is enough for
me" while asking for the default to change.

Apply the deletion test to the whole document: remove every sentence that mentions the setting. The
remaining text no longer stated a requirement, so the setting was the frame.

The accepted report puts the setting in the role the evidence supports. It does not fix the problem,
so it is neither a workaround nor an alternative: it is a negative result, and it appears under a
heading that says so, "Even `junit.jupiter.params.displayname.default` does not fix it", between the symptom and
the ask. Placed there it is the strongest argument that configuration cannot answer the request, and
placed last it would have been an aside.

A setting that does work is the other case, and it goes after everything that states the problem. The
accepted Gradle report carries its `Workaround` section there, with the causal analysis below it.

## Case 4: two symptoms in one block

The draft merged two symptoms: one class of parameterized test losing the method name, and another
losing the arguments of the class invocation.

The observable questions settle it. Could a maintainer accept one and refuse the other? Yes. Do they
live under different owners? Yes: one belongs to the build tool that writes the report file, the other
to the test framework that supplies the names, and they are different repositories. Two expected
blocks, and in this case two reports, each stating that it does not depend on the other.

## Case 5: a confident cause for a project that had already fixed it

The draft proposed filing against the test framework without checking whether the framework still had
the defect. It did not: two related reporting defects had been fixed and shipped in a maintenance
release.

The version and tracker checks catch this before any prose exists. The accepted report carries the
repaired form: it names the already-shipped fixes, bounds what each one covers, states that both were
verified on a released version and on a build from source, and then states the gap that remains. It
also carries a section arguing why the remaining gap belongs to that project and not to the build
tool, which is the honest answer when a defect lives at a boundary.

## Published before-and-after pairs worth copying

These come from the projects' own guidance rather than from the two reports above.

| Before | After |
| --- | --- |
| "Software crashes." | "Cancelling a File Copy dialog crashes File Manager." |
| "Browser should work with my web site." | "Down-arrow scrolling doesn't work in a `<textarea>` styled with `overflow:hidden`." |
| "How do I get the color picker to take a hexadecimal RGB value?" | "I am trying to replace an image's color table with values of my choosing. The only way I can see is to edit each slot, and the color picker will not take a hexadecimal RGB value." |
| "I get SIG11 errors on kernel compiles and suspect a hairline crack in a motherboard trace. How do I check for those?" | The hardware, the timings, and what was already swapped out. The theory is removed and the observations stay. |
| "hi" … four minutes … "what time was that thing again?" | Both in one message. |
