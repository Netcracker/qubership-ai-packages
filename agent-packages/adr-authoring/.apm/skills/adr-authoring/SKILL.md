---
name: adr-authoring
description: >-
  Author an Architecture Decision Record. Use whenever the user wants to capture, write, or draft an architecture or
  system-design decision — "write an ADR", "document this decision", "add a decision record", "we decided to use X,
  record it" — even when they don't say "ADR" but describe a choice worth tracking (a pattern, a non-functional
  requirement, a dependency, an interface, or a tool selection). Also use to supersede or amend an existing ADR, to
  rewrite a record so that code can be checked against it, and to name the rules a change implements or defers.
---

# Authoring an ADR

An ADR has three readers. An approver decides whether the decision is right. A maintainer asks later why the code is
this way. A checker, a person or an agent, holds a diff and has to reach a verdict on every requirement of the record.

The format serves the checker without costing the other two much: requirements are numbered rules with a defined
vocabulary, and the reasons stay in the record.

## What belongs in an ADR

One decision per record, with one approver and one reason to change. Two approvers or two reasons mean two records.

Reach for an ADR when a choice affects structure (for example a pattern such as microservices), a non-functional
requirement (security, availability, fault tolerance), a dependency, a published interface or API, or a construction
technique (a library, framework, or tool). A rough test: if the decision needed a meeting to settle, it is worth
recording.

## Local conventions

- **Location**: follow the directory and the filename pattern the repository already uses. In a repository with no
  records, use `docs/adr/` and `0001-tool-for-password-management.md`. Pick the next free number by scanning the
  existing files. ADRs are public unless an exception is approved.
- **Status**: one of `Proposed`, `Accepted`, `Rejected`, `Superseded`. A new record starts as `Proposed`. Set `Accepted`
  only once the team has signed off and **Open points** is empty.
- **Date**: ISO 8601 (`2025-02-16`), and only the date the decision was accepted. Add `#### Date` on acceptance.
- **Immutability**: an accepted ADR is final. To change a decision, write a new ADR rather than editing the old one, and
  link the two in both directions under **Related ADRs**.
- **Superseding a whole record**: set the old record's status to `Superseded`, and name the reason in the new record's
  **Consequences**.
- **Superseding part of a record**: the old record stays `Accepted`. The new record names what it replaces under
  **Related ADRs**, by rule number, or by section and a short quote where the old record has no numbers. When the new
  record is accepted, the old record gains a line under **Related ADRs** that names the same statements. That line is
  the only edit an accepted record takes.

## Template

Fill this exact structure. Keep the heading levels: the metadata block relies on them.

