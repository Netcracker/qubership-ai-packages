Reading the diff and running the offline description gate (`make check-descriptions`, passed). I'm now writing up the report.

# Final review: `d79c43d..HEAD` (one commit, 4f69810)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it is a skill (`SKILL.md`), a README, and version bumps. I applied the §2a analogues under every item and did not run `comment-drift.py`, because it has no members to parse. I loaded the `final-review` skill and used the developer-style skill's sections for wording only. The `apm-authoring` and `test-authoring` skills were not read. There is no previous report.

**Claimed cases** (from the commit message):
1. Slot 2: an audit-found defect is described by what found it, and the sentence ends there. A derived consequence is written only when traced to what a caller sees.
2. Slot 2: "say so" is kept only for a defect with no symptom by construction.
3. Slot 2 and the What slot each carry a bad and a good example.
4. What slot: a sentence recoverable from one hunk is translation. A public identifier is named once. §7 points to this rule, and §2 asks for "what changed that the diff does not show".
5. Rejected alternatives are stated as facts about the merged code.
6. Open questions are answered, kept in Scope, or dropped.
7. Checklist: Symptom and Alternatives are extended, and Discussion and Translation are new.
8. The changelog row for the symptom is aligned with the slot 2 rule.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)
Findings:
- **Slot 3 row, "Change and approach" (line 83): "What was done".** The commit message says the "what changed" wording was what made drafts list the changes. The §2 What paragraph and the Scope row were reworded, but this commit-body table row was not. Taste.
- **Translation example, `SKILL.md:354-362`: the After text does not match the sentence under it.**
  - The text says "the first sentence says why they are no longer needed", but the first sentence explains the early-caller failure. It does not explain why the `ensureOpen()` calls are redundant.
  - The After text also ends with "it sends directly", which is the kind of hunk translation (`Y now calls Z`) the new rule bans.
  - The first sentence also puts an outcome in prose ("fails at once"), although the commit message says the example "no longer puts an outcome in prose". Substantive: the skill's own example partly fails its own rule.
- **Line 463-464 is wrapped short** ("wanted. Leave" then "a question out only…"). Taste, a reflow slip.
- Other cross-references are correct: §2 slot 2, §7 (line 763), §8 checklist items, "User-visible changes" as the PR slot 3 name, and "Scope slot".

## Item 2: claimed cases covered (analogue: the section that handles each claim)
- Cases 1 and 2: lines 81, 92-96, 98-101, 475, and checklist line 803-806.
- Case 3: the slot 2 Before/After at 92-93, and the What Before/After at 349-356.
- Case 4: lines 342-348, 763, and 826-827.
- Case 5: 368-374 and the checklist.
- Case 6: 458-465 and 835-838. The Scope row (199) matches.
- Cases 7 and 8: covered.
- **Commands the change tells someone to run:** none.
- **Hunks no sentence claims.** The version bump 1.3.0 to 1.4.0 appears in four files (`marketplace.json`, `apm.yml`, the package `apm.yml`) and the README hunk. The commit message does not mention them. The marketplace gate probably requires aligned versions, but I did not check whether earlier commits also left the bump unmentioned. Taste: add one sentence.
- **Stated measurements are not checkable here:** "fifteen blind drafts", "two of two", "three of three", "none of four". Reproduction is not possible from the repository, and the commit says `research/` has no cases for this skill. No finding; this is noted in Item 6.

## Item 3: boundaries, partitions, negative control (analogue: genres and situations, plus the table of added instructions)
Added instructions, each with an input where it does not serve:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it and stop | A defect an audit found that also has an observed symptom in a bug report | "An audit found this" and no symptom, dropping the reported one | Not stated. Slot 2 still says "what a user observes", so an observed symptom is not clearly kept. Substantive: add "unless a symptom was observed". |
| Trace a derived consequence to what a caller sees | A one-line fix whose effect is obvious | A derived-consequence sentence the reader did not need | "earns a sentence only after it is traced" ends it. Not a finding. |
| Hunk-recoverable sentence is translation | A change with no tests and a one-line diff | An empty What slot | "A decision does not exempt the sentence" conflicts with "the first sentence says why". The §3 Decision question covers it. Taste. |
| Name a public identifier once | An identifier the diff shows in a rename of a private field | Nothing, because "public" bounds it | "public identifier" ends it. Not a finding. |
| Mechanism is a fact about the merged code; an obstacle the change removes is a step | A trivial change with no alternative | A forced alternative sentence | Already ended by the table row "problem statement makes approach obvious". Not a finding. |
| Open question: answer, keep in Scope, or drop | A description with no discussion | Nothing | "left out only when it does not bear on this change" ends it. Not a finding. |

The negative control exists for the symptom rule: both branches (audit-found and no-symptom-by-construction) are given. The state left by an earlier version of the skill is not relevant to a text-only skill.

## Item 3a: level, placement, environment
Content sits in the existing §2 and §7 sections, matching the sibling layout. I did not run the marketplace gate (`make check`). I did run `make check-descriptions`, which passed with all 27 descriptions within the limit.

## Item 4: names by content, not position
None. The change adds no ordinals or "see below". It uses §-references and slot numbers that already existed.

## Item 5: the failure report (analogue: does the rule have a detection)
Each new rule has a checklist item (Symptom, Translation, Alternatives, Discussion). The Translation check ("delete each sentence of the What slot in turn") detects the rule rather than a weaker property. The "outcome in prose" rule has no checklist item; this repeats the Item 1 finding.

## Item 6: what the writer says it verified
The commit message reports blind-draft counts and says plainly that the final open-question rule and What-slot example were not re-run. Applying the rules again to the change's own worked example fails: see the Item 1 finding on the translation example. The input where the added items are noise (Item 3 table) was not tried by the writer.

## Item 7: siblings
- The version is aligned across the package `apm.yml`, the root `apm.yml`, and `marketplace.json` (line 291). Other packages still show 1.3.0 or 1.4.0 by their own version, which is unrelated.
- The README is updated to match the new rules.
- No sentence counts the slots or checklist items as a fixed number, so none went stale.
- Slot 4 and the changelog row 3 are aligned with the new slot 2 rule.
- The commit-body table (slot 3, line 83) is the one sibling not touched; see Item 1.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The translation example's explanation does not match its After text, which contains an outcome in prose and "it sends directly" | Substantive | `SKILL.md:354-362` | Rewrite the After sentence so it states the reason only, and make the sentence under it describe it correctly. |
| The audit-found rule does not say what to do when a symptom was also observed | Substantive | `SKILL.md:81, 92` | Add a clause such as "unless a symptom was observed". |
| "What was done" in the commit-body slot 3 row can still invite listing changes | Taste | `SKILL.md:83` | Align it with "what changed that the diff does not show". |
| The version bump and README hunk are not claimed by the commit message | Taste | the four changed non-skill files | Add one sentence. |
| Short wrapped line | Taste | `SKILL.md:463-464` | Reflow. |

I did not run the skill against any input or the full marketplace gate, I did not pass over the prose for style, and I did not verify the draft counts quoted in the commit message.
