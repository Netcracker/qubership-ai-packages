You are the fresh reviewer of rule 9 of the agent-instruction-authoring skill, *Review a change without the case*.
Each of the three changes below edits a skill after a bad output. For each, you get the skill's instruction files as
they read after the change, then the diff of the change. You get nothing about the case that prompted it.

For each change, go through every added or changed sentence as rule 9 asks, then give the change one verdict on a line
of its own: `Verdict: general change` where every such sentence has its class and two inputs and none is a patch, or
`Verdict: contains patches` where at least one is. For a change that contains patches, quote each patch sentence and
say which rule makes it one.

## Change 1

### `SKILL.md` after the change

~~~~~markdown
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

An ADR has four readers. An approver decides whether the decision is right. A maintainer asks later why the code is
this way. An agent that writes code under the record needs to know what the code must do and how to tell that it does.
A checker, a person or an agent, holds a diff and has to reach a verdict on every requirement of the record.

The format serves the agent that writes code and the checker without costing the other two much: requirements are
numbered rules with a defined vocabulary, each rule names the check that confirms it where one exists, and the reasons
stay in the record. The agent that writes code reads **Terms**, **Rules**, **Confirmation**, and **Implementation
notes**, and anything no rule states is its choice. It works on code, not on a record, so this skill never loads for
it; the repository's guide and the instruction that points at the guide carry what it needs (**The reading guide**).

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

A rule records a decision: the answer to a question that has more than one reasonable answer, which an authority
settles for this system. Sort each requirement before you write it as a rule:

- **Decision**: it becomes a rule, also where the code does not meet it yet and where a dependency already provides it.
- **Defect**: a contract, a convention, or an accepted record already settles the requirement for this system, and the
  code departs from it with no recorded reason. An example is a Dockerfile that replaces the entrypoint that the
  platform's images keep. Restoring the code is a fix, not a decision: it gets no rule, also where the input restates
  the contract as a decision, unless this record replaces the accepted record that settles it, as a rewrite or a
  superseding record does. Propose an issue to the user instead, with its type (such as Bug), a title, and the contract
  the code departs from, or name the issue that already reports the departure. A requirement that only makes the fix
  work, such as a volume the restored entrypoint writes to, goes into the same issue. The proposal goes into your
  message to the user, and the record names neither the issue nor the fix.
- **Guarantee of a dependency**: a library, a base image, or a platform promises it to code that follows its contract,
  and no authority chose it for this system. An example is a base image whose entrypoint adds the certificates in a
  directory to the trust store. The guarantee gets no rule, and code that does not follow the contract falls under
  **Defect**. Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base
  image's README, state the guarantee in **Context** as a fact, with its source. Where its source is a decision record,
  cite its rule by what it is about instead (**One home**).

Reach for an ADR when a choice affects structure (for example a pattern such as microservices), a non-functional
requirement (security, availability, fault tolerance), a dependency, a published interface or API, or a construction
technique (a library, framework, or tool). A rough test: if the decision needed a meeting to settle, it is worth
recording.

## Local conventions

- **Location and metadata**: from the repository's records, take the directory, the filename pattern, the numbering, and
  the language, and copy their metadata block as they write it: its fields, its heading levels, and any markdownlint
  comments around them. Take every other section from the template below, even where the existing records lack it. In a
  repository with no records, use `docs/adr/`, `0001-tool-for-password-management.md`, and the whole template. Pick the
  next free number by scanning the existing files. ADRs are public unless an exception is approved.
- **Record numbers**: a retired record number is never reused. Where documents outside the repository cite a retired
  number, the record that takes over maps it to the new number in its Context, because a merge can drop the pull request
  description.
- **Status**: one of `Proposed`, `Accepted`, `Rejected`, `Superseded`. A new record starts as `Proposed`. Set `Accepted`
  only once the team has signed off and **Open points** is empty. A proposal the team declines merges with the status
  `Rejected`: it binds nothing and records why, so that the question is not reopened without new facts. Where an
  accepted record chose another option, the declined one goes under that record's **Alternatives considered** instead.
  Where the team wants to forbid an option, write an `Accepted` record, such as "We will not use X", with a rule a
  checker can apply.
- **Date**: ISO 8601 (`2025-02-16`), and only the date the decision was accepted. On acceptance, add the Date heading
  with that date after the status line, at the level of the other metadata headings.
- **Immutability**: an accepted ADR is final once it merges. To change a decision, write a new ADR rather than editing
  the old one. The new record links the old one under **Related ADRs** at once, and the old record links back when the
  new one is accepted. A requirement added to an accepted record goes into a new record the same way; tell the user that
  the accepted record stays as it is. An accepted record takes these edits and no other: the Date heading on acceptance,
  the status `Superseded` when a later record replaces it whole, a line under **Related ADRs** that names a later record
  and what it replaces or adds, an addition to or a correction of **Confirmation** or **Implementation notes**, and an
  editorial fix that changes no rule, such as a broken link.
- **Superseding a whole record**: when the new record is accepted, set the old record's status to `Superseded`, and
  name the reason in the new record's **Consequences**.
- **Superseding part of a record**: the old record stays `Accepted`. The new record names what it replaces under
  **Related ADRs**, by rule number, or by section and a short quote where the old record has no numbers. When the new
  record is accepted, the old record gains a line under **Related ADRs** that names the same statements.

## Template

Fill this structure. `references/structural-invariant.md` is a whole record written in it, with structural rules.

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

<The problem and the forces at play, as facts. No requirement belongs here, and no rule of this record or another is
restated (**One home**).>

## Decision

<The decision, in active voice: "We will...", in one or two sentences.>

### Terms

- **<term>**: <definition with its exact extent>.

### Rules

#### <Topic>

- **R1** (`<layer>`). <One requirement.>
- **R2** (`<layer>`). <One requirement.>

### Confirmation

- **R1**: <The test, lint rule, or build check that shows the rule holds.>

### Implementation notes

Adds no requirement. <The recommended way to meet the rules, an example, the migration of existing code.>

### Justification

<Why this decision won, with the rules each reason supports: "(R3, R4)".>

### Alternatives considered

- **A1. <The rejected design, named so that a reader recognizes it in code>.** Rejected by R3: <reason>.

## Consequences

Positive:

- <A gain this decision brings.>

Negative:

- <A cost this decision accepts.>

Follow-ups:

- <Work the record creates outside the code it governs.>

## Open points

- **O1.** <The question, the answers under consideration, who decides it, and the rules it affects.>
```

A record with nothing to say under **Related ADRs**, **Terms**, **Confirmation**, **Implementation notes**,
**Positive**, **Follow-ups**, or **Open points** leaves that heading out. A record leaves **Rules** out only where
**Form** says so.

## Terms

A checker fails first on a word with two possible extents. Define a term here when a rule depends on where it stops:
which tokens, which addresses, which unit of work.

- A term fixes only the extent of a word: which things, or which outcomes, it covers. What the system does with a member
  is a rule. Where the extent is itself the decision, such as which algorithms count as a verified signature or which
  key sources are trusted, state it as a rule, and let the term point at the rule by number.
- Give each term one definition and one extent. A sentence such as "counts as X here" widens a term in one place, and
  the next reader misses it. Define a second term instead.
- Define a boundary word by its members or by a test: "any host other than `a.svc` and `b.svc`", not "outside the
  cluster". List the members in the record only for a set that does not change: an accepted record takes no edit that
  changes a rule, so each new member of a listed set takes a new record. For a set that is expected to change, such as
  allowed hosts, libraries, or regions, define a named set by an identifier, such as `egress-allowlist`, state as a rule
  what qualifies a member, keep the members in one file in the repository, and let the code refer to the identifier.
  Adding a member is then one pull request that changes the file and the code that handles it. Where the criterion
  cannot be checked from the repository, such as a security review of a key source, it goes into the definition of the
  term, and a rule that requires an entry in `CODEOWNERS` for that file takes the place of the criterion's rule.
- A term lives in the record that owns the concept. Another record that uses the word lists it under **Terms** with a
  pointer, such as "**provider**: as ADR-0091 defines it", and uses it unchanged.
- Use one word per concept in the Rules, the Justification, and the Consequences, and give each outcome one wording:
  "stops the start", not also "does not start" and "refuses to start".
- Where only the program's entry point can produce an outcome literally, define the outcome word and say how a library
  below it meets the rule: "stops the start" means that the process exits before it serves a request, and a parser meets
  it by returning an error.

## Rules

A rule is one requirement that a checker can turn into a test with a definite result.

- **Form**: write each rule in the shape that fits its requirement.
  - A behavior rule states the trigger, the subject, and the observable result: an input and what happens to it, a
    number with a unit, a named error, a value in a named setting. Name who or what acts.
  - A structural rule states an invariant over code, dependencies, or configuration, such as "no module under `core/`
    depends on a module under `web/`", "a new module is written in Kotlin", or "`renovate.json` extends the
    organization preset". Prefer an invariant that a machine checks, such as an architecture test, a linter, or the
    build, and name that check under **Confirmation**. Without such a check, the rule still has to be checkable by
    reading the diff, such as its imports or its build files.

  A decision that constrains nothing a checker can see in the repository, such as how architecture reviews are run,
  has no **Rules**, and a check reports its record as unchecked. A process decision that leaves a trace in the
  repository, such as a configuration file, has rules about that trace.
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
- **Layer**: `(<layer>)` names the code the rule constrains, and the checker looks there first, so read the code before
  you tag a rule. For a behavior rule, that is the component whose code produces the result; for a structural rule, it
  is the code the invariant ranges over, build files included. A rule over the whole repository carries the tag of every
  layer. Where the check runs belongs under **Confirmation**. Use the names of the repository's reading guide. Where the
  code does not exist yet, name the component that will hold it.
- **Numbers freeze**: number rules in reading order, and renumber them freely until the record merges or one of its
  rule numbers appears in an issue, a commit, or another pull request. After either, never renumber or reuse a
  number. A rule added before the record is accepted and merged takes the next free number, under whichever topic it
  belongs to, and a removed rule leaves a gap. Outside its record, always cite a rule with its record, as `ADR-0091 R7`,
  and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`. Every record the text cites appears under
  **Related ADRs**, except a retired number that Context maps to its replacement (**Record numbers**), which has no
  file to link.
- **One home**: a requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short
  quote where the record has no numbers). Where you cite a rule of another record, in any section, name what the rule
  is about, not what it decides: "the retry limit of ADR-0031 R4", not "ADR-0031 R4 allows three retries". A
  restatement drifts. In the rule's own record, a section other than **Rules** and Context may say what the rule
  decides, with its number, as **Negative**, **Open points**, and **Confirmation** do. A table that summarizes rules
  holds rule numbers.
- **Cite only what the reader needs**: in any section, a citation earns its place where removing it would change what
  a checker tests, or would leave an approver without the reason for a rule or the cost of a consequence. Leave out a
  citation that only shows the writer knows the neighboring records: a "see also", a rule that shares a word or a
  subject with this one, a rule the change must merely not break, a reminder that a rule still applies. A rule in
  force applies to every change whether or not it is cited. Where a rule reads unclearly without a citation, rewrite
  the citing rule rather than adding a citation.
- **Every requirement is a rule**: nothing outside **Rules** may add a requirement that a change can fail,
  **Confirmation** and **Implementation notes** included. Where such a section refers to a requirement, it cites the
  rule that states it (**One home**), not the record.
- **No position words**: "the addresses above" and "the check below" stop working when the text moves. Cite the rule.
- **No pointer rules**: a rule that only repeats a requirement of another rule, or only says that another rule
  applies, adds a number and no requirement. Leave it out; where an approver needs the link, give it in the
  Justification.

Reasons belong in the Justification. Keep a reason inside a rule only where it limits how the rule reads.

## Confirmation and implementation notes

**Confirmation** names, for each rule, the test, lint rule, or build check that shows the rule holds. Prefer a check a
machine runs, and name it so that a reader can find it: the test, the linter rule, or the build task. The cases that a
passing machine check covers need no judgment from the checker (**Checking a change**, step 3). A record usually comes
before its code, so the section starts with the checks that exist and gains entries as checks land; an accepted record
takes those additions (**Immutability**). A rule with no check yet has no entry.

**Implementation notes** gives the agent that writes the code the recommended way to meet the rules, an example, and
the migration of existing code. It opens with "Adds no requirement.", and a checker ignores it. A sentence there that a
change could fail belongs in **Rules**.

## Justification and alternatives

Cite rules by number, so that a checker who doubts a rule's reach can find its reason. A reason often settles an
ambiguity that the rule left open, and the rule then needs fixing.

Write each rejected alternative so that a reader recognizes it in code: "Find a key by `kid` alone", not "a simpler
lookup". Where the record forbids the alternative, name the rule that rejects it, and make sure the text of that rule
excludes it. The verdict on code that implements the alternative then lands on that rule, and a change that defers the
rule defers the alternative too. An alternative with no such rule only explains the choice, so write it without a rule
number. Where the record reverses an earlier answer, say so in that alternative.

## Consequences

**Positive** and **Negative** list only consequences a reader would not infer from the decision itself: "we chose
PostgreSQL, so we have somewhere to store data" belongs in neither. Within that limit, Negative carries every cost the
decision accepts.

- **Negative** keeps a checker from reporting an accepted cost as a defect. Where the decision changes an answer that
  existing callers get, name the case and the test that shows it. Where it changes a default, a required setting, or
  what the system trusts, a rule states what an existing installation gets on upgrade, and Negative cites it.

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
point that names the assumption. Do not write `Assumption:` inside a rule. A question about a defect gets neither the
rule nor the open point: propose its issue (**What belongs in an ADR**).

