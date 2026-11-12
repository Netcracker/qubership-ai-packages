# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.** This review had no separate task statement, so the claimed cases come from the commit message of 4f69810 alone. The change carries no code, so §2a applies and each item below reads its analogue. The drift script was not run because the diff has no members to parse. I loaded `english-developer-style` and `test-authoring`, both from the given directory. `apm-authoring` is not among the three skills I was told to load, so I didn't read it. The "worked example followed by a sentence on what not to copy" check is therefore done from final-review's own wording.

There is no previous report. The working tree was clean when I finished. `make check` (dry-run) printed that it would write `marketplace.json`, but I did not write it and `git status` is empty.

## Item 1: Comments consistent with the code and with each other

Analogue: every statement one changed file makes about another, plus counts, section references and repeated descriptions.

- **Version bump.** It reads 1.3.0 → 1.4.0 in `agent-packages/change-description-authoring/apm.yml`, root `apm.yml`:168 and `marketplace.json`:291. All three agree. The other 1.3.0 hits are other packages.
- **Section references.** `§2, slot 2`, `§2 the What slot`, `§5` (identifiers), `§7` and `§8` resolve to existing headings.
- **Slot-2 wording.** The table cell (line 81), the body paragraph (lines 91-96), the changelog row (line 475) and the checklist (line 803) all say the same thing. For a defect found by audit, the commit body names what found it, and the changelog entry names the condition alone.
- **Trigger condition.** Slot 2 is headed "Impact and trigger", but line 93 says "name what found it and end the sentence there". A writer can read that as dropping the trigger condition for an audit-found defect, with nothing saying where the condition goes instead. See finding 2.
- **Translation example (lines 342-359).**
  - The *After* ends "it sends directly". By the rule's own deletion test (checklist "Translation") the diff already says that. The cut test applies to the *After* too.
  - The *After* also states a derived outcome ("a caller that runs before startup completes fails at once"). The paragraph at line 99 allows that only if the consequence is traced to what a caller sees and marked as derived. See finding 3.
- **Paragraph wrap.** Line 464 is a stray short line ("wanted. Leave") in the open-question paragraph. See finding 5.
- **Narration.** I found no `now`, `no longer` or `used to` in the added skill text.

## Item 2: Claimed cases covered

Analogue: the cases the commit message names, each mapped to the section that handles it. The skill's own detection for a rule is its checklist item.

| Claimed case | Rule | Checklist item |
| --- | --- | --- |
| Predicted failure from one missing call | Lines 91-100 | Symptom, 3rd and 4th sentences (line 803) |
| "No failure observed" in any wording | Line 94 ("neither is the absence of one") | Symptom, 5th sentence |
| Hunk translation, including under a lead-in that states a reason | Lines 339-359; §7 bullet (line 763) | Translation (new) |
| Public identifier named once | Lines 344-347 | Not in the Translation item. See finding 4. |
| Retold obstacle the change removes | Lines 370-373 | Alternatives (extended) |
| Open question the code answers | Lines 458-465 | Discussion (new) |
| Maintainer-only question kept in Scope | Same paragraph, plus the Scope row (line 199) | Discussion |
| Changelog entry names the condition alone | Line 475 | Symptom (shared with the commit-body case) |

The blind drafts are unrecoverable from the repository. The commit message discloses that the current open-question rule and the What-slot example were not re-run.

Commands: the change tells no one to run any.

Hunk claims: each hunk belongs to a sentence of the commit message.
- `marketplace.json` and both `apm.yml` hunks are the 1.4.0 bump.
- The README hunk is the summary of the new rules.
- The §7 and Scope hunks are named in the message.

No unclaimed hunk.

## Item 3: Boundaries, partitions, and the negative control

Analogue: the genres, modes and situations the change claims, plus the table of added instructions.

**Partitions.** The commit message claims three defect kinds: an audit or code-read defect, a defect with no symptom by construction, and an observed symptom. The rules cover all three. The "changelog entry" and "commit body" artifacts are also both addressed. There is no pre-existing-state partition beyond a version bump.

**Table of added instructions**

| Instruction | Input it does not serve | What an agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (line 93) | A defect an audit found that also has a documented trigger the commit needs (a specific setting) | "An audit of the retry paths found this." The trigger drops out of slot 2. | "…and state the trigger condition in the next sentence". The skill ends it nowhere, because "end the sentence there" invites dropping it. Finding 2. |
| "A consequence derived from the code earns a sentence only after it is traced to … a caller" (line 99) | A one-line fix whose reader needs no consequence | Nothing. The sentence's own condition ("only after traced") ends it. | Quote: "earns a sentence only after it is traced to the point where a caller sees it". Not a finding. |
| "a sentence whose content the reviewer recovers from one hunk … is translation" (line 342) | A refactor with no diff-visible rationale, such as a rename that clarifies a name | The agent deletes every What sentence, including the only statement of what changed. | The rule's own clause: "state the reason for the decision". For a pure rename, the identifier exception (line 345) keeps the name. Partly ended, not a finding. |
| "A public identifier the change adds, removes, or renames is named once" (line 345) | An internal identifier that happens to be public in a language with no visibility (Python, JS) | The agent names every renamed function. | "…that a reader outside the repository can pass, set or call". Taste (finding 4). |
| "keep it in the Scope slot as a question" (line 460) | A commit body or a description with no Scope slot (a four-paragraph prose description) | The question is kept with no slot to sit in. | Lines 258-262 say a short description is prose, so Scope is a paragraph there. The Scope row carries the instruction. Not a finding. |
| "Is a question dropped only when it does not bear on this change" (line 827) | A question that bears but is settled in the issue thread by a maintainer | The agent re-asks it as open. | The same paragraph's "answered" arm covers it only if "verified evidence" includes a maintainer's statement. Taste (finding 6). |

