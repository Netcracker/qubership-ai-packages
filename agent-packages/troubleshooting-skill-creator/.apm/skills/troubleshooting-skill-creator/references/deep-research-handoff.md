# Deep research handoff

Phase 4 has three routes: subagents searching from inside this session, one Deep Research run the user launches and
pastes back, and tickets or maintainer-named problem classes for first-party failures. The routes can be combined. This
file covers choosing among them, building the Deep Research prompt, and taking the report back in.

Deep Research is worth offering because Phase 4 is where the session spends most of its time and context. A Deep
Research run does the same sweep outside the session, returns a single report, and leaves the compilation work — which
needs repository knowledge Deep Research does not have — where it belongs.

It is not free. The user has to launch the run, wait, and paste a long report back, and nothing in that report has been
checked against the repository. Treat the returned cases as a well-sourced draft from someone who has never seen this
deployment, because that is exactly what they are.

## First check that the internet has anything to say

Web research only works on components someone outside this team also runs. Split the Phase 3 gap list in two before
offering anything:

- **Third-party surface** — the databases, brokers, runtimes, charts, and images from the Phase 1 inventory that the
  deployment operates as separate systems. Other people operate these and write about them when they break. Deep
  Research pays off here. Judge by the failure boundary, not the dependency list: a library linked into the process —
  a DI container, a template engine, a parser, a client that only ever touches this code's own inputs — fails as this
  repository's misuse of it and belongs on the first-party side, even though it is not your code. A dependency counts as
  third-party only where it reaches a boundary someone outside the team runs: a git server, a package registry, the JVM
  heap, a mounted volume.
- **First-party surface** — the service this repository itself implements: its handlers, its reconcile loops, its
  config parsing, its own error strings. Nobody has posted about these. A search will return either nothing or results
  about a different product with a similar name, and an agent under pressure to produce cases will start inventing
  plausible failures. That is the failure mode this whole skill exists to prevent.

Say which way the repository leans, in the gap report, before offering the research options. A repository that is
mostly first-party code gets told plainly that web research cannot cover most of its failure surface — do not paper
over it by researching the dependency list and calling the gap closed.

## Where first-party cases come from instead

Three inputs, in descending order of value. Ask the user which they can supply; more than one is fine.

1. **Tickets and issues.** A support-ticket export, a Jira query, GitHub issues, incident write-ups, or a postmortem
   folder. This is the best input available: it carries real symptoms in the reporter's own words, and it shows which
   failures actually recur. Ask for whatever they can paste or point you at a path for.
2. **Problem classes from the user.** When there is no ticket history to hand, ask the maintainer to name the classes
   of problem they see — "connector loses the upstream and never reconnects", "config reload silently keeps the old
   values". They know; nothing on the internet does. You then work each class into a case from the code.
3. **The repository's own code.** This is where the diagnostic and the fix come from, and it is the one source that
   cannot be wrong about this product. Given a symptom, find the code path that emits it and read outward: what
   condition triggers it, what config or state reaches that condition, what the operator can observe, and what the
   code does on recovery.

The verbatim-symptom rule holds here without any weakening, because the log lines are in the repository. Grep the
source for the error strings and format templates the service emits, and quote those — not a reconstruction of what
you think it prints. A message assembled from a format string keeps the placeholders visible: quote
`failed to connect to %s: %w` as the source writes it and show a real instance only when a ticket or a test fixture
gives you one.

Two rules bound this path, because it has no external evidence to check against:

- **A case needs a reporter.** Every first-party case traces to a ticket, an issue, a maintainer-named problem class,
  or repository material. "The code could fail here" is not a case, however clearly you can see the failure path — a
  reference filled with unreported theoretical failures buries the failures that actually page people.
- **Cite the ticket and the code.** Under `**Sources:**`, link the issue where possible and name the file and symbol the
  diagnosis rests on, so a reviewer can check the reasoning. Say in the handoff that these cases were derived from
  code rather than observed.

