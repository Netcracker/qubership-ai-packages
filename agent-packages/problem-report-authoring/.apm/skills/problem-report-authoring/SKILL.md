---
name: problem-report-authoring
description: >-
  Load before writing or reviewing a report of a problem someone else has to act on: a bug report or
  issue in any tracker (GitHub, GitLab, Jira, a team's own backlog) or on a mailing list, a feature
  or change request, or a short problem message to a colleague. A session that reproduced something
  reaches this point when asked to write it up, file it, or tell the team. Also load for "review
  this draft", "is this ready to file", and before `gh issue create`, `glab issue create`, or a Jira
  create screen. Governs what the report establishes before its first sentence (which project owns
  the defect, whether the version is supported, whether the report exists already), what each slot
  carries, the test an expected-behavior block must pass, and the reports that pass every rule and
  are still useless. Not for a commit message or pull request description
  (change-description-authoring), a documentation page (docs-page-authoring), or the regression
  test (test-authoring).
---

# Authoring a problem report

This skill governs **what a problem report establishes before it is written, what each part of it
carries, and how a reviewer detects a bad one without the author present**. Wording, tense, sentence
length, and dialect belong to the developer-style skill of the language the report is written in
(`english-developer-style` for English); load it too.

Three artifacts fall under it, and they share a spine: a bug report, a feature or change request, and a
short problem message to a colleague. The channel can be any tracker or a mailing list, and the
project can be someone else's or your own: the person who picks the report up months from now knows
no more than a stranger would. What differs between the three is length, what may be left unsaid,
and the opening of a request (§3).

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

1. **Step 1. Read the channel.** Where this project takes reports of this kind, the form or template and its
   required fields in their order, the markup the channel renders, the contribution guide, the AI
   policy, the security channel, and the support window. Record the required field names and their
   order before writing a sentence. Where the person filing has already named the channel or the
   format, use what they said. What to read on each platform, and what stands in for the form on a
   mailing list or in a team's own backlog: `references/project-conventions.md`.
1. **Step 2. Establish ownership and currency.** Which project owns the defect, whether it survives on a
   supported version, whether it is already reported, and how many reports this is (§4).
1. **Step 3. Write into the form's fields, in the form's order,** with §3 governing what goes in each.
1. **Step 4. Apply the expected-behavior test** to every expected block (§5). This is the center of the
   skill.
1. **Step 5. Run your own checks and paste the transcripts** (§6), answer what the project asks of a report
   written with a tool (§7), fill or mark every required field (§8), and hand over what you could not
   do (§10).

## 3. Framing

- **Open with the user-facing symptom, in the project's vocabulary.** "I do X, Y breaks", before any
  statement about the project's internals. R1, R4, R5. *Test:* read the first paragraph. If its
  subject is a class, a function, a file, or a commit inside the target project rather than an action
  you took, it fails.
- **The title names the symptom, not the fix you have in mind.** R1, R4. Where the channel prefixes
  titles with a component or a tag, keep the prefix and put the symptom after it. *Test:* a defect
  title containing `add`, `make`, or `change` aimed at the project is naming a solution.
- **Mark causal analysis as a guess, and make the report stand without it.** R1, R2. Even a correct
  analysis is no substitute: the project has to see the failure happen before it fixes anything, and
  an analysis the report leans on is a report about your theory. Mark the block once, at its head, and
  say there that the rest stands without it, as `gradle/gradle#39079` does. Add it as a section of
  your own, or write it into a form field whose own text asks for a cause or a diagnosis. The rule
  says nothing about position, so it holds under any field order and inside a single description box.

  *Test (the analysis deletion test):* two questions. **Delete the block you marked. Do the symptom,
  the expected behavior, the steps and the pasted output still stand on their own?** If what remains
  no longer states the problem, the analysis was carrying the report. **Then: does any sentence naming
  a place in the project's code as the cause of the failure sit inside the symptom, the steps, or the
  pasted output?** Each one is a defect there, wherever the form puts its fields. The expected block
  is not covered by the second question: grounding an expectation in the project's own code, its
  documentation or the error it raises is what §5 asks for, and saying why the behavior is wrong is
  not the same as saying where it breaks.

- **State the goal, not only the step you got stuck on.** R2, R5. *Test:* a sentence names the task
  you, or the user you stand for, could not complete, in words that do not depend on the project's
  API.
- **Describe what you did and what the machine did, in order.** R1, R3. Each step has an observable
  result.
- **Where the target form's field order disagrees with this skill, the form wins.** R1. Projects order
  actual and expected behavior differently, and one project can order its bug form and its feature
  form oppositely. What survives any field order is the opening: whichever field the form puts first,
  its first sentence is an action you took and what you observed, not a place in the project's code.
  *Test:* compare your fields, or your headings where the form is a template, against the form's own
  labels, in sequence.
- **A message to a colleague is the same spine, shortened.** R5. What may be dropped is the context you
  share; what may never be dropped is the ask itself. `references/colleague-message.md`.
- **A request leads with the problem, not with the API you want.** R2. The first section names a task
  you could not complete, not a construct the project lacks. The rest of the request genre is
  `references/request-genre.md`.
- **A known workaround goes after everything that states the problem, and the expected behavior must
  not depend on it.** R2. A report framed around its own workaround reads as "configuration is enough
  for me" while asking for the default to change. *Test (the workaround deletion test):* delete every
  sentence that mentions the workaround or the setting you tried. If what remains no longer states a
  requirement, one of them was the frame.
- **A setting you tried that does not solve the problem is neither a workaround nor an alternative.**
  R2. It is a negative result, and it belongs with the symptom, under a heading or in a sentence that
  says it does not fix the problem; where the form has no slot between the symptom and the ask, it
  closes the field that states the symptom. A setting that fixes one symptom and not another is a
  workaround for the first and a negative result for the second, and the workaround section says
  which. Putting a failed setting last with the alternatives hides the strongest argument that
  configuration cannot answer the request. *Test:* find where the report says what happened when the
  setting was tried. If the report never says that the setting fails, or a setting that fixes nothing
  is filed under a workaround or alternatives heading, the setting is in the wrong role.

## 4. Before you file: ownership, currency, duplicates, count

- **Isolate which project owns the defect, and put the commands and their outputs in the report.**
  R1, R2. A symptom seen through a stack is not evidence about any layer in it. Where the project's
  guide publishes its own isolation procedure, run that one. Where none is published, remove one
  layer at a time and record each result. *Test:* the report contains a command sequence a reviewer
  can re-run, whose last step uses only the target project. Where the defect only appears through a
  dependency, the last step is the shortest chain that still fails, and the report names the
  dependency that stays and why: either it was removed and the failure went with it, or the symptom
  cannot exist without it. Report the elimination, not the conclusion. For a request there is no
  failing run, and the argument comes from the contract instead (`references/request-genre.md`).
- **Reproduce on a version the project still supports, and say which.** R1, R2. A defect already
  fixed in a release you did not test is a common reason a report comes back as not reproducible. For
  a team's own project, the supported version is the release that is deployed or the branch the team
  maintains. *Test:* the version is stated exactly, as a release number or a commit, in the form's
  version field or a versions section of your own; it falls inside the support window; and where the
  reproducer declares a version, it declares the same one.
- **Search for the report, and write the nearest hit into the report.** R1, R4. Search the tracker
  with closed and resolved items included, or the list archive where reports travel by email, and
  say what makes yours different from the nearest hit. Record the query as well, in the report where
  the form asks what you searched and otherwise in the hand-over note (§10), because a null result
  establishes nothing on its own. Do not suppress a report because something similar exists; a second
  report of a live defect is cheap and usually adds information. Where you cannot reach the tracker,
  the report says the search was not done, and the note carries the queries the person filing should
  run. An unreachable tracker is a gap to hand over, not a step to drop.
- **File one report per owner, and one expected block per independently fixable symptom.** R1, R2,
  R3. *Test:* count the distinct expected outcomes, then ask two questions. Do they live under
  different owners, in different repositories, or in components with different maintainers? That
  makes two reports. Could a maintainer accept one and refuse the other on its merits? That makes two
  expected blocks, in one report where the owner is the same. Where you cannot tell, file separately
  and link the two reports: a maintainer can merge two reports and cannot split one. Each report says
  that it does not depend on the other.
- **Obey the project's routing.** R1. Contact links, "ask here instead" lines, issue types, and
  component questions decide where this belongs. A correct report in the wrong queue is closed
  regardless of its quality. A suspected vulnerability never goes to a public tracker or list: the
  project's security channel takes it, and whether to send it there is the human's call (§10).

## 5. The expected-behavior test

Send every expected block through six questions in order. The first "no" is the finding.

1. **Question 1. Is there a literal?** At least one string, number, exit status, or emitted artifact that a
   machine could compare against. An expected block built from adjectives, such as correct,
   consistent, or works, states nothing.
1. **Question 2. Is the literal sufficient?** Could two materially different outputs both satisfy it? Hand the
   block to a reviewer and ask them to write the assertion from it alone. If they cannot, it fails.
1. **Question 3. Does every identifier resolve by content?** Name the thing; do not index it. An ordinal, an
   offset, or a position identifies nothing to a reader who holds only your text, and it moves when
   the underlying data changes, so a report archived last week names a different case today. Where the
   artifact's own vocabulary is positional, such as a byte offset or a line number, keep the ordinal
   and put the content beside it.
1. **Question 4. Is the grounding named, and how strong?** State what the expectation rests on, naming something
   fetchable, in the block or in a section of its own that the block points to. Strongest first: the
   project's own documentation or specification; runtime logic, meaning a crash, an assertion, or an
   error the project itself raises; the expectation of its user community. Weaker: an industry
   standard the project does not claim to implement, another product's behavior, what the project
   used to do, and your own preference. The order is not taste: maintainers act on the first three
   and most often close a report grounded in the next three as invalid, and a personal preference is
   weak because nothing outside you supports it. Use a weak grounding where it is all you have, and
   say that it is weak. Prior behavior becomes strong only where the project ships a regression form
   that makes the last working version a required field.
1. **Question 5. Was every claim about today's behavior executed?** The behavior you are asking for does not exist
   yet, so it cannot be run. Everything you say around it can: that a form works in an existing tool,
   that a reader could re-run one case from it, that another consumer of the same data already renders
   it, that the setting does not help. Each of those is a claim about a tool you have, and each needs a
   pasted transcript. Proposing a shape because it would let a reader do something, without having
   tried it, is how a report acquires a claim that is simply false. Mark the proposed rendering as one
   possible shape; make the claims around it verifiable. *Test:* every sentence about what a tool does
   today has a pasted command or output behind it.
1. **Question 6. One block per symptom, and is the requirement separated from the rendering?** Say which part you
   need and which part is the project's to choose. A maintainer must be able to accept the requirement
   and reject the shape.

Do not ground an expectation only in another system's behavior, and never without stating the value
you expect. Worked repairs: `references/worked-cases.md`.

## 6. The reproducer

- **Everything needed to reproduce is in the report.** R1, R3. Every file, version, and command it
  references is present or publicly fetchable.
- **Run what you ship, after your last edit to it, from a clean directory.** R1, R2. Reduction
  silently fixes the defect often enough that this is the check with the highest yield. *Test:* the
  pasted output carries incidental detail nobody invents, such as paths, timestamps, and the tool's
  exact punctuation, and it matches the shipped reproducer's own identifiers.
- **Reduce until nothing outside the target project is needed, then stop.** R1, R2. This is the
  ownership procedure of §4 run to its end: reduction earns its keep by eliminating suspect layers,
  not by being small. Where the defect only appears through a dependency, say so and ship the
  shortest chain.
- **Ship it in the form the channel accepts.** R1. Projects disagree: one requires a repository or an
  archive, another forbids both and wants an inline snippet, a third wants a link to a running
  reproduction, and a mailing list wants it inline or linked because attachments may not arrive. The
  form's own field text, or the project's reporting guide, decides.
- **Paste the failing output verbatim, as text.** R1, R4. Not a screenshot, not a paraphrase. R4
  arrives by searching for that string. *Test:* the report carries the tool's own output as text,
  punctuation included, in a code block where the markup has one and indented where it has none.
- **Give the version of the target project and of every layer between it and the symptom.** R1, R4.
  *Test:* every tool named in the reproduction chain has a version string somewhere in the report.
- **Where the project provides a reproducer oracle, run it and link the run.** R1, R2. A linked run
  is evidence a triager can open, which no sentence in your report is. *Test:* the report carries a
  link to a run that shows the failure being reported.
- **Never write a step you did not execute.** R1, R2. Where you could not run something in this
  session, the report does not claim it: say what is missing and what would establish it, and put the
  command in the hand-over note (§10).

## 7. Reports written by an agent

- **Put the summary and the critical details where the reader meets them first:** the title and the
  opening sentence of the first field. R1. Do not make a triager scan pages; each section carries at
  least one fact absent from every earlier one (§9). *Test:* the version, the symptom, and the
  expected value are all reachable without scrolling past a section that restates another.
- **Do not enumerate speculative consequences.** R1, R2. "This could allow" with no observed instance
  is the tell triagers name. Keep an impact you actually observed, and paste the observation.
- **Disclose the tool where the project asks, in the form it asks for.** Read the policy first; some
  projects also constrain who may answer follow-up questions. `references/machine-authorship.md`.

## 8. Filling the form

- **Fill the project's required fields, by their names, so the text drops in unchanged.** R1. This
  buys admission and routing: projects close reports that skip the checklist, and component fields
  decide who sees it. It buys nothing else: a filled form is the condition for being read, not a
  finished report. Where the tracker has fields rather than a text template, such as a Jira create
  screen, fill the fields and keep the description for what has no field of its own. Where the
  channel has no fields at all, as on a mailing list, the sections the project's reporting guide
  names are the form, and the version, the environment, and the reproducer go in the body. Your own
  sections may sit inside a field or after the form's last field; they never replace one. A template
  heading nothing enforces and you have nothing for may be dropped, a required field never.
- **A field you have no evidence for says what is missing, not a plausible guess.** R1, R2. "Not
  established: I could not test on Windows" is usable. An invented environment is worse than a blank.
- **Write in the markup the channel renders.** R1, R4. A fenced block in a channel that renders plain
  text arrives as literal backticks, and Markdown decoration in an email is noise to the reader's
  mail client. *Test:* open an item already filed in the same place and look at how its author entered
  a code block and a heading; use that.

## 9. Reports that pass every rule and are still useless

| Shape | Detection |
| --- | --- |
| Every field filled, nothing said | Cross-field consistency: the version the report states is the one the reproducer declares, where it declares one, and the identifiers in the expected block appear in the reproducer. A form whose fields do not reference each other is filled, not written |
| "It should work" | Question 2 of §5: ask whether a reviewer could write the assertion from the block alone |
| A reproducer that was never run | Re-run it. Composed output lacks incidental detail; this is why the check is a run and not a reading |
| A confident cause for a project that already shipped the fix | The version check and the tracker search of §4, against closed issues and release notes as well as open ones |
| A report framed around its own workaround | The workaround deletion test in §3 |
| The same fact in four sections | Each section must contain a fact absent from every earlier section |
| A grounding that names a document which does not say it | Fetch the named artifact and read the sentence claimed for it |

## 10. What is not yours to decide, and what you hand over

Raise these and let the human answer:

- Whether the person filing can explain and defend the report without the tool that wrote it. Several
  projects make this a condition of filing.
- Whether to file at all when personal preference is the only grounding available.
- Whether a project's AI policy permits an agent-authored report.
- Whether the request is one the project would want, and what it is worth.
- Whether a defect that may be a vulnerability goes to the security channel, and in what form.

**The report states a gap; the hand-over note says what to do about it.** A tracker you could not
reach, a reproducer you could not run, a version you could not install, a sign-off only a person can
give: the report says, in the field concerned or beside the claim it would have supported, that this
was not established, and never claims the work. The note to the person filing, kept apart from the
report body, carries each gap with the query or the command that would close it.

## 11. Review checklist

Run it over a draft, yours or someone else's. Every item gets an answer, "none" included.

- Channel: is this the place the project names for this kind of report, and is the markup the one it
  renders?
- Title: does it name the symptom, or a fix you have in mind?
- First paragraph: an action you took and what broke, or a class inside the project?
- Summary: are the version, the symptom, and the expected value reachable without scrolling past a
  section that restates another?
- Goal: is the task you could not finish stated, and not only the step you got stuck on?
- Routing: does the project want this here, and does the report match none of its redirect conditions?
- Ownership: is the isolation in the report as commands and outputs, for a request as the contract
  argument, or only as a conclusion?
- Currency: is the version stated exactly, inside the support window, and the same one the
  reproducer declares?
- Duplicates: is the nearest hit in the report with what makes this one different, and is the query
  recorded?
- Count: how many owners, so how many reports; how many independently fixable symptoms, so how
  many expected blocks?
- Expected behavior: run the six questions of §5 over every block, and name which question failed.
- Grounding: which of the seven sources is it, and is a weak one marked weak?
- Execution: does every claim about what a tool does today carry a pasted transcript, and is a
  proposed rendering marked as one possible shape?
- Analysis: is the block marked as a guess, does the report stand when you delete it, and does any
  sentence naming the cause sit inside the symptom, the steps, or the pasted output?
- Workarounds: is a setting that works placed after everything that states the problem, and a setting
  that failed stated as a failure rather than filed as a workaround or alternative? Run the
  workaround deletion test on both.
- Impact: is every consequence the report names one you observed and pasted?
- Reproducer, for a filed report: is it complete, in the form the channel accepts, does it depend
  on nothing outside the target project or name the layer that stays and why, does the pasted output
  carry incidental detail and match the reproducer's own identifiers, does each step have an
  observable result, is the failing output pasted as text, does every layer in the chain carry a
  version, and where the project offers a reproducer oracle, is its run linked?
- Disclosure: does the project ask anything of a report written with a tool, and is it answered?
- Form: do the form's fields appear by name in the form's order, with your own sections inside or
  after them and never in place of one, and does every required field carry an observation or an
  explicit "not established"?
- Request: are the slots of `references/request-genre.md` present, and does it pass the API
  deletion test?
- Colleague message: is the ask in the first message, the ruled-out list present, every identifier
  one that resolves in the shared repository, and the reply you want named?
- Raised: are the questions of §10 put to the human, and not answered in the report?
- Hand-over: is every step you did not execute and every check you could not run stated in the
  report as not established, and carried in the note with the command that would close it?
- Vacuous shapes: run §9.
