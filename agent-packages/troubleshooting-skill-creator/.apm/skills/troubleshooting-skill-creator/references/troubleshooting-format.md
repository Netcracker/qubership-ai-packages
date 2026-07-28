# Troubleshooting reference format

Every troubleshooting reference in this skill follows the structure below. The structure serves two readers at once: an
engineer scanning the page for a symptom they recognize, and an agent that locates a symptom with grep or a fuzzy search
and then reads one section instead of the whole file.

When repository material and an external source describe the same failure, preserve the target repository's symptom
wording and technical content. External sources may fill gaps or strengthen the explanation, but they do not replace
deployment-specific knowledge.

## Heading levels

Heading levels are fixed. An agent walks up from a matched line to the nearest `###` heading and reads until the next
heading at level 3 or above, so a level that shifts between components breaks the read.

| Level | Meaning | Example |
| --- | --- | --- |
| `#` | Document title. Exactly one per file. | `# <Product> — troubleshooting` |
| `##` | Component that owns the sections below it. | `## <Component>` |
| `###` | One case, or one reference section. | `### Component cannot connect to its backend` |

Do not use `####` or deeper. Inside a `###` section, structure comes from bold labels, not from headings. This is what
makes a section a self-contained unit: whatever line the search matched, the enclosing `###` section is the whole
answer.

Group components under `##` in the order a reader is likely to reach them, rather than alphabetically. A file has no
table of contents: the `**Symptoms:**` labels are what a search matches, and duplicating every case title in an index
only gives the file a second place to go stale.

An agent gets its index by matching each `###` heading together with the `**Symptoms:**` block right under it, which
returns every case heading next to its symptoms. The index is derived on each read and stored nowhere, so it cannot
drift from the cases. Every `###` title must be unique across the document because the reader loads a selected section
by its exact title. A duplicate title is ambiguous and makes the catalog invalid.

## Two kinds of level-3 section

A `###` section is either a case or a reference section. Both are legitimate, and both live in the same file.

- A **case** describes one failure and how to fix it. It starts with `**Symptoms:**` and follows the case template.
- A **reference section** describes principles, tuning knobs, or background that no single failure owns. It has no
  `**Symptoms:**` label and no fixed template.

The presence of `**Symptoms:**` as the first label is what distinguishes the two. An agent that lands in a section reads
that label to know whether it found a fix or background reading. Do not add a `**Symptoms:**` label to a reference
section to make it look uniform.

In a case, `**Symptoms:**` comes immediately after the `###` heading, separated by one blank line and nothing else. No
intro sentence, no note, no admonition. The search that builds the index expects the heading one blank line above the
`**Symptoms:**` label, so anything wedged in between costs the case its title in the index.

Reference sections earn their place when the material helps a reader who has not yet identified their failure —
performance principles, sizing guidance, configuration tips. Keep them at the end of their component's `##` block, after
the cases.

## Case template

Write the labels in this order. Omit an optional label rather than filling it with `Not applicable`.

```markdown
### <Symptom as the reader observes it>

**Symptoms:**

* <observable fact>
* <observable fact>

**Root cause:**

<why this happens>

**How to check:**

1. <step that confirms or rules out the cause>

**How to fix:**

1. <step the operator runs>

**How to avoid this issue:**

<configuration or practice that prevents recurrence>

**Data to collect:**

* <evidence to attach when escalating>

**Sources:**

* [<page title>](<url>)
```

Required, in this order: `**Symptoms:**`, `**Root cause:**`, `**How to check:**`, `**How to fix:**`, `**Sources:**`.

Optional, at the positions shown: `**How to avoid this issue:**`, `**Data to collect:**`.

### What each label holds