```markdown
# <The decision, stated as a sentence a reader can act on>

## Status

<Proposed | Accepted | Rejected | Superseded>

#### Owner

<GitHub account of the person responsible for this ADR>

#### Participants and approvers

<One line per person or team: the role, the account, and what they approve.>

#### Related ADRs

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
- Define an outcome word that a package below the top layer cannot perform literally, such as "stops the start".

## Rules

A rule is one requirement that a checker can turn into a test with a definite result.

- **Form**: state the trigger, the subject, and the observable result: an input and what happens to it, a number with a
  unit, a named error, a value in a named setting. Name who or what acts.
- **Scope**: put every limit of the rule inside it. "Loads its source" passes a load of every source, and a reader who
  needs "and no other source" will not find it in the Justification.
- **One number, one check**: split a rule when its parts live in different layers, arrive in different changes, or have
  different reasons, so that `Implements` can claim the part a change brings. The branches of one check stay one rule,
  such as a missing and an invalid value of one field. A table or a numbered list may be part of one rule when the rule
  is the whole mapping or the order.
- **A rule stands alone**: it reads correctly without its neighbors. "Such a request", "those requests", and "these"
  lose their subject when a rule is split or moved, so repeat the subject. Where two inputs share a word, name the
  input: "a token in `Authorization`", not "a token".
- **Result**: a constraint on a file or a setting names what happens when it is broken.
- **Exceptions**: an exception sits inside the rule it limits, or the rule points at it by number. A rule that reads as
  unconditional gets checked as unconditional.
- **Precedence**: where two rules can apply to one case, one of them says which wins.
- **Layer**: `(<layer>)` names the part of the system where the check runs, so read the code before you tag a rule. The
  checker looks there first. Use the names of the repository's reading guide, and two tags only where two layers each
  hold part of the rule.
- **Numbers are permanent**: number rules in the order they are written, and never renumber or reuse one. A rule added
  later takes the next free number, under whichever topic it belongs to. A removed rule leaves a gap. Outside its
  record, always cite a rule with its record, as `ADR-0091 R7`.
- **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
  conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.
- **Every requirement is a rule**: nothing in Context, Participants, Justification, or Consequences may add a
  requirement. A reference such as "as ADR-0091 states" points at a rule that says it.
- **No position words**: "the addresses above" and "the check below" stop working when the text moves. Cite the rule.
- **No pointer rules**: a rule that only says that another rule applies adds a number and no requirement.

Reasons belong in the Justification. Keep a reason inside a rule only where it limits how the rule reads.

## Justification and alternatives

Cite rules by number, so that a checker who doubts a rule's reach can find its reason. A reason often settles an
ambiguity that the rule left open, and the rule then needs fixing.

Write each rejected alternative so that a reader recognizes it in code: "Find a key by `kid` alone", not "a simpler
lookup". Name the rule that rejects it, because a change that defers the rule defers the alternative too. A rejected
alternative binds like a rule: code that implements one violates the record. Where the record reverses an earlier
answer, say so in that alternative.

## Consequences

- **Negative** carries every cost the decision accepts. It keeps a checker from reporting an accepted cost as a defect.

- **Follow-ups** carries work outside the code the record governs, such as a record to update. A follow-up never holds a
  requirement.

## Open points

An open point is a question the record does not settle yet. It names who decides and which rules it touches. A checker
reports code on an open point as "cannot tell". The status stays `Proposed` until the list is empty.

Where the user's input leaves a question thin, make a reasonable assumption, write the rule as if it held, and add an
open point that names the assumption. Do not write `Assumption:` inside a rule.

## Delivery stays out of the record

A record states what the code must do, not when it arrives. Delivery state goes stale, and an accepted record cannot be
edited, so a change declares it in its description instead, and names under `Defers` the change that will bring each
rule:

```text
Implements: ADR-0092 R6, R8; ADR-0091 R54.
Defers: ADR-0091 R38 to #208; ADR-0095 R2 to the wiring change.
```

## The reading guide

A repository that uses numbered rules keeps a `README.md` beside its records. It states how to read a record, the layers
with the code each one covers, the two lines above, that anything no rule states is the implementer's choice, and how to
check a change:

1. Read the two lines. They are claims, so they guide the check and settle only the deferred rules.
2. Walk every rule of the layers the change touches, named or not. A missing line shows in no diff, so this walk finds
   the rule a change forgot.
3. Give each rule one verdict, and group the rows by root cause, because one defect can break several rules.

| Verdict | Meaning |
| --- | --- |
| Conforms | The code meets the rule. |
| Violates | The change touches the rule and does not meet it. Code that implements a rejected alternative counts too. |
| Deferred | The change names the rule under `Defers`. |
| Not touched | The change does not touch the rule. |
| Cannot tell | The rule does not decide the case, or an open point covers it. |

A change touches a rule when it adds or changes code that runs in the case the rule describes, or names the rule under
`Implements`. A defect in unchanged code that the change only moves or calls is not touched, and the report names it
apart. Where two verdicts could apply, `Deferred` wins over the others, and `Cannot tell` wins over `Violates`.

## Rewriting an existing record

A rewrite must keep every decision, and a lost fact leaves no trace in the new text. List the facts of the old record
first, then mark each as present, restated, moved, or absent, and read the new text for what it adds. Have a reader who
did not write the new text do this. Number the rules only after the old text is settled. A sentence with two readings
becomes an open point, not a choice, and the reading is settled against the source of the decision, not against the code
that happens to exist.

## Drafting from the user's input

Turn the user's notes, meeting summary, or free-text description into the template above. Write plain, simple technical
English and keep it minimal. Preserve every link the user supplied. Default the status to `Proposed` unless the user
states the decision is already accepted.

Before you publish a record, read each rule as a checker would:

1. Can you name a trigger and the observable result? If not, the rule has an undefined term or no layer.
2. Do the parts of the rule belong to different layers or changes? If so, split it, and read each part alone.
3. Does a word in the rule have a defined extent? Check its least convenient member.
4. Does another rule apply to the same case? If so, one of them says which wins.
5. Does each cited rule say what the citation claims?
6. Did Context, Justification, Participants, or Consequences add a requirement? Move it to the Rules.
7. Did a set of related records state one thing twice? Keep one, and cite it from the others.
