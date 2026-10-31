# Final review: `d79c43d..HEAD` (4f69810, "stop drafts from inventing symptoms and translating hunks")

**Inputs and scope.** There is no separate task statement, so the claimed cases come from the commit message alone. This change has no code, so I used the §2a analogues and did not run the drift script (nothing to parse). I loaded `english-developer-style` from the given skills directory. The `apm-authoring` authoring skill is not among the three provided and I did not load it. I read the whole diff first. There is no previous report. The only check I ran was `make check-descriptions`, which passed (27 descriptions within 1020 characters). `make check` needs `uvx` and the network, so I did not run it.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another, counts, cross-references)

- **Version.** `1.4.0` appears in `agent-packages/change-description-authoring/apm.yml`, root `apm.yml:168` and `.claude-plugin/marketplace.json:291`. All three agree, and no other file carries `1.3.0` for this package.
- **Cross-references.** I checked each one against the target and found no problem: "§2, slot 2" (changelog row), "§2, the What slot" (§7), "(§5)" for public identifiers, and the checklist's "§2, §3".
- **Substantive.** The What-slot "After" example (SKILL.md, in the `Before:`/`After:` pair after "state the reason for the decision") contradicts the rule it illustrates.
  - The rule says a sentence recoverable from one hunk is translation. The After says "`QueryExecutor.execute` used `sendWithRetry` only to reopen a closed pool; with the pool open from startup it sends directly."
  - That second clause is "Y now calls Z" restated, which is the exact form the rule gives as translation.
  - The After also states the outcome in prose ("a caller that runs before startup completes fails at once instead of opening the pool on demand").
  - The following paragraph says that outcome belongs on its own line under "User-visible changes". The skill's own slot 3 rule says "A fact stated in slot 3 is not restated in slot 2."
  - A reader copying the example gets both defects. The commit message says the example "no longer puts an outcome in prose", which is false.
  - The explanatory sentence "the first sentence says why they are no longer needed" is also off. The first sentence states a behavior, not why `ensureOpen()` became unnecessary.
