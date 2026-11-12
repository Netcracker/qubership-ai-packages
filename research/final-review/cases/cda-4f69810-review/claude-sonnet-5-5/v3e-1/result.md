I've read the diff and checked the cross-references. The drift script is not applicable, because the change has no code. Here is the report.

# Final review of `d79c43d..HEAD` (one commit, `4f69810`)

**Inputs.** There is no task statement, so the claimed cases come from the commit message alone. That limits item 2. The change has no code: it edits a skill, its README, and version metadata. Every item below therefore uses the §2a analogue. I read `english-developer-style` as the style skill. I did not load `apm-authoring`, because the instructions allowed only the three named skills, so the skill-package rules are not applied. I did not run `comment-drift.py`, because there are no members to parse. There is no previous report.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Checked: the counts, the `§` references, the version strings, and the descriptions repeated across the manifests.
- `§7 points to this rule` holds. The §7 bullet at SKILL.md:763 now says "the same test applies sentence by sentence (§2, the What slot)".
- Version `1.4.0` is aligned across `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `marketplace.json`.
- The slot 2 skip condition, the changelog part 3, and the checklist "Symptom" item agree with each other.
- Finding 1 is a contradiction between the new principle and the retained example (SKILL.md:93-96).
- Finding 2 is a worked example that fails the rule it demonstrates (SKILL.md:~350-358).

## Item 2: claimed cases covered (analogue: sections that handle each claim)

The commit message claims these cases. Each has a section.

| Claim | Where it is handled |
| --- | --- |
| Slot 2: audit or code-reading defect, bad and good example | SKILL.md:90-96 |
| Slot 2: derived consequence traced and marked | SKILL.md:98-101 |
| What slot: hunk translation, bad and good example | SKILL.md:~342-360 |
| Rejected alternatives: mechanism as a fact about merged code | SKILL.md:~369-373 |
| Open questions | SKILL.md:~458-465 |
| Checklist: Symptom and Alternatives check the above; new Discussion and Translation items | SKILL.md:~803-838 |
| Changelog part 3 | SKILL.md:475 |

- Commands: none are added.
- Every hunk belongs to a claim. The README bullets, the version bumps, and the Scope-slot row carrying the maintainer question all map to a sentence of the message. The Scope-slot row is covered by "Open questions … stays in the Scope slot".
- Detection of the new rules comes only from the checklist items. The commit reports a measured result for the final wording (none of two drafts stated an absence). It admits that the current open-question rule and the What-slot example were not re-run.

No findings.

## Item 3: boundaries, partitions, and the negative control (analogue)

The partitions are:
- defect found by audit or code reading;
- defect with no symptom by construction;
- defect with an observed symptom;
- derived consequence;
- hunk translation versus a decision-carrying sentence;
- open question settled by the code versus one only a maintainer can settle;
- open question that does not bear on the change.

The commit's drafts cover the first and the last few of these. It says it did not re-run the final open-question rule or the What-slot example. This is not a new finding, because the commit states it. The pre-existing-state partition does not apply to a skill update.

**Table of added instructions**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found an audit-found defect, and end the sentence | A defect an audit found that also has an observed symptom from a user report | Only "An audit … found this", dropping the reported log line R3 greps for | None. Slot 2 and the changelog part 3 both say "for a defect an audit or a code reading found, the condition alone". Add "unless a report also observed it" (substantive, finding 3). |
| Trace a derived consequence to the caller and mark it as derived | A defect whose consequence is already observed in the issue | A "derived" marker on an observed symptom | Ended by the checklist wording "quoted from an observation, or traced … and marked". Not a finding. |
| A sentence recoverable from one hunk is translation; state the reason, not the edit | A one-hunk change (a typo, a version bump) | A What slot with every sentence deleted, so no What slot | "the Why slot has no skip condition" and the Translation checklist item "delete each sentence". The text does not say what remains when all are deleted. Taste. |
| Name a public identifier once | A change that adds no public identifier | Nothing | "A public identifier the change adds, removes, or renames". Condition is self-ending. Not a finding. |
| A retold obstacle that the change removes is a step, not a reason against the alternative | A description with no rejected alternative | Nothing | "A rejected alternative earns its sentence only where a reader would propose it". Not a finding. |
| Answer an open question, keep it as a question in Scope, or drop it | A change with no issue or review thread | Nothing | Ends where there is no question. Not a finding. |

Not findings: "name the public identifier once", ended by "the change adds, removes, or renames"; "answer the open question", ended by "left open in the issue or review".

## Item 3a: level, placement, and the environment

- The edits sit in the existing skill, the README, and the existing metadata files.
- Registration entries are the three version strings. They match each other.
- I did not run `make check`, because it needs network through `uvx`.
- There are no sentences that could appear unchanged in any tutorial on the topic.

None.

## Item 4: names by content, not by position

New headings and references use `§2`, "the What slot", and "slot 2". These are the document's own existing addressing scheme. Nothing refers to "above" or "below" or to an ordinal.

None.

## Item 5: the failure report (analogue: what each rule tells the reader to look at)

- The new checklist items "Symptom", "Alternatives", "Discussion", and "Translation" each give an observable test, such as "delete each sentence in turn; where the diff still says it, leave it deleted".
- "Does the sentence end at what found it?" detects the rule it is attached to.
- The "Discussion" item reaches the open-question rule.

None.

## Item 6: what the writer says it verified

- The commit message gives measured numbers for the blind drafts: with the final wording, none of two stated an absence. The retold obstacle went from two of four to none of four. The open question went from three of three to none of four. Hunk translation persists in about one draft in two.
- It states which wording was not re-run.
- It states that there are no research cases.
- The exemplar and bad-case pair for the What-slot rule has not been re-applied to the rewritten example. That leads to finding 2.

## Item 7: siblings of the change

- **README.** The README bullets were updated. `git grep` for "stated absence" and "no observable symptom" finds no other copy of the old skip condition.
- **Twin paths of the symptom rule.** The old slot 2 wording ("say so") was in the Symptom checklist, slot 2, and changelog part 3. All three are updated.
- **Instructions trigger file.** It carries no rule content, so it needs no change.
- **`merge-model.md`.** It mentions "problem, symptom, approach" generically. Those mentions are still accurate.
- **Commit-body variant.** The commit-body section (§2) has no copy of the symptom or What-slot rule.
- **Set size.** I found no sentence that counts the checklist items or the slots in a way the change made stale.

None.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The new text says "neither is the absence of [a failure] [known]" (SKILL.md:93-94), and the next sentence still tells the writer to state "no symptom by construction", with a leak whose error path logs nothing as the example (SKILL.md:94-96). A leak is an unobserved symptom: it eventually exhausts a resource, so an agent that follows the example states an absence the previous sentence calls unknown. | Substantive | `SKILL.md:93-96` | Replace the leak example with one that has no caller-visible outcome in any state (for example, a duplicate log call). Or tie "by construction" to a stated reason in the code. |
| 2 | The What-slot worked example's *After* contains a hunk translation: "with the pool open from startup it sends directly" restates `QueryExecutor.execute now uses sendDirect`, which the diff shows. The rule just above says a sentence recoverable from one hunk is cut. The *After* also predicts "a caller that runs before startup completes fails at once", derived from code and not marked as derived, which §2 slot 2 requires. | Substantive | `SKILL.md:~350-358` | Cut "with the pool open from startup it sends directly" from the *After*, or mark the sentence as derived. Re-apply the Translation checklist item to the example. |
| 3 | The audit rule says "name what found it and end the sentence there" with no exception for a defect that an audit found and a user later reported. The agent would drop the log line R3 greps for. | Substantive | `SKILL.md:90-93`, `SKILL.md:475` | Add a clause such as "unless a report also observed it" to slot 2 and changelog part 3. |
| 4 | The Translation rule gives no outcome when deleting every What sentence leaves the slot empty. | Taste | `SKILL.md:~822` | Add "and omit the slot if nothing is left", or accept it as is. |
| 5 | A line break splits "Leave" from "a question out" (`SKILL.md:~463-464`). The paragraph above wraps at about 100 columns, and this line is cut short. | Taste | `SKILL.md:~463` | Re-wrap the paragraph. |

This review did not run `make check`, did not fetch or read any cited issue or exemplar, did not apply `apm-authoring`, did not re-run the blind drafts behind the commit's measurements, and did not pass over the prose for style alone.
