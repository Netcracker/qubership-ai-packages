---
name: adr-authoring
description: >-
  Author an Architecture Decision Record. Use whenever the user wants to capture, write, or draft an architecture or
  system-design decision — "write an ADR", "document this decision", "add a decision record", "we decided to use X,
  record it" — even when they don't say "ADR" but describe a choice worth tracking (a pattern, a non-functional
  requirement, a dependency, an interface, or a tool selection). Also use to supersede or amend an existing ADR, to
  rewrite a record so that code can be checked against it, to name the rules a change implements or defers, and to
  check a change against them.
---

# Authoring an ADR

An ADR has three readers. An approver decides whether the decision is right. A maintainer asks later why the code is
this way. A checker, a person or an agent, holds a diff and has to reach a verdict on every requirement of the record.

The format serves the checker without costing the other two much: requirements are numbered rules with a defined
vocabulary, and the reasons stay in the record.

## What belongs in an ADR

One decision per record, with one deciding authority and one reason to change. Two decisions that different people
settle, or that change for different reasons, mean two records. Several people may approve one decision. Split no
further: choices that one authority settles for one reason, and that a change would edit together, are one decision and
stay one record. A part that changes what an earlier record decided goes into a record that supersedes that part, not
into a record about something else.

Every rule follows from the title and the Decision sentence. A rule that does not, such as the removal of an unrelated
feature or a liveness probe in a record about tokens, belongs in a record of its own, where a reader looking for it will
find it by its title. Where a request covers two decisions, propose the split to the user rather than writing the second
record unasked.

Reach for an ADR when a choice affects structure (for example a pattern such as microservices), a non-functional
requirement (security, availability, fault tolerance), a dependency, a published interface or API, or a construction
technique (a library, framework, or tool). A rough test: if the decision needed a meeting to settle, it is worth
recording.

## Local conventions

- **Location**: follow the directory, the filename pattern, the metadata, the heading levels, and the language the
  repository's records already use. In a repository with no records, use `docs/adr/`,
  `0001-tool-for-password-management.md`, and the template below. Pick the next free number by scanning the existing
  files. ADRs are public unless an exception is approved.
- **Record numbers**: a retired record number is never reused. Where documents outside the repository cite a retired
  number, the record that takes over maps it to the new number in its Context, because a merge can drop the pull request
  description.
- **Status**: one of `Proposed`, `Accepted`, `Rejected`, `Superseded`. A new record starts as `Proposed`. Set `Accepted`
  only once the team has signed off and **Open points** is empty.
- **Date**: ISO 8601 (`2025-02-16`), and only the date the decision was accepted. On acceptance, add `### Date` with
  that date after the status line.
- **Immutability**: an accepted ADR is final once it merges. To change a decision, write a new ADR rather than editing
  the old one. The new record links the old one under **Related ADRs** at once, and the old record links back when the
  new one is accepted. A requirement added to an accepted record goes into a new record the same way; tell the user that
  the accepted record stays as it is. An accepted record takes these edits and no other: `### Date` on acceptance, the
  status `Superseded` when a later record replaces it whole, a line under **Related ADRs** that names a later record and
  what it replaces or adds, and an editorial fix that changes no rule, such as a broken link.
- **Superseding a whole record**: when the new record is accepted, set the old record's status to `Superseded`, and
  name the reason in the new record's **Consequences**.
- **Superseding part of a record**: the old record stays `Accepted`. The new record names what it replaces under
  **Related ADRs**, by rule number, or by section and a short quote where the old record has no numbers. When the new
  record is accepted, the old record gains a line under **Related ADRs** that names the same statements.

## Template

Fill this structure.

```markdown
# <The decision, stated as a sentence a reader can act on>

## Status

<Proposed | Accepted | Rejected | Superseded>

### Date

<The date the decision was accepted. Leave this heading out until then.>

### Owner

<GitHub account of the person responsible for this ADR>

### Participants and approvers

<One line per person or team: the role, the account, and what they approve.>

### Related ADRs

- [ADR-NNNN: <title>](<link>): <what this link gives, by rule number where the target has them>.

## Context

<The problem and the forces at play, as facts. No requirement belongs here.>

## Decision

<The decision, in active voice: "We will...", in one or two sentences.>

### Terms

- **<term>**: <definition with its exact extent>.

### Rules

#### <Topic>

- **R1** (`<layer>`). <One requirement.>
- **R2** (`<layer>`). <One requirement.>

### Justification

<Why this decision won, with the rules each reason supports: "(R3, R4)".>

### Alternatives considered

- **A1. <The rejected design, named so that a reader recognizes it in code>.** Rejected by R3: <reason>.

## Consequences

Negative:

- <A cost this decision accepts.>

Follow-ups:

- <Work the record creates outside the code it governs.>

## Open points

- **O1.** <The question, the answers under consideration, who decides it, and the rules it affects.>
```