## Delivery stays out of the record

A record states what the code must do, not when it arrives. Delivery state goes stale, and an accepted record takes only
the edits that **Immutability** lists. So in a repository whose guide asks for the trailers (**The reading guide**), a
change to code that a binding record governs declares delivery itself. Two trailers at the end of its commit message and
of its pull request description name the rules it brings and, under `Defers`, the change that will bring each rule it
leaves out:

```text
Implements: ADR-0092 R6, R8; ADR-0091 R54
Defers: ADR-0091 R38 to #208; ADR-0095 R2 to #215
```

A `Defers` target is an issue or a pull request that exists. Where no change exists yet, ask the user to open an issue
for the rule, and name it: a guessed number or a placeholder would stay in the merged commit. Without an issue, leave
the rule out of the trailers, and say in the description which rules wait for a change that has no issue yet. In a pull
request with several commits, each commit carries the trailers of its own part, and the description carries them for
the whole change; a checker reads the description. The trailers may also name a rule of a `Proposed` record about the
code, because code often lands before its record is accepted.

`Implements` claims every case of a rule. A change that brings only some of its cases names the rule under `Defers`,
with the change that brings the rest. A change that brings no rule and leaves none out, such as a refactoring or a fix
that keeps every rule met, carries neither trailer.

## The reading guide

A repository that wants its changes checked against numbered rules keeps a guide in a `README.md` beside its records,
or in a section of the `README.md` already there. The guide commits the team to a process: every change to code under
the paths it maps ends its commit message and its pull request description with the trailers. Before you add a guide,
ask the user, and name that commitment in the question, unless the user's request already agrees to it. Without a
guide, records still carry numbered rules, and no change owes the trailers (**Checking a change** says how such a
repository is checked).

The guide holds the following, and no copy of this skill's procedure:

- the layers, each named by its role and mapped to the paths of its code, and the paths that belong to no layer, such
  as `docs/adr/`. A path belongs to no layer only while no rule constrains it: a file that a rule constrains, such as
  `go.mod` under a rule about dependencies or a workflow under a rule about releases, belongs to a layer. A test
  beside its code belongs to the layer of that code, and a separate test directory belongs to the layer it tests or to
  no layer. A change that adds a file that neither the layers nor that list cover extends one of them;
- which statuses bind a change: unless the repository decides otherwise, `Accepted` records bind a change, and
  `Proposed`, `Superseded`, and `Rejected` records do not. Where the guide makes `Proposed` records bind, a `Proposed`
  rule that replaces an accepted rule still binds nothing until its record is accepted, and the accepted rule governs
  until then;
- what the agent that writes code reads in the records that govern it, **Terms**, **Rules**, **Confirmation**, and
  **Implementation notes**, and that anything no rule states is its choice;
- the two trailers;
- a link to **Checking a change** in this skill: to a copy that `apm install` deploys into the repository, such as
  `.agents/skills/adr-authoring/SKILL.md`, or, where the repository does not commit deployed files, to the skill on
  GitHub at the version the repository pins.

The agent that writes code under a record never loads this skill, so the guide reaches it only through a file it reads.
When you add the guide, add a short paragraph to the repository's agent instructions: to `AGENTS.md` where it is
written by hand, or, where `apm compile` renders `AGENTS.md`, to an instructions file in the repository's own
`.apm/instructions/`; then run `apm compile` and commit the files it renders. The paragraph says that the records
govern code under the paths the guide maps, that the guide is read before that code changes, and that the commit
message and the pull request description end with the trailers. It names the guide and does not copy its map.

## Checking a change

1. Read the two trailers in the pull request description. They are claims: `Implements` makes a rule touched, and
   `Defers` can make an untouched rule `Deferred`, but neither shows that the code meets a rule. An entry that names a
   `Proposed` rule that binds nothing (step 4) counts for no verdict and is not an error, because code often lands
   before its record is accepted; an entry that names a `Proposed` rule that binds the change counts like any other. Any
   other entry that names no rule of a binding record counts for nothing in the steps that follow, and so does a
   `Defers` target that is not an existing issue or pull request; the report lists each as a trailer error.
2. Walk every rule of a binding record that sits in a layer the change touches, every other rule of a binding record
   that the change touches, named or not, and every rule of a binding record that the change names under `Defers`. A
   change touches a layer when it adds, changes, or removes a file that the guide maps to that layer. A changed file
   that the guide neither maps to a layer nor lists as belonging to none is a guide error, and the report lists it.
   Skip a rule whose own record names it as replaced under **Related ADRs**: that line, like the status `Superseded`,
   is added when the replacement is accepted. A binding record without numbered rules is not walked, and the report
   lists it as unchecked. A missing line of code shows in no diff, so this walk finds the rule a change forgot.
3. Give each rule one verdict, and group the rows by root cause, because one defect can break several rules. Report
   `Not touched` rules as a count. Where the machine check that a rule's **Confirmation** names ran on the change and
   passed, and the change leaves that check and its configuration as they were, the cases the check covers meet the
   rule without further judgment, and the report names the check. The other cases of the rule are judged as usual, and
   so is every case where the checker cannot see the result.
4. Read each `Proposed` rule that binds nothing, because its record does not bind the change or because it replaces an
   accepted rule, where the rule sits in a layer the change touches or the trailers name it, as if it bound the
   change. For each such rule that the change would fail under every reading and every answer an open point lists, the
   report adds the line `would violate ADR-NNNN Rn`, and gives the rule no verdict.

| Verdict | Meaning |
| --- | --- |
| Conforms | The change touches the rule, and in the case it meets the rule under every reading and every answer an open point lists. |
| Violates | The change touches the rule, and in the case it fails the rule under every reading and every answer an open point lists. |
| Deferred | The change names the rule under `Defers` and does not touch it, and the rule is unmet under at least one reading or its outcome depends on an open point. |
| Not touched | The change does not touch the rule, and the rule is not `Deferred`. |
| Cannot tell | The change touches the rule, and in the case it meets the rule under one reading or answer and fails it under another, or the repository does not show the outcome. |

A case of a rule is one input or condition the rule describes, with the outcome the rule requires for it: a missing
value and an invalid value of one field are two cases of one rule, and each member of a set a rule covers, such as each
endpoint, is a case of its own. For a structural rule, each unit the invariant ranges over, such as each package or each
project, is a case, and so is each relation the invariant forbids, such as an import of a forbidden package. A change
alters an outcome where it adds or removes such a unit or such a relation, or makes a unit that met the invariant fail
it, or the reverse, so a new forbidden import alters an outcome even in a package that failed the invariant before. A
file that adds or removes no relation the invariant forbids, and leaves every unit meeting or failing the invariant as
before, alters no outcome. Where the change alters no outcome of the rule, the rule is `Not touched`, unless the change
names it under `Implements`. A case meets the rule only for every value of each setting and input the rule leaves free.
A judged case whose outcome the repository does not show, such as a limit a proxy enforces, gets `Cannot tell`, and the
report names what it could not see. A change touches a rule when it adds, changes, or removes code, configuration, or a
file in a way that alters the outcome of a case the rule describes, under any of its readings and for any value of a
setting or input, or when it names the rule under `Implements`. Without that name, a defect in unchanged code that the
change only moves or calls does not touch the rule, and the report names it apart. The report also names apart a case of
a touched rule that failed before the change, that the change leaves as it was, and that is not judged, such as an older
forbidden import in a package that gains a new one.

Code that acts only in a case no rule describes touches no rule: that case is the implementer's choice. A word that
could reach the case, as `expired` reaches a token inside a clock-skew allowance, gives the rule two readings.

Judge each case whose outcome the change alters for any value of a setting or input, and every case of a rule the change
names under `Implements`, by the table against the code as it stands after the change. A touched rule gets `Violates` if
any of its judged cases gets `Violates`, otherwise `Cannot tell` if any gets `Cannot tell`, otherwise `Conforms`. A rule
named under `Defers` that the change also touches gets the verdict of a touched rule, and the report names the deferral
beside it.

In a repository without a guide, `Accepted` records bind a change, the trailers count for nothing, and no file is a
guide error: step 2 walks only the rules the change touches, and no rule is `Deferred`.

## Rewriting an existing record

A `Proposed` record is rewritten in place. An accepted record is final once it merges, so its rewrite is a new
`Proposed` record that supersedes the old one on acceptance, and the old record governs every change until then (**The
reading guide**, on which statuses bind). Before rewriting accepted records, tell the user how many new records that
makes, and ask whether to proceed.

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

Where the input asks a question about a defect, or you would ask one, answer it as **What belongs in an ADR** says:
name the contract the code departs from, and propose the issue. Do not ask the user to choose between the contract and
the departure. Where the user says that the departure is deliberate, or asks for the rule after you name the defect,
it is a decision, and it gets a rule.

Before you publish a record, read each rule as a checker would, against **What belongs in an ADR**, **Form**, **One
number, one check**, **Precedence**, **One home**, **No pointer rules**, **Cite only what the reader needs**, and
**Every requirement is a rule**, across the whole set of related records. Then read every sentence outside **Rules**
that cites a rule, in Context, the Justification, and the Consequences too, against **One home** and **Cite only what
the reader needs**. Two checks have no rule of their own:

1. Test each defined word on its least convenient member.
2. Read each cited rule, and confirm that it says what the citation claims.
~~~~~

### The diff

~~~~~diff
diff --git a/agent-packages/adr-authoring/.apm/skills/adr-authoring/SKILL.md b/agent-packages/adr-authoring/.apm/skills/adr-authoring/SKILL.md
index a8f4dbe7..cfb0a16e 100644
--- a/agent-packages/adr-authoring/.apm/skills/adr-authoring/SKILL.md
+++ b/agent-packages/adr-authoring/.apm/skills/adr-authoring/SKILL.md
@@ -49,7 +49,9 @@ settles for this system. Sort each requirement before you write it as a rule:
 - **Guarantee of a dependency**: a library, a base image, or a platform promises it to code that follows its contract,
   and no authority chose it for this system. An example is a base image whose entrypoint adds the certificates in a
   directory to the trust store. The guarantee gets no rule, and code that does not follow the contract falls under
-  **Defect**. Where a rule or a reason depends on the guarantee, state it in **Context** as a fact, with its source.
+  **Defect**. Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base
+  image's README, state the guarantee in **Context** as a fact, with its source. Where its source is a decision record,
+  cite its rule by what it is about instead (**One home**).
 
 Reach for an ADR when a choice affects structure (for example a pattern such as microservices), a non-functional
 requirement (security, availability, fault tolerance), a dependency, a published interface or API, or a construction
@@ -116,7 +118,8 @@ Fill this structure. `references/structural-invariant.md` is a whole record writ
 
 ## Context
 
-<The problem and the forces at play, as facts. No requirement belongs here.>
+<The problem and the forces at play, as facts. No requirement belongs here, and no rule of this record or another is
+restated (**One home**).>
 
 ## Decision
 
@@ -241,14 +244,29 @@ A rule is one requirement that a checker can turn into a test with a definite re
 - **Numbers freeze**: number rules in reading order, and renumber them freely until the record merges or one of its
   rule numbers appears in an issue, a commit, or another pull request. After either, never renumber or reuse a
   number. A rule added before the record is accepted and merged takes the next free number, under whichever topic it
