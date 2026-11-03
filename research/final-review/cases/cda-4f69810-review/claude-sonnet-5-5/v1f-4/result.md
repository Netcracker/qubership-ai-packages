# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.** The change has one commit and touches 5 files: `SKILL.md`, `README.md` and `apm.yml` of `change-description-authoring`, the root `apm.yml`, and `.claude-plugin/marketplace.json`. No task statement was handed over, so item 2 takes its claimed cases from the commit message alone. The change has no code, so §2a applies throughout. I did not run `comment-drift.py` because there are no members to parse. I loaded `final-review` and did not load `english-developer-style`, `test-authoring`, or `apm-authoring`. The `apm-authoring` sections are cited from the skill's text only. I ran `scripts/check-skill-descriptions.py`, which passes, and I did not run any other repository gate.

## Item 1: comments consistent with the code and with each other

The analogue is each statement the changed files make about each other: section references, counts, repeated descriptions, and the version in four places.

- **Section references.** The commit message says "§7 points to this rule". The §7 bullet now reads "(§2, the What slot)", which exists. The "(§5)" in the identifier sentence (`SKILL.md:347`) points at "Trailers and the identifiers a reader greps", which matches. The "(§2, slot 2)" in the changelog row (`SKILL.md:475`) exists.
- **Versions.** All four places say 1.4.0: package `apm.yml`, root `apm.yml`, marketplace entry, and the skill. The package description is identical in all three manifests.
- **Slot 2 text against its other statements.** Finding 1 below.
- **Slot 2 table against the checklist.** The Symptom checklist item (`:803-806`) and the slot 2 skip column and body text agree.
- **Slot 2 against the changelog row.** These differ by design: the row says "the condition alone", the commit slot says "name what found it". The changelog row is consistent with the commit message.
- **Narration of the change.** No `now` / `no longer` / `used to` narrates the change. The `now` in the Before/After example is example text.

Finding 1: the new rule overlaps the old one without a tie-break. Line 94 keeps "Where the defect has no symptom by construction (a leak on an error path with nothing logged), say so". The new rule says a defect found by an audit or a code reading is described by what found it, "and end the sentence there". A leak on an error path is typically found by exactly an audit or a code reading. The agent then has two rules that give opposite instructions. One says state the absence. The other forbids stating it, since the Before example bans "it has not been seen to fail". The commit message says "say so" is kept "for a defect with no symptom by construction". The text never says which rule wins when both conditions hold. That is substantive, because it leaves the same ambiguity that the commit message says drafts exploited.

## Item 2: claimed cases covered

The claimed cases are the commit message's. Each is listed with the section that handles it and the detection a reader has.

| Claim | Where handled | Detection |
| --- | --- | --- |
| Slot 2, audit/code-found defect: name what found it, end the sentence | `:91-96`, table row `:81`, changelog row `:475` | Checklist Symptom (`:803-806`) |
| Slot 2 has a bad and a good example | `:93` Before/After | Present |
| Derived consequence only when traced to what a caller sees, and marked derived | `:98-101` | Checklist Symptom ("traced in the code and marked as derived") |
| "Say so" kept for a defect with no symptom by construction | `:94-96` | Checklist Symptom, last clause |
| What slot: a sentence recoverable from one hunk is translation | `:342-346` | New Translation item (`:826`) |
| What slot has a bad and a good example | `:350-358` | Present |
| A public identifier is named once | `:346-347` | Not in the checklist. The Translation item says "delete each sentence ... where the diff still says it, leave it deleted" and has no exception for identifiers. See finding 2. |
| §7 points to this rule | `:762-764` | Present |
| §2 asks for "what changed that the diff does not show" | `:288` | Present |
| Rejected alternative stated as a fact about the merged code; an obstacle the change removes is a step it took | `:371-374` | Alternatives checklist item |
| Open question: answered, kept in Scope, or dropped | `:458-465`, Scope table row `:262`, README | Discussion checklist item |
| Checklist: Symptom and Alternatives extended; Discussion and Translation added | `:803-806`, `:826-838` | n/a |

The "Discussion" and "Translation" checklist items sit in the file. Commit body slot 5 is not touched. The commit-body Scope text (`#### Scope`, `:442`) is not extended for the maintainer-only question, which matters for finding 3 below.

Commands: the change tells no one to run a command.

