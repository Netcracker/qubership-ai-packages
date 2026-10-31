I'm finishing the review of `d79c43d..HEAD`, one commit that changes a skill (SKILL.md, README, and version metadata). I'm not running the drift script because there are no members to parse, and I'm filling in the form through its no-code analogues in §2a.

# Final review: `d79c43d..HEAD` (4f69810)

**Inputs**
- There is no task statement. The claimed cases come from the commit message alone.
- No previous report exists.
- I ran `comment-drift.py d79c43d HEAD`. It printed nothing, as expected for a change with no code.
- Skills loaded: `final-review` and the `english-developer-style` copy under the given skills directory. `apm-authoring` is not among the three allowed skills, so I did not load it. The cited `apm-authoring` rules are therefore unchecked.

## Item 1: Comments consistent with the code and with each other (analogue: statements one file makes about another)
Finding F1, below. Everything else checked out.
- **Version numbers.** 1.3.0 → 1.4.0 appears in `agent-packages/change-description-authoring/apm.yml`, root `apm.yml`, and `marketplace.json:291`. The remaining `1.3.0` at `marketplace.json:57` belongs to another package.
- **Section references.** `§2`, `§5`, `§7` and `§8` resolve. `§5` does list "the public identifier the change touches", which backs the exception in the new What-slot text. The §7 bullet points to "§2, the What slot", and the §8 Translation item exists.
- **Slot 2 and changelog row.** The slot 2 skip condition, the slot 2 prose, the changelog row 3 and the §8 Symptom item all say the same thing about audit-found defects. The older sentence "a stated absence does not [look like an omission]" is kept, but it is now limited to "no symptom by construction".
- **README.** The two README bullets match the SKILL text.
- **Narration.** No new comment narrates the change.

## Item 2: Claimed cases covered (analogue: sections that handle each claim)
- **Commands to run:** none in the changed files.
- **Slot 2, audit-found defect.** The rule, a before/after example, a table row, a changelog row and the §8 Symptom item cover it.
- **Slot 2, derived consequence.** The rule and the §8 Symptom item cover it. The rule has no example of its own. The commit claims examples only for slot 2 and the What slot.
- **What-slot translation.** The rule, an example and the §8 Translation item cover it. See F1.
- **Rejected alternatives.** The rule and the §8 Alternatives item cover it.
- **Open questions.** The rule, the Scope table row and the §8 Discussion item cover it.
- **Hunks.** All five files map to the commit message. The version bumps are claimed by the package change itself.

## Item 3: Boundaries, partitions, and the negative control

Table of added or widened instructions, one input each that the instruction does not serve:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Audit-found defect: "name what found it and end the sentence there" | An audit found the defect, but a user's log line for it is also in the issue | "An audit found this", with the quoted diagnostic dropped. Slot 2 and the §8 Symptom item still ask for observed symptoms to be quoted, so the text is ambiguous. | "…, and a symptom someone observed is still quoted" | Taste |
| Derived consequence earns a sentence only after tracing | A one-hop consequence, such as a typo in an error message | Nothing. The rule's own condition ("only after it is traced") ends it. | Quote: "earns a sentence only after it is traced…" | Not a finding |
| What slot: delete sentences the diff still says | A one-line fix whose What slot would be left empty | An empty What slot | "keep one sentence naming the behavior" | Taste |
| Rejected alternative stated as a fact about the merged code | A change with no alternative a reviewer would propose | Nothing. Quote: "earns its sentence only where a reader would propose it". | n/a | Not a finding |
| Open question goes in the Scope slot | A description that §4 rule 5 makes a commit body, which has no Scope slot (the checklist says Scope is absent there) | The question has no slot. The text neither drops it nor places it elsewhere. | "in a commit body, in the Why slot" | Taste |

- **Partitions.** The commit message states that the open-question rule and the What example were not re-run, and that no cases under `research/` were re-run. That is an honest statement of the partitions without evidence.
- **Pre-existing state.** Not applicable. The change is a package version bump with no migration.

## Item 3a: Level, placement, and the environment
None. The edits sit in the sections that own each rule, and the README and the registration entries are updated in the same places as for earlier versions. I did not run the repository's registration gate, because I did not find it quickly and the task rules out changing files. I did not check `references/merge-model.md` for statements that contradict the new rules.

## Item 4: Names by content, not by position
None. The new text refers to "slot 2", "the What slot" and "§7". These are the file's existing headings and names, not ordinals. The "Before:" and "After:" labels are the file's existing idiom.

## Item 5: The failure report
- Every new rule has a §8 checklist item: Symptom, Translation, Alternatives and Discussion.
- The Translation item ("delete each sentence of the What slot in turn; where the diff still says it, leave it deleted") detects the rule it is attached to.
- Because of F1, the skill's own worked example fails that detection.

## Item 6: What the writer says it verified
The commit message gives draft counts: both drafts, then 5 of 10, then none of 2 on symptoms; 2 of 4 → 0 of 4 on the retold obstacle; 3 of 3 → 0 of 4 on the open question. It also says translation "persists in about one draft in two", and that the final open-question rule and the What example were not re-run. This is stated evidence. The remaining translation failures also match F1.

## Item 7: Siblings of the change
- **Version string.** The package `apm.yml`, root `apm.yml` and `marketplace.json` agree.
- **Other files naming the skill.** The `english-developer-style` skills, rules, `.cursor` and `.claude` files name the package without describing its slots, so they need no change. `docs-page-authoring` only cross-references it.
- **Set size.** No sentence counts slots or checklist items: "Five slots" and "Six slots" are unchanged, and no slot was added.
- **Sibling to the Slot 2 rule.** Commit-body slot handling (§2 Commit body) has no mention of "has not been seen" or an equivalent phrase, so the grep found no sibling.
- **Not read.** I did not read `references/merge-model.md` in full.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The new What-slot *After* example fails the rule it illustrates. Its second sentence, "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly", is "Y now calls Z" recoverable from one hunk. Those identifiers are not public. The first sentence states a derived consequence ("a caller that runs before startup completes fails at once") as fact, while the same commit's new rule requires a derived consequence to be traced and marked as derived. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:353-356` (and the paragraph after it) | Rewrite the *After* so that every sentence survives the §8 Translation check: keep the reason ("the pool is open from startup, so the retry path that reopened it is dead") and either mark the early-caller failure as derived or drop it. Apply the §8 Translation check and the Symptom check to the example before committing. |
| F2 | The audit rule and the §8 Symptom item do not say whether a symptom someone observed is still quoted when an audit also found the defect. | Taste | `SKILL.md:92-96`, `SKILL.md:800-805` | Add a clause such as "a symptom someone observed is still quoted". Prefer this reading, but either is defensible. |
| F3 | The open-question rule says to keep the question in the Scope slot, but a description that §4 rule 5 turns into a commit body has no Scope slot. | Taste | `SKILL.md:458-466` | Add one clause naming where the question goes in that shape. |

I did not run the suite or the registration gate. I did not check that the cited counts in the commit message match the drafts, and I did not verify the claimed research drafts. The review did not include a style pass over the prose.
