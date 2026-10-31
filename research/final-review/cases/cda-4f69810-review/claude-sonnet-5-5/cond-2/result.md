# Final review: `d79c43d..HEAD` (commit 4f69810)

**Inputs.** There is no separate task statement. The claimed cases come from the commit message only, so item 2 is answered from that alone. The change is a skill package (`SKILL.md`, README, versions, marketplace entry) with no code. I used the §2a analogues and did not run `comment-drift.py`, because there are no members for it to parse. I loaded `apm-authoring` from the given skills directory. I did not load `english-developer-style`, so wording enters only where a sentence reads wrongly. `make check` needs `uvx` and the network, so I did not run it. I checked the version alignment by hand instead.

## Item 1: comments consistent with the code and with each other

*Analogue: every statement the changed files make about each other or about their own sections.*

1. **Substantive.** `SKILL.md:342-359` (the What-slot example) contradicts itself and the commit message.
   - The *After* sentence 1 reads "a caller that runs before startup completes fails at once". That is an outcome stated in prose.
   - The paragraph right after the example says that outcome belongs on its own `User-visible changes` line (`:359`). The slot table at `:197` and the outcome-line rules at `:313-317` say the same.
   - The commit message says the What-slot example "no longer puts an outcome in prose". It does, and the commit says that example was not re-run.
   - A drafting agent copies the *After* and writes the outcome in prose and again as a line.
   - Request: drop the outcome clause from the *After*. For instance, "The pool opens at startup, so `ensureOpen()` has nothing left to open", with the failure carried by the User-visible line.
2. **Substantive.** The changelog row (`:475`) tells the reader to see "(§2, slot 2)" for "the condition alone". Slot 2 (`:91-94`) says "name what found it and end the sentence there". It never mentions a changelog entry or "the condition alone". A changelog writer following the reference finds a different rule.
   - Request: state the changelog form in slot 2, or in the row itself.
3. **Taste.** `:357-359` is a caveat after an example. It says what the example omits and where the omitted outcome goes. `apm-authoring` rule 2 says such an example teaches what the caveat forbids. I prefer that the *After* be the shape you want, and the caveat be cut once finding 1 is fixed. Expect this to be declined.
4. No other contradictions found.
   - The README summary matches the new rules.
   - The `:81` skip condition matches slot 2.
   - Checklist items "Symptom", "Translation", "Alternatives" and "Discussion" each point at a rule that exists.
   - `§7`'s "(§2, the What slot)" resolves.
   - "§5" for public identifiers resolves, to the identifiers section.

## Item 2: claimed cases covered

*Analogue: each rule claimed in the commit message, against the section that carries it and a way to detect it.*

| Claimed | Section | Checklist item |
| --- | --- | --- |
| Slot 2, audit-found defect | `:81`, `:91-96` | Symptom |
| Derived consequence marked | `:98-101` | Symptom |
| What-slot translation, with a bad and a good example | `:342-359` | Translation |
| Rejected-alternative mechanism | `:369-372` | Alternatives |
| Open questions | `:458-464` | Discussion |
| Changelog condition alone | `:475` | Reached only through "Symptom". It says nothing about the changelog. |

- **Version bump.** It is claimed by the version-bump hunks in `marketplace.json`, `apm.yml` and the package `apm.yml`, and all three agree on 1.4.0.
- **Unclaimed hunks.** None.
- **Unclaimed checks.** The commit message's "a changelog entry for it names the condition alone" has no checklist question. The changelog check at `:842` is unchanged. Rule 4 of `apm-authoring` wants every rule reachable. This is the same defect as finding 2, so I did not file it separately.
- **Commands.** The change tells no one to run a command.

## Item 3: boundaries, partitions, and the negative control

*Analogue: the claimed genres and inputs, and the negative control. The table of added instructions is below.*

- **Partitions.** The commit claims four defects: invented symptom, hunk translation, retold obstacle, open question.
  - The evidence it states is a blind-draft count (fifteen Opus drafts) from one pull request.
  - It admits the current open-question rule and the What-slot example were not re-run, and that translation "persists in about one draft in two".
  - The commit states this plainly, so it is not a finding. It means the translation rule has little evidence and the example in finding 1 has none.
- **Install state.** The package is installed over an earlier version, but it is a skill with no persisted state. Nothing to report.