Hunks to claims: every hunk belongs to a sentence of the commit message.

- The README's added bullets cover the three rules.
- The version bumps are not named in a sentence. A skill content change that bumps a minor version is conventional here, so this is not a finding.
- The package `apm.yml`, root `apm.yml`, and marketplace entry are consistent.

## Item 3: boundaries, partitions, and the negative control

The partitions are the defect kinds and the situations the new rules cover. The negative control is the input where the rule does not apply.

Instructions added, per the §2a table:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (`:91-93`) | A defect found by reading the code that also has a reported symptom, such as a maintainer-reported crash whose cause was found by reading | The agent may drop the reported symptom and write only "Reading the code found this", which loses the quoted diagnostic R3 greps for | None in the text. The slot's skip column says "for a defect an audit or a code reading found, the body names what found it", and `:91` says "end the sentence there". Nothing says a symptom that was observed is still quoted. The Symptom checklist item asks "is every symptom quoted from an observation", which allows the quoted symptom, but the rule that fires first says to stop. See finding 4. |
| "A consequence derived from the code earns a sentence only after it is traced to the point where a caller sees it ... stated as derived" (`:98-101`) | A defect whose consequence is obvious and one step away, such as a null dereference on the first line | The agent writes a derivation sentence for a trivial consequence | Partly ended by "earns a sentence only after it is traced", but a trivially traced one is still required to be marked as derived. Taste. |
| "A sentence whose content the reviewer recovers from one hunk ... is translation" (`:342-346`) | A one-line fix where the hunk is the whole change | The agent deletes all What sentences, leaving the Why slot only | The What slot's table row skips nothing. The commit-body slot 3 has "Skip when: problem statement makes the approach obvious", but the PR description's What slot has no skip. The Translation checklist item says "leave it deleted", so a description may end up with an empty What slot. Substantive, but small. See finding 2. |
| "A public identifier ... is the exception: name it once" (`:346-347`) | A change that renames a private-in-practice identifier the issue never mentioned | The agent lists it anyway under the exception | Bounded by "public identifier ... (a system property, a flag, an option)". Fine. |
| "An obstacle the change itself removes is a step the change had to take, not a reason against the alternative" (`:371-372`) | A rejected alternative whose obstacle is partly removed and partly remains | The agent drops the alternative or keeps the retold obstacle | Ended by "check the mechanism against the code after the change". Fine. |
| "Where only a maintainer can answer it ... keep it in the Scope slot as a question" (`:460-463`) | A commit body, where the Scope slot does not exist, and a trivial question (a style preference in the review thread) | In a commit body the agent has no slot to put it in. For a trivial question the agent keeps it open in Scope. | "Leave a question out only when it does not bear on this change" covers the trivial one. The commit-body case is not addressed. See finding 3. |

Staleness of state: the change replaces nothing an earlier install left behind, other than the version the manifests already update. No limits, no replaced mechanism.

Evidence for the rules in the commit message: the drafts ran against 1.0.1, before the outcome slot and the length rules, and the final open-question rule and the What-slot example were not re-run. The commit message says both. No cases under `research/change-description-authoring/` were re-run, which the message also states. The negative control, an input where the new rules are noise, is not stated. See finding 5.

## Item 3a: level, placement, and the environment

The analogue is whether each rule sits in the right place.

- The slot 2 and What slot rules sit in `SKILL.md` §2, beside the neighbours they extend. The README bullets sit in the existing list.
- The open-question rule sits under "#### Scope" of the PR description. Its sibling table row is updated. The commit body has no Scope slot, so the rule does not reach there.
- The registration entries are the three manifests plus the marketplace file, and all agree.
- Gate: `check-skill-descriptions.py` passes. I did not run the markdown linters.

## Item 4: names by content, not by position

none. The new text refers to slots by name ("the What slot", "slot 2"). "Slot 2" is an ordinal, but it is the skill's established table numbering, which the existing text uses throughout (`:123` "slot 2's", `:216` "Slot 3"). The new references follow that convention. The commit message's "§2, slot 2" is the same.

## Item 5: the failure report

For a skill, the rule is that each rule has a detection that detects the rule, not a weaker property.