-  belongs to, and a removed rule leaves a gap. Outside its record, always cite a rule with its record, as `ADR-0091 R7`.
-- **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
-  conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.
+  belongs to, and a removed rule leaves a gap. Outside its record, always cite a rule with its record, as `ADR-0091 R7`,
+  and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`. Every record the text cites appears under
+  **Related ADRs**, except a retired number that Context maps to its replacement (**Record numbers**), which has no
+  file to link.
+- **One home**: a requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short
+  quote where the record has no numbers). Where you cite a rule of another record, in any section, name what the rule
+  is about, not what it decides: "the retry limit of ADR-0031 R4", not "ADR-0031 R4 allows three retries". A
+  restatement drifts. In the rule's own record, a section other than **Rules** and Context may say what the rule
+  decides, with its number, as **Negative**, **Open points**, and **Confirmation** do. A table that summarizes rules
+  holds rule numbers.
+- **Cite only what the reader needs**: in any section, a citation earns its place where removing it would change what
+  a checker tests, or would leave an approver without the reason for a rule or the cost of a consequence. Leave out a
+  citation that only shows the writer knows the neighboring records: a "see also", a rule that shares a word or a
+  subject with this one, a rule the change must merely not break, a reminder that a rule still applies. A rule in
+  force applies to every change whether or not it is cited. Where a rule reads unclearly without a citation, rewrite
+  the citing rule rather than adding a citation.
 - **Every requirement is a rule**: nothing outside **Rules** may add a requirement that a change can fail,
-  **Confirmation** and **Implementation notes** included. A reference such as "as ADR-0091 states" points at a rule that
-  says it.
+  **Confirmation** and **Implementation notes** included. Where such a section refers to a requirement, it cites the
+  rule that states it (**One home**), not the record.
 - **No position words**: "the addresses above" and "the check below" stop working when the text moves. Cite the rule.
-- **No pointer rules**: a rule that only says that another rule applies adds a number and no requirement.
+- **No pointer rules**: a rule that only repeats a requirement of another rule, or only says that another rule
+  applies, adds a number and no requirement. Leave it out; where an approver needs the link, give it in the
+  Justification.
 
 Reasons belong in the Justification. Keep a reason inside a rule only where it limits how the rule reads.
 
@@ -449,8 +467,10 @@ the departure. Where the user says that the departure is deliberate, or asks for
 it is a decision, and it gets a rule.
 
 Before you publish a record, read each rule as a checker would, against **What belongs in an ADR**, **Form**, **One
-number, one check**, **Precedence**, **One home**, and **Every requirement is a rule**, across the whole set of related
-records. Two checks have no rule of their own:
+number, one check**, **Precedence**, **One home**, **No pointer rules**, **Cite only what the reader needs**, and
+**Every requirement is a rule**, across the whole set of related records. Then read every sentence outside **Rules**
+that cites a rule, in Context, the Justification, and the Consequences too, against **One home** and **Cite only what
+the reader needs**. Two checks have no rule of their own:
 
 1. Test each defined word on its least convenient member.
 2. Read each cited rule, and confirm that it says what the citation claims.
~~~~~

## Change 2

### `SKILL.md` after the change

~~~~~markdown
---
name: apm-authoring
description: How to author APM packages — instructions, skills, prompts, agents, hooks. Use when editing APM primitives (`apm.yml`, `*.instructions.md`, `SKILL.md`, `*.prompt.md`, `*.agent.md`, hooks) or laying out a new `agent-packages/<name>/`.
---

# Authoring APM packages

[APM](https://github.com/microsoft/apm) is a package manager for AI-agent
primitives: **instructions** (always-on rules), **skills** (on-demand
how-to guides), **prompts** (user-invoked slash-commands), **agents**
(sub-agent personas with tool boundaries) and **hooks** (lifecycle
scripts). A platform can ship its conventions as APM packages so service
developers receive them as `apm dependencies` and agents like Claude
Code, Copilot and Cursor pick them up natively.

This skill is the contract between library authors and the agents that
read their packages. Apply it whenever you touch `apm.yml`, anything
under a `.apm/` tree, or set up a new `agent-packages/<name>/`.

## Package layout

A library repo can host one or more APM packages. Each one lives under
`agent-packages/<package-name>/` so the path itself is the disambiguator:

```text
agent-packages/
└── <package-name>/                  # = `name:` in apm.yml
    ├── apm.yml
    └── .apm/
        ├── instructions/            # *.instructions.md — always-on rules
        │   └── <package-name>.instructions.md
        ├── skills/                  # SKILL.md — on-demand how-tos
        │   └── <package-name>/
        │       └── SKILL.md
        ├── prompts/                 # avoid — Codex skips prompts; use a user-invoked skill
        │   └── <name>.prompt.md
        ├── agents/                  # optional — *.agent.md, sub-agent personas
        │   └── <name>.agent.md
        └── hooks/                   # optional — lifecycle scripts
```

Rules:

- `<package-name>` is descriptive and unique (`context-propagation-go-usage`,
  `hardened-dockerfile-usage`), **not** a generic placeholder like
  `user-guide`. Multiple packages can sit side-by-side in one repo, so the
  directory name has to identify the package on its own.
- A package holds a **coherent set** of primitives (instructions,
  skills, prompts, agents, hooks) that share an audience and a
  trigger surface (e.g. `<lib>-usage` for
  day-to-day code; a separate `<lib>-troubleshooting` if the failure-mode
  catalogue is large enough to deserve its own activation). Bundle by
  topic, not by file count — a one-skill package and a five-skill package
  are both fine if each set is internally coherent.
- An **auto-triggered** skill needs a paired instructions file.
  Without the trigger merged into `AGENTS.md` / `CLAUDE.md` the agent
  has no signal to pull the skill in. Keep names aligned so the link
  is obvious from the tree. Two cases need no instruction: a small
  always-true rule may ship as a standalone instruction with no skill
  behind it (see next section), and a **user-invoked** skill — the
  replacement for a slash-command — carries its activation rule in its
  own `description:`, so the user invokes it by name and no paired
  instruction is needed (see "Agents, hooks, and prompts").

The host repo itself is also an APM project: its own AGENTS.md / CLAUDE.md
must be **rendered by `apm compile`** from a local `.apm/` package plus
declared dependencies. Do not hand-author AGENTS.md / CLAUDE.md — `apm
compile` overwrites it.

## Choosing the right primitive

APM ships five kinds of primitives. Pick the one that matches *when*
the rule needs to fire and *who* invokes it:

- **Instructions** (`*.instructions.md`) — rules merged into the
  agent's root file (`AGENTS.md` / `CLAUDE.md`) by `apm compile` and
  living in session context on every turn. Cost: tokens × every
  consumer × every turn.
- **Skills** (`SKILL.md`) — on-demand how-to guides loaded only after
  the agent decides a skill is relevant (steered by the trigger
  phrase in a paired instruction). Cost paid only when activated.
- **Prompts** (`*.prompt.md`) — slash-commands the **user** invokes
  explicitly (`/review-pr`). The primitive exists, but `apm compile`
  does not deploy it to the Codex target, so a prompt silently
  vanishes there
  ([microsoft/apm#1781](https://github.com/microsoft/apm/issues/1781)).
  For a user-invoked workflow, ship a **skill without a paired
  instruction** instead (see below): it deploys to every target, and
  the user still invokes it by name.
- **Agents** (`*.agent.md` under `agents/`) — sub-agent personalities
  with their own context window and tool-permission boundaries.
  Spawned via `Agent` / `Task`-style tools. Use when a task deserves
  its own scratch context, or the parent should not have a particular
  tool, or the work is parallelizable.
- **Hooks** (`hooks/`) — lifecycle scripts that run at specific
  points in the agent loop (pre/post tool call, on-stop, etc.). They
  do not enter the model's context at all — they execute in the
  harness. Use them for deterministic enforcement (linters, secret
  scanners, log filters) where prose advice is unreliable.

For most library-usage packages the bulk of the work is **one
instruction** (the trigger) plus **one skill** (the how-to). A
user-invoked workflow is also a skill — one without a paired
instruction, invoked by name (see "Agents, hooks, and prompts").
Agents and hooks are reserved for the two cases the instruction-skill
pair cannot cover: isolated sub-tasks and hard enforcement.

### Instruction vs skill: the common case

The decision that comes up on almost every package is whether a given
rule should ship as a persistent instruction or as a skill. Decide
for each piece of guidance:

- **Persistent (instruction)** — rules the agent should follow on
  **every turn regardless of which files are open**, plus the
  trigger phrase that names a skill. The best instructions are
  *nudges*: cases where the LLM already knows how to do the task
  but defaults to a sub-optimal flavour of it.
  - "Pass `--batch --quiet` when invoking Maven" — saves tokens
    by suppressing chatty output. The LLM already knows Maven; the
    instruction only steers the flag.
  - "Place new ADRs under `docs/adr/<NNNN>-<slug>.md`" — repo-wide
    directory convention the LLM cannot guess.
  - "Use the `gh` CLI for all GitHub operations" — picks the right
    tool regardless of what file the agent is touching.
- **On-demand (`SKILL.md`)** — anything tied to a specific file
  type, library, or task: setup checklists, multi-step how-tos,
  code templates, library-specific call patterns, failure-mode
  catalogues. The paired instruction-trigger fires only when the
  agent reaches a relevant file, so the body never pollutes
  unrelated turns (codebase exploration, bug triage, CI debugging
  on another stack). Counter-examples — these look like instruction
  material but belong in a skill:
  - "Use `logger.InfoC(ctx, …)` in `*.go` handlers" → ships in a
    `go-authoring` (or logging-specific) skill, triggered on
    `**/*.go`. Loading it on every turn would pay tokens for it
    while reading SQL, editing YAML, or reviewing CI logs.
  - "Dockerfiles use `USER 10001:10001` and `--chown=10001:0`"
    → ships in a `hardened-dockerfile-usage` skill, triggered on
    `**/{Dockerfile,Dockerfile.*,*.Dockerfile}`.

Heuristic: an instruction earns its place only if the agent
benefits from it on **every** turn, not just when working on a
specific stack. "Always true, short, *and* cross-cutting" is an
instruction; "true when working on X" is a skill triggered by X.
If an instructions file grows past a paragraph, or starts referring
to a specific language or file type, the overflow probably wants
to move into a `SKILL.md` and be replaced by a one-line trigger.

## What an instructions file is for

Two things only: a narrow `applyTo:` and a short trigger body. Both
land in the merged `AGENTS.md` / `CLAUDE.md`, so every byte costs
tokens on every turn for every consumer.

`applyTo:` is **not a reliable runtime gate**, because what it does
depends on the compile target:

- **`apm compile` to `AGENTS.md` / `CLAUDE.md`** (the dominant
  target for Claude Code, Codex, etc.) — the target format has no
  concept of per-file scoping, so once an instruction lands in the
  merged file it loads on every turn regardless of the path the
  agent is touching. APM uses `applyTo:` here only as a *placement
  heuristic*: it picks which subdirectory's root file an
  instruction goes into (e.g. `applyTo: "frontend/**/*.tsx"` may
  land in `frontend/CLAUDE.md` instead of the repo root). Best
  effort, no guarantee.
- **Native deployment to agents that read primitives directly**
  (Cursor `.cursor/rules/*.mdc`, Copilot custom-instructions) —
  `applyTo:` (or its target-native equivalent) survives into the
  deployed file and the agent runtime treats it as a real scope
  filter.

Because at least one major target cannot honour `applyTo:` as a
runtime gate, **state the file scope in the trigger sentence
itself** — "When editing `*.go` …" — so the rule fires correctly
whatever target `apm compile` produces. Don't rely on `applyTo:`
alone to gate behaviour.

Rules for the file:

- Use a narrow `applyTo:` mask (`**/*.go`,
  `**/{Dockerfile,Dockerfile.*,*.Dockerfile}`, `**/pom.xml`) so APM can
  place the instruction near the code it governs. `**/*` is fine only
  for umbrella packages where the rule really is universal.
- The body says **what the user is doing** when the skill should
  activate — a verb phrase, ideally with the file mask — not "when the
  user works with library X". The library name is bookkeeping; the
  verb is the trigger.

```markdown
---
description: Go coding standards for cross-service context propagation.
applyTo: "**/*.go"
---

When editing `*.go` and propagating request context (X-Request-Id,
X-Version, headers, etc.) between microservices, apply the
`context-propagation-go-usage` skill.
```

Avoid in the trigger:

- `When the user works with github.com/.../<long-import-path>
  library — registering providers, initializing context,
  propagating headers, writing custom providers, working with snapshots …`
  This is the skill body, not a trigger. Pick the user-facing verb.
- Negative scope (`Do NOT use for the X operator`). If a different repo
  must not pick up your skill, that repo's own scope handles it. Don't
  fight other packages from yours.
- Padding the trigger with "or reviewing code that does …". The verb
  phrase already covers both creation and review; adding the second
  half just inflates the persistent-context cost.

## What a SKILL.md is for

The skill is what the agent reads **after** it decides to engage. Its job
is to teach the agent things it cannot infer from imports, types, or
generic documentation. Four rules:

### 1. Encode platform-specific knowledge, nothing else

Include only what the agent cannot reasonably know:

- **Required ordering** of init steps (`configloader.Init` before
  `logging.GetLogger`; `serviceloader.Register` before
  `fiberserver.Process`).
- **Side-channel contracts** (env vars, `application.yaml` files that
  must exist, k8s projected volumes that must be mounted).
- **Failure modes that look fine in code** (`Process()` panics if the
  security middleware was not registered; `AllowedHeader` silently
  no-ops without `HEADERS_ALLOWED`).
- **Helpers that replace ad-hoc work** (`ctxhelper.AddSerializableContextData`
  instead of manual header copying).
- **Conventions a reviewer would otherwise have to memorize**
  (`USER 10001:10001`, `--chown=10001:0`, `appuser`).

Leave out everything else. In particular, don't include:

- Generic ecosystem knowledge — `go get`, adding to `pom.xml`, Dockerfile
  multi-stage basics, how `CGO_ENABLED=0` produces a static binary. The
  agent already knows. Stating it dilutes the signal of what is
  platform-specific.
- Material that belongs in the library's own API docs. Languages publish
  generated docs (godoc → pkg.go.dev, javadoc, rustdoc, pydoc) and the
  agent can fetch them when needed. Repeating method signatures and
  parameter prose in the skill creates a second source of truth that
  drifts.
- Implementation-detail asides ("returns an interface with level-based
  methods", "does not override GOMEMLIMIT if already set"). If the
  developer doesn't act on it, the skill doesn't need it.

### 2. One canonical example per concern

State the rule, then show one concrete example. Do not show two examples
that vary in trivial ways — a reviewer rightly asks "is this any
different from the previous example?". If a real variant exists (Quarkus
fast-jar vs Spring Boot uber-jar; net/http vs Fiber middleware), show it
once and label what makes it different.

An example that needs a caveat after it teaches what the caveat forbids,
because the agent copies the example. At commit `51b35c9`,
`change-description-authoring` showed its pull request description under
four headings and then said "The *After* above carries headings only to
label its slots"; the description of pgjdbc/pgjdbc#4388, a 17-line fix,
came out under three headings. Show the shape you want in the common
case instead.

When listing pitfalls, prefer **rule + brief reason** over a wall of
`// WRONG: …` snippets. Negative examples without the matching positive
flow leave the reader guessing what was supposed to happen. A
"Common pitfalls" section is fine — keep each entry to a one-line cause
and one-line fix.