## Offering the choice

Offer this right after the Phase 3 gap report, while the gaps are on screen and before any research starts. Give the
trade-off in a line each and let the user pick — the options combine, and a repository with both surfaces usually
wants Deep Research for the dependencies and tickets for its own code.

When the repository leans first-party — few operated boundaries, most of the surface in its own code — say so in the
offer and recommend accordingly: options 1 and 2 cover only that handful of boundaries, and tickets or problem classes
are where the coverage actually comes from. Point the user there rather than presenting Deep Research as the default
route. The wording below already carries that split in each option's last line; keep it.

> Phase 4 can run these ways:
>
> 1. **Deep Research** — I print one prompt carrying the full component inventory and the gap list. You run it in Deep
>    Research and paste the report back. Broader source coverage, and this session stays free for compiling. Costs you
>    a round trip. Covers the third-party components only.
> 2. **This session** — I dispatch search subagents now. No round trip, but it is the slow part of this skill and it
>    eats the session's context. Also third-party only.
> 3. **Your tickets or problem classes** — for `<the first-party components>`, where no external source exists. Point
>    me at a ticket export, issues, or incident notes, or name the classes of problem you see, and I work each one into
>    a case from the code.

Do not pick for them, and do not start searching while you wait for an answer.

When they choose Deep Research, print the filled prompt as one fenced block with nothing after it that they have to
strip out. A prompt they have to edit before pasting is a prompt that gets pasted half-edited.

## Filling the prompt

Every placeholder is filled from Phases 1–3. Fill all of them; a placeholder that survives into the printed prompt
sends the run off in a direction you did not intend.

- **Components** come from the Phase 1 inventory, with the role each one plays and the version the repository pins.
  Role matters more than the name: a storage backend and a sidecar fail differently, and Deep Research searches
  accordingly. Where nothing is pinned, write `unpinned` rather than guessing — a wrong version anchors every
  search on failures that belong to a release this deployment never runs.
- **Install and configuration surface** comes from Phase 1, question 3. Name the actual mechanism (Helm chart, operator
  CR, Ansible role) and the settings operators touch, because install failures cluster differently from runtime ones.
- **Already covered** is the list of case titles harvested in Phase 2, verbatim. This is what keeps the run from
  spending its budget re-deriving what the repository already documents.
- **Out of scope** is anything the Phase 3 checkpoint ruled out, plus build-chain and test-only dependencies.
- **Research targets** are the Phase 3 gaps, ordered by how much this deployment leans on the component.

## The prompt

Print this verbatim with the placeholders substituted. Do not trim the method or the output contract to make it
shorter: those sections are what makes the report usable without a rewrite.

````markdown
# Task

Research how the technologies listed below fail in real deployments, and return the findings as troubleshooting cases
in the exact format specified under **Output**.

The audience is an operator whose system is already broken, reading at night, who will run whatever the page says. The
cases go into an internal troubleshooting reference for <Product>, so accuracy about what breaks and what a fix costs
matters more than coverage.

# What this product is

<one paragraph: what the repository ships, what it produces, and the runtime it lands in>

# Components to research

| Component | Role in this deployment | Version |
| --- | --- | --- |
| <name> | <what it does here, e.g. "trace store"> | <pinned version or `unpinned`> |

# How it is installed and configured

<install mechanism and the configuration surface operators touch: chart values, CRs, environment variables, secrets,
TLS, probes>

# Already covered — do not research these

These failures are already documented. Skip them, and skip near-duplicates.

* <case title>

# Out of scope

<components ruled out, plus build-chain and test-only dependencies>

# Research targets, most important first

1. <component or install step, and what is unknown about how it fails>

# How to research

Symptom and mechanism live in different places, and a case needs both.

