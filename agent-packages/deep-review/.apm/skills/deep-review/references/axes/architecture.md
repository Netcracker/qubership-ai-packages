# Axis: architecture

Finding prefix: `ARCH`. This is a **synthesis** axis: it runs last, and its prompt is distilled from the evidence
axes' reports. The distilled prompt adds the repository's specifics; this file is the invariant part.

You are judging the **design**, not the code. The question is not "does this work today" — assume it does — but "is
this the right shape, and what will it cost to live with for the next two years".

The evidence reports handed to you are a list of **symptoms**. Your job is to find the decisions that generated them,
plus the ones that have not produced a symptom yet.

## The filter

A finding qualifies only if fixing it changes at least one of:

- a **public contract** — API shape, resource model, schema, wire format, configuration surface;
- a **boundary** between this component and another — who calls whom, with what guarantees;
- the **identity or data model** — what uniquely names a thing, what state lives where;
- the **authority model** — which component is the source of truth, who arbitrates conflicts;
- the **control-flow model** — synchronous versus asynchronous, push versus poll, level-triggered versus
  edge-triggered, who owns retries;
- the **failure domain** — what shares fate with what;
- the **lifecycle model** — install, upgrade, migration, coexistence with what this replaces.

Two tests before you write anything up:

1. **The patch test.** Could a competent engineer fix this in one commit without touching a contract, a schema, or a
   boundary? If yes, it is not an architecture finding.
2. **The recurrence test.** If this exact defect were fixed tomorrow, would the same design keep producing defects of
   the same family? If yes, describe the design, not the defect.

Restating an evidence finding at higher volume is rejected. Citing one as proof that a design pressure is already
leaking into practice is exactly right.

## Method

Do steps 1 and 2 **before** forming opinions about the code, so the implementation does not anchor you.

1. **Enumerate the forces.** Independently of this repository, list what a component of this kind has to survive:
   scale, concurrency, restart, partial failure, an external system that is itself a source of truth, version skew,
   migration from a predecessor, extension by third parties, disaster recovery. Write the list down first.
2. **Reconstruct the implicit ADRs.** The team wrote no decision records. Recover them: for each load-bearing
   decision, name it, cite where it is encoded, and state what it buys and what it costs. Roughly 12–20. This
   inventory is a deliverable in its own right.
3. **Map authority.** For every piece of state, say who owns it, who caches it, how divergence is detected, and how
   it is repaired. Divergences that nothing detects are the highest-value findings in this review.
4. **Pressure-test with change.** For each force from step 1, and for each scenario in the distilled prompt, trace
   what the design makes you do. Cheap absorption means the design is right; a change that touches four layers means
   it is not.
5. **Check the genre.** This component belongs to a well-explored family. Compare its answers against how that family
   normally solves these problems, and where it deviates, say whether the deviation is justified by the domain or is
   an accident. Use prior art as a source of solved problems — do not propose adopting any of it wholesale.
6. **Check the grain.** The genre check compares the component with its family. This step compares each technology
   inside it with what that technology was made for, one row of the profile's technology inventory at a time. A
   component can be a normal member of its family and still be built on a tool that makes every change expensive. Run the
   signals below on every row; collect the evidence findings whose `Tool limit:` line names the row's technology;
   then decide. The rule for a finding is under "Fitness findings".
7. **Rank by reversibility.** Separate one-way doors — published API, persisted formats, identity semantics,
   packaging, anything a consumer already depends on — from decisions that can be revisited later.

## Fitness findings

Prefix `FIT`, one per inventory row at most. The claim has a fixed shape: **a technology carries a role for which its
distinctive properties are unused or in the way, and the project builds workarounds to keep it in that role.**
"Unusual" is not a defect. SQLite as a file format, a relational table as a queue at low volume, a Kubernetes
ConfigMap as a read-mostly store can each be the right choice. The finding is a mismatch that has a measured cost and
no force in the domain to justify it.

Signals, each of which is a fact to collect rather than an opinion to hold:

| Signal | How to measure it |
| --- | --- |
| Inverted layers | The artifact on technology X stays constant while the domain changes, and the program lives in X's data or configuration layer. Compare `git log` on the X files against `git log` on the domain inputs they process |
| An interpreter inside the interpreter | Code on X reads a data structure that describes a program: an AST, a rule list, a step list, a state table |
| Emulation of a stated non-goal | Manual unrolling where X has no recursion, sentinels where X has no null or no exception, polling where X has no events, files renamed in sequence where X has no queue. Count the lines and cite the non-goal in X's documentation |
| Defects that follow from X's limits | The evidence findings whose `Tool limit:` names X. Two or more, from any axes, is the strongest evidence this step gets; on the run that motivated this step all five came from one axis |
| Escape hatches | The share of the work on X that goes through X's own exits: external calls, custom built-ins, `unsafe`, shelling out |
| Unused core | The features X is chosen for, per its documentation, that this system does not use: bundles, partial evaluation, streaming, transactions, user-authored artifacts |
| Tooling gap | No debugger, no unit-level test, no profiler for the artifacts on X, so the artifact is tested only end to end. Quote the team where they said it |
| Persona | X is designed for one kind of author and written here by another |

