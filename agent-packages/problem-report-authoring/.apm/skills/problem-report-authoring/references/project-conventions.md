# Reading the channel before you write

Open this at step 1 of the skill. Each lookup is short, and each answer changes the report. Where the
person filing has already told you the format, the fields, or the channel, use what they said and
skip the lookup that would have established it.

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

## GitHub

- `.github/ISSUE_TEMPLATE/*.yml` are issue forms: read each field's `label`, its order, and
  `validations: required: true`. `*.md` files there are templates. Pick the one that matches your
  artifact; a project's bug form and feature form can order their fields oppositely.
- `.github/ISSUE_TEMPLATE/config.yml` routes: its contact links send questions to Discussions or a
  forum and security to a private channel, and a report filed past them is closed.
- A form's required fields are enforced only in the web UI, so a report created with
  `gh issue create` or the API carries the labels as headings you write yourself.

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
  priority or fix version, leave it alone.
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
can ask you, so the report can be shorter and can leave shared context unsaid, and the duplicate
search is the backlog itself, including what was closed as not now. What does not change is the
symptom-first opening, the expected-behavior test, and for a request the acceptance criterion and
the non-goals, which is what a backlog item is most often missing.

## What a lookup does not establish

A redirect target is not known to accept the report; a search that returned nothing does not
establish absence, because trackers match titles and labels and a duplicate is often worded
differently; a version inside the support window says nothing about the development branch; and the
field text that names the accepted reproducer form does not say that your reproducer reproduces.

## The one rule that overrides the skill

The form wins on order: where the project's required field order disagrees with any ordering
preference in the skill, write into the project's order. What survives, and why, is stated once, in
§3 of the skill: the first sentence of the first field is an action you took and what you observed,
and the analysis rules ask nothing about position.