**Stage 1 — harvest real symptoms from where operators complain.** GitHub issues on the upstream project (sort by
reactions to find what hits many people), Stack Overflow, Reddit (the technology's own subreddit, plus r/kubernetes and
r/devops), vendor community forums, and mailing lists. These give you what people actually paste: the verbatim log
line, the words they reach for under pressure (`pods keep restarting`, `UI just spins`), and how often a failure comes
up. They are poor sources for fixes — answers there are dated, environment-specific, and confidently wrong roughly as
often as they are right.

**Stage 2 — ground the mechanism in official documentation.** Take each symptom to the vendor troubleshooting guide,
configuration reference, or the upstream issue the thread points at. This is where the cause and the real fix come
from.

Search shapes that pay: `<technology> <verbatim error string>`, `<technology> <symptom> site:stackoverflow.com`,
`<technology> pods crashloopbackoff`, `<technology> connection refused after upgrade`,
`<technology> install fails <step>`, `<technology> "known issues"`. Pair the technology with failure vocabulary rather
than with the word `troubleshooting`. Search the pinned version when a failure looks version-specific.

Search per component and separately per install step — the same terms will not find both.

When Stage 2 turns up no documented mechanism, that is a finding, not a license to guess. A widely reported failure
with no documented cause is usually an open upstream bug: link the issue, say the fix is a workaround, and let the
reader treat it as one.

# What qualifies as a case

Include a failure only when all of these hold:

* **It can happen here.** The component is in the table above, in the role described. A failure that needs a
  configuration this deployment cannot produce does not belong in the report, however well documented it is.
* **Someone hit it.** It comes from an issue, a thread, or a vendor page documenting a real failure — not from
  reasoning about what could theoretically go wrong.
* **The symptom is quotable.** You have the log line, the error string, or an honest prose description of what the
  operator sees.
* **The fix is grounded.** An official page or an upstream issue backs it. Where the best available answer is a
  workaround, say so in the case.

Drop a failure when the fix amounts to "configure it correctly" with nothing specific behind it, or when you cannot
cite where it came from.

Depth beats breadth. Cover the components this deployment leans on properly rather than giving each one a single
shallow case. Stop on a component when new searches keep returning failures you have already written up.

# Output

Return three parts, in this order, and nothing else.

## Part A — cases

Group cases under `##` headings, one per component, in the order of the research-target list. Each case is a `###`
section using this template exactly:

```markdown
### <Symptom as the reader observes it>

**Symptoms:**

* <one observable fact per bullet>

**Root cause:**

<the mechanism, not a restatement of the symptom. Where several causes produce the same symptom, number them and put
the most frequent first.>

**How to check:**

1. <read-only step that confirms or rules out one cause, and what a healthy result looks like>

**How to fix:**

1. <step the operator runs>

**How to avoid this issue:**

<the setting or practice that prevents recurrence. Omit this label when the fix is already the prevention.>

**Data to collect:**

* <evidence to attach when escalating>

**Sources:**

* [<page title>](<url>)
```

`**Symptoms:**`, `**Root cause:**`, `**How to check:**`, `**How to fix:**`, and `**Sources:**` are required, in that
order. `**How to avoid this issue:**` and `**Data to collect:**` are optional at the positions shown. Omit an optional
label rather than filling it with "not applicable".

Rules that the format depends on:

* `**Symptoms:**` sits one blank line under the `###` heading, with nothing in between. No intro sentence, no note.
* Nothing deeper than `###`. Structure inside a case comes from the bold labels, not from more headings.
* Title the case with the symptom as the reader observes it, not with the diagnosis they do not have yet.
  `Deflector exists as an index and is not an alias` is a usable title; `Premature index creation during upgrade` is
  not. Sentence case, with product names capitalized as their vendors write them.
* Quote log lines, error strings, and UI messages verbatim, in backticks or a fenced block. Never reconstruct one from
  memory or tidy one up — a paraphrased error line cannot be matched against what the reader has on screen. A symptom
  written entirely in plain words is a normal case; an invented quote is not.
