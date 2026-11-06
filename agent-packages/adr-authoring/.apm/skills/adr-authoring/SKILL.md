---
name: adr-authoring
description: >-
  Author an Architecture Decision Record. Use whenever the user wants to capture, write, or draft an architecture or
  system-design decision — "write an ADR", "document this decision", "add a decision record", "we decided to use X,
  record it" — even when they don't say "ADR" but describe a choice worth tracking (a pattern, a non-functional
  requirement, a dependency, an interface, or a tool selection). Also use to supersede or amend an existing ADR, to
  restate a record as numbered rules that code can be checked against, and to name the rules a change implements or
  defers.
---

# Authoring an ADR

An ADR has three readers. An approver decides whether the decision is right. A maintainer asks later why the code is
this way. A checker, a person or an agent, holds a diff and has to reach a verdict on every requirement of the record.

The format serves the checker without costing the other two much: requirements are numbered rules with a defined
vocabulary, and the reasons stay in the record.

## What belongs in an ADR

One decision per record, with one deciding authority and one reason to change. Two decisions that different people
settle, or that change for different reasons, mean two records. Several people may approve one decision. Split no
further: decisions that one authority settles for one reason, and that a change would edit together, stay one record. A
part that changes what an earlier record decided goes into a record that supersedes that part, not into a record about
something else.

Every rule follows from the title and the Decision sentence. A rule that does not, such as the removal of an unrelated
feature or a liveness probe in a record about tokens, belongs in a record of its own, where a reader looking for it will
find it by its title.

Reach for an ADR when a choice affects structure (for example a pattern such as microservices), a non-functional
requirement (security, availability, fault tolerance), a dependency, a published interface or API, or a construction
technique (a library, framework, or tool). A rough test: if the decision needed a meeting to settle, it is worth
recording.

## Local conventions

- **Location**: follow the directory, the filename pattern, and the heading levels the repository's records already use.
  In a repository with no records, use `docs/adr/`, `0001-tool-for-password-management.md`, and the template below. Pick
  the next free number by scanning the existing files. ADRs are public unless an exception is approved.
- **Record numbers**: a number is never reused. Where a set of records still under review is split or merged after its
  numbers were cited outside its pull request (in an issue, a questionnaire, or another change), the old numbers are
  retired and the new records take the next free ones. The Context of the first new record maps each retired number to
  the records that took its parts, because a squash merge drops the pull request description and a search of the tree
  has to find them.
- **Status**: one of `Proposed`, `Accepted`, `Rejected`, `Superseded`. A new record starts as `Proposed`. Set `Accepted`
  only once the team has signed off and **Open points** is empty.
- **Date**: ISO 8601 (`2025-02-16`), and only the date the decision was accepted. On acceptance, add `### Date` with
  that date after the status line.
- **Immutability**: an accepted ADR is final. To change a decision, write a new ADR rather than editing the old one, and
  link the two in both directions under **Related ADRs**. An accepted record takes three edits and no other: `### Date`
  on acceptance, the status `Superseded` when a later record replaces it whole, and a line under **Related ADRs** that
  names a later record and what it replaces.
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