A record with nothing to say under **Related ADRs**, **Terms**, **Follow-ups**, or **Open points** leaves that heading
out.

## Terms

A checker fails first on a word with two possible extents. Define a term here when a rule depends on where it stops:
which tokens, which addresses, which unit of work.

- Give each term one definition and one extent. A sentence such as "counts as X here" widens a term in one place, and
  the next reader misses it. Define a second term instead.
- Define a boundary word by its members or by a test: "any host other than `a.svc` and `b.svc`", not "outside the
  cluster".
- A term lives in the record that owns the concept. Another record that uses the word lists it under **Terms** with a
  pointer, such as "**provider**: as ADR-0091 defines it", and uses it unchanged.
- Use one word per concept in the Rules, the Justification, and the Consequences, and give each outcome one wording:
  "stops the start", not also "does not start" and "refuses to start".
- Where only the program's entry point can produce an outcome literally, define the outcome word and say how a library
  below it meets the rule: "stops the start" means that the process exits before it serves a request, and a parser meets
  it by returning an error.

## Rules

A rule is one requirement that a checker can turn into a test with a definite result.

- **Form**: state the trigger, the subject, and the observable result: an input and what happens to it, a number with a
  unit, a named error, a value in a named setting. Name who or what acts.
- **Contract, not mechanism**: a rule states what a component guarantees to its callers, not how a caller uses it
  today. Name the role, such as "policy evaluation", rather than the engine that fills it, such as OPA, unless the
  record is the one that chose the engine. An internal field layout or function name belongs in the code; a field of a
  published interface or of a persisted format that the record decides is part of the contract, and a rule states it.
- **Scope**: put every limit of the rule inside it. "Loads its source" passes a load of every source, and a reader who
  needs "and no other source" will not find it in the Justification. Where a limit arrives in a later change, state it
  as a rule of its own, and let the rule it limits point at it by number, as **Exceptions** allows.
- **One number, one check**: split a rule when its parts arrive in different changes or have different reasons, so
  that `Implements` can claim the part a change brings. One check whose parts sit in two layers and arrive in one change
  stays one rule, and carries both layer tags. The branches of one check stay one rule, such as a missing and an invalid
  value of one field. A table or a numbered list may be part of one rule when the rule is the whole mapping or the
  order.
- **A rule stands alone**: it reads correctly without its neighbors. "Such a request", "those requests", and "these"
  lose their subject when a rule is split or moved, so repeat the subject. Where two inputs share a word, name the
  input: "a token in `Authorization`", not "a token".
- **Result**: a constraint on a file or a setting names what happens when it is broken.
- **Exceptions**: an exception sits inside the rule it limits, or the rule points at it by number. A rule that reads as
  unconditional gets checked as unconditional.
- **Precedence**: where two rules can apply to one case, one of them says which wins.
- **Layer**: `(<layer>)` names the part of the system where the check runs, so read the code before you tag a rule. The
  checker looks there first. Use the names of the repository's reading guide. Where the code does not exist yet, name
  the component that will hold the check.
- **Numbers freeze**: number rules in reading order, and renumber them freely until the record merges or one of its
  rule numbers appears in an issue, a commit, or another pull request. After either, never renumber or reuse a
  number. A rule added before the record is accepted and merged takes the next free number, under whichever topic it
  belongs to, and a removed rule leaves a gap. Outside its record, always cite a rule with its record, as `ADR-0091 R7`.
- **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
  conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.
- **Every requirement is a rule**: nothing outside **Rules** may add a requirement. A reference such as "as ADR-0091
  states" points at a rule that says it.
- **No position words**: "the addresses above" and "the check below" stop working when the text moves. Cite the rule.
- **No pointer rules**: a rule that only says that another rule applies adds a number and no requirement.