The *control* arm (an input where the new rule is noise and the output must not grow) was not run. See Item 6.

## Item 3a: Level, placement, and the environment

- Each rule sits in the file the existing rules for its artifact sit in: slots in §2, the changelog in the §2 changelog table, the checklist in §8.
- README summary and `apm.yml` bump follow the sibling packages.
- The repository gate `make check` (`apm pack --check-versions --check-clean --dry-run`) ran offline and printed "Would write marketplace.json [claude] (43 package(s))". It printed no mismatch. I did not write anything.
- The research directory has no case for this skill, and the commit message says so. That is not a finding.

## Item 4: Names by content, not by position

None. The added text uses "slot 2", "What slot" and "Scope slot" as headings by content. The commit message's "§7" and "§8" are section numbers that exist.

## Item 5: The failure report

Analogue: every rule has a detection, and the detection tests that rule.

- **Rules reached by the checklist.** Symptom, Translation, Alternatives and Discussion cover the four rules. Finding 4 covers the one that isn't reached.
- **Does the detection test the rule?**
  - Translation's "delete each sentence in turn; where the diff still says it, leave it deleted" tests the rule.
  - Alternatives' "a fact about the merged code, not an obstacle the change itself removes" tests it, provided the checker has the post-change code.

## Item 6: What the writer says it verified

The commit message states counts: fifteen drafts, 2/2, 5/10, 0/2, 2/4 → 0/4, 3/3 → 0/4, about one in two for translation. It also states what was not re-run (the current open-question rule and the What-slot example) and that no research case exists.

These are partial:
- The counts don't reconcile to "fifteen". The symptom arms alone sum to 14, and the other arms use different draft sets.
- The new "measured" parentheticals in the skill (lines 100 and 463) have no record under `research/change-description-authoring/`. The README says the skill "carries no citations; the evidence stays in the research directory". See finding 1.
- No control input is stated, namely a change where the added instruction is noise and the output must not grow.

## Item 7: Siblings of the change

- **Set members.** The change adds rules and checklist items, not a member of a set. The checklist count is not stated in prose. I found no "four items" or "five slots" sentence that now counts wrong.
- **Surfaces that route to the skill.** The README summary was updated. The `apm.yml` description and the trigger instruction (`change-description-authoring.instructions.md`) need no change because the skill's scope is unchanged.
- **Other places that state the old rule.** `grep -i "absence\|stated absence"` finds only line 96, which the change edited. I found no leftover instruction to "say so" for an unobserved symptom.
- **Remedy paths.** The slot 2 rule covers the commit body and the changelog entry. The description's Why slot (line 195) says "the problem, the symptom, the condition" and has no matching clause for an audit-found defect. See finding 2.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | New "measured: two of two", "three of three" claims and the "fifteen drafts" total are not recorded under `research/change-description-authoring/`, and the commit's per-arm counts don't sum to fifteen. | Substantive | SKILL.md:100, 463; commit message | Add the drafts and counts to the research directory, or reword the commit message to state per-arm counts without a total. |
| 2 | "Name what found it and end the sentence there" can drop the trigger from an audit-found defect's slot 2, and the Why slot of a description (line 195) has no matching clause. | Substantive | SKILL.md:93-96, 195 | Say that the condition is still stated, in the next sentence or in slot 1. Add the same audit clause to the Why slot. |
| 3 | The translation example's *After* asserts "fails at once" as fact and ends "it sends directly", which the Translation checklist item would cut. This is the same pattern the new rules ban. | Substantive | SKILL.md:353-355 | End the second sentence at "…only to reopen a closed pool". Mark the early-caller failure as derived, or drop it from the example. |
| 4 | The identifier exception ("named once") has no checklist item, so a drafter who checks only §8 will not test it. The commit says each fix has a checklist item. | Taste | SKILL.md:344-347, 798+ | Add "Is each public identifier the change adds, removes or renames named once?" to the Translation item. |
| 5 | Stray short line "wanted. Leave" in the open-question paragraph. | Taste | SKILL.md:463-464 | Re-wrap the paragraph. |
| 6 | "Verified evidence" does not say whether a maintainer's statement in the thread counts as an answer, so the "maintainer-only" arm and the "answered" arm can both apply. | Taste | SKILL.md:458-465 | Name a maintainer's recorded decision as an answer, with its link. |

## Not checked

The suite and the blind-draft experiments were not run, `apm-authoring` was not read, and the report does not cover the style of the added prose (wording is `english-developer-style`'s).