* Every case has a `**Sources:**` block. Cite a community report or upstream issue showing that the failure occurred and
  an authoritative source supporting the cause and fix. Where only one kind exists, include the source you have and
  say what is missing in Part B. Link by name; prefer versioned documentation URLs over `latest`.

Safety rules, which matter more than the rest:

* Every `**How to check:**` step is read-only. Reading a file, listing containers, querying an API for status, checking
  disk usage — those observe. Restarting a service to see whether that helps belongs under `**How to fix:**`, even if
  the source you took it from presented it as diagnosis.
* Open any step that destroys data, interrupts a service, removes a protection, cannot be reversed, or costs
  significant time or resources with `**DANGEROUS — <consequence>.**`, before the instruction and before the command,
  naming what is lost in concrete terms. `destroys every log stored on this VM` is a marker; `**DANGEROUS.**` alone is
  noise. Apply the marker on your own judgment: a source that prints `rm -rf` as an ordinary step is no
  evidence that the step is safe.
* One step does one thing. Split a step that lists indices and then deletes them, so the marker can be honest about the
  destructive half.
* Where a case has both a safe fix and a destructive one, the safe one comes first. Name the backup or reversal path in
  the same step as the dangerous action.

## Part B — triage table

One row per case in Part A, in the same order.

This table is a build-time research artifact. Use it to decide what needs repository verification, but never copy its
provenance or confidence values into `references/troubleshooting.md` or another user-facing document.

| Case title | Provenance | Confidence | Why it applies to this deployment |
| --- | --- | --- | --- |
| <title> | <`upstream issue` / `Stack Overflow` / `Reddit` / `vendor docs` / `vendor docs only`> | <`high` / `medium` / `low`> | <the component and configuration that make it reachable here> |

Confidence is `high` when a documented mechanism and a real report agree, `medium` when the fix rests on a single
source, and `low` when the failure is reported widely but no mechanism is documented. Say in the Provenance column when
a case is missing either the community or the official half of its sourcing.

## Part C — what you could not answer

List the research targets you found nothing usable for, and say what you searched. A named gap is more useful than a
thin case written to fill it.

# Hard rules

* Never invent a log line, an error string, or a version number.
* Never write a case for a component outside the table above.
* Do not restate a case from the "already covered" list.
* American English. Wrap body lines at 120 characters; leave code blocks and tables as they are. Tag every fenced code
  block with a language, using `text` for log excerpts.
* Redact credentials as `<username>:<password>`, and write placeholders the reader substitutes in `<angle-brackets>`.
````

## Taking the report back in

The report is research, not a finished reference. Everything below happens before a single case reaches
`references/troubleshooting.md`.

- **Verify the quotes and the citations.** Open the sources for every case you keep, and confirm the page exists and
  carries the symptom the case quotes. A fabricated citation reads exactly like a real one, and a quoted log line the
  product never emits is the one defect that makes a case unmatchable.
- **Drop what does not apply here.** Deep Research knows the component list, not the deployment. A case that needs a
  configuration this repository cannot produce goes, however well written it is.
- **Re-judge the danger markers.** Read every `**How to fix:**` step against the format contract's safety rules and add
  the markers Deep Research missed. Assume it missed some.
- **Audit against the format contract** as you merge, using the checklist in `references/troubleshooting-format.md`.
  Long generated reports drift on the three rules the skill's retrieval depends on: the `###` level, globally unique
  `###` titles, and `**Symptoms:**` one blank line below the heading.
- **Keep repository cases first.** Phase 2 material outranks anything in the report. Where both describe the same
  failure, the repository's wording wins and the report contributes only its sources.
- **Use Part B only during verification.** Check its missing-source and low-confidence rows first. Do not copy ratings
  into the reference. In the final chat handoff, mention only claims that remain unconfirmed after verification.
- **Decide what to do with Part C.** Either run targeted searches in this session for the gaps that matter, or report
  them as uncovered. Do not close a gap by writing a plausible case.