Reasons belong in the Justification. Keep a reason inside a rule only where it limits how the rule reads.

## Justification and alternatives

Cite rules by number, so that a checker who doubts a rule's reach can find its reason. A reason often settles an
ambiguity that the rule left open, and the rule then needs fixing.

Write each rejected alternative so that a reader recognizes it in code: "Find a key by `kid` alone", not "a simpler
lookup". Where the record forbids the alternative, name the rule that rejects it, and make sure the text of that rule
excludes it. The verdict on code that implements the alternative then lands on that rule, and a change that defers the
rule defers the alternative too. An alternative with no such rule only explains the choice, so write it without a rule
number. Where the record reverses an earlier answer, say so in that alternative.

## Consequences

- **Negative** carries every cost the decision accepts. It keeps a checker from reporting an accepted cost as a defect.
  Where the decision changes an answer that existing callers get, name the case and the test that shows it. Where it
  changes a default, a required setting, or what the system trusts, a rule states what an existing installation gets on
  upgrade, and Negative cites it.

- **Follow-ups** carries work outside the code the record governs, such as a record to update. A follow-up never holds a
  requirement.

## Open points

An open point is a question the record does not settle yet. It names who decides, the answers under consideration, and
which rules it affects. A checker gives `Cannot tell` to a case whose outcome depends on which of those answers is
chosen, and an open point that lists no answers gives `Cannot tell` to every case of the rules it affects. The status
stays `Proposed` until the list is empty.

Where the user's input leaves a value open that a rule needs, such as a count, a timeout, an error name, or a setting,
write a visible placeholder in the rule, such as `<retry count>`, and an open point that asks for it; never invent the
value. Ask for an owner or an approver in the conversation instead.
Where it leaves a question thin otherwise, make a reasonable assumption, write the rule as if it held, and add an open
point that names the assumption. Do not write `Assumption:` inside a rule.

## Delivery stays out of the record

A record states what the code must do, not when it arrives. Delivery state goes stale, and an accepted record takes only
the edits that **Immutability** lists, so a change to code that a record with numbered rules governs declares delivery
itself. Two trailers at the end of its commit message and of its pull request description name the rules it brings
and, under `Defers`, the change that will bring each rule it leaves out:

```text
Implements: ADR-0092 R6, R8; ADR-0091 R54
Defers: ADR-0091 R38 to #208; ADR-0095 R2 to #215
```

A `Defers` target is an issue or a pull request that exists. Where no change exists yet, ask the user to open an issue
for the rule, and name it: a guessed number or a placeholder would stay in the merged commit. Without an issue, leave
the rule out of the trailers, and say in the description which rules wait for a change that has no issue yet. In a pull
request with several commits, each commit carries the trailers of its own part, and the description carries them for
the whole change; a checker reads the description.

`Implements` claims every case of a rule. A change that brings only some of its cases names the rule under `Defers`,
with the change that brings the rest. A change that brings no rule and leaves none out, such as a refactoring or a fix
that keeps every rule met, carries neither trailer.

## The reading guide

A repository that uses numbered rules keeps a `README.md` beside its records, added by the change that adds its first
record with numbered rules. Where the directory already has a `README.md`, add the guide as a section of it. Tell the
user that you added it. The guide states how to read a record, the layers, each named by its role and mapped to the
paths of its code, the two trailers, that anything no rule states is the implementer's choice, which statuses bind a
change, and how to check a change. A change that adds code under no mapped path extends the map. Unless the repository
decides otherwise, `Accepted` and `Proposed` records bind a change, and `Superseded` and `Rejected` records do not.
Copy the steps, the table, and the three paragraphs after the table into the guide word for word, and name the version
of this skill they come from, as the repository's `apm.yml` or lock file pins it, so that a reader can compare the
guide with the skill:

1. Read the two trailers in the pull request description. They are claims: `Implements` makes a rule touched, and
   `Defers` can make an untouched rule `Deferred`, but neither shows that the code meets a rule. An entry that names no
   rule of a binding record, or a `Defers` target that is not an existing issue or pull request, counts for nothing in
   steps 2 and 3, and the report lists it as a trailer error.
