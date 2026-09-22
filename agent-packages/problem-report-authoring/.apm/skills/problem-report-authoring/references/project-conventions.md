# Reading the channel before you write

Open this at step 2 of the skill, once step 1 has named the project that owns the defect. Each lookup
is short, and each answer changes the report. Where the
person filing has already told you the format or the fields, use what they said and skip the lookup
that would have established them. The routing and the security lookups are never skipped: a channel
the person named can still be the wrong queue for this report, and a suspected vulnerability never
goes to the public one. Where you cannot reach the project at all, see *When the project is
unreachable* below.

## What to establish, on any platform

| Lookup | Where it usually lives | What it decides |
| --- | --- | --- |
| The channel for this kind of report | The contribution guide or reporting page; the create dialog; the list's information page | Whether this belongs here, in a forum, on another list, or in the security channel |
| The form or template and its required fields | The form file; the create screen; a template pre-filled into the description; the list's expected sections | Your headings and their order |
| The reproducer form | The form's own field text; the contribution guide | Inline snippet, repository, archive, link, or attachment |
| The support window | A release schedule, `SUPPORT.md`, the newest release; for a team's own project, the deployed release or the maintained branch | Whether the version is worth reporting |
| The AI policy | `AI_POLICY.md`, the AI section of the contribution guide, a checkbox in the form | Disclosure (`machine-authorship.md`) |
| The security channel | `SECURITY.md`, a security page, a private-reporting option | Where a suspected vulnerability goes instead of the public queue |
| The markup the channel renders | An item already filed there, opened to see how its author entered a code block | Fenced blocks, wiki markup, or plain text |
| Where to search for duplicates | The tracker's search with closed items included; the list archive | The query and the nearest hit you record |
| Whether the project asks for one problem per issue | The contribution guide; the form's own text | Whether related symptoms under one owner share a report or get linked ones |

## GitHub

- `.github/ISSUE_TEMPLATE/*.yml` are issue forms: read each field's `label`, its order, and
  `validations: required: true`. `*.md` files there are templates. Pick the one that matches your
  artifact; a project's bug form and feature form can order their fields oppositely.
- `.github/ISSUE_TEMPLATE/config.yml` routes: its contact links send questions to Discussions or a
  forum and security to a private channel, and a report filed past them is moved or closed.
- A form's required fields are enforced only in the web UI, so a report created with
  `gh issue create` or the API carries the labels as headings you write yourself.
- A suspected vulnerability goes through the repository's private reporting form where the
  repository has one (the Security tab, "Report a vulnerability"). That form has fields of its own,
  and for that report it is the form this lookup reads; `SECURITY.md` names the route where the
  form is off.

## GitLab

- `.gitlab/issue_templates/*.md`, chosen from the template dropdown; `Default.md` applies without a
  choice, and a project or group can set a default template in its settings, so open the create
  dialog and read what it pre-fills.
- A suspected vulnerability goes in as a confidential issue or through the channel `SECURITY.md`
  names, never as a public one.

## Jira, Bugzilla, and similar trackers

- The issue type is routing: bug, improvement, and task are different queues with different required
  fields. The create screen lists the fields for the type you picked; fill them, and keep the
  description for what has no field. Where the project reserves a field for triagers, such as
  priority or fix version, leave it alone; where the create screen makes such a field required, keep
  its default. In a team's own backlog the field is the reporter's where the team's process says so,
  and it is then set from the impact observed, as a support form's severity is.
- Markup differs per instance: wiki markup (`{code}`, `{noformat}`, `h2.`) on Jira Server and Data
  Center, an editor with its own format on Jira Cloud, plain text on some instances and on Bugzilla.
  Copy what an existing issue in the same project does.
- Where the instance restricts who may create issues, the project's reporting page names the
  route: a mailing list, a web form, or an account request.

## Mailing lists

- Plain text: no HTML and no Markdown decoration, because markers arrive as literal characters and do
  not survive quoting. A small reproducer goes inline; a large one goes to a repository or a paste
  with a link, because attachments may be stripped.
- The subject is the title, after whatever prefix the list uses; read the last ten subjects in the
  archive. A new report starts a new thread, never a reply to an unrelated message.
- No fields exist, so the version, the environment, and the reproducer go in the body. The archive is
  the duplicate search.

## A team's own backlog

The files above rarely exist. What stands in for them: the tracker's required fields, the last few
items other people filed and that were picked up, whatever the team treats as ready to work on, and
the deployed release or the maintained branch as the support window. The reader is a colleague who
can ask you, so the report can be shorter and can leave shared context unsaid. Three checks of the
skill reduce here, and the opening admits more. The ownership isolation of §4 reduces to naming the
service and the request or the input that fails, unless the failure crosses a service boundary,
because the repository path already names the owner. The duplicate search is the backlog itself,
including what was closed as not now. The private names of §6 stay as they are, because the channel
does not leave the organization; secrets still come out. What does not change is the
expected-behavior test and, for a request, the acceptance criterion and the non-goals, the two slots
a backlog item most often lacks. The opening still states the symptom first, and its subject may be
internal: a class, a service, or a commit is shared vocabulary here, as in a colleague message, as
long as the paragraph says what the caller or the user observed. An issue you file to fix yourself
owes the symptom, the version, and the reproducer or the observation, because the reader of the
closed issue months later has only them; ownership, duplicates, and disclosure are answered in a
line each.

## A vendor's support form

A hosted service or a commercial product with no public tracker takes reports through a support
form. The lookups above collapse to three: the form's fields and severity definitions, the status
and known-issues pages, and the vendor's documentation. What each field carries, and what replaces a
version and a reproducer there: `question-and-support-ticket.md`.

## Where the project takes questions

Most projects route "is this a defect?" away from the bug queue: a discussions board, a forum, a
list, a chat channel, or a question issue type, named in the contribution guide or the create
dialog's contact links. Read that before deciding which form to fill; the slots of a question are in
`question-and-support-ticket.md`.

## When the project is unreachable

A sandboxed session or an offline checkout cannot fetch the form, the guide, the policy, or the
tracker. Read what a local clone carries: `.github/ISSUE_TEMPLATE/`, `.gitlab/issue_templates/`,
`CONTRIBUTING.md`, `SECURITY.md`, and the changelog for the support window. Every lookup you could
not make is a gap in the hand-over note, with the URL or the query that closes it, and the report
does not claim the lookup was done. The deliverable is then the body in a file of its own, the
command that files it (`gh issue create --title ... --body-file ...`), and the note outside that
file.

## What a lookup does not establish

A redirect target is not known to accept the report; a search that returned nothing does not
establish absence, because trackers match titles and labels and a duplicate is often worded
differently; a version inside the support window says nothing about the development branch; and the
field text that names the accepted reproducer form does not say that your reproducer reproduces.

## The one rule that overrides the skill

The form wins on order and on the meaning of a field: where the project's required field order
disagrees with any ordering preference in the skill, write into the project's order, and a field
labeled for expected behavior, a proposed solution, or a workaround carries what its label asks for
wherever it sits. Fields the person filing named stand in for the form (step 2 of the skill), and
the same rule reads against them. What survives is stated in §3 of the skill: the first field whose
label asks what happened, for a description, or for the steps opens with an action you took and what
you observed, or for a request or a question with the task you could not complete, and the analysis
rules ask nothing about position.