### 3. Don't separate "create" and "review"

The skill should make the same recommendation whether the agent is
writing new code or reviewing existing code. Avoid a dedicated
"Reviewing an existing X" section that restates the same rules in
checklist form — that's two sources to keep in sync. Express the rules
once, in active voice, and let them apply to both directions.

### 4. Fix a bad output where the rule stops, not by adding what to write

This applies to a skill and to any instruction file an agent reads
(`*.instructions.md`, `AGENTS.md`, `CLAUDE.md`, a rule file). When an
agent leaves a part of its output empty or fills it with something wrong
(a commit body that guesses at a cause, a review that pads a section
with "none found because…"), first give that part a condition that ends
it: when the part is absent, and, where it is owed, what to state and
where to stop. A clause on where to stop bounds the part on the inputs
that need it; only the condition on when it is absent keeps it off the
inputs where it is noise. A rule that says "write X" fires on every
input, including those where X is noise, and such rules pile up one per
bad output until every output carries all of them. Add one only where
the reader needs X on every input.

Before adding a rule to a section, read the rules that earlier failures
added there (`git log -S '<phrase>'` finds each one's commit and
reason), and drop the ones the new rule makes unnecessary.

## Agents, hooks, and prompts

`apm` supports these three primitives in addition to instructions
and skills, but day-to-day authoring on a library-usage package
rarely needs them. This skill does not restate their file formats —
fetch the [upstream `apm` documentation](https://github.com/microsoft/apm)
when you reach for one.

The rule that does belong here is about *when* to reach for them:
**the user decides whether to introduce an agent or a hook — do not
pick one unilaterally over a skill or instruction. Don't ship a prompt
at all; use a user-invoked skill (the Prompts bullet explains why).**

- **Agents** (`*.agent.md`) change the runtime shape — separate
  context budget, restricted tool set, parallelisable. Worth it
  when a sub-task is heavy enough to deserve its own scratch
  context, but not as a default. If the user has not asked for an
  agent, propose a skill first.
- **Hooks** run scripts at lifecycle events and do not enter the
  model's context. Use them for deterministic enforcement (linters,
  secret scanners, log filters) when prose advice has demonstrably
  failed. Don't pre-emptively wire a hook for "good hygiene".