- **Taste.** The Scope paragraph (SKILL.md, "A question the issue or the review left open…") has a hard wrap that leaves "wanted. Leave" and then a one-clause line. It reads as an editing leftover.
- **Taste.** §3 (the changelog entry's argument) and §7b step 5 ("symptom dropped" as a finding) are written for the case where the symptom is always present. Neither mentions the new audit-found exception.
  - A comparison that applies §7b to a rewrite which correctly removed a predicted symptom would still report "symptom dropped".
  - I would add "except where §2 slot 2 forbids it" in one place.
- No narration (`now`, `no longer`, `used to`) was added to the skill's own rules. The "now calls" and "no longer" in the quoted examples are quoted bad text.

## Item 2: claimed cases covered (analogue: the situations the commit message says the change handles, matched to the section that handles them)

| Claim in the commit message | Where handled |
| --- | --- |
| Audit-found defect: name what found it, no predicted failure, no "none seen" | Slot 2 prose, slot 2 table skip, the changelog row 3, and the checklist Symptom item. All present. |
| Derived consequence traced to the caller and marked as derived | Slot 2 second paragraph and the checklist Symptom item. |
| Hunk translation, public identifier exception, `§7` pointer, "what changed that the diff does not show" | The What-slot paragraph, §7, the §2 reviewer paragraph, and the checklist Translation item. |
| Rejected alternative: mechanism as a fact about the merged code; an obstacle the change removes is a step | §2 rejected-approach paragraph and the checklist Alternatives item. |
| Open question: answered, kept in Scope, or dropped | The Scope paragraph, the Scope table row, and the checklist Discussion item. |
| Slot 2 and What slots carry bad and good examples | The slot 2 pair is present. The What-slot pair is present but defective (Item 1). |

- **Commands to run:** none in the changed files.
- **Hunk-to-claim reading:** every hunk belongs to a sentence of the commit message. This includes the README bullets, the version bumps, and the §7 sentence.

## Item 3: boundaries, partitions, and the negative control (analogue: partitions, the negative control, and the table of added instructions)

The commit message states two things it did not test. One is the current open-question rule and the What-slot example. The other is the hunk-translation rule, which the commit says "persists in about one draft in two". It also ran no cases under `research/`.

- **Partitions the evidence leaves open.**
  - The audit-found rule has two partitions with no evidence: the defect found by audit that is also observed in production, and the rule applied to a changelog entry. The drafts only exercised the pull-request description.
  - The open-question rule has "kept for a maintainer" and "dropped" untested. The drafts only showed "answer from the code".
- **Pre-existing state:** a skill package upgraded from 1.3.0 leaves no state to meet.

**Table of added instructions.** Each row names the input it does not serve and the clause that would end it.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Slot 2: for an audit-found defect, name what found it and end the sentence there | A defect an audit found that a user has since hit, with an exception text in the issue | One sentence naming the audit. The slot-skip cell says "the body names what found it", so the quoted exception, which R3 greps for, may be left out. The instruction before it (slot 2 "carries what a person outside the code observes: the exception…") asks for the opposite. | "…and no symptom has been observed" (taste: the first paragraph's "end the sentence" can be read as only that sentence) |
| Derived consequence: trace it to the caller and mark it as derived | A consequence visible at the call site with no mechanism on the way | A sentence tagged "derived" with a trace of no steps | Ended by "through every mechanism on the way". Listed here, not a finding. |
| Translation: cut a sentence the reviewer recovers from one hunk | A one-line fix whose only What sentence is the edit | An empty What slot, since the reason belongs to Why | Ended by "state the reason for the decision, not the edit". Listed here, not a finding. |
| Rejected alternative stated as a fact about the merged code | A change with no alternative a reviewer would propose | A manufactured alternative with a mechanism | Ended by "earns its sentence only where a reader would propose it". Listed here, not a finding. |
| Open question: answer it, keep it in Scope, or drop it | A pull request with no open question | Nothing | Ended by "A question the issue or the review left open". Listed here, not a finding. |
| Changelog row 3: for an audit-found defect, the condition alone | An audit-found defect with a known user-visible exception class | Condition only, no class | Same as row 1 (taste). |

## Item 3a: level, placement, and the environment (analogue: file placement and the repository gate)

- The rules sit in the same SKILL.md sections as their siblings: slot 2 in the commit-body table and the pull-request description, Scope in the Scope slot, and checklist items in §8.
- The README bullets and the marketplace entries are the ones the repository's gate checks. `make check-descriptions` passed offline.
- **Taste.** The "After" example for the audit-found defect and the "A consequence derived…" paragraph sit in the commit-body slot 2 prose. The pull-request Why slot refers to slot 2 only through "the commit body's slots 1 to 3 written for a reader who has the diff open". Say that Why inherits the audit rule so that a reader of the pull-request table alone does not miss it.
- No sentence is generic enough to appear in any tutorial on the topic.

## Item 4: names by content, not by position

none. The new text uses "the What slot", "the Scope slot" and "slot 2" (a named slot, not an ordinal in running text). The new checklist items are labelled Translation and Discussion.

## Item 5: the failure report (analogue: what a rule tells the reader to look at, and whether each detection reaches it)

- The rule "name what found it; say neither failure nor absence" is reached by the checklist Symptom item. The Symptom item does ask the right questions.
- The rule against hunk translation is reached by the Translation item, whose check ("delete each sentence in turn; where the diff still says it, leave it deleted") detects the rule it attaches to.
- There is no detection for the length of the What-slot sentences, but the Translation item covers that case.

## Item 6: what the writer says it verified

The commit message gives counts: two of two drafts predicted a symptom without the rule, five of ten stated "none seen" under a ban on the word, none of two under the final wording, retold obstacle two of four to none of four, open question three of three to none of four, and translation persisting in about one draft in two.

- **Substantive.** The total does not add up.
  - Those sub-counts come to more than fifteen drafts if they are disjoint, and the commit does not say how they overlap.
  - Two of the counts are copied into the skill text as "measured: two of two drafts…" and "measured: three of three drafts repeated…". A reader cannot check either number.
- The two rules most likely to be wrong are the ones the commit says were not re-run: the current open-question rule and the What-slot example. The example is the defective one (Item 1), so the missing run is the likely reason it slipped through.
- The report gives no exemplar that passes and no bad case that fails for the audit-found rule applied to a changelog entry.
- Per the skill, I did not run the drafts myself.

## Item 7: siblings of the change

- **Set members.** The change adds a rule to the Symptom list, not a member to a set. The README bullets now cover all three new rules.
- **Places that mention the old symptom behavior.**
  - The §1 correction paragraph, the "Skip when" text of slot 2, and the changelog row 3 are covered.
  - §3 and §7b step 5 are not (Item 1, taste).
- **Counts in prose.** I searched for "two", "three" and "five slots". Nothing counts the checklist or the slots in a way the two new checklist items change.
- **Siblings for the remedy.** The audit rule appears for the commit body, the changelog and the checklist. The pull-request Why row is not updated (Item 3a, taste).
- **Other packages.** `docs-page-authoring/README.md`, `problem-report-authoring/README.md` and `english-*-developer-style` only link to this package or name it. None restates the symptom or Scope rules.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The What-slot "After" example carries a hunk translation ("it sends directly") and an outcome in prose that the next paragraph says belongs under "User-visible changes". The commit message says the example no longer puts an outcome in prose. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, the Before/After pair after "state the reason for the decision" (about lines 349-358) | Rewrite the After to state only the reason (the pool opens at startup, so the lazy open is not needed) and leave the early-caller failure to its own line. Re-run the example against the Translation checklist item. |
| The two "measured" counts and the commit's "over fifteen drafts" total cannot be reconciled. The commit also says the current open-question rule and the What-slot example were not re-run. | Substantive | commit message; SKILL.md lines ~100 and ~463 | State how the drafts overlap, or drop the counts from the skill text. Re-run the What-slot example. |
| Slot 2's skip cell and "name what found it" can be read to drop a quoted exception for a defect an audit found and a user later hit. | Taste | SKILL.md line 81 and lines 90-96; changelog row at line 475 | Add "and no symptom has been observed" to the audit clause. |
| §3 and §7b step 5 list "symptom dropped" as a finding without the audit-found exception. | Taste | SKILL.md lines ~508-512 and ~794 | One clause: "unless §2 slot 2 forbids it". |
| The pull-request Why row does not mention the audit rule that its commit-body twin carries. | Taste | SKILL.md line ~195 | Say that Why inherits slot 2's audit rule. |
| Hard wrap leaves "wanted. Leave" with a one-clause line. | Taste | SKILL.md lines ~458-465 | Re-wrap the paragraph. |

This review did not run the blind-draft trials or `make check`, and did not pass the prose over for style beyond the places where a sentence reads wrongly.