2. Walk every rule of a binding record that sits in a layer the change touches, every other rule of a binding record
   that the change touches, named or not, and every rule of a binding record that the change names under `Defers`. A
   change touches a layer when it adds, changes, or removes a file that the guide maps to that layer, and a changed file
   under no mapped path is a guide error that the report lists. Skip a rule whose
   own record names it as replaced under **Related ADRs**: that line, like the status `Superseded`, is added when the
   replacement is accepted. A rule of a `Proposed` record that replaces an accepted rule binds nothing until its record
   is accepted: the walk skips it, a trailer entry that names it counts for nothing, and the accepted rule governs until
   then. A binding record without numbered rules is not walked, and the
   report lists it as unchecked. A missing line of code shows in no diff, so this walk finds the rule a change forgot.
3. Give each rule one verdict, and group the rows by root cause, because one defect can break several rules. Report
   `Not touched` rules as a count.

| Verdict | Meaning |
| --- | --- |
| Conforms | The change touches the rule, and in the case it meets the rule under every reading and every answer an open point lists. |
| Violates | The change touches the rule, and in the case it fails the rule under every reading and every answer an open point lists. |
| Deferred | The change names the rule under `Defers` and does not touch it, and the rule is unmet under at least one reading or its outcome depends on an open point. |
| Not touched | The change does not touch the rule, and the rule is not `Deferred`. |
| Cannot tell | The change touches the rule, and in the case it meets the rule under one reading or answer and fails it under another, or the repository does not show the outcome. |

A case of a rule is one input or condition the rule describes, with the outcome the rule requires for it: a missing
value and an invalid value of one field are two cases of one rule, and each member of a set a rule covers, such as each
endpoint, is a case of its own. A case meets the rule only for every value of each setting and input the rule leaves
free. A judged case whose outcome the repository does not show, such as a limit a proxy enforces, gets `Cannot tell`,
and the report names what it could not see. A change touches a rule when it adds, changes, or removes code,
configuration, or a file in a way that alters the outcome of a case the rule describes, under any of its readings and
for any value of a setting or input, or when it names the rule under `Implements`. Without that name, a defect in
unchanged code that the change only moves or calls does not touch the rule, and the report names it apart.

Code that acts only in a case no rule describes touches no rule: that case is the implementer's choice. A word that
could reach the case, as `expired` reaches a token inside a clock-skew allowance, gives the rule two readings.

Judge each case whose outcome the change alters for any value of a setting or input, and every case of a rule the change
names under `Implements`, by the table against the code as it stands after the change. A touched rule gets `Violates` if
any of its judged cases gets `Violates`, otherwise `Cannot tell` if any gets `Cannot tell`, otherwise `Conforms`. A rule
named under `Defers` that the change also touches gets the verdict of a touched rule, and the report names the deferral
beside it.

## Rewriting an existing record

A `Proposed` record is rewritten in place. An accepted record is final once it merges, so its rewrite is a new
`Proposed` record that supersedes the old one on acceptance, and the old record governs every change until then. Before
rewriting accepted records, tell the user how many new records that makes, and ask whether to proceed.

A rewrite must keep every decision, and a lost fact leaves no trace in the new text. List the facts of the old record
first, then mark each as present, restated, moved, or absent, and read the new text for what it adds. Ask the user once
who does this check: a reader who did not write the new text, such as a fresh subagent or a colleague. Without an
answer, do it yourself and say so. Keep the fact list in the conversation, not in the repository. Number the rules only
after the old text is settled. A sentence with two readings becomes an open point, not a choice, and the reading is
settled against the source of the decision, not against the code that happens to exist.

## Drafting from the user's input

Turn the user's notes, meeting summary, or free-text description into the template above. Write plain, simple technical
prose in the language of the repository's records, or in English where there are none. Preserve every link the user
supplied. Default the status to `Proposed`. Where the user states that the decision is accepted and the record has no
open point, set `Accepted`; where it has one, keep `Proposed` and tell the user which open points block acceptance.

Before you publish a record, read each rule as a checker would, against **What belongs in an ADR**, **Form**, **One
number, one check**, **Precedence**, **One home**, and **Every requirement is a rule**, across the whole set of related
records. Two checks have no rule of their own:

1. Test each defined word on its least convenient member.
2. Read each cited rule, and confirm that it says what the citation claims.