- **Prompts** (`*.prompt.md`) run only when the user types the
  slash-command. Don't ship one: `apm compile` does not deploy prompts
  to the Codex target, so a package that relies on a prompt breaks
  silently for Codex users
  ([microsoft/apm#1781](https://github.com/microsoft/apm/issues/1781),
  closed as not planned). For a single-use workflow the user would
  otherwise invoke as a slash-command, write a **skill without a paired
  instruction** instead: it deploys to every target, and the user (or
  another agent) invokes it by name. Put the activation rule in the
  skill's `description:` — e.g. "Use only when the user asks to triage
  dependency PRs" — so it does not auto-fire on unrelated turns.

## Frontmatter and formatting

- YAML frontmatter starts at column 0. Do not indent its keys or content
  body. (Indented frontmatter renders as a blockquote inside `<pre>` and
  may not be parsed as frontmatter at all.)
- Use plain Markdown source for tables, lists and code fences. Do not
  paste rendered ASCII boxes (`┌──┬──┐`) — they are unreadable in the
  source view, agents process them poorly, and they don't survive edits.
- Code blocks specify the language (` ```go `, ` ```dockerfile `,
  ` ```yaml `).
- Skill `description:` is the field the agent uses to decide whether
  the skill is relevant. Make it a verb-led sentence describing the
  user task, not a feature list of the library.

## Versions

Do not hard-code library or image versions in skills.

- The repository's own `go.mod`, `pom.xml`, existing Dockerfile, etc. is
  the source of truth for the version a service uses. The skill should
  point the agent at that, not at a number that will be stale next
  quarter.
- Where the skill must mention a version (e.g., a base-image migration
  story), make it clear that the value is illustrative and direct the
  agent to the upstream release page.
- Distribution names should be precise or omitted. Don't write
  "OpenJDK" when you mean "Eclipse Temurin" or just "Java 21" — be
  specific or generic, never sloppy.

The skill itself is versioned in `apm.yml`. Bump that when the contract
changes (new required step, breaking rename), not on every prose edit.

## apm.yml

Minimal valid manifest:

```yaml
name: <package-name>           # matches agent-packages/<package-name>/
version: 1.0.0
description: One-sentence purpose.
author: <your-org>

# Optional: list other APM packages this one depends on.
dependencies:
  apm:
    - ../<sibling-package>                                   # same repository
    - <owner>/<repo>/<path>/agent-packages/<package>#<ref>   # another repository
```

Conventions for the dependency list:

- A package in the same repository is a relative path from this
  package's directory: `../<name>`. It resolves at the same commit as
  the package that declares it, so it needs no ref of its own.
- A package in another git repository is an absolute reference,
  `<owner>/<repo>/<path>/agent-packages/<name>#<ref>`. Pin a tag
  (`#v1.2.0`, not `@v1.2.0`) for stable consumers; pin a branch
  (`#feat/agent-packages`) only while a feature is still in review.
- Each remote dependency line resolves to one `agent-packages/<name>/`
  folder, so the suffix in the URL must end in the package directory,
  never the repo root.

## Reference: the umbrella pattern

A platform with several libraries should expose **one umbrella** package
for service developers to depend on, plus one leaf package per library
hosted alongside that library's source. The umbrella's only job is the
dependency list and a near-empty instructions file. Don't duplicate
library content in the umbrella; transitive resolution is what makes the
model work.

## Editing a skill that came from a dependency

Local primitives — files under your repo's own `.apm/` — are free to
edit and recompile. Deployed primitives that arrived via
`apm install` (under `.github/skills/`, `.cursor/rules/`, or wherever
the runtime expects them) are **not** the source of truth: a local
edit will be overwritten the next time anyone runs `apm install`
against the lockfile.

If the user asks to fix or extend a skill that came from a
dependency:

1. Locate the upstream package via `apm_modules/`:
   - **Skills, agents, prompts** — search for the folder/file by
     its name under `apm_modules/`.
   - **Instructions** — grep `apm_modules/` for the rule's text
     (instructions get merged on compile, so name-matching does not
     help).

   The matching `apm_modules/<owner>/<repo>/.../` path tells you
   the source repo; cross-check with `apm.yml` / `apm.lock` for the
   pinned version.
1. File a PR against that repo's `.apm/<primitive-folder>/<name>/`
   (e.g. `.apm/skills/<name>/SKILL.md`).
1. Once the upstream change is released, bump the version in this
   repo's `apm.yml` and run `apm install` followed by `apm compile`.

## Common authoring pitfalls

- **Trigger sentence is a feature list.** Replace with a one-verb
  description of the user task.
- **Skill restates language docs.** Drop the prose that simply mirrors
  godoc; link or trust the agent to fetch.
- **Multiple near-identical examples.** Collapse to one and explain the
  axis of variation if a second is genuinely different.
- **Tables drawn with box-drawing characters.** Convert to Markdown
  table syntax or to a bullet list.
- **Hard-coded versions in the skill body.** Defer to the consumer's
  manifest or to the upstream release page.
- **Generic wisdom mixed with platform rules.** If a paragraph could
  appear unchanged in any tutorial on the topic, it doesn't belong here.
- **Negative-only checklists.** Pair each `WRONG` with the positive
  flow, or replace with a one-line rule plus reason.
- **`agent-packages/user-guide/` as a directory name.** Use the
  package's actual name; multiple packages collide otherwise.
- **Hand-edited AGENTS.md / CLAUDE.md in a repo that already uses
  APM.** Edit the local `.apm/` package and re-run `apm compile`.
- **One "write X" rule per bad output.** Give that part of the output
  the condition that ends it first (rule 4); a "write X" rule fires
  where X is noise.
- **An example followed by "do not copy this part".** Change the
  example to the common case (rule 2).
- **Shipping a workflow as a prompt.** `apm compile` skips prompts for
  the Codex target, so the slash-command silently disappears there.
  Write a user-invoked skill (no paired instruction) instead.
~~~~~

### The diff

~~~~~diff
diff --git a/agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md b/agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md
index 9e5067ed..090da6fc 100644
--- a/agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md
+++ b/agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md
@@ -284,14 +284,16 @@ once, in active voice, and let them apply to both directions.
 
 This applies to a skill and to any instruction file an agent reads
 (`*.instructions.md`, `AGENTS.md`, `CLAUDE.md`, a rule file). When an
-agent leaves a part of its output empty or fills it with something
-wrong (a commit body that guesses at a cause, a review that pads a
-section with "none found because…"), first give that part a condition
-that ends it: what to state and where to stop, or when the part is
-absent. A rule that says "write X" fires on every input, including
-those where X is noise, and such rules pile up one per bad output until
-every output carries all of them. Add one only where the reader needs
-X on every input.
+agent leaves a part of its output empty or fills it with something wrong
+(a commit body that guesses at a cause, a review that pads a section
+with "none found because…"), first give that part a condition that ends
+it: when the part is absent, and, where it is owed, what to state and
+where to stop. A clause on where to stop bounds the part on the inputs
+that need it; only the condition on when it is absent keeps it off the
+inputs where it is noise. A rule that says "write X" fires on every
+input, including those where X is noise, and such rules pile up one per
+bad output until every output carries all of them. Add one only where
+the reader needs X on every input.
 
 Before adding a rule to a section, read the rules that earlier failures
 added there (`git log -S '<phrase>'` finds each one's commit and
~~~~~

## Change 3

### `SKILL.md` after the change

~~~~~markdown
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

- **State the goal where the step you got stuck on may not be the only way to it.** R2, R5. A
  maintainer who knows another way to the task answers the goal, not the step. A crash, a red build,
  a typo, or a broken page is its own goal, and the report needs no sentence for it. *Test:* where a
  reader could know another way to what you were doing, a sentence names the task you, or the user
  you stand for, could not complete, in words that do not depend on the project's API.
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

- **Isolate which project owns the defect, where more than one could, and put the evidence in the
  report.** R1, R2. A symptom seen through a stack is not evidence about any layer in it. Where the
  symptom sits in the project's own files, as a typo, a dead link, or a crash whose trace stops in
  its code, the place the report names is the evidence, and no isolation is owed. Where the
  project's guide publishes its own isolation procedure, run that one. Where none is published and
  the failure can be re-run, remove one layer at a time and record each result. Where nothing can be
  re-run (a production incident, a hosted service, a visual defect), isolate by observation with one
  thing varied: which layer's code the trace stops in, which browser or theme or platform shows it
  and which does not, which build first showed it. Report the elimination, not the conclusion.
  *Test:* the report contains either a sequence a reviewer can re-run whose last step uses only the
  target project, or the observations that vary one thing at a time and what each showed. Where the
  defect only appears through a dependency, the last step is the shortest chain that still fails,
  and the report names the dependency that stays and why: either it was removed and the failure went
  with it, or the symptom cannot exist without it. For a request there is no failing run, and the
  argument comes from the contract instead (`references/request-genre.md`).
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
  hit into the report with what makes yours different. The nearest hit is the closest item the
  search returned, one with another symptom included: the sentence on the difference spares a
  triager the same search. An open report of the same defect takes your
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
  found nothing, the report says so only in a slot the form or the genre has for what you searched,
  and the sentence there carries the query, because a null result establishes nothing on its own
  and a reader can judge it only by the query; with no such slot, the query goes to the hand-over
  note. Where you cannot reach
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
  split one. Where the count produced several reports, or a related report is known, each report
  says what it depends on: nothing, the other report, or a coordinated change on both sides, as in a
  protocol change that needs the client and the server together. A single report with no known
  relative says nothing about dependencies.
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
   Where the observation shows the expectation by itself, as a crash, a misspelled name beside the
   right one, or a link that returns 404 does, the observation is the grounding and needs no
   sentence of its own. Seven sources, strongest first. (1) The project's own documentation or
   specification, which includes its compatibility promise, so a documented or tested behavior that
   changed with no changelog entry, a public API a semantic versioning statement covers, and a
   behavior an earlier release the project still supports had, with the last good and the first bad
   named, are all grounded here, whether or not a page states the behavior; where the project's
   compatibility statement excludes undocumented behavior, a regression of such behavior is source
   6. (2) Runtime logic, meaning a crash, an assertion, or an error the project itself raises. (3)
   The expectation of its user community. Weaker: (4) an industry standard the project does not
   claim to implement, (5) another product's behavior, (6) a behavior the project never documented
   and you relied on, and (7) your own preference. The order is not taste: maintainers act on the
   first three, a report grounded only in the next three is the one commonly closed as invalid, and
   a personal preference is weak because nothing outside you supports it. Use a weak grounding where
   it is all you have, and say what it rests on in plain words, such as "nothing in the
   documentation promises this; it rests on our own setup"; do not write the word "weak" into the
   report. Where the artifact follows the rule you expect everywhere except in the place you report,
   as with a file that pins every call but one, that consistency supports the block once you have
   checked that the exception has no stated reason: a comment, a document, or a difference in what
   it does. It is not the project's specification. Name the strongest grounding first, and add
   another only where it establishes a requirement the first does not: a policy the project is bound
   by, such as one of the organization that owns it, or a constraint of the person asking,
   attributed to them, that explains why an existing option does not serve them
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

- **Every claim carries its source.** R1, R2. There are four kinds, and the report says which
  wherever a reader could take one for another; a report whose evidence is all your own pasted
  output needs no label. The kinds:
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
  GitHub, GitLab, or a package registry, is named and linked as it is. Where you changed or removed
  anything, say in one sentence that names were changed and what kinds of value were removed; do not
  list the originals, and where nothing changed, say nothing. Two kinds of
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
- **Give the version of the target project and of every layer between it and the symptom whose
  behavior the symptom could depend on.** R1, R4. A misspelled name in a README fails under any
  version of the tool that reads it, and the report gives the page and its commit, not the tool's
  version (§4). For an application on a device, the identifier is the build number with the platform and the OS
  version, not the marketing version alone. For a deployment, the chain includes the cluster or
  platform version, the operator or chart version, and the values or the resource that produced the
  failure, with private values substituted. *Test:* every tool, runtime, browser, operating system,
  or service in the reproduction chain whose version could change the outcome has a version or an
  identifier somewhere in the report.
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
  Where there is no form and no guide, a defect report opens with the core (§7): what you did and
  what you observed, with the pasted output, and what you expected. The parts below follow it in
  this order, each only where its condition holds: what the expectation rests on, where the core
  does not show it (§5, question 4); the version of every layer, where the symptom could depend on
  more than the project's files at the commit the report names (§6); the reproducer, where
  reproducing takes more than opening the place the report names or running the command it pastes;
  the workaround, where one exists; the analysis, marked, where you have one. A report whose parts
  fit in a few sentences carries no headings: a misspelled name in a document is a title and two
  sentences (`references/worked-cases.md`, case 7). Any form's order replaces this one. A request and
  a question take the slots their references name, in that order, under the same rule: a slot whose
  condition does not hold is left out, and one that fits in a few paragraphs carries no headings.
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

Run it over a draft, yours or someone else's. An item applies only where the rule it asks about
applies, and each rule above says when that is; an item whose condition the draft does not meet is
skipped, not answered with "none". An item that applies is answered by pointing at a sentence the
report already has, or by naming the finding. The answers are the reviewer's, not the report's: they
go in the review or the hand-over note, and a sentence added to the report to answer an item passes
the reader deletion test (§7) first. A report to a team's own backlog is read against every item,
with Ownership, Duplicates, and Redaction reduced as `references/project-conventions.md` says; an
issue you file in your own repository to fix yourself is read the same way, and its Ownership,
Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the
issue. A question owes every item except Expected behavior and Analysis, which it does not carry,
and it owes the Question or support ticket item below. A support ticket owes every item, with
Currency, Reproducer, Ownership, Duplicates, and Grounding read through the table in
`references/question-and-support-ticket.md`. A comment on an existing report owes Channel, Currency,
Execution, Attribution, Redaction, Disclosure, the comment half of Duplicates, and Reproducer for
the transcript it pastes, and Expected behavior where it adds an expected outcome. A colleague
message owes only the items its reference table keeps, and the Colleague message item below.

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
- Goal: where a reader could know another way to what you were doing, is the task you could not
  finish stated, and not only the step you got stuck on?
- Routing: does the project want this here, does the report match none of its redirect conditions,
  where you are not sure it is a defect, does the report say so and go where questions go, and where
  it may be a vulnerability, is it kept out of the public queue, the public search, and any public
  reproducer run?
- Ownership: where more than one project could own the defect, is the isolation in the report as
  re-runnable steps or as observations with one thing varied, for a request as the contract
  argument, or only as a conclusion?
- Currency: is the version an identifier that resolves to one build, inside the support window, the
  same one the reproducer declares, and for a regression are last good and first bad both stated?
- Duplicates: where the search found something, is the nearest hit in the report with what makes
  this one different; is the query recorded where §4 puts it; and does an open report of the same
  defect get a comment rather than a second report, carrying the version, the difference, your
  transcript where the thread lacks one, and nothing the thread already says?
- Count: how many owners, so how many reports; under one owner, how many independently fixable
  problems, so how many expected blocks in one report where they share a component, or linked reports
  where they do not or the project asks for one problem per issue; and where there are several
  reports or a related one is known, does each say what it depends on?
- Expected behavior, for a filed report: run the seven questions of §5 over every block, and name which
  question failed.
- Grounding: where the core does not show the expectation, which of the seven sources is it, and
  is a compatibility promise or a documented
  behavior that changed counted as the project's own specification, unless the project's
  compatibility statement excludes undocumented behavior?
- Execution: does every claim about what a tool does today carry a transcript, an attributed
  observation, or a cited document, does a claim about a run carry a run, and is a proposed
  rendering marked as one possible shape?
- Attribution: where a reader could take one kind of evidence for another, does each transcript,
  log, or recording say who produced it, and is nothing the reporter observed written as if you
  reproduced it?
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
  chain whose version could change the outcome carry one, and where the project runs reproducers, is
  the run linked, unless the defect may be a vulnerability? Where the reproducer came from someone
  else's draft, was it read before it ran, and was the run authorized and isolated or marked as not
  established?
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
  captured evidence labeled as redacted; and where anything was changed, does one sentence say
  what?
- Disclosure: does the project ask anything of a report written with a tool, and is it answered?
- Form: do the form's fields, or the fields the person filing named, appear by name in that order,
  does each carry what its label asks for, are your own sections inside or after them and never in
  place of one, does every required field carry an observation or an explicit "not established", is
  every optional field you had nothing for left blank, and where there is no form, does the report
  open on the core and carry only the parts of §8 whose condition holds, in its order?
- Request: does it state the problem and the acceptance criterion, does it carry each other slot of
  `references/request-genre.md` where that slot's condition holds, and does it pass the API deletion
  test?
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
~~~~~

### `references/colleague-message.md` after the change

~~~~~markdown
# The short form: telling a colleague

Open this when the artifact is a chat message to someone who shares the codebase, not a filed
report. Shared context may be assumed, and the message is a few lines long. The table says which
rules of the skill hold, which change shape, and which lapse; a rule not listed lapses.

| Rule | In a message to a colleague |
| --- | --- |
| Symptom first (§3) | Holds for the first line. In a shared repository a commit, a branch, or a symbol is shared vocabulary, so "main is red since abc123, run link" is a symptom, not internals |
| The goal, not only the step (§3) | Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none |
| Causal analysis marked with its confidence (§3) | Holds, and the analysis may come right after the symptom, ahead of the steps: a colleague who shares the code often wants the theory early. The message still says what you saw independently of it |
| Expected behavior (§5) | Reduced to one line each: the literal or relation you expect and what you got, where the symptom line does not say them already. "Checkout spins" says both. The seven questions are not run on a chat message |
| Evidence attributed, nothing invented (§6) | Holds. A CI run counts by its link; a step a colleague ran is theirs |
| Secrets removed, private names substituted (§6) | Secrets out: a token in a pasted log is a token in the chat history. Private names stay; the reader shares them |
| Failing output pasted as text (§6) | Holds for the error text; a screenshot may accompany it, never replace it. Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim |
| Reproducer (§6) | The command and its output where a command shows the failure, without packaging it as a project or reducing it; for something you saw on a screen, what you did and where. The versions of your tools only where the failure could depend on them; a failure CI shows too does not |
| Summary first, no speculative consequences (§7) | Hold: the ask in the first message is the summary, and a consequence you did not observe stays out |
| Ownership and currency (§4) | Reduced to naming the branch or the build where it is not the obvious one |
| Duplicate search, routing, form lookup, the project's reproducer service | Lapse |

## The four rules

- **Put the ask in the first message.** A greeting alone costs a round trip and a wait. Send the
  question, the symptom, and what you need in one message. "Checkout spins for me on staging since
  this morning; can you check the payment service?" is complete: an observation, enough context to
  act, and an ask.
- **Say what you already ruled out, where you ruled anything out.** This is the half that makes a
  longer message useful: it tells the reader where not to look and shows what your evidence covers.
  It is also where an attempted fix belongs, rather than described in place of the outcome you
  cannot reach. A one-line notice that ruled out nothing says nothing here; do not invent a list.
- **Name shared artifacts by identifiers that resolve.** A branch, a commit, a file, a symbol, a test
  name, a run link, and the ref they exist at. A colleague reads your message inside the repository;
  anything they cannot grep costs them a question.
- **Say what you want back.** A decision, a pointer, a review, or a look at a service. A message that
  describes a situation and stops has asked for nothing, and the reader has to guess whether it is
  theirs. A post to a channel rather than to a person names who is asked, or says that it asks
  nothing and links the ticket it announces.

## What may be dropped, and what may not

| Drop | Keep |
| --- | --- |
| The project's vocabulary explained | The exact error text |
| The full environment | The version or branch, when it is not the obvious one |
| The template's field names | What you expect and what you got, one line each, where the symptom does not say them |
| Background you both lived through | What you already ruled out, where you did |

## The escalation

Where the answer turns out to matter beyond the conversation, the message becomes the first draft of a
filed report, and the rules that lapsed or were reduced here apply in full: the ownership and currency
checks, the duplicate search, the seven questions on the expected block, and a reproducer someone can
run.
~~~~~

### `references/project-conventions.md` after the change

~~~~~markdown
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
expected-behavior test and, for a request, the acceptance criterion, the slot a backlog item most
often lacks. The opening still states the symptom first, and its subject may be
internal: a class, a service, or a commit is shared vocabulary here, as in a colleague message, as
long as the paragraph says what the caller or the user observed. An issue you file to fix yourself
owes the symptom, the version, and the reproducer or the observation, because the reader of the
closed issue months later has only them; ownership, duplicates, and disclosure need no line in
it.

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
~~~~~

### `references/request-genre.md` after the change

~~~~~markdown
# The request genre

Open this when the artifact is a feature or change request rather than a defect report. Most of the
skill still applies. What changes is the opening, the slots a defect report does not have, and what
becomes of the rules a defect report owes. There is no reproducer of the behavior you are asking
for, because it does not exist; every claim about today's behavior still carries its transcript or
the document it rests on (question 5 of the skill's expected-behavior test), and a demonstration of
what the current release does is usually the strongest section of a request. The reproduction on a
supported version is replaced by confirming that the current release does not already do this, and
the duplicate search by finding whether someone asked before; what it found goes in the
prior-proposals slot below. Ownership does not lapse: where the behavior sits between two projects, say which one owns
the contract and why it is the right addressee. Only the method changes, because there is no failing
run to bisect, so the argument comes from the contract rather than from a command sequence.

## The opening is inverted

A defect report opens with what broke. A request opens with what you could not do. A project's
feature form can make expected behavior or a proposed solution its first required field while
leaving current behavior optional. The form wins on order and on meaning: that field carries the
solution, marked as one possible shape, and the task you could not complete opens the first field
whose label admits it, such as context, motivation, or a description. Where no field does, the task
is the first sentence of the solution field, before the solution. Where the solution field comes
first and a later field takes the problem, the solution field opens with the task in one sentence
and the later field states it in full; the one-line opening is not a duplicate. The document's order
is the form's, and what the rule asks is that a reader meets the task before any construct the
project lacks.

*Test (the API deletion test):* remove every sentence that names your proposed API. If the remaining
text no longer states a problem, you have written a patch request with a preamble.

The title names the task or the capability, not the API: "no way to limit a retry by elapsed time"
rather than "add `maxElapsed` to `RetryPolicy`". Where you have a patch ready, say so in one line at
the end; a maintainer decides whether to ask for it, and the request has to stand without it.

## The slots

Every request carries the first two. Each other slot appears only where its condition holds, and a
two-paragraph request often needs none of them. A slot is what the request says, not a heading: a
request that fits in a few paragraphs carries no headings, and each fact appears once, so a setting
that does not serve you is stated beside the problem and not again under alternatives.

- **The problem.** A task you could not complete, in your own vocabulary. Not "the API lacks X".
- **The acceptance criterion: how anyone will know it worked.** One sentence that could become a
  test or a measurement. Phrasing it as a question the project can answer later beats any ritual
  template.
- **Who else is blocked, and what it costs, where you know or the change is costly.** Where you know
  of a party other than yourself, or of what leaving it undone costs, name them. Where the change
  costs the project something a maintainer will weigh, such as a new dependency, a changed default,
  or an API to support, a maintainer first asks how far the problem extends: name the party, or say
  that you are the only known case.
- **What is out of scope, where the request could be read as asking for more.** Where a maintainer
  could assume a related change comes with yours, one non-goals sentence names it and keeps the
  review bounded.
- **Whether it has been proposed before, and how yours differs, where the search found something or
  the process asks.** A link to the prior discussion and the difference in one sentence. Where the
  process makes what you searched a required field, the query goes there; otherwise a search that
  found nothing goes to the hand-over note, as §4 of the skill says.
- **Alternatives, where you considered one a maintainer would suggest.** In a slot of its own below
  the problem statement, subordinate, and stated with why it was ruled out. Ruling something out is
  information about your requirements; leading with it is a frame that undercuts the request. One
  kind moves: a setting you tried that does **not** solve the problem is a negative result rather
  than an alternative, and it belongs with the problem statement, in a sentence that says it does
  not fix it, as §3 of the skill says.
- **A sketch, optional and labeled.** A mock-up, a snippet, or before-and-after code helps a
  maintainer see the shape you mean. It sits below the problem statement and is marked as one possible
  shape, not as the requirement. Separate the requirement from the rendering explicitly: say which
  part you need and which part is the project's to choose.

## Grounding, for a request

The grounding order in the skill applies here too, and it costs more here. A request grounded only
in "another product does it this way" or in personal preference is the shape maintainers close.
Ground it in a task the project's own documentation says it supports, in an error the project itself
raises, or in users who hit the same wall. A genuinely new need has no documented promise behind it,
and that does not disqualify it: the grounding is then the task and what it costs today, stated as
such, with who else has it where you know. Evidence of a defect and justification for an improvement are different
things; a request does not borrow the language of a defect report to look stronger.

## A request in a team's own backlog

The forms and guides the skill reads in step 2 rarely exist there; what stands in for them is in
`project-conventions.md`. The slots above still apply, and the acceptance criterion is the one a
backlog item most often lacks.

## What the request does not owe, and the backport ask

Priority, severity, a milestone, an estimate, or a design, on a project's own tracker. Those are the
project's, and offering them is read as scope you have already claimed. Two channels differ: on a
vendor's support form severity is a field the requester sets (`question-and-support-ticket.md`), and
in a team's own backlog priority is the reporter's where the team's process says so
(`project-conventions.md`). A backport is different: where you need the change on a maintenance
line, say which line and why, with evidence that the line still takes changes. That is an ask with a
grounding, not a milestone you have set.
~~~~~

### `references/worked-cases.md` after the change

~~~~~markdown
# Worked cases

Open this when an expected block failed the test in the skill and you need the repair, or when you
want to see the rules applied end to end. Each case pairs a draft that failed a rule with the report
that serves. Cases 1 to 6 come from one investigation into test reporting in a build tool and
a test framework, so they show the rules on a library defect with a reproducer; the rules they
illustrate are the skill's, not the ecosystem's. Case 7 is constructed rather than taken from a
project, and shows the short end: a report that is only its core. Both accepted reports of cases 1
to 6 are public and worth opening:
[gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
[junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041).

## Case 1: an index where the reader needs a value

The draft asked for a test-report entry named `methodInParameterizedClass(String)[2][1]`. Question 1
of the expected-behavior test passes: there is a literal. Question 2 passes: it is unique. **Question
3 fails.** The two ordinals index the argument source, and a reader who holds only the report cannot
tell what ran.

The repair is to name the thing and keep the index only as a tiebreak. The accepted report asks for
`firstParameterizedMethod(String) [1] value = ""` and states the reason in one line: an index does not
say what ran, and it moves when a row is added to the argument source, so a report archived last week
names a different case today.

It also separates the requirement from the rendering, in the report's own words: the exact rendering
is the project's to choose, and what the reporter needs is the method name and the arguments.

## Case 2: a proposed form nobody ran

The same draft argued for the index form partly on the grounds that a reader could re-run a single
case with it. **Question 5 fails:** no transcript, and the claim was never tested.

Running it produced the strongest section of the accepted report. Two invocations fail with
the tool's own message, a third form works, and the report says which one and why it is unavailable
from the report file. A rejected assertion became evidence.

The rule is about the claims around the proposal, not the proposal. The behavior you are asking for
does not exist, so nothing can run it. What can run is every claim you make about a tool you have, and
the argument for a shape is usually one of those.

## Case 3: a setting in the wrong role

The draft for JUnit opened around a configuration setting, so it read as "configuration is enough for
me" while asking for the default to change.

The draft had filed the setting in the workaround role, so the skill's workaround deletion test
applies to it as filed: remove every sentence that presents the setting as a workaround. The
remaining text no longer stated a requirement, so the setting was carrying the report.

The accepted report puts the setting in the role the evidence supports. It does not fix the problem,
so it is neither a workaround nor an alternative: it is a negative result, and it appears under a
heading that says so, "Even `junit.jupiter.params.displayname.default` does not fix it", between the
symptom and the ask. Placed there it is the strongest argument that configuration cannot answer the
request, and placed last it would have been an aside.

A setting that does work is the other case, and it goes after everything that states the problem. The
accepted Gradle report carries its `Workaround` section there, with the causal analysis below it.

## Case 4: two symptoms in one block

The draft merged two symptoms: one class of parameterized test losing the method name, and another
losing the arguments of the class invocation.

The owner question settles it. The method name is lost by the build tool that writes the report
file; the class-invocation arguments are absent from the name the test framework supplies, and the
two are different repositories. So two reports, each stating that it does not depend on the other.
The build-tool report keeps two expected blocks of its own, one per symptom in the file it writes,
because a maintainer there could accept one and refuse the other.

## Case 5: a confident cause for a project that had already fixed it

The draft proposed filing against the test framework without checking whether the framework still had
the defect. It did not: two related reporting defects had been fixed and shipped in a maintenance
release.

The version and tracker checks catch this before any prose exists. The accepted report carries the
repaired form: it names the already-shipped fixes, bounds what each one covers, states that both were
verified on a released version and on a build from source, and then states the gap that remains. It
also carries a section arguing why the remaining gap belongs to that project and not to the build
tool, which is the honest answer when a defect lives at a boundary.

## Case 6: the analysis marked once, and the report standing without it

The accepted Gradle report carries its reading of the source under a heading of its own, and opens
that section with one sentence: this part is a guess and may be wrong, and the sections above stand
without it. Nothing above that section names a class in Gradle as the cause; the symptom, the
expected names, and the reproducer are stated from outside. Delete the section and the report still
states the problem, which is the first question of the analysis deletion test in §3 of the skill.

The draft that failed the same test traced the defect into a Gradle class inside the field that
states the current behavior. Deleting its marked reasoning left the report standing, so it passed the
first question; the trace inside the symptom failed the second.

## Case 7: a misspelled name with nothing past the core

The draft for a misspelled environment variable on a configuration page carried five headings: the
observation, the expected name, the operating system and the version of the service it was run
against, the commit that introduced the misspelling, and the search that found nothing. Every part
was true, and every part past the core failed its condition in §8 of the skill: the name the code reads is the
expectation and its grounding, the service ignores the misspelled name on every version, and nobody
needs the history to fix one word. The report that serves is the core and a title:

```markdown
Configuration page names `LOG_LEVL`; the service reads `LOG_LEVEL`

The "Logging" section of `docs/configuration.md` (at `9c41e07`) tells you to set `LOG_LEVL=debug`.
The service ignores that variable and keeps logging at `info`; `LOG_LEVEL=debug` switches it to
`debug`, and `LOG_LEVEL` is the name `config/env.go` reads.
```

The search queries, the history, and the offer of a pull request go in the hand-over note.

## Published before-and-after pairs worth copying

These come from projects' own guidance rather than from the two reports above.

| Before | After |
| --- | --- |
| "Software crashes." | "Cancelling a File Copy dialog crashes File Manager." |
| "Browser should work with my web site." | "Down-arrow scrolling doesn't work in a `<textarea>` styled with `overflow:hidden`." |
| "How do I get the color picker to take a hexadecimal RGB value?" | "I am trying to replace an image's color table with values of my choosing. The only way I can see is to edit each slot, and the color picker will not take a hexadecimal RGB value." |
| "I get SIG11 errors on kernel compiles and suspect a hairline crack in a motherboard trace. How do I check for those?" | "Kernel compiles die with SIG11 at random points on this board. Here is the hardware, the timings, and what I already swapped out." The theory is gone; the observations stay. |
| "hi" … four minutes … "what time was that thing again?" | "Hi. What time was that thing again?" |
~~~~~

### The diff

~~~~~diff
diff --git a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/SKILL.md b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/SKILL.md
index 4d833dd5..44154bdd 100644
--- a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/SKILL.md
+++ b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/SKILL.md
@@ -123,9 +123,11 @@ in it.
   expectation in the project's own code, its documentation, or the error it raises is required by §5,
   and saying why the behavior is wrong is not the same as saying where it breaks.
 
-- **State the goal, not only the step you got stuck on.** R2, R5. *Test:* a sentence names the task
-  you, or the user you stand for, could not complete, in words that do not depend on the project's
-  API.
+- **State the goal where the step you got stuck on may not be the only way to it.** R2, R5. A
+  maintainer who knows another way to the task answers the goal, not the step. A crash, a red build,
+  a typo, or a broken page is its own goal, and the report needs no sentence for it. *Test:* where a
+  reader could know another way to what you were doing, a sentence names the task you, or the user
+  you stand for, could not complete, in words that do not depend on the project's API.
 - **Describe what you did and what the machine did, in order.** R1, R3. Each step has an observable
   result. A step is a command, a click, a request, or a deploy; the result is what you saw after it.
 - **Where the target form disagrees with this skill on order or on the meaning of a field, the form
@@ -170,19 +172,21 @@ in it.
 
 ## 4. Before you file: ownership, currency, duplicates, count
 
-- **Isolate which project owns the defect, and put the evidence in the report.** R1, R2. A symptom
-  seen through a stack is not evidence about any layer in it. Where the project's guide publishes its
-  own isolation procedure, run that one. Where none is published and the failure can be re-run,
-  remove one layer at a time and record each result. Where nothing can be re-run (a production
-  incident, a hosted service, a visual defect), isolate by observation with one thing varied: which
-  layer's code the trace stops in, which browser or theme or platform shows it and which does not,
-  which build first showed it. Report the elimination, not the conclusion. *Test:* the report
-  contains either a sequence a reviewer can re-run whose last step uses only the target project, or
-  the observations that vary one thing at a time and what each showed. Where the defect only appears
-  through a dependency, the last step is the shortest chain that still fails, and the report names
-  the dependency that stays and why: either it was removed and the failure went with it, or the
-  symptom cannot exist without it. For a request there is no failing run, and the argument comes from
-  the contract instead (`references/request-genre.md`).
+- **Isolate which project owns the defect, where more than one could, and put the evidence in the
+  report.** R1, R2. A symptom seen through a stack is not evidence about any layer in it. Where the
+  symptom sits in the project's own files, as a typo, a dead link, or a crash whose trace stops in
+  its code, the place the report names is the evidence, and no isolation is owed. Where the
+  project's guide publishes its own isolation procedure, run that one. Where none is published and
+  the failure can be re-run, remove one layer at a time and record each result. Where nothing can be
+  re-run (a production incident, a hosted service, a visual defect), isolate by observation with one
+  thing varied: which layer's code the trace stops in, which browser or theme or platform shows it
+  and which does not, which build first showed it. Report the elimination, not the conclusion.
+  *Test:* the report contains either a sequence a reviewer can re-run whose last step uses only the
+  target project, or the observations that vary one thing at a time and what each showed. Where the
+  defect only appears through a dependency, the last step is the shortest chain that still fails,
+  and the report names the dependency that stays and why: either it was removed and the failure went
+  with it, or the symptom cannot exist without it. For a request there is no failing run, and the
+  argument comes from the contract instead (`references/request-genre.md`).
 - **Reproduce on a version the project still supports, and say which.** R1, R2. A defect already
   fixed in a release you did not test is a common reason a report comes back as not reproducible. For
   a team's own project, the supported version is the release that is deployed or the branch the team
@@ -194,7 +198,9 @@ in it.
   the last good and the first bad, and the bisected commit where you have it.
 - **Search for the report, and act on what you find.** R1, R4. Search the tracker with closed and
   resolved items included, or the list archive where reports travel by email, and write the nearest
-  hit into the report with what makes yours different. An open report of the same defect takes your
+  hit into the report with what makes yours different. The nearest hit is the closest item the
+  search returned, one with another symptom included: the sentence on the difference spares a
+  triager the same search. An open report of the same defect takes your
   evidence as a comment, not a second report, unless the project's process says otherwise. The
   comment carries the version you saw it on, what in your case differs from the thread, and your
   transcript where the thread has none or a different one; it restates nothing the thread already
@@ -205,8 +211,10 @@ in it.
   names the nearest hit and the difference in one sentence, and the query goes to the hand-over
   note. An open pull request that already makes the change is the nearest hit; whether a comment
   there serves better than a new report is for the person filing (§10). Where the search
-  found nothing, the sentence that says so carries the query, because a null result establishes
-  nothing on its own and a reader can judge it only by the query. Where you cannot reach
+  found nothing, the report says so only in a slot the form or the genre has for what you searched,
+  and the sentence there carries the query, because a null result establishes nothing on its own
+  and a reader can judge it only by the query; with no such slot, the query goes to the hand-over
+  note. Where you cannot reach
   the tracker, the hand-over note (§10) carries the queries the person filing should run; an
   unreachable tracker is a gap to hand over, not a step to drop.
 - **File one report per owner, one expected block per independently actionable problem, and describe
@@ -218,8 +226,10 @@ in it.
   issue (a step 2 lookup), and two linked reports where they share no component or the guide asks
   for one problem per issue. Two outcomes a maintainer cannot fix separately are one block. Where
   you cannot tell, file separately and link the two: a maintainer can merge two reports and cannot
-  split one. Each report says what it depends on: nothing, the other report, or a coordinated change
-  on both sides, as in a protocol change that needs the client and the server together.
+  split one. Where the count produced several reports, or a related report is known, each report
+  says what it depends on: nothing, the other report, or a coordinated change on both sides, as in a
+  protocol change that needs the client and the server together. A single report with no known
+  relative says nothing about dependencies.
 - **Obey the project's routing.** R1. Contact links, "ask here instead" lines, issue types, and
   component questions decide where this belongs. A correct report in the wrong queue is moved or
   closed, and either way it waits. A suspected vulnerability never goes to a public tracker, forum,
@@ -250,26 +260,29 @@ Send every expected block through seven questions in order. The first "no" is th
    offset, a line number, or an array index, keep the ordinal and put the content beside it.
 1. **Question 4. Is the grounding named, and how strong?** State what the expectation rests on,
    naming something fetchable, in the block or in a section of its own that the block points to.
-   Seven sources, strongest first. (1) The project's own documentation or specification, which
-   includes its compatibility promise, so a documented or tested behavior that changed with no
-   changelog entry, a public API a semantic versioning statement covers, and a behavior an earlier
-   release the project still supports had, with the last good and the first bad named, are all
-   grounded here, whether or not a page states the behavior; where the project's compatibility
-   statement excludes undocumented behavior, a regression of such behavior is source 6. (2) Runtime
-   logic, meaning a crash, an assertion, or an error the project itself raises. (3) The expectation
-   of its user community. Weaker: (4) an industry standard the project does not claim to implement,
-   (5) another product's behavior, (6) a behavior the project never documented and you relied on,
-   and (7) your own preference. The order is not taste: maintainers act on the first three, a report
-   grounded only in the next three is the one commonly closed as invalid, and a personal preference
-   is weak because nothing outside you supports it. Use a weak grounding where it is all you have,
-   and say what it rests on in plain words, such as "I am the only case I know of"; do not write the
-   word "weak" into the report. Where the artifact follows the rule you expect everywhere except in
-   the place you report, as with a file that pins every call but one, that consistency supports the
-   block once you have checked that the exception has no stated reason: a comment, a document, or a
-   difference in what it does. It is not the project's specification. Name the strongest grounding
-   first, and add another only where it establishes a requirement the first does not: a policy the
-   project is bound by, such as one of the organization that owns it, or a constraint of the person
-   asking, attributed to them, that explains why an existing option does not serve them
+   Where the observation shows the expectation by itself, as a crash, a misspelled name beside the
+   right one, or a link that returns 404 does, the observation is the grounding and needs no
+   sentence of its own. Seven sources, strongest first. (1) The project's own documentation or
+   specification, which includes its compatibility promise, so a documented or tested behavior that
+   changed with no changelog entry, a public API a semantic versioning statement covers, and a
+   behavior an earlier release the project still supports had, with the last good and the first bad
+   named, are all grounded here, whether or not a page states the behavior; where the project's
+   compatibility statement excludes undocumented behavior, a regression of such behavior is source
+   6. (2) Runtime logic, meaning a crash, an assertion, or an error the project itself raises. (3)
+   The expectation of its user community. Weaker: (4) an industry standard the project does not
+   claim to implement, (5) another product's behavior, (6) a behavior the project never documented
+   and you relied on, and (7) your own preference. The order is not taste: maintainers act on the
+   first three, a report grounded only in the next three is the one commonly closed as invalid, and
+   a personal preference is weak because nothing outside you supports it. Use a weak grounding where
+   it is all you have, and say what it rests on in plain words, such as "nothing in the
+   documentation promises this; it rests on our own setup"; do not write the word "weak" into the
+   report. Where the artifact follows the rule you expect everywhere except in the place you report,
+   as with a file that pins every call but one, that consistency supports the block once you have
+   checked that the exception has no stated reason: a comment, a document, or a difference in what
+   it does. It is not the project's specification. Name the strongest grounding first, and add
+   another only where it establishes a requirement the first does not: a policy the project is bound
+   by, such as one of the organization that owns it, or a constraint of the person asking,
+   attributed to them, that explains why an existing option does not serve them
    (`references/request-genre.md`).
 1. **Question 5. Was every claim about today's behavior observed, or read from a document?** The
    expected behavior may not exist anywhere yet, so nothing runs it. Everything you say around it
@@ -303,7 +316,9 @@ all it rests on. Worked repairs: `references/worked-cases.md`.
 
 ## 6. Evidence and the reproducer
 
-- **Every claim carries its source.** R1, R2. There are four kinds, and the report says which:
+- **Every claim carries its source.** R1, R2. There are four kinds, and the report says which
+  wherever a reader could take one for another; a report whose evidence is all your own pasted
+  output needs no label. The kinds:
   reproduced by you in this session, with the transcript; observed by the reporter or another
   person, with their transcript, log, or recording and their name or role; documented, with the
   document; inferred, and marked as such. The inferred kind is the kind of a causal analysis no
@@ -336,8 +351,9 @@ all it rests on. Worked repairs: `references/worked-cases.md`.
   name (`references/question-and-support-ticket.md`). In the organization's own tracker or chat the
   real names stay, because the reader finds the service, the class, and the host by them; where one
   report has to serve both readers, the sanitized copy is a second document. Code that is public, on
-  GitHub, GitLab, or a package registry, is named and linked as it is. Say in one sentence that
-  names were changed and what kinds of value were removed; do not list the originals. Two kinds of
+  GitHub, GitLab, or a package registry, is named and linked as it is. Where you changed or removed
+  anything, say in one sentence that names were changed and what kinds of value were removed; do not
+  list the originals, and where nothing changed, say nothing. Two kinds of
   content take the changes differently. Captured evidence (a log, a trace, an incident record) is
   redacted in place and labeled as redacted; nothing re-runs it, because the event is past. A
   reproducer whose inputs you changed is re-run before it ships, under the run rule below, because a
@@ -391,12 +407,15 @@ all it rests on. Worked repairs: `references/worked-cases.md`.
   becomes: the image was taken with default settings or a fresh profile where the defect survives
   them, and the build is visible in it or stated beside it. The redaction rule reads the image like
   any other evidence: document text, file names, and account names in it are content.
-- **Give the version of the target project and of every layer between it and the symptom.** R1, R4.
-  For an application on a device, the identifier is the build number with the platform and the OS
+- **Give the version of the target project and of every layer between it and the symptom whose
+  behavior the symptom could depend on.** R1, R4. A misspelled name in a README fails under any
+  version of the tool that reads it, and the report gives the page and its commit, not the tool's
+  version (§4). For an application on a device, the identifier is the build number with the platform and the OS
   version, not the marketing version alone. For a deployment, the chain includes the cluster or
   platform version, the operator or chart version, and the values or the resource that produced the
   failure, with private values substituted. *Test:* every tool, runtime, browser, operating system,
-  or service named in the reproduction chain has a version or an identifier somewhere in the report.
+  or service in the reproduction chain whose version could change the outcome has a version or an
+  identifier somewhere in the report.
 - **Where the project runs reproducers for you, use it and link the run.** R1, R2. A playground, a
   build scan, a CI job for reproducers, or a sandbox the project hosts produces a run a triager can
   open, which no sentence in your report is. A suspected vulnerability never goes there (§4).
@@ -461,11 +480,17 @@ report you review is held to all of them whoever wrote it.
   go in the body. Your own sections may sit inside a field or after the form's last field; they
   never replace one. An optional field you have nothing for, or nothing that passes the reader
   deletion test (§7), is left blank; a required one never.
-  Where there is no form and no guide, the sections of a defect report are these, in this order:
-  what you did and what you observed, with the pasted output; what you expected and what that rests
-  on; the version of every layer; the reproducer; the workaround where one exists; the analysis,
-  marked. Any form's order replaces it. A request and a question take the slots their references
-  name, in that order.
+  Where there is no form and no guide, a defect report opens with the core (§7): what you did and
+  what you observed, with the pasted output, and what you expected. The parts below follow it in
+  this order, each only where its condition holds: what the expectation rests on, where the core
+  does not show it (§5, question 4); the version of every layer, where the symptom could depend on
+  more than the project's files at the commit the report names (§6); the reproducer, where
+  reproducing takes more than opening the place the report names or running the command it pastes;
+  the workaround, where one exists; the analysis, marked, where you have one. A report whose parts
+  fit in a few sentences carries no headings: a misspelled name in a document is a title and two
+  sentences (`references/worked-cases.md`, case 7). Any form's order replaces this one. A request and
+  a question take the slots their references name, in that order, under the same rule: a slot whose
+  condition does not hold is left out, and one that fits in a few paragraphs carries no headings.
 - **A required field you have no evidence for says what is missing, not a plausible guess.** R1, R2.
   "Not established: I could not test on Windows" is usable. An invented environment is worse than a
   blank. The same sentence in an optional field is noise: leave the field blank.
@@ -520,21 +545,22 @@ file of its own, the command that files it with `--body-file`, and the note outs
 
 ## 11. Review checklist
 
-Run it over a draft, yours or someone else's. For a report filed in a tracker or sent to a list,
-every item gets an answer, "none" included. The answers are the reviewer's, not the report's: an
-item is answered by pointing at a sentence the report already has, or in the hand-over note, and a
-sentence added to the report to answer an item passes the reader deletion test (§7) first. A
-report to a team's own backlog owes every item, with
-Ownership, Duplicates, and Redaction reduced as `references/project-conventions.md` says; an issue
-you file in your own repository to fix yourself owes the same, and its Ownership, Duplicates, and
-Disclosure answers are one line each. A question owes every item except Expected behavior and
-Analysis, which it does not carry, and it owes the Question or support ticket item below. A support
-ticket owes every item, with Currency, Reproducer, Ownership, Duplicates, and Grounding read through
-the table in `references/question-and-support-ticket.md`. A comment on an existing report owes
-Channel, Currency, Execution, Attribution, Redaction, Disclosure, the comment half of Duplicates,
-and Reproducer for the transcript it pastes, and Expected behavior where it adds an expected
-outcome. A colleague message owes only the items its reference table keeps, and the Colleague
-message item below.
+Run it over a draft, yours or someone else's. An item applies only where the rule it asks about
+applies, and each rule above says when that is; an item whose condition the draft does not meet is
+skipped, not answered with "none". An item that applies is answered by pointing at a sentence the
+report already has, or by naming the finding. The answers are the reviewer's, not the report's: they
+go in the review or the hand-over note, and a sentence added to the report to answer an item passes
+the reader deletion test (§7) first. A report to a team's own backlog is read against every item,
+with Ownership, Duplicates, and Redaction reduced as `references/project-conventions.md` says; an
+issue you file in your own repository to fix yourself is read the same way, and its Ownership,
+Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the
+issue. A question owes every item except Expected behavior and Analysis, which it does not carry,
+and it owes the Question or support ticket item below. A support ticket owes every item, with
+Currency, Reproducer, Ownership, Duplicates, and Grounding read through the table in
+`references/question-and-support-ticket.md`. A comment on an existing report owes Channel, Currency,
+Execution, Attribution, Redaction, Disclosure, the comment half of Duplicates, and Reproducer for
+the transcript it pastes, and Expected behavior where it adds an expected outcome. A colleague
+message owes only the items its reference table keeps, and the Colleague message item below.
 
 - Channel: is this the place the project names for this kind of report, and is the markup the one it
   renders?
@@ -548,33 +574,37 @@ message item below.
   sentence pass the reader deletion test, and past about 300 words of prose, was it read sentence by
   sentence? Does every optional field carry only what passes the test, and is every pasted output
   trimmed to the lines the report points at (§7)?
-- Goal: is the task you could not finish stated, and not only the step you got stuck on?
+- Goal: where a reader could know another way to what you were doing, is the task you could not
+  finish stated, and not only the step you got stuck on?
 - Routing: does the project want this here, does the report match none of its redirect conditions,
   where you are not sure it is a defect, does the report say so and go where questions go, and where
   it may be a vulnerability, is it kept out of the public queue, the public search, and any public
   reproducer run?
-- Ownership: is the isolation in the report as re-runnable steps or as observations with one thing
-  varied, for a request as the contract argument, or only as a conclusion?
+- Ownership: where more than one project could own the defect, is the isolation in the report as
+  re-runnable steps or as observations with one thing varied, for a request as the contract
+  argument, or only as a conclusion?
 - Currency: is the version an identifier that resolves to one build, inside the support window, the
   same one the reproducer declares, and for a regression are last good and first bad both stated?
-- Duplicates: is the nearest hit in the report with what makes this one different, is the query
-  recorded where §4 puts it, and does an open report of the same defect get a comment rather than a
-  second report, carrying the version, the difference, your transcript where the thread lacks one,
-  and nothing the thread already says?
+- Duplicates: where the search found something, is the nearest hit in the report with what makes
+  this one different; is the query recorded where §4 puts it; and does an open report of the same
+  defect get a comment rather than a second report, carrying the version, the difference, your
+  transcript where the thread lacks one, and nothing the thread already says?
 - Count: how many owners, so how many reports; under one owner, how many independently fixable
   problems, so how many expected blocks in one report where they share a component, or linked reports
-  where they do not or the project asks for one problem per issue; and does each report say what it
-  depends on?
+  where they do not or the project asks for one problem per issue; and where there are several
+  reports or a related one is known, does each say what it depends on?
 - Expected behavior, for a filed report: run the seven questions of §5 over every block, and name which
   question failed.
-- Grounding: which of the seven sources is it, and is a compatibility promise or a documented
+- Grounding: where the core does not show the expectation, which of the seven sources is it, and
+  is a compatibility promise or a documented
   behavior that changed counted as the project's own specification, unless the project's
   compatibility statement excludes undocumented behavior?
 - Execution: does every claim about what a tool does today carry a transcript, an attributed
   observation, or a cited document, does a claim about a run carry a run, and is a proposed
   rendering marked as one possible shape?
-- Attribution: does each transcript, log, or recording say who produced it, and is nothing the reporter
-  observed written as if you reproduced it?
+- Attribution: where a reader could take one kind of evidence for another, does each transcript,
+  log, or recording say who produced it, and is nothing the reporter observed written as if you
+  reproduced it?
 - Analysis: is the block marked with its confidence, does the report stand when you delete it, and
   does any sentence you wrote name the cause inside the symptom or the steps?
 - Workarounds: is a setting that works placed after everything that states the problem, or in the
@@ -586,9 +616,10 @@ message item below.
   nothing outside the target project or name the layer that stays and why, does the pasted output
   carry incidental detail and match the reproducer's own identifiers, does each step have an
   observable result, is the failing output pasted as text where it is text, does every layer in the
-  chain carry a version, and where the project runs reproducers, is the run linked, unless the
-  defect may be a vulnerability? Where the reproducer came from someone else's draft, was it read
-  before it ran, and was the run authorized and isolated or marked as not established?
+  chain whose version could change the outcome carry one, and where the project runs reproducers, is
+  the run linked, unless the defect may be a vulnerability? Where the reproducer came from someone
+  else's draft, was it read before it ran, and was the run authorized and isolated or marked as not
+  established?
 - Observation set, where nothing reproduces on demand: count, window, rate, first-seen build,
   correlations, and the attempts made and their results; for a crash on a user's device, the crash
   report by its ID, the device and OS versions, and the user's steps attributed to the user?
@@ -603,15 +634,17 @@ message item below.
   except an identifier the reader finds the resource by, and where it does not, are the real names
   kept; where a personal datum is the failing input, was a synthetic value tried in its place; does
   the reproducer still run with no placeholder in its way; was it re-run after the substitution; is
-  captured evidence labeled as redacted; and does one sentence say what was changed?
+  captured evidence labeled as redacted; and where anything was changed, does one sentence say
+  what?
 - Disclosure: does the project ask anything of a report written with a tool, and is it answered?
 - Form: do the form's fields, or the fields the person filing named, appear by name in that order,
   does each carry what its label asks for, are your own sections inside or after them and never in
   place of one, does every required field carry an observation or an explicit "not established", is
-  every optional field you had nothing for left blank, and where there is no form, are the sections
-  the ones §8 names, in its order?
-- Request: are the slots of `references/request-genre.md` present, and does it pass the API
-  deletion test?
+  every optional field you had nothing for left blank, and where there is no form, does the report
+  open on the core and carry only the parts of §8 whose condition holds, in its order?
+- Request: does it state the problem and the acceptance criterion, does it carry each other slot of
+  `references/request-genre.md` where that slot's condition holds, and does it pass the API deletion
+  test?
 - Question or support ticket: are the slots of `references/question-and-support-ticket.md` present,
   and is the ask stated?
 - Colleague message: is the ask in the first message, is what you ruled out stated where you ruled
diff --git a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/colleague-message.md b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/colleague-message.md
index c861450b..73c5bd73 100644
--- a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/colleague-message.md
+++ b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/colleague-message.md
@@ -7,13 +7,13 @@ rules of the skill hold, which change shape, and which lapse; a rule not listed
 | Rule | In a message to a colleague |
 | --- | --- |
 | Symptom first (§3) | Holds for the first line. In a shared repository a commit, a branch, or a symbol is shared vocabulary, so "main is red since abc123, run link" is a symptom, not internals |
-| The goal, not only the step (§3) | Holds |
+| The goal, not only the step (§3) | Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none |
 | Causal analysis marked with its confidence (§3) | Holds, and the analysis may come right after the symptom, ahead of the steps: a colleague who shares the code often wants the theory early. The message still says what you saw independently of it |
 | Expected behavior (§5) | Reduced to one line each: the literal or relation you expect and what you got, where the symptom line does not say them already. "Checkout spins" says both. The seven questions are not run on a chat message |
 | Evidence attributed, nothing invented (§6) | Holds. A CI run counts by its link; a step a colleague ran is theirs |
 | Secrets removed, private names substituted (§6) | Secrets out: a token in a pasted log is a token in the chat history. Private names stay; the reader shares them |
-| Failing output pasted as text (§6) | Holds for the error text; a screenshot may accompany it, never replace it |
-| Reproducer (§6) | The command and its output where a command shows the failure, without packaging it as a project or reducing it; for something you saw on a screen, what you did and where |
+| Failing output pasted as text (§6) | Holds for the error text; a screenshot may accompany it, never replace it. Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim |
+| Reproducer (§6) | The command and its output where a command shows the failure, without packaging it as a project or reducing it; for something you saw on a screen, what you did and where. The versions of your tools only where the failure could depend on them; a failure CI shows too does not |
 | Summary first, no speculative consequences (§7) | Hold: the ask in the first message is the summary, and a consequence you did not observe stays out |
 | Ownership and currency (§4) | Reduced to naming the branch or the build where it is not the obvious one |
 | Duplicate search, routing, form lookup, the project's reproducer service | Lapse |
diff --git a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/project-conventions.md b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/project-conventions.md
index 67e2c4f3..1e041968 100644
--- a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/project-conventions.md
+++ b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/project-conventions.md
@@ -79,13 +79,13 @@ service and the request or the input that fails, unless the failure crosses a se
 because the repository path already names the owner. The duplicate search is the backlog itself,
 including what was closed as not now. The private names of §6 stay as they are, because the channel
 does not leave the organization; secrets still come out. What does not change is the
-expected-behavior test and, for a request, the acceptance criterion and the non-goals, the two slots
-a backlog item most often lacks. The opening still states the symptom first, and its subject may be
+expected-behavior test and, for a request, the acceptance criterion, the slot a backlog item most
+often lacks. The opening still states the symptom first, and its subject may be
 internal: a class, a service, or a commit is shared vocabulary here, as in a colleague message, as
 long as the paragraph says what the caller or the user observed. An issue you file to fix yourself
 owes the symptom, the version, and the reproducer or the observation, because the reader of the
-closed issue months later has only them; ownership, duplicates, and disclosure are answered in a
-line each.
+closed issue months later has only them; ownership, duplicates, and disclosure need no line in
+it.
 
 ## A vendor's support form
 
diff --git a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/request-genre.md b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/request-genre.md
index 8a13677b..5465737d 100644
--- a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/request-genre.md
+++ b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/request-genre.md
@@ -7,8 +7,8 @@ for, because it does not exist; every claim about today's behavior still carries
 the document it rests on (question 5 of the skill's expected-behavior test), and a demonstration of
 what the current release does is usually the strongest section of a request. The reproduction on a
 supported version is replaced by confirming that the current release does not already do this, and
-the duplicate search by finding whether someone asked before, which the prior-proposals slot below
-carries. Ownership does not lapse: where the behavior sits between two projects, say which one owns
+the duplicate search by finding whether someone asked before; what it found goes in the
+prior-proposals slot below. Ownership does not lapse: where the behavior sits between two projects, say which one owns
 the contract and why it is the right addressee. Only the method changes, because there is no failing
 run to bisect, so the argument comes from the contract rather than from a command sequence.
 
@@ -34,24 +34,33 @@ the end; a maintainer decides whether to ask for it, and the request has to stan
 
 ## The slots
 
+Every request carries the first two. Each other slot appears only where its condition holds, and a
+two-paragraph request often needs none of them. A slot is what the request says, not a heading: a
+request that fits in a few paragraphs carries no headings, and each fact appears once, so a setting
+that does not serve you is stated beside the problem and not again under alternatives.
+
 - **The problem.** A task you could not complete, in your own vocabulary. Not "the API lacks X".
-- **Who else is blocked, and what it costs.** Both directions: the cost of doing it and the cost of
-  leaving it undone. Name a party other than yourself, or say explicitly that you are the only known
-  case. A maintainer's first question is how far the problem extends.
 - **The acceptance criterion: how anyone will know it worked.** One sentence that could become a
   test or a measurement. Phrasing it as a question the project can answer later beats any ritual
   template.
-- **What is out of scope.** A non-goals sentence keeps the discussion from expanding into the change
-  you did not ask for. Maintainers use it to bound the review.
-- **Whether it has been proposed before, and how yours differs.** A link to the prior discussion, or an
-  explicit statement of what you searched. This is the slot §4 of the skill sends the query to; some
-  processes make it a required field.
-- **Alternatives, including your workaround.** In a slot of their own below the problem statement,
-  subordinate, and stated with why each was ruled out. Ruling something out is information about your
-  requirements; leading with it is a frame that undercuts the request. One kind moves: a setting you
-  tried that does **not** solve the problem is a negative result rather than an alternative, and it
-  belongs with the problem statement, under a heading or in a sentence that says it does not fix it,
-  as §3 of the skill says.
+- **Who else is blocked, and what it costs, where you know or the change is costly.** Where you know
+  of a party other than yourself, or of what leaving it undone costs, name them. Where the change
+  costs the project something a maintainer will weigh, such as a new dependency, a changed default,
+  or an API to support, a maintainer first asks how far the problem extends: name the party, or say
+  that you are the only known case.
+- **What is out of scope, where the request could be read as asking for more.** Where a maintainer
+  could assume a related change comes with yours, one non-goals sentence names it and keeps the
+  review bounded.
+- **Whether it has been proposed before, and how yours differs, where the search found something or
+  the process asks.** A link to the prior discussion and the difference in one sentence. Where the
+  process makes what you searched a required field, the query goes there; otherwise a search that
+  found nothing goes to the hand-over note, as §4 of the skill says.
+- **Alternatives, where you considered one a maintainer would suggest.** In a slot of its own below
+  the problem statement, subordinate, and stated with why it was ruled out. Ruling something out is
+  information about your requirements; leading with it is a frame that undercuts the request. One
+  kind moves: a setting you tried that does **not** solve the problem is a negative result rather
+  than an alternative, and it belongs with the problem statement, in a sentence that says it does
+  not fix it, as §3 of the skill says.
 - **A sketch, optional and labeled.** A mock-up, a snippet, or before-and-after code helps a
   maintainer see the shape you mean. It sits below the problem statement and is marked as one possible
   shape, not as the requirement. Separate the requirement from the rendering explicitly: say which
@@ -63,15 +72,15 @@ The grounding order in the skill applies here too, and it costs more here. A req
 in "another product does it this way" or in personal preference is the shape maintainers close.
 Ground it in a task the project's own documentation says it supports, in an error the project itself
 raises, or in users who hit the same wall. A genuinely new need has no documented promise behind it,
-and that does not disqualify it: the grounding is then the task, who has it, and what it costs them
-today, stated as such. Evidence of a defect and justification for an improvement are different
+and that does not disqualify it: the grounding is then the task and what it costs today, stated as
+such, with who else has it where you know. Evidence of a defect and justification for an improvement are different
 things; a request does not borrow the language of a defect report to look stronger.
 
 ## A request in a team's own backlog
 
 The forms and guides the skill reads in step 2 rarely exist there; what stands in for them is in
-`project-conventions.md`. The slots above still apply, and the acceptance criterion and the
-non-goals are the two a backlog item most often lacks.
+`project-conventions.md`. The slots above still apply, and the acceptance criterion is the one a
+backlog item most often lacks.
 
 ## What the request does not owe, and the backport ask
 
diff --git a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/worked-cases.md b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/worked-cases.md
index 05128214..7a571756 100644
--- a/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/worked-cases.md
+++ b/agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/references/worked-cases.md
@@ -2,9 +2,11 @@
 
 Open this when an expected block failed the test in the skill and you need the repair, or when you
 want to see the rules applied end to end. Each case pairs a draft that failed a rule with the report
-that was accepted. All six cases come from one investigation into test reporting in a build tool and
+that serves. Cases 1 to 6 come from one investigation into test reporting in a build tool and
 a test framework, so they show the rules on a library defect with a reproducer; the rules they
-illustrate are the skill's, not the ecosystem's. Both accepted reports are public and worth opening:
+illustrate are the skill's, not the ecosystem's. Case 7 is constructed rather than taken from a
+project, and shows the short end: a report that is only its core. Both accepted reports of cases 1
+to 6 are public and worth opening:
 [gradle/gradle#39079](https://github.com/gradle/gradle/issues/39079) and
 [junit-team/junit-framework#6041](https://github.com/junit-team/junit-framework/issues/6041).
 
@@ -89,6 +91,25 @@ The draft that failed the same test traced the defect into a Gradle class inside
 states the current behavior. Deleting its marked reasoning left the report standing, so it passed the
 first question; the trace inside the symptom failed the second.
 
+## Case 7: a misspelled name with nothing past the core
+
+The draft for a misspelled environment variable on a configuration page carried five headings: the
+observation, the expected name, the operating system and the version of the service it was run
+against, the commit that introduced the misspelling, and the search that found nothing. Every part
+was true, and every part past the core failed its condition in §8 of the skill: the name the code reads is the
+expectation and its grounding, the service ignores the misspelled name on every version, and nobody
+needs the history to fix one word. The report that serves is the core and a title:
+
+```markdown
+Configuration page names `LOG_LEVL`; the service reads `LOG_LEVEL`
+
+The "Logging" section of `docs/configuration.md` (at `9c41e07`) tells you to set `LOG_LEVL=debug`.
+The service ignores that variable and keeps logging at `info`; `LOG_LEVEL=debug` switches it to
+`debug`, and `LOG_LEVEL` is the name `config/env.go` reads.
+```
+
+The search queries, the history, and the offer of a pull request go in the hand-over note.
+
 ## Published before-and-after pairs worth copying
 
 These come from projects' own guidance rather than from the two reports above.
~~~~~