`**Symptoms:**` — see [Writing symptoms](#writing-symptoms) below.

`**Root cause:**` — the mechanism, not a restatement of the symptom. When several causes produce the same symptom,
number them and order them by how often they turn out to be the real one.

`**How to check:**` — steps that tell the causes apart and confirm one. Each step names the command, file, or page
that yields the answer, and says what a healthy result looks like.

`**How to fix:**` — steps the operator runs. Fix the cause the check confirmed; do not offer a fix menu that repeats
the cause list. Where a fix destroys data or degrades the system, say so on the step itself rather than in a note the
reader meets afterward.

`**How to avoid this issue:**` — the setting or practice that prevents recurrence. Skip it when the fix already is the
prevention.

`**Data to collect:**` — the evidence someone needs when the fix does not work and the case is escalated.

`**Sources:**` — required provenance for the symptom, cause, and fix. Repository cases cite the relevant document,
ticket, test, or `path:line`. Externally researched cases link the report that shows the failure and the authoritative
source that supports the mechanism or fix. When one part is unavailable, keep the source you have and report the
unconfirmed claim in chat during handoff; do not add a confidence marker to the reference.

## Case titles

Title the case with the symptom as the reader observes it, not with the diagnosis they do not have yet. Someone facing
`Connection refused on the backend port` does not yet know whether the service is down or the port is wrong, so that is
a usable title and `Backend service misconfiguration` is not.

Two cases whose titles differ only by their cause need a distinguishing word in the title, and a forward reference from
each to the other, so a reader who lands on the wrong one leaves for the right one.

Headings are sentence case, with product names capitalized as their vendors write them: `Disk full on the service VM`,
not `Disk Full on the Service VM`.

## Writing symptoms

`**Symptoms:**` lists what a person observes. It is the anchor for every search that reaches this file, and the reason
searches land in the right section.

- Quote verbatim log lines, error strings, and UI messages in backticks or a fenced block. Reproduce them exactly — a
  paraphrased error line cannot be matched against what the reader has in front of them.
- Describe symptoms that produce no log line in plain words. A slow UI, a virtual IP that never moves, and a container
  that keeps restarting are complete symptoms without a quotable string.
- Use the words a person reaches for when they describe the failure — `slow`, `restarting`, `not accessible`,
  `connection refused`. A fuzzy search matches on these, and they are the only handle a prose symptom offers.
- Put one observation per bullet.

Verbatim strings and prose carry equal weight. A case whose symptoms are entirely prose is a normal case, and quoting a
log line the product does not emit to make a case look uniform is worse than writing no quote at all.

## Safety: do no harm

A troubleshooting page is read by someone whose system is already broken, under time pressure, often at night. They will
run what it tells them to run. A step that costs more than it says is the page's fault, not theirs.

### Diagnosis never changes the system

Every step under `**How to check:**` must be read-only. Reading a file, listing containers, querying an API for status,
and checking disk usage are observations. Restarting a service to see whether that helps, deleting an index to test a
theory, or editing a config to try something is not diagnosis, and it does not belong there.

A `**How to check:**` step that changes state is a defect in the page, not a step that needs a warning. Move it to
`**How to fix:**` or remove it. This rule has no exceptions: fixing may carry risk, diagnosing may not.

### Dangerous steps carry a marker and a consequence

A step is dangerous when it does any of the following:

- Destroys or loses data, even data you consider worthless.
- Interrupts a running service, including a restart.
- Removes a protection or a safety limit.
- Cannot be reversed.
- Costs enough time, CPU, or disk to matter on a system already in trouble.

Mark every such step by opening it with the marker and the consequence, in bold, before the instruction and before any
command:

````markdown
1. **DANGEROUS — destroys every log stored on this VM.** Stop the containers, remove the OpenSearch data, and start
   them again. Restore from a backup afterward if you need the logs.

   ```bash
   rm -rf /var/lib/example-service/data/
   ```
````

The consequence is what makes the marker useful. `**DANGEROUS.**` alone is noise — everything eventually gets one, and
the reader stops seeing it. Name what is lost, and name it concretely: `destroys every log stored on this VM` and
`log ingestion stops until the restart completes` are the same marker carrying very different weight, and the reader
needs to tell them apart at a glance.

The marker goes **before** the command, never in a note after it. A reader follows steps in order: a warning placed
after the command is read once the data is already gone.

One step does one thing. A step that lists indices and then deletes them cannot be marked honestly — the marker would
either brand the safe half dangerous or arrive too late for the destructive half. Split it: the listing is one step,
the deletion is the next, and the marker opens the step it belongs to.

### Safe first, destructive last

When a case has both a safe fix and a destructive one, the safe one comes first. Order the steps so the reader reaches
the destructive option only after the cheaper ones are ruled out, and say what rules them out.

Where a reversal, a backup, or a restore path exists, name it in the same step as the dangerous action. Do not describe
how to destroy something without describing how to get it back, when getting it back is possible.

Where a destructive step exists only because a real fix is missing — a workaround for a bug, say — write that. A
reader who knows they are applying a workaround treats it differently from a reader who thinks it is the cure.

## Formatting

- Wrap body lines at 120 characters. Frontmatter, fenced code blocks, and pipe tables are exempt — leave them as they
  are.
- Tag every fenced code block with a language. Use `text` for log excerpts and command output that has no syntax to
  highlight.
- Wrap a code block whose lines exceed 120 characters — a real log line, usually — in
  `<!-- markdownlint-disable line-length -->` and `<!-- markdownlint-enable line-length -->`. Never wrap the log line
  itself to fit.
- Link by name: `[Backend configuration reference](https://example.com/configuration)`, not a bare URL.
- Reference another case by its title in the same file, so the anchor survives a retitle.
- Write in American English and follow the repository's `english-developer-style` rule.
- Redact credentials in every command and configuration excerpt. Use `<username>:<password>`.
- Use `<angle-brackets>` for placeholders the reader substitutes.

## Auditing a file against this format

Run these checks over a whole file, whether you are about to commit a change or reviewing an existing page. Each one
yields a verdict on a specific line, not an impression.

Structure:

- Is there exactly one `#`, and is the deepest heading `###`?
- Is every `###` title unique across the whole document, including case and reference-section titles?
- Does every `###` section either open with `**Symptoms:**` or clearly read as a reference section?
- Does every case carry `**Symptoms:**`, `**Root cause:**`, `**How to check:**`, `**How to fix:**`, and `**Sources:**`,
  in that order?
- Does every case put `**Symptoms:**` one blank line under its heading, with nothing between the two?
- Does a reader who greps a symptom land inside the section that fixes it?

Safety — the checks that matter most, because a failure here breaks a system rather than annoying a reader:

- Is every step under `**How to check:**` read-only? Any step that restarts, deletes, edits, or disables something is a
  defect: it belongs under `**How to fix:**`.
- Does every step that destroys data, interrupts a service, removes a protection, cannot be reversed, or costs
  significant resources open with `**DANGEROUS — <consequence>.**`?
- Does every marker name a concrete consequence, rather than stopping at `**DANGEROUS.**`?
- Does every marker sit before its command, rather than in a note after it?
- Where a safe fix and a destructive fix both exist, does the safe one come first?
- Where a backup or reversal is possible, is it named in the same step as the dangerous action?

Content:

- Are the quoted log lines copied from real output rather than reconstructed?
- Does every case apply to this deployment, rather than being inherited from a similar one? A case whose preconditions
  cannot occur in the shipped code or configuration does not belong here, however well written it is.