**Added instructions: 7**

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:91` "Where reading the code or an audit found the defect, name what found it and end the sentence there" | An audit-found defect later reproduced, with a quotable exception | "An audit found this", with the diagnostic R3 greps for dropped | "only where no symptom was observed or reproduced" |
| `:826` Translation: "delete each sentence of the What slot in turn" | A one-line fix whose whole What slot is recoverable from the hunk | An empty What slot, while `:189-200` lists no skip condition for it | "only where another slot still states the behavioral change" |
| `:458-461` keep a maintainer-only question in Scope | A description that becomes the permanent commit body (`:823`, §4) | An open question frozen into history after it is settled | "only while the pull request is open" |

Not findings: `:98` (the derived-consequence rule ends where nothing is derived), `:342-347` (hunk translation, other inputs), `:371` (the obstacle check ends where the alternative has no retold mechanism), `:835` (the Discussion checklist item restates `:458`).

I took the three rows' inputs from the artifact's own text: the audit case in `:91`, the PR-as-commit-body case in `:823`, and the What-slot rules. I counted rows 1 and 3 as substantive and row 2 as taste. The request in each case is the ending clause shown.

## Item 3a: level, placement, and the environment

*Analogue: placement and registration.*

- The rules sit in the one existing skill file, in the sections the sibling rules use. No new files.
- The registration entries (`apm.yml`, `marketplace.json`, the package `apm.yml`) are the ones the gate compares, and all three show 1.4.0.
- I could not run the gate offline. The `1.3.0` lines that remain in `marketplace.json` and `apm.yml` belong to other packages. I confirmed that by the `qubership-user-essentials` hit.
- The trigger surface (`description:` frontmatter) is unchanged, and the new rules do not widen scope beyond what it already covers.

Findings: none.

## Item 4: names by content, not by position

*Analogue: the change's headings, cross-references, case names.*

- The new text uses content names ("What slot", "Scope slot", "Translation", "Discussion"), not ordinals.
- "slot 2" and "§2" are the document's own stable numbering.
- "the first sentence" in the Translation item is not a cross-reference.

Findings: none.

## Item 5: the failure report

*Analogue: what each rule tells the reader to look at, and whether it reaches its detection.*

- The Translation and Discussion checklist items name an action ("delete each sentence in turn", "does the description give the answer") that detects the rule.
- The Symptom item detects the three-way split of slot 2.
- One gap: the "condition alone" rule for the changelog has no detection (see finding 2).

Findings: none beyond finding 2.

## Item 6: what the writer says it verified

*Analogue: an exemplar that passes, a bad case that fails.*

- The commit message states the measured effect per rule, including the one that did not hold ("persists in about one draft in two") and the two things not re-run.
- The new *Before/After* pair, applied to the rewritten rule, does not pass. The *After* still puts an outcome in prose, which the same section's rules forbid (finding 1). This is the "rewrite that now fails the change's own worked example" case. It follows from item 1.

Findings: none beyond finding 1.

## Item 7: siblings of the change

*Analogue: the places that list or route to the artifact.*

- **Set membership.** The change adds no package or slot.
- **Routing surfaces.** The README, `marketplace.json`, root `apm.yml` and package `apm.yml` carry the version.
  - The README "What it covers" bullets mention each new rule.
  - The research tree `research/change-description-authoring/` has no case for this change. The commit says so.
- **Counts.** I searched the prose for a restated slot count ("five slots", "six slots"). It still says five and six, and the change adds none. The slot-2 skip text in the table at `:81` and the prose at `:91-96` now say the same thing.
- **Same symptom elsewhere.** The commit-body section (`:74-170`) carries the symptom rule once, in slot 2. The pull-request "Why" slot at `:195` ("The problem, the symptom, the condition that reaches it") has no audit-found exception. A pull-request description written for an audit-found defect, with no mention of what found it, is still asked for "the symptom". The skip condition at `:81` covers only the commit body. The checklist item "Symptom" covers both, so the gap is in the Why row. Request: one clause in the Why row, or a pointer to slot 2.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| What-slot *After* states an outcome in prose, contradicting the next paragraph and the commit message | Substantive | `SKILL.md:342-359` | 1 |
| Changelog row points to §2 slot 2 for "condition alone", which slot 2 does not say | Substantive | `SKILL.md:475`, `:91` | 1 |
| Caveat paragraph after the example | Taste | `SKILL.md:357-359` | 1 |
| Audit rule drops a reproduced diagnostic | Substantive | `SKILL.md:91` | 3 |
| Translation check empties the What slot on a one-line fix | Taste | `SKILL.md:826` | 3 |
| Maintainer-question rule leaves a stale question in a commit body | Substantive | `SKILL.md:458-461` | 3 |
| PR Why row has no audit-found exception | Substantive | `SKILL.md:195` | 7 |

Checks not done: the `comment-drift.py` run (no code in the change), `make check` (needs network), and the `english-developer-style` pass.