- **O1.** <The question, who decides it, and the rules it affects.>
```

A record with nothing to say under **Terms**, **Follow-ups**, or **Open points** leaves that heading out.

## Terms

A checker fails first on a word with two possible extents. Define a term here when a rule depends on where it stops:
which tokens, which addresses, which unit of work.

- Give each term one definition and one extent. A sentence such as "counts as X here" widens a term in one place, and
  the next reader misses it. Define a second term instead.
- Define a boundary word by its members or by a test: "any host other than `a.svc` and `b.svc`", not "outside the
  cluster".
- A term lives in the record that owns the concept. Other records name that record and use the word unchanged.
- Use one word per concept in the Rules, the Justification, and the Consequences, and give each outcome one wording:
  "stops the start", not also "does not start" and "refuses to start".
- Where only the program's entry point can produce an outcome literally, define the outcome word and say how a library
  below it meets the rule: "stops the start" means that the process exits before it serves a request, and a parser meets
  it by returning an error.

## Rules

A rule is one requirement that a checker can turn into a test with a definite result.

- **Form**: state the trigger, the subject, and the observable result: an input and what happens to it, a number with a
  unit, a named error, a value in a named setting. Name who or what acts.
- **Contract, not mechanism**: a rule states what a component guarantees to its readers, not how a reader consumes it
  today. Name the role, such as "policy evaluation", rather than the engine that fills it, such as OPA, unless the
  record is the one that chose the engine. An internal field layout or function name belongs in the code; a field of a
  published interface or of a persisted format that the record decides is part of the contract, and a rule states it.
- **Scope**: put every limit of the rule inside it. "Loads its source" passes a load of every source, and a reader who
  needs "and no other source" will not find it in the Justification.
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
- **Numbers**: number rules in the order they are written. Until the record merges or a rule is cited outside its
  pull request, whichever comes first, renumber freely so that the numbers run in order. After that, never renumber or
  reuse one: a rule added later takes the next free number, under whichever topic it belongs to, and a removed rule
  leaves a gap. Outside its record, always cite a rule with its record, as `ADR-0091 R7`.
- **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
  conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.
- **Every requirement is a rule**: nothing in Context, Participants, Justification, or Consequences may add a
  requirement. A reference such as "as ADR-0091 states" points at a rule that says it.
- **No position words**: "the addresses above" and "the check below" stop working when the text moves. Cite the rule.
- **No pointer rules**: a rule that only says that another rule applies adds a number and no requirement.

Reasons belong in the Justification. Keep a reason inside a rule only where it limits how the rule reads.

## Justification and alternatives

Cite rules by number, so that a checker who doubts a rule's reach can find its reason. A reason often settles an
ambiguity that the rule left open, and the rule then needs fixing. The benefits of the decision live here too, so the
Consequences carry no Positive list.

Write each rejected alternative so that a reader recognizes it in code: "Find a key by `kid` alone", not "a simpler
lookup". Name the rule that rejects it, and make sure the text of that rule excludes the alternative: a checker gives
its verdict on the rule, so an alternative the rule does not exclude is not rejected. A change that defers the rule
defers the alternative too. An alternative rejected for a reason that is not a requirement, such as cost or a license,
names that reason instead of a rule.

Where the record reverses an earlier answer, say so in that alternative and link where the answer is recorded: a
record, an issue, or a review comment. An answer with nothing to link to gets no mention; the reason that rejects the
alternative is enough.

## Consequences

- **Negative** carries every cost the decision accepts. It keeps a checker from reporting an accepted cost as a defect.
  Where the system already runs, two costs are easy to miss:
  - A request that gets a different answer than it gets today. Name the request and, where a test or a golden shows the
    answer, its name, so that a parity or regression report can cite the record.
  - What an existing installation gets on upgrade: a setting that goes away, a value that now stops the start, or trust
    that widens.

  A system with no installation and no answers yet has neither cost, and the record does not mention them.

- **Follow-ups** carries work outside the code the record governs, such as a record to update. A follow-up never holds a
  requirement.

## Open points

An open point is a question the record does not settle yet. It names who decides and which rules it touches. A checker
reports code on an open point as "cannot tell". The status stays `Proposed` until the list is empty.

Where the user's input leaves a question thin, make a reasonable assumption, write the rule as if it held, and add an
open point that names the assumption. Do not write `Assumption:` inside a rule.

## Delivery stays out of the record

A record states what the code must do, not when it arrives. Delivery state goes stale, and an accepted record cannot be
edited, so a change to code that a record with numbered rules governs declares delivery itself. Two trailers at the end
of its commit message and of its pull request description name the rules it brings and, under `Defers`, the change that
will bring each rule it leaves out:

```text
Implements: ADR-0092 R6, R8; ADR-0091 R54
Defers: ADR-0091 R38 to #208; ADR-0095 R2 to #215
```

A `Defers` target is an issue or a pull request that exists. Where no change exists yet, ask the user to open an issue
for the rule, and name it: a guessed number or a placeholder would stay in the merged commit.

`Implements` claims every case of a rule. A change that brings only some of its cases names the rule under `Defers`,
with the change that brings the rest. A change that brings no rule and leaves none out, such as a refactoring or a fix
that keeps every rule met, carries neither trailer.

## The reading guide

A repository that uses numbered rules keeps a `README.md` beside its records, added by the change that adds its first
record with numbered rules. It states how to read a record, the layers with the code each one covers, the two trailers,
that anything no rule states is the implementer's choice, which statuses bind a change, and how to check a change.
Unless the repository decides otherwise, `Accepted` and `Proposed` records bind a change, and `Superseded` and
`Rejected` records do not. Copy the steps, the table, and the definitions below into the guide word for word, so that a
reader can compare the guide with this skill:

1. Read the two trailers. They are claims: `Implements` makes a rule touched, and `Defers` makes an untouched rule
   `Deferred`, but neither shows that the code meets a rule.
2. Walk every rule of a binding record that sits in a layer the change touches, every other rule of a binding record
   that the change touches, named or not, and every rule of a binding record that the change names under `Defers`. Skip
   a rule whose own record names it as replaced under **Related ADRs**: that line, like the status `Superseded`, is
   added when the replacement is accepted. Until then the old rule binds, so a change that follows a `Proposed`
   replacement and breaks the old rule gets `Violates` on it. A missing line shows in no diff, so this walk finds the
   rule a change forgot.
3. Give each rule one verdict, and group the rows by root cause, because one defect can break several rules.

| Verdict | Meaning |
| --- | --- |
| Conforms | The change touches the rule, no open point covers the case, and the change meets the rule under every reading. |
| Violates | The change touches the rule, no open point covers the case, and the change fails the rule under every reading. |
| Deferred | The change names the rule under `Defers` and does not touch it. |
| Not touched | The change neither touches the rule nor names it under `Defers`. |
| Cannot tell | The change touches the rule, and an open point covers the case, or the change meets one reading of the rule and fails another. |

A change touches a rule when it adds, changes, or removes code, configuration, or files that act in the case the rule
describes, or names the rule under `Implements`. A defect in unchanged code that the change only calls, or moves without
changing it, is not touched, and the report names it apart. Code that acts only in a case no rule describes touches no
rule: that case is the implementer's choice. Judge each case the change acts in, and every case of a rule the
change names under `Implements`, by the table against the code as it stands after the change. A touched rule gets
`Violates` if any of its cases gets `Violates`, otherwise `Cannot tell` if any case gets `Cannot tell`, otherwise
`Conforms`.
A rule named under `Defers` that the change also touches gets the verdict of a touched rule, and the report names
the deferral beside it.

## Restating an existing record

Restating an accepted record as numbered rules means writing a new record that supersedes it whole and starts as
`Proposed`. Restating a record that is still `Proposed` replaces its text in place.

A restatement must keep every decision, and a lost fact leaves no trace in the new text. List the facts of the old
record first, then mark each as present, restated, moved, or absent, and read the new text for what it adds. Have a
reader who did not write the new text do this. Number the rules only after the old text is settled. A sentence with two
readings becomes an open point, not a choice, and the reading is settled against the source of the decision, not
against the code that happens to exist.

## Drafting from the user's input

Turn the user's notes, meeting summary, or free-text description into the template above. Write plain, simple technical
English, and leave out a sentence that none of the three readers needs. Preserve every link the user supplied. Default
the status to `Proposed`. Where the user states that the decision is accepted and the record has no open point, set
`Accepted`; where it has one, keep `Proposed` and tell the user which open points block acceptance.

Before you publish a record, read each rule as a checker would, against the sections **What belongs in an ADR**,
**Terms**, and **Rules**, and then check what one rule cannot show: that each citation says what the cited rule says.