- **Symptom.** The extended item detects the audit, derived, and no-symptom rules. It is reached by the checklist.
- **Translation.** "Delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" detects translation. It conflicts with the identifier exception (`:346-347`): a sentence that names a public identifier is recoverable from the diff, yet the rule says to name it. The checklist item has no exception clause, so it detects a weaker or different property. Finding 2.
- **Discussion.** It detects the three outcomes (answered, kept in Scope, dropped).
- **Alternatives.** The second question detects "a mechanism that is a fact about the merged code".

## Item 6: what the writer says it verified

The commit message states the evidence. Drafts were run, with counts: both of two drafts predicted a failure without a rule; five of ten stated no failure under a ban on the word; none of two did with the final wording; the retold obstacle went from two of four to none of four; the open question from three of three to none of four; translation dropped but persists in about one draft in two. It states what was not re-run. The numbers are small, but the writer states them as small. Not a finding, apart from the unrun cases already listed.

The "Discussion and Translation" checklist items, and the identifier exception, have no stated bad case. The Translation rule's own residual rate (about one draft in two) is stated, with no mention of an input where it makes the output worse.

## Item 7: siblings of the change

The siblings are the places that enumerate or route to the skill, and the other places that state the changed rules.

- **Manifests.** The index and marketplace entries are updated. The description text is unchanged, so the other manifests' descriptions do not need it.
- **`english-developer-style` and `docs-page-authoring`.** They name the skill only as a pointer (`english-developer-style/SKILL.md:28`, `:509`, `:571`; `docs-page-authoring/SKILL.md:13`, `:21`, `:248`). None restates the symptom rule. No sibling is stale.
- **Counts of the old size.** The slot counts did not change ("Five slots", "Six slots"), and the Discussion and Translation checklist items add no counted list. No sentence counts the checklist.
- **The commit-body twin.** Finding 3: the commit-body Scope text and the PR-description Scope text are siblings. The PR table row and `:458` are updated, and the commit body is not. The rule the commit message names, "keeps the question in the Scope slot", has no Scope slot in a commit body, which has five slots (Subject, Problem, Impact and trigger, Change and approach, Outcome, References). Commit body slot 3 ("Change and approach") carries the alternative, with no place for a maintainer-only question.
- **Same-symptom paths.** The changelog row is updated. The summary form under "Pull request description" (`:236`, `## Summary` / `## Testing`) and the third template (`:246-262`) show the Why/What/Scope headings. I did not check whether the example templates there show the new rules.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The audit/code-found rule and the "no symptom by construction, say so" rule both fire on a leak found by an audit. One bans stating the absence of a symptom, the other requires stating it. | Substantive | `SKILL.md:91-96` | Add a tie-break sentence, for example "…; if an audit found a defect with no symptom by construction, name what found it and stop", or say that the first rule wins. |
| 2 | The Translation checklist item has no exception for the public-identifier rule (`:346-347`), so a description that follows the rule fails the item. The same item can empty the What slot of a one-line fix, and the PR What slot has no skip condition. | Substantive | `SKILL.md:826-827` against `:346-347` | Add "except a public identifier named once (§2)" to the item, and a clause such as "…; where nothing is left, the What slot is skipped" to the rule or its table row. |
| 3 | The open-question rule is written for the PR description only. A commit body has no Scope slot, and the commit-body text gives a maintainer-only question nowhere to live. | Substantive | `SKILL.md:458-465`, commit body table `:78-84` | Say where the question goes in a commit body (for example "in the body, as the last paragraph before the trailers") or say that the rule applies to pull request descriptions only. |
| 4 | "Name what found it and end the sentence there" can drop a symptom that was observed and reported, such as a bug a maintainer hit and then traced by reading the code. | Substantive | `SKILL.md:91-93`, table row `:81` | Add "only where no symptom has been reported" to the condition, or point to the quoted-diagnostic requirement. |
| 5 | The commit message states no input where the new rules are noise, and the drafts ran against 1.0.1 with the open-question rule and What example not re-run. | Taste | commit message | If the writer re-runs, one run on a one-line fix with a reported symptom checks findings 2 and 4. |
| 6 | The open-question paragraph has a stray short line ("wanted. Leave"), which breaks the file's wrapping at about 100 columns. | Taste | `SKILL.md:462-463` | Reflow so that "Leave a question out only when …" joins the previous line. |

I did not run the suites or the markdown/spelling linters, did not re-run any blind draft, and did not do a style pass over the prose.
