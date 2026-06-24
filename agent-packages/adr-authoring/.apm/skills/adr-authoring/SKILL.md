---
name: adr-authoring
description: >-
  Author an Architecture Decision Record. Use whenever the user wants to capture,
  write, or draft an architecture or system-design decision — "write an ADR",
  "document this decision", "add a decision record", "we decided to use X, record
  it" — even when they don't say "ADR" but describe a choice worth tracking (a
  pattern, a non-functional requirement, a dependency, an interface, or a tool
  selection). Also use to supersede or amend an existing ADR.
---

# Authoring an ADR

You already know the ADR genre. This skill only pins the local conventions our
repositories enforce, so the record you write fits the contract on the first try.

## What belongs in an ADR

One decision per record. Reach for an ADR when a choice affects structure (for
example a pattern such as microservices), a non-functional requirement (security,
availability, fault tolerance), a dependency, a published interface or API, or a
construction technique (a library, framework, or tool). A rough test: if the
decision needed a meeting to settle, it is worth recording.

## Local conventions

These are the parts the generic ADR format does not pin down:

- **Location** — store the file under `docs/adr/` in the same repository. ADRs are
  public unless an exception is approved.
- **Filename** — lowercase with dashes and a 4-digit prefix:
  `0002-tool-for-password-management.md`. Pick the next free number by scanning the
  existing files in `docs/adr/`; start at `0001` if the folder is empty.
- **Status** — one of `Proposed`, `Accepted`, `Rejected`, `Superseded`. A new
  record starts as `Proposed`; only set `Accepted` once the team has signed off.
- **Date** — ISO 8601 (`2025-02-16`), and only the date the decision was accepted.
  Leave it blank while the status is `Proposed`.
- **Immutability** — an accepted ADR is final. To change a decision, write a new
  ADR rather than editing the old one. Link the two in both directions under
  **Related ADRs**, and in the new record's **Consequences** note that it
  supersedes the old one and why. Set the old record's status to `Superseded`.

## Template

Fill this exact structure. Keep the `####` heading levels — the metadata block
relies on them.

```markdown
# <Architecture Decision Title>

## Status
<Proposed | Accepted | Rejected | Superseded>
#### Date
<ISO 8601 date the decision was accepted; blank while Proposed>
#### Owner
<GitHub account of the person responsible for this ADR>
#### Participants and approvers
<Teams and GitHub accounts involved in the decision>
#### Related ADRs
<Links to related or superseded ADRs, if any>

## Context
<Problem statement and the forces at play — technical, organizational, project-specific. A value-neutral description of the facts.>

## Decision
<The decision, in active voice: "We will...">

### Justification
<Why this option won, which alternatives were considered, and why they were rejected.>

## Consequences
<The resulting context — positive, negative, and neutral effects on the team and project.>
```

## Drafting from the user's input

Turn the user's notes, meeting summary, or free-text description into the template
above. Write plain, simple technical English and keep it minimal. Where the input
leaves a section thin, make a reasonable assumption and mark it clearly (for
example "Assumption: ..."), rather than leaving the section empty or stalling.
Preserve every link the user supplied. Default the status to `Proposed` unless the
user states the decision is already accepted.
