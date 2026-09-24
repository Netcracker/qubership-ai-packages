---
name: problem-report-authoring
description: >-
  Load before writing or reviewing a report of a problem someone else has to act on: a bug report or
  issue in any tracker (GitHub, GitLab, Jira, a team's own backlog) or on a mailing list, a feature
  or change request, a question when you are not sure it is a defect, a vendor support ticket, a
  comment on an existing report, or a short problem message to a colleague. A session that
  reproduced something reaches this point when asked to write it up, file it, or tell the team. Also
  load for "review this draft", "is this ready to file", and before `gh issue create`, `glab issue
  create`, or a Jira create screen. Governs what the report establishes before its first sentence,
  what each slot carries, how evidence is attributed, the test an expected-behavior block must pass,
  and the reports that pass every rule and are still useless. Not
  for a commit message or pull request description (change-description-authoring), a docs page
  (docs-page-authoring), or the regression test (test-authoring).
---

# Authoring a problem report

This skill governs **what a problem report establishes before it is written, what each part of it
carries, and how a reviewer detects a bad one without the author present**. Wording, tense, sentence
length, and dialect belong to the developer-style skill of the language the report is written in
(`english-developer-style` for English); load it too.

The artifacts under it share one structure: a bug report, a feature or change request, a question
where you are not sure the behavior is a defect, a support ticket to a vendor, and a short problem
message to a colleague. The channel can be any tracker, a forum, a support portal, or a mailing list,
and the project can be someone else's or your own: the person who picks the report up months from now
knows no more than a stranger would. What differs between them is length, what may be left unsaid,
which rules lapse, and the slots each genre adds: the opening and the slots of a request are in
`references/request-genre.md`, the question and the support ticket in
`references/question-and-support-ticket.md`, the colleague message in `references/colleague-message.md`,
and what a team's own backlog reduces in `references/project-conventions.md`. The head of §11 says
which checks each genre owes.

**The form you already know is the wrong one.** A change description is written for a reader who
holds the diff: it names the symptom and moves at once to the mechanism and the fix, inside a
project both of you work on. A triager holds no diff, your cause is a guess, and the fix is the
project's to choose, so that shape produces a report that opens inside the target project's
internals and argues for a patch. Writing a report in the shape of a pull request description is the
failure this skill exists to prevent.

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

The expensive work happens before any prose exists. Steps 1 and 2 can invalidate the whole report,
and step 2 can send you back to step 1: a support window read there can rule the version out, and a
routing rule can move the report to another project, whose channel you then read. A step you cannot
complete does not hold the report back: the report says what was not established where a claim
rests on it or a triager asks it (§10), and the hand-over note carries the step. The
routing and the security lookups are not gaps to file past: a suspected vulnerability with no
private channel found stays with you (§4). What every report has to carry is an observation, the
context a reader needs to act on it, and the ask; the steps raise the confidence a reader can place
in it.

1. **Step 1. Establish ownership and currency.** Which project owns the defect and whether it survives
   on a version that project still supports (§4). The channel you read next is that project's.
1. **Step 2. Read the channel.** Where that project takes reports of this kind, the form or template
   and its required fields in their order, the markup the channel renders, the contribution guide,
   the AI policy, the security channel, and the support window; then search it for the report (§4).
   Record the required field names and their order before writing a sentence. Where the person
   filing has already named the format or the fields, what they named stands in for the form: write
   into it, and skip the lookup that would have established it. A channel they named is still
   checked against the routing and the security policy. Where you cannot reach the project (a
   sandboxed session, an offline checkout), read what a local clone carries and list the lookups you
   could not do in the hand-over note (§10). What to read on each platform:
   `references/project-conventions.md`.
1. **Step 3. Write the core (§7) where the form's opening goes, then the fields in the form's
   order,** with §3 governing what goes in each and §6 governing how each piece of evidence is
   attributed and pasted. Count the reports and the expected blocks (§4) once the expected outcomes
   are written down, because the count is taken over them.
1. **Step 4. Apply the expected-behavior test** to every expected block (§5). This is the center of the
   skill.
1. **Step 5. Answer what the project asks of a report written with a tool** (§7), fill or mark every
   required field (§8), and hand over what you could not do (§10).

## 3. Framing

- **Open with the user-facing symptom, in the project's vocabulary.** "I do X, Y breaks", before any
  statement about the project's internals. R1, R4, R5. *Test:* read the first paragraph. Its subject
  is an action you took or the surface the project documents for its users: a public method or type,
  a command, an endpoint, a configuration key, a screen. For a library the public API is that
  surface, so "`getObject(int, LocalDateTime.class)` returns the wrong hour across a DST change"
  passes. A first paragraph whose subject is a private class, a source file, or a commit inside the
  target project fails: it opens inside internals a triager has not seen. In your own project, and
  in a message to a colleague, a class, a service, or a commit is shared vocabulary and may be the
  subject, as long as the paragraph still says what the user or the caller observed
  (`references/project-conventions.md`, `references/colleague-message.md`). A request and a question
  open with the task you could not complete instead, in your own words
  (`references/request-genre.md`, `references/question-and-support-ticket.md`); the test there is
  that the first paragraph names the task before it names anything the project lacks.
- **The title names the symptom, not the fix you have in mind.** R1, R4. Where the channel prefixes
  titles with a component or a tag, keep the prefix and put the symptom after it. *Test:* a defect
  title containing `add`, `make`, or `change` aimed at the project is naming a solution. A request's
  title names the task you cannot do or the capability, not the API you propose.
- **Mark causal analysis with the confidence you have, and make the report stand without it.** R1, R2.
  A reading of the source is a guess, and the block says so once, at its head, and says there that the
  rest stands without it. A cause established by an experiment, such as a revert or a bisect, is not a
  guess: say which experiment and paste it, and it becomes evidence under §6. Either way the project
  has to see the failure happen before it fixes anything, and a report that leans on the analysis is a
  report about your theory. Add the analysis as a section of your own, or write it into a form field
  whose own text asks for a cause or a diagnosis. The rule says nothing about position, so it holds
  under any field order and inside a single description box.

  *Test (the analysis deletion test):* two questions. **Delete the block you marked. Do the symptom,
  the expected behavior, the steps and the pasted output still stand on their own?** If what remains
  no longer states the problem, the analysis was carrying the report. **Then: does any sentence you
  wrote name a place in the project's code as the cause, inside the symptom or the steps?** Each one is
  a defect there, wherever the form puts its fields. A pasted stack trace, a profile, or a diagnostic
  the project itself raises names the project's code on its own; that is evidence, and it stays
  verbatim (§6). The expected block is not covered by the second question either: grounding an
  expectation in the project's own code, its documentation, or the error it raises is required by §5,
  and saying why the behavior is wrong is not the same as saying where it breaks.

- **State the goal, not only the step you got stuck on.** R2, R5. *Test:* a sentence names the task
  you, or the user you stand for, could not complete, in words that do not depend on the project's
  API.
- **Describe what you did and what the machine did, in order.** R1, R3. Each step has an observable
  result. A step is a command, a click, a request, or a deploy; the result is what you saw after it.
- **Where the target form disagrees with this skill on order or on the meaning of a field, the form
  wins.** R1. Projects order actual and expected behavior differently, and one project can order its
  bug form and its feature form oppositely. Every ordering preference in this skill yields: actual
  before expected, the workaround after the problem, the analysis in a section of its own. A field
  labeled for expected behavior, a proposed solution, or a workaround carries what its label asks for,
  wherever the form puts it, and never the actual behavior because it happened to come first. What
  survives any field order is the opening: the first field whose label asks what happened, for a
  description, or for the steps, wherever the form places it after version and environment pickers,
  starts with an action you took and what you observed. Where a form has no such field, that sentence
  opens the first free-text field under a heading of its own (§8). For a request or a question the
  opening names the task you could not complete, and the field it goes in is the one
  `references/request-genre.md` names. *Test:* compare your fields, or your headings where the form
  is a template, against the form's own labels, in sequence, and read each field against its label.
- **Say when you are not sure it is a defect.** R1. A report that claims a bug and turns out to be a
  misuse costs a triager a round trip; a question that says "I expected X from the documentation at Y,
  I got Z, is this a defect or my misuse" goes where the project takes questions and is answered
  there. The slots of that form: `references/question-and-support-ticket.md`.
- **A message to a colleague is the same structure, shortened.** R5. What may be dropped is the context
  you share; what may never be dropped is the ask itself. `references/colleague-message.md`.
- **A request leads with the problem, not with the API you want.** R2. The first section names a task
  you could not complete, not a construct the project lacks. The rest of the request genre is
  `references/request-genre.md`.
- **A known workaround goes after everything that states the problem, and the expected behavior must
  not depend on it.** R2, R4. A workaround is a setting or a step that makes the failure go away. A
  report framed around its own workaround is read as "configuration is enough for me" while it asks
  for the default to change. Where the form has a workaround field, the workaround goes there. *Test
  (the workaround deletion test):* delete every sentence that mentions a workaround. If what remains no
  longer states a requirement, the workaround was carrying the report. A setting that defines the
  failing case is not a workaround and stays: "with `maxRetries=0` the client still retries" is the
  symptom, and deleting the setting would delete the report. A workaround you ran carries the
  measurement that shows what it changed, such as the failure rate before and after it; where the
  measurement you would expect to move did not, say which one did.
- **A setting you tried that does not solve the problem is a negative result, not a workaround.** R2.
  It belongs with the symptom, under a heading or in a sentence that says it does not fix the problem.
  A setting that fixes one symptom and not another is a workaround for the first and a negative result
  for the second, and the workaround section says which. A failed setting filed under a workaround or
  alternatives heading hides the strongest argument that configuration cannot answer the request.
  *Test:* find where the report says what happened when the setting was tried. If it never says that
  the setting fails, the setting is in the wrong role.

## 4. Before you file: ownership, currency, duplicates, count

- **Isolate which project owns the defect, and put the evidence in the report.** R1, R2. A symptom
  seen through a stack is not evidence about any layer in it. Where the project's guide publishes its
  own isolation procedure, run that one. Where none is published and the failure can be re-run,
  remove one layer at a time and record each result. Where nothing can be re-run (a production
  incident, a hosted service, a visual defect), isolate by observation with one thing varied: which
  layer's code the trace stops in, which browser or theme or platform shows it and which does not,
  which build first showed it. Report the elimination, not the conclusion. *Test:* the report
  contains either a sequence a reviewer can re-run whose last step uses only the target project, or
  the observations that vary one thing at a time and what each showed. Where the defect only appears
  through a dependency, the last step is the shortest chain that still fails, and the report names
  the dependency that stays and why: either it was removed and the failure went with it, or the
  symptom cannot exist without it. For a request there is no failing run, and the argument comes from
  the contract instead (`references/request-genre.md`).
- **Reproduce on a version the project still supports, and say which.** R1, R2. A defect already
  fixed in a release you did not test is a common reason a report comes back as not reproducible. For
  a team's own project, the supported version is the release that is deployed or the branch the team
  maintains. *Test:* the version is stated as an identifier that resolves to one build: a release
  number, a commit, an image tag with its digest or build SHA, a CI build number; for a hosted
  service, the environment URL and the timestamp of the observation with its timezone; for a
  documentation defect, the page URL and the version it shows. It falls inside the support window,
  and where the reproducer declares a version, it declares the same one. A regression declares two,
  the last good and the first bad, and the bisected commit where you have it.
- **Search for the report, and act on what you find.** R1, R4. Search the tracker with closed and
  resolved items included, or the list archive where reports travel by email, and write the nearest
  hit into the report with what makes yours different. An open report of the same defect takes your
  evidence as a comment, not a second report, unless the project's process says otherwise. The
  comment carries the version you saw it on, what in your case differs from the thread, and your
  transcript where the thread has none or a different one; it restates nothing the thread already
  says, and it is not a bare "same here". A report closed as fixed sends you back to the version
  check. A report closed as will-not-fix or a rejected proposal is cited, with what changed since. A
  related but different problem gets a linked report. Record the query in the slot the form or the
  genre has for what you searched. Where it has none and the search found something, the report
  names the nearest hit and the difference in one sentence, and the query goes to the hand-over
  note. An open pull request that already makes the change is the nearest hit; whether a comment
  there serves better than a new report is for the person filing (§10). Where the search
  found nothing, the sentence that says so carries the query, because a null result establishes
  nothing on its own and a reader can judge it only by the query. Where you cannot reach
  the tracker, the hand-over note (§10) carries the queries the person filing should run; an
  unreachable tracker is a gap to hand over, not a step to drop.
- **File one report per owner, one expected block per independently actionable problem, and describe
  the dependencies you know.** R1, R2, R3. *Test:* count the distinct expected outcomes, then ask two
  questions, in order. Do they live under different owners, in different repositories, or in
  components with different maintainers? That makes two reports, always. Under one owner: could a
  maintainer fix one without touching the other? If so, they are two expected blocks in one report
  where the symptoms share a component and the project's guide does not ask for one problem per
  issue (a step 2 lookup), and two linked reports where they share no component or the guide asks
  for one problem per issue. Two outcomes a maintainer cannot fix separately are one block. Where
  you cannot tell, file separately and link the two: a maintainer can merge two reports and cannot
  split one. Each report says what it depends on: nothing, the other report, or a coordinated change
  on both sides, as in a protocol change that needs the client and the server together.
- **Obey the project's routing.** R1. Contact links, "ask here instead" lines, issue types, and
  component questions decide where this belongs. A correct report in the wrong queue is moved or
  closed, and either way it waits. A suspected vulnerability never goes to a public tracker, forum,
  or list, and never into a public search or a public reproducer run with the exploit in it. The
  project's security channel takes it; where none is published, the platform's private reporting, a
  security address, or a maintainer contact stands in, and until one is found the report stays with
  you. The human decides whether to send it and to whom (§10). The private report carries the
  versions you saw it on, the observation or the proof of concept in the form the private channel
  accepts, the impact you observed and, marked as unconfirmed, the impact you suspect, and what you
  expect about disclosure. Where the platform has a private reporting form, that form has fields of
  its own, and it is the form step 2 reads for this report.

## 5. The expected-behavior test

Send every expected block through seven questions in order. The first "no" is the finding.

1. **Question 1. Is there something a machine could check?** At least one literal, such as a string, a
   number, an exit status, or an emitted artifact, or one relation between observables, such as
   "keyboard focus stays inside the dialog" or "a retried request creates no second payment". An
   expected block built from adjectives, such as correct, consistent, or works, states nothing.
1. **Question 2. Does it separate acceptable from unacceptable behavior?** Hand the block to a reviewer
   and ask them to write the assertion from it alone. If they cannot, it fails. An invariant, a range,
   or a relation passes when the assertion follows from it; an exact literal is required only where
   the exact value matters, and then it is stated.
1. **Question 3. Does every identifier resolve by content?** Name the thing; do not index it. An ordinal, an
   offset, or a position identifies nothing to a reader who holds only your text, and it moves when
   the underlying data changes. Where the artifact's own vocabulary is positional, such as a byte
   offset, a line number, or an array index, keep the ordinal and put the content beside it.
1. **Question 4. Is the grounding named, and how strong?** State what the expectation rests on,
   naming something fetchable, in the block or in a section of its own that the block points to.
   Seven sources, strongest first. (1) The project's own documentation or specification, which
   includes its compatibility promise, so a documented or tested behavior that changed with no
   changelog entry, a public API a semantic versioning statement covers, and a behavior an earlier
   release the project still supports had, with the last good and the first bad named, are all
   grounded here, whether or not a page states the behavior; where the project's compatibility
   statement excludes undocumented behavior, a regression of such behavior is source 6. (2) Runtime
   logic, meaning a crash, an assertion, or an error the project itself raises. (3) The expectation
   of its user community. Weaker: (4) an industry standard the project does not claim to implement,
   (5) another product's behavior, (6) a behavior the project never documented and you relied on,
   and (7) your own preference. The order is not taste: maintainers act on the first three, a report
   grounded only in the next three is the one commonly closed as invalid, and a personal preference
   is weak because nothing outside you supports it. Use a weak grounding where it is all you have,
   and say what it rests on in plain words, such as "I am the only case I know of"; do not write the
   word "weak" into the report. Where the artifact follows the rule you expect everywhere except in
   the place you report, as with a file that pins every call but one, that consistency supports the
   block once you have checked that the exception has no stated reason: a comment, a document, or a
   difference in what it does. It is not the project's specification. Name the strongest grounding
   first, and add another only where it establishes a requirement the first does not: a policy the
   project is bound by, such as one of the organization that owns it, or a constraint of the person
   asking, attributed to them, that explains why an existing option does not serve them
   (`references/request-genre.md`).
1. **Question 5. Was every claim about today's behavior observed, or read from a document?** The
   expected behavior may not exist anywhere yet, so nothing runs it. Everything you say around it
   can be checked: that a setting does not help, that another consumer of the same data shows the
   value, that the previous release behaves differently, that a reader could re-run one case from
   the proposed form. Each of those is a claim about a tool you have, and each needs a transcript or
   an observation, attributed under §6. A claim about what a document states, such as a limit, a
   default, or a service level, cites the document at the sentence that makes it; a claim that a
   tool does something when run is observed, because a page can be stale. Proposing a shape because
   it would let a reader do something, without having tried it, is how a report acquires a claim
   that is simply false. Mark the proposed rendering as one possible shape; make the claims around
   it verifiable. *Test:* every sentence about what a tool does today has a pasted command, output,
   attributed observation, or cited document behind it, and a claim about a run has a run.
1. **Question 6. One block per independently actionable problem (§4), and where the ask is about the shape
   of an output, is the requirement separated from the rendering?** For a name, a message, a layout,
   or a format, say which part you need and which part is the project's to choose. A maintainer must
   be able to accept the requirement and reject the shape.
1. **Question 7. Where the obvious shape is impossible, does the block say so?** Ask what a
   maintainer will say first against the requirement. Where it is that the thing cannot be done and
   you hold a shape that works, checked against a document or a run, give it in one sentence marked
   as one possibility. Where you hold none, say what makes the obvious shape impossible and leave
   the mechanism open: not knowing how to implement it does not fail the block, and neither does a
   crash, an outage, or a new capability whose fix nobody outside the project can know. An
   unchecked shape is marked as untested (question 5). An objection that something already covers
   it is answered where §3 puts a negative result, not repeated here. *Test:* the block does not
   read as asking for something the maintainer knows to be impossible.

Whatever the grounding, state the value you expect. A block grounded in another system's behavior
alone says what that system does, not what this one promised, and it says in plain words that this is
all it rests on. Worked repairs: `references/worked-cases.md`.

## 6. Evidence and the reproducer

- **Every claim carries its source.** R1, R2. There are four kinds, and the report says which:
  reproduced by you in this session, with the transcript; observed by the reporter or another
  person, with their transcript, log, or recording and their name or role; documented, with the
  document; inferred, and marked as such. The inferred kind is the kind of a causal analysis no
  experiment established (§3) and never of a claim about today's behavior, which question 5 of §5
  requires observed or documented. Evidence someone else gathered is evidence, attributed to them,
  and the report does not present it as your reproduction. The rule against invention: **never write
  a step nobody executed.** A step the reporter ran counts, attributed; a CI run counts by its link;
  a step nobody ran is stated as not established, and the command goes in the hand-over note (§10).
- **Everything needed to reproduce is in the report.** R1, R3. Every file, version, and command it
  references is present or publicly fetchable. A suspected vulnerability is the exception: its
  reproducer travels only through the private channel (§4).
- **Remove what is secret in every channel, rename what is private where the channel leaves the
  organization, and keep the reproducer runnable.** R1, R2, R3. A tracker, a chat, and a list
  archive keep what they are given, so read every transcript, log, request, configuration file,
  screenshot, recording, and reproducer before it goes in. A secret or a personal datum (an
  authorization header, a token, a session cookie, a URL with a key in it, a customer's record) is
  replaced with a placeholder that names what stood there, such as `<redacted: bearer token>`, in
  every channel. Where the datum is the input that triggers the failure, as with a record a parser
  or an import rejects, replace it with a synthetic value of the same shape that still fails and
  re-run the reproducer with it; where only the real value fails, say so and offer it through a
  private channel. The report never carries the real value. A name that is not public (an internal
  system or service, a hostname, a company package, a class, a file, a project, a user or a team) is
  replaced only where the channel leaves the organization the name belongs to: a public tracker, a
  list, a vendor's ticket. There it is replaced with a plausible name of the same shape, such as
  `billing-api` for the real service and `com.example.orders` for the real package, used
  consistently across the code, the configuration, the output, and the prose, so that the reproducer
  still builds and runs and the pasted output still matches it. An identifier the reader finds the
  resource by stays: a vendor's support desk locates your tenant, your hostname on its platform, or
  your bucket by that name and by nothing else, and a DNS or TLS failure can depend on the exact
  name (`references/question-and-support-ticket.md`). In the organization's own tracker or chat the
  real names stay, because the reader finds the service, the class, and the host by them; where one
  report has to serve both readers, the sanitized copy is a second document. Code that is public, on
  GitHub, GitLab, or a package registry, is named and linked as it is. Say in one sentence that
  names were changed and what kinds of value were removed; do not list the originals. Two kinds of
  content take the changes differently. Captured evidence (a log, a trace, an incident record) is
  redacted in place and labeled as redacted; nothing re-runs it, because the event is past. A
  reproducer whose inputs you changed is re-run before it ships, under the run rule below, because a
  substitution can change what triggers the failure. *Test:* no placeholder stands where a value has
  to run, every substitute is spelled the same in every place the original appeared, the pasted
  output of a reproducer was produced by the substituted reproducer, and redacted captured evidence
  says so.
- **Where no reproducer exists, ship the observation set.** R1, R2. An intermittent failure, a
  production incident, or a flaky test may have no command that fails on demand. The report then
  carries how many times it happened in what window, since which build, at what rate, what it
  correlates with (a deploy, a load pattern, a platform), what you tried in order to reproduce it
  and what each attempt showed. A passing attempt is evidence too. A production log goes through the
  rule above before it is pasted: secrets out, and private names substituted where the channel
  leaves the organization. For an application on a user's device, the observation set adds the crash
  report from the reporting service by its ID, symbolicated where the service does that, the device
  and OS versions it covers, and the user's steps attributed to the user.
- **Where the evidence is too large to read or to paste, ship the extract and offer the artifact.**
  R1, R2. A heap dump, a core dump, a support bundle, a dataset, or a recording of hours is not
  attached. The report carries what you extracted from it, such as the failing entries, the
  histogram, or the query that found them, names the artifact with its size and the build it came
  from, and offers it on request or through the channel's private upload. The redaction rule above
  reads the extract; the artifact itself goes only to a reader authorized to hold what it contains.
- **Where the evidence is a measurement, ship the conditions it was taken under.** R1, R2, R3. A
  slowdown, a memory growth, or an output size has no failing line to paste. The report carries the
  exact command measured, the number of runs and their spread, whether the runs were warm or cold,
  the machine and what else it was doing, and the same measurement on the last good release. *Test:*
  a reader could repeat the measurement and know whether their number agrees with yours.
- **Run what you ship, after your last edit to it, from a clean directory.** R1, R2. Reduction
  silently fixes the defect often enough that this is the check with the highest yield. *Test:* the
  pasted output carries incidental detail nobody invents, such as paths, timestamps, and the tool's
  exact punctuation, and it matches the shipped reproducer's own identifiers. A reproducer you did
  not write, from a draft under review or from a reporter, is untrusted code: read it before
  anything runs it, run it only where the task authorizes a run and in an environment whose loss you
  accept, and otherwise mark the run as not established and hand it over (§10).
- **Reduce until nothing outside the target project is needed, then stop.** R1, R2. This is the
  ownership procedure of §4 run to its end: reduction is worth doing because it eliminates suspect
  layers, not because the result is small. Where the defect only appears through a dependency, say so
  and ship the shortest chain.
- **Ship it in the form the channel accepts.** R1. Projects disagree: one requires a repository or an
  archive, another forbids both and wants an inline snippet, a third wants a link to a running
  reproduction, and a mailing list wants it inline or linked because attachments may not arrive. The
  form's own field text, or the project's reporting guide, decides.
- **Paste the failing output verbatim, as text, wherever the artifact is text.** R1, R4. R4 arrives by
  searching for that string, and a screenshot of a log or a paraphrase of it cannot be found. Verbatim
  means the tool's own text with only the placeholders and the substituted names of the rule above
  changed. *Test:* the
  report carries the tool's own output as text, punctuation included, in a code block where the
  markup has one and indented where it has none, and nothing in it was reworded except a placeholder
  that names what it replaces. A visual defect is the exception: it ships the image or the recording,
  one sentence saying what to look at in it, and any text visible in it as text. The run rule above
  becomes: the image was taken with default settings or a fresh profile where the defect survives
  them, and the build is visible in it or stated beside it. The redaction rule reads the image like
  any other evidence: document text, file names, and account names in it are content.
- **Give the version of the target project and of every layer between it and the symptom.** R1, R4.
  For an application on a device, the identifier is the build number with the platform and the OS
  version, not the marketing version alone. For a deployment, the chain includes the cluster or
  platform version, the operator or chart version, and the values or the resource that produced the
  failure, with private values substituted. *Test:* every tool, runtime, browser, operating system,
  or service named in the reproduction chain has a version or an identifier somewhere in the report.
- **Where the project runs reproducers for you, use it and link the run.** R1, R2. A playground, a
  build scan, a CI job for reproducers, or a sandbox the project hosts produces a run a triager can
  open, which no sentence in your report is. A suspected vulnerability never goes there (§4).
  *Test:* where the project offers one, the report carries a link to a run that shows the failure
  being reported.

## 7. Length, impact, and disclosure

These rules hold for every report. Projects state the summary rule and the ban on speculative
consequences as rules about machine-written reports, because those break them most often, and a
report you review is held to all of them whoever wrote it.

- **Put the summary and the critical details where the reader meets them first:** the title and the
  opening sentence of the field §3 names for the opening. R1. Do not make a triager scan pages; each section
  carries at least one fact absent from every earlier one (§9). *Test:* the version, the symptom, and
  the expected value are all reachable without scrolling past a section that restates another.
- **Write the core first, and cut what answers no reader.** R1, R2. The core says what you did or
  observed, what you expected or ask for, and the one piece of evidence that shows the gap; where
  the form or the genre opens differently (§3), the core goes where the opening goes. Every other
  sentence answers a question a reader in §1 asks: reproducing, isolating, routing, whom it affects,
  what to do until it is fixed, how to know it worked, the response you want, or a statement the
  project's policy requires. An answer stays only where it is established: a workaround you ran,
  with the measurement that shows its effect (§3), an affected set you observed or can cite, a
  requirement the project is bound by. An untried workaround, a list of places you did not check,
  and a guess at who is affected go to the hand-over note. *Test (the reader deletion test):* delete
  the sentence; if no reader loses an established answer, it goes, however true it is. The section
  test of the summary rule removes only repetition; this one removes true facts that answer nobody.
  The queries once the report names the nearest hit (§4) and listings that came back empty and
  support no claim go to the note as well; the elimination of §4 and the negative results of §3
  stay. A shape of the fix you have not verified stays only marked as untested (§5, question 5).
- **The report is not a transfer of your notes.** R1, R2. The notes hold everything you established;
  the report holds what its readers need. *Checkpoint:* when the prose outside code blocks runs
  past about 300 words, or past one screen, go through it sentence by sentence with the reader
  deletion test before you add anything else. The number is a trigger for the test, not a
  quota: a report that needs more after the test keeps it.
- **An optional field carries only what passes the reader deletion test.** R1. A Logs or Additional
  information field is not a slot to fill. A log of a run that succeeded belongs there as a control
  or a measurement (§6): the last good release, the variant that does not fail, the timed runs.
  Otherwise one line showing the step you report ran is enough, and a field with nothing that
  passes is left blank (§8).
- **Paste the output that carries the claim, verbatim.** R1, R3. Trim a long listing to the lines
  the report points at and say that you trimmed it; the command stays whole, so anyone can re-run it
  and see the rest. A stack trace is not trimmed, and neither is the incidental detail that shows
  the run happened (§6).
- **Do not enumerate speculative consequences.** R1, R2. "This could allow" with no observed instance
  is the tell triagers name. Keep an impact you actually observed, and paste the observation. Where
  the impact matters to routing, as with a suspected vulnerability, say that it is unconfirmed and
  route it privately (§4).
- **Disclose the tool where the project asks, in the form it asks for.** Read the policy first; some
  projects also constrain who may answer follow-up questions. `references/machine-authorship.md`.

## 8. Filling the form

- **Fill the project's required fields, by their names, so the text drops in unchanged.** R1. Where
  the person filing named the fields, theirs stand in for the form (step 2). Filling the form gets
  the report admitted and routed: projects close reports that skip the checklist, and component
  fields decide who sees it. It does nothing else: a filled form is the condition for being read,
  not a finished report. Where the tracker has fields rather than a text template, such as a Jira
  create screen or a vendor's support form, fill the fields and keep the description for what has no
  field of its own. Where the channel has no fields at all, as on a mailing list, the sections the
  project's reporting guide names are the form, and the version, the environment, and the reproducer
  go in the body. Your own sections may sit inside a field or after the form's last field; they
  never replace one. An optional field you have nothing for, or nothing that passes the reader
  deletion test (§7), is left blank; a required one never.
  Where there is no form and no guide, the sections of a defect report are these, in this order:
  what you did and what you observed, with the pasted output; what you expected and what that rests
  on; the version of every layer; the reproducer; the workaround where one exists; the analysis,
  marked. Any form's order replaces it. A request and a question take the slots their references
  name, in that order.
- **A required field you have no evidence for says what is missing, not a plausible guess.** R1, R2.
  "Not established: I could not test on Windows" is usable. An invented environment is worse than a
  blank. The same sentence in an optional field is noise: leave the field blank.
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
| A weakness with no failure, padded to look like a bug | Find the one observation that shows the gap (a resolved reference, a permission, a setting). If it sits below standards, policy quotes, or logs that show nothing about the gap, the report is padded. Where the weakness may be a vulnerability, it goes by the private route of §4 |
| The same fact in four sections | Each section must contain a fact absent from every earlier section |
| A grounding that names a document which does not say it | Fetch the named artifact and read the sentence claimed for it |
| Evidence the reporter gathered, written as if you reproduced it | The attribution rule of §6: each transcript names who ran it |

## 10. What is not yours to decide, and what you hand over

Raise these where they are still open, and let the human answer. A question the person filing has
answered already, or one the project's policy settles, is not asked again:

- Whether the person filing can explain and defend the report without the tool that wrote it, where
  the project makes this a condition of filing.
- Whether to file at all when personal preference is the only grounding available, or when the
  project shows no maintainer activity: no release and no reply from a maintainer to a report in a
  long time.
- Whether a pull request that carries the report as its motivation serves better than a report, as
  with a documentation sample that does not compile or a defect you hold a fix for.
- Whether a comment on an open report or pull request that already covers the problem serves better
  than a new report.
- Whether a project's AI policy permits an agent-authored report, where the policy does not say.
- Whether the request is one the project would want, and what it is worth, where the person filing
  has not said so.
- Whether a defect that may be a vulnerability is sent, to which private channel, and in what form.
  It is never filed publicly.

**The report states a gap; the hand-over note says what to do about it.** A tracker you could not
reach, a reproducer you could not run, a version you could not install, a lookup you could not make, a
sign-off only a person can give: the report says, in the field concerned or beside the claim it
would have supported, that this was not established, and never claims the work. A gap that answers
a triager's question (§1: does it reproduce, on a supported version, is it a duplicate) is stated
even where no claim rests on it; any other gap goes to the note alone. The note to the person
filing, kept apart from the report body, carries each gap with the query or the command that would
close it. Where you file through a command such as `gh issue create`, the deliverable is the body in a
file of its own, the command that files it with `--body-file`, and the note outside that file.

## 11. Review checklist

Run it over a draft, yours or someone else's. For a report filed in a tracker or sent to a list,
every item gets an answer, "none" included. The answers are the reviewer's, not the report's: an
item is answered by pointing at a sentence the report already has, or in the hand-over note, and a
sentence added to the report to answer an item passes the reader deletion test (§7) first. A
report to a team's own backlog owes every item, with
Ownership, Duplicates, and Redaction reduced as `references/project-conventions.md` says; an issue
you file in your own repository to fix yourself owes the same, and its Ownership, Duplicates, and
Disclosure answers are one line each. A question owes every item except Expected behavior and
Analysis, which it does not carry, and it owes the Question or support ticket item below. A support
ticket owes every item, with Currency, Reproducer, Ownership, Duplicates, and Grounding read through
the table in `references/question-and-support-ticket.md`. A comment on an existing report owes
Channel, Currency, Execution, Attribution, Redaction, Disclosure, the comment half of Duplicates,
and Reproducer for the transcript it pastes, and Expected behavior where it adds an expected
outcome. A colleague message owes only the items its reference table keeps, and the Colleague
message item below.

- Channel: is this the place the project names for this kind of report, and is the markup the one it
  renders?
- Title: does it name the symptom, or a fix you have in mind?
- First paragraph: an action you took or a documented surface you used and what broke, or for a
  request or a question the task you could not complete, or, outside your own project and a
  colleague message, a private class inside the project?
- Summary: are the version, the symptom, and the expected value reachable without scrolling past a
  section that restates another?
- Length: does the report open on the core where the form and the genre allow, does every other
  sentence pass the reader deletion test, and past about 300 words of prose, was it read sentence by
  sentence? Does every optional field carry only what passes the test, and is every pasted output
  trimmed to the lines the report points at (§7)?
- Goal: is the task you could not finish stated, and not only the step you got stuck on?
- Routing: does the project want this here, does the report match none of its redirect conditions,
  where you are not sure it is a defect, does the report say so and go where questions go, and where
  it may be a vulnerability, is it kept out of the public queue, the public search, and any public
  reproducer run?
- Ownership: is the isolation in the report as re-runnable steps or as observations with one thing
  varied, for a request as the contract argument, or only as a conclusion?
- Currency: is the version an identifier that resolves to one build, inside the support window, the
  same one the reproducer declares, and for a regression are last good and first bad both stated?
- Duplicates: is the nearest hit in the report with what makes this one different, is the query
  recorded where §4 puts it, and does an open report of the same defect get a comment rather than a
  second report, carrying the version, the difference, your transcript where the thread lacks one,
  and nothing the thread already says?
- Count: how many owners, so how many reports; under one owner, how many independently fixable
  problems, so how many expected blocks in one report where they share a component, or linked reports
  where they do not or the project asks for one problem per issue; and does each report say what it
  depends on?
- Expected behavior, for a filed report: run the seven questions of §5 over every block, and name which
  question failed.
- Grounding: which of the seven sources is it, and is a compatibility promise or a documented
  behavior that changed counted as the project's own specification, unless the project's
  compatibility statement excludes undocumented behavior?
- Execution: does every claim about what a tool does today carry a transcript, an attributed
  observation, or a cited document, does a claim about a run carry a run, and is a proposed
  rendering marked as one possible shape?
- Attribution: does each transcript, log, or recording say who produced it, and is nothing the reporter
  observed written as if you reproduced it?
- Analysis: is the block marked with its confidence, does the report stand when you delete it, and
  does any sentence you wrote name the cause inside the symptom or the steps?
- Workarounds: is a setting that works placed after everything that states the problem, or in the
  form's own field for it, and a setting that failed stated as a failure rather than filed as a
  workaround or alternative? Does a workaround you ran carry the measurement that shows its effect?
  Run the workaround deletion test, and keep a setting that defines the failing case out of it.
- Impact: is every consequence the report names one you observed and pasted?
- Reproducer, for a filed report: is it complete, in the form the channel accepts, does it depend on
  nothing outside the target project or name the layer that stays and why, does the pasted output
  carry incidental detail and match the reproducer's own identifiers, does each step have an
  observable result, is the failing output pasted as text where it is text, does every layer in the
  chain carry a version, and where the project runs reproducers, is the run linked, unless the
  defect may be a vulnerability? Where the reproducer came from someone else's draft, was it read
  before it ran, and was the run authorized and isolated or marked as not established?
- Observation set, where nothing reproduces on demand: count, window, rate, first-seen build,
  correlations, and the attempts made and their results; for a crash on a user's device, the crash
  report by its ID, the device and OS versions, and the user's steps attributed to the user?
- Extract, where the evidence is too large to read or to paste: is the artifact left unattached,
  what was extracted from it in the report with the artifact's size and build, and is it offered on
  request or through a private upload?
- Measurement, where the evidence is a number: the command, the runs and their spread, the machine,
  and the same measurement on the last good release?
- Redaction: was every transcript, log, image, and file read for secrets, personal data, and private
  names; is each secret a placeholder that names what stood there; where the channel leaves the
  organization, is each private name a plausible substitute spelled the same everywhere it appears,
  except an identifier the reader finds the resource by, and where it does not, are the real names
  kept; where a personal datum is the failing input, was a synthetic value tried in its place; does
  the reproducer still run with no placeholder in its way; was it re-run after the substitution; is
  captured evidence labeled as redacted; and does one sentence say what was changed?
- Disclosure: does the project ask anything of a report written with a tool, and is it answered?
- Form: do the form's fields, or the fields the person filing named, appear by name in that order,
  does each carry what its label asks for, are your own sections inside or after them and never in
  place of one, does every required field carry an observation or an explicit "not established", is
  every optional field you had nothing for left blank, and where there is no form, are the sections
  the ones §8 names, in its order?
- Request: are the slots of `references/request-genre.md` present, and does it pass the API
  deletion test?
- Question or support ticket: are the slots of `references/question-and-support-ticket.md` present,
  and is the ask stated?
- Colleague message: is the ask in the first message, is what you ruled out stated where you ruled
  anything out, does every identifier resolve in the shared repository, are what you expect and what
  you got each stated in a line where the symptom line does not already say them, is the reply you
  want named, and for a post to a channel, is the person asked named or the post marked as asking
  nothing?
- Raised: are the questions of §10 that are still open put to the human, and not answered in the
  report?
- Hand-over: is every step nobody executed and every check or lookup you could not make carried in
  the note with the command that would close it, and stated in the report as not established beside
  each claim that rests on it, or in the field concerned where it answers a triager's question?
- Vacuous shapes: run §9.