The "what would an engineer choose from scratch" question is not a signal: every reviewer answers it differently. It
belongs in the finding's **Alternative** line, after the signals have made the case.

A `FIT` finding is reported when all of these hold: the upstream documentation of X states a purpose or a non-goal
that the role contradicts, quoted with its URL; the role is cited at `path:line`; and at least two signals from the
table are measured, or one signal plus two or more evidence findings, from any axes, that name X in `Tool limit:`.
With fewer than that, write one line under *Checked and sound*: `X in role R: <the signal checked> found nothing`.
Where a force in the domain justifies the role and is written nowhere, report the finding at its severity, say under
**Force in the domain** that the force is undocumented and what to write down, and leave the `ACCEPTED-DEBT` label to
the consolidator, which applies it once the verifier has upheld the finding on that ground.

A constraint from the owner ("X is not forked", "X stays") fixes how X is used, not whether X fits the role. Treat it
as a bound on the **Alternative** line, never as a reason to skip the row. The focus file carries the constraint as
a directed question to this axis for that reason.

Block for a `FIT` finding:

```markdown
### FIT-01 <technology> carries <role> that its <property> does not serve — HIGH

- **Designed for:** the quoted purpose or non-goal, with the URL
- **Role here:** `path:line`, and the size of the artifact on it and around it
- **Signals measured:** each signal from the table with its number or its quote
- **Findings it generated:** evidence findings by id whose `Tool limit:` names this technology
- **Force in the domain:** the reason the role could be right, and where it is written, or `none found`, with what
  you searched
- **Alternative:** what would carry the role instead, within the owner's constraints, and what that trades away
- **Cost to change:** now versus after the next release
- **Проверка:** `executed` / `traced` / `inferred`, plus the artifact
```

In the structured payload a `FIT` finding fills the common fields from the block — `file` from **Role here**,
`expected` from **Designed for**, `actual` from **Signals measured**, `trigger` with the change or load under which the
mismatch costs, `consequence` and `fix` as usual — and puts the rest under `fit` (`designedFor`, `signalsMeasured`,
`findingsGenerated`, `forceInDomain`, `alternative`, `costToChange`).

## Report additions

On top of the standard format, this axis produces:

**Verdict** — at most fifteen lines. Is the architecture fit to carry this system for two years? Name the three
decisions that most need revisiting, and the single one-way door that will be most expensive to walk back.

**Decision inventory:**

| # | Decision | Encoded in | Buys | Costs | Reversible? |
| --- | --- | --- | --- | --- | --- |

Every row of the profile's technology inventory has a decision row here, stated as the choice of that technology for
that role, whether or not it produced a finding. A row the team never wrote down is still a decision, and the
premise of the whole project is the one most likely to be missing.

**Findings**, using this block instead of the standard one (a `FIT` finding uses its own block, above):

```markdown
### ARCH-01 <the decision, stated as a decision> — CRITICAL

- **Decision:** what was chosen, in one sentence
- **Encoded in:** `path:line`, and the other places that assume it
- **Force it fails under:** the requirement, scale, or change that breaks it
- **Consequence:** what the consumer, the operator, or the next maintainer experiences
- **Alternative:** what to do instead, where the genre or the upstream documentation establishes it, and what that
  trades away
- **Cost to change:** now versus after the next release
- **Symptoms already visible:** evidence findings that this decision generated, by id
- **Проверка:** `executed` / `traced` / `inferred`, plus the artifact — and what would settle the rest
```

In the structured payload: `file` from **Encoded in**, `actual` from **Decision**, `trigger` from **Force it fails
under**, `expected` from **Alternative** with its source, `consequence` and `fix` (the cost to change) as usual.

Severity uses the common ladder from `common-rules.md`, on this axis read as: `CRITICAL` for a one-way door that is
wrong or a design that loses data under normal operation; `HIGH` for a design that forces a painful change within a
year or makes a required capability unreachable; `MEDIUM` and `LOW` for friction that compounds. A defensible
trade-off that is merely undocumented is reported at its severity with the missing document named under **Force in
the domain** or **Alternative**; the consolidator relabels it `ACCEPTED-DEBT` after verification.

**Pressure-test table** — one row per scenario: what the architecture makes you do, whether it absorbs the change, and
the cost.
