I've finished reading the diff and the changed skill. The last check was the drift script, which I'm not using here because this change has no code. I'm now writing up the report.

# Final review: `d79c43d..HEAD` (one commit, `4f69810`)

**Inputs.**
- The change is a skill edit with no code, so I used the §2a analogues for every item. I did not run the drift script, because there are no members to parse.
- There is no separate task statement. The claimed cases come from the commit message alone.
- No previous report exists.
- I loaded `english-developer-style` and `test-authoring` from the given skills directory. The repository's own `apm-authoring` skill was not loaded, since you limited me to those three. Wording enters this review only where a sentence reads wrongly.

**Claimed cases, from the commit message:**
- (a) Slot 2 rewritten for defects found by an audit or a code reading.
- (b) A derived consequence is written only when traced to what a caller sees.
- (c) The changelog entry names the condition alone for such a defect.
- (d) What-slot translation rule, with a bad and a good example, plus an exemption for public identifiers.
- (e) §7 points to the translation rule.
- (f) §2 asks for "what changed that the diff does not show".
- (g) Rejected-alternative mechanism is stated as a fact about the merged code, and an obstacle the change removes does not count.
- (h) Open-question rule.
- (i) §8 gains Translation and Discussion items; Symptom and Alternatives are extended.
- (j) README, `apm.yml` and marketplace version bumped to 1.4.0.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files and sections)

- **Cross-references.** §2, §5 and §7 exist. The changelog row 3 points to "§2, slot 2", and that rule is there. §7's "§2, the What slot" is also there.
- **Counts.** "Five slots" and "six slots" are unchanged and still match. The README bullet matches the SKILL.md rules.
- **Finding 1 (substantive).** The new What-slot example contradicts itself and its own rule, in `SKILL.md` around line 349.
  - *After* sentence 1 puts the outcome in prose ("a caller that runs before startup completes fails at once"). The paragraph after the example then says the `IllegalStateException` "is an outcome, and it goes on its own line under 'User-visible changes'". That states the outcome twice. It also breaks "A fact stated in slot 3 is not restated in slot 2" and "State each causal link once". The commit message says the example "no longer puts an outcome in prose", and it still does.
  - *After* sentence 2 ends "it sends directly". That is the "Y now calls Z" form the rule just called translation. An agent copying the *After* writes the pattern the rule bans.
  - The paragraph after the example says "the first sentence says why they are no longer needed". Sentence 1 gives the reason for the new behavior. The `ensureOpen()` reasoning is in sentence 2.
- **Finding 2 (taste).** The open-question rule says to keep an unsettled question "in the Scope slot", but the commit body has no Scope slot. Where the description becomes the commit body (§4 rule 5), the rule has no destination. A clause would settle it.
- **Finding 3 (churn, noted only).** The new paragraph has a lone `Leave` at the end of a wrapped line, so the wrap is ragged.
- No narration of the change (`now`, `used to`) was added in the skill's rule text. The example *Before* strings are quoted, so I did not count them.

## Item 2: claimed cases covered (analogue: a detection for each rule)

| Claim | Where handled |
| --- | --- |
| (a) | Slot 2 skip column and prose, §8 Symptom |
| (b) | The "consequence derived" paragraph, §8 Symptom |
| (c) | Changelog row 3 |
| (d) | The "same holds for the code" paragraph and §8 Translation, covering the sentence-by-sentence deletion check. The "Translation" example fails Finding 1. |
| (e) | §7 added sentence |
| (f) | The "reviewer decides" paragraph |
| (g) | The rejected-alternative paragraph and §8 Alternatives |
| (h) | The Scope paragraph and §8 Discussion |
| (i) | §8 |
| (j) | Four version fields, all 1.4.0 |

- **Commands.** The change tells the reader to run none.
- **Hunk claims.** Every hunk belongs to a sentence of the commit message.
- **Finding 4 (taste).** The commit message says "Over fifteen blind Opus drafts". The counts in the message add up to 14 or more depending on how they are grouped (2 + 10 + 2 for the symptom rule, then 4 and 3 + 4 for the other two). The reader cannot reconcile them. The skill text's own "two of two" and "three of three" match the message.

## Item 3: boundaries, partitions, negative control (analogue: genres, situations, and added instructions)

- **Pre-existing state.** No persisted state is involved.
- **Limits and replacement mechanisms.** None apply.
- **Partitions.** Rule (a) covers three situations: an audit found it, a symptom was observed, and a defect with no symptom by construction. All three are written. Rule (h) covers three: answered, maintainer-only, and irrelevant. All three are written.
- **Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A defect a user observed, which an audit also confirmed | May drop the observed diagnostic, because the audit "found" it | The "quoted from an observation" check in §8 reaches this, and the *Before* and *After* show only the unobserved case. Taste: add "where a user did not observe it". |
| "A consequence derived from the code earns a sentence only after it is traced … and is stated as derived" | A one-line typo fix | Nothing; no consequence is derived | Already ended by the condition "a consequence derived". |
| "A sentence whose content the reviewer recovers from one hunk is translation" | A one-hunk change | May delete the only What sentence | §2's What slot and the Translation check do not say to keep one sentence that states the reason. Substantive: the rule says "state the reason … not the edit", which covers it, but the §8 check says "leave it deleted" without that exception. Suggested clause: "…and stop at the reason". |
| "A public identifier … is named once" | Several renamed identifiers | A list of them, which is the translation the rule bans | "Named once" is read per identifier, so this is a hypothetical. Taste. |
| "A question the issue or the review left open is answered, kept open, or left out" | A trivial change with no discussion | Nothing, since the rule conditions on a question | Ended by its own condition. |

The third row is **Finding 5 (taste)**. The Translation checklist item reads "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". Applied to a one-hunk fix, it can remove the only sentence that states the reason. The rule text keeps the reason, and the checklist item does not.

## Item 3a: level, placement, and the environment (analogue: which file each rule lives in, and registration)

- **Placement.** The edits are in the skill body, the package README, and the version fields of `apm.yml`, the package `apm.yml`, and `.claude-plugin/marketplace.json`.
- **Version.** All four values read 1.4.0. A minor bump is right for added rules.
- **Gate.** I did not run `make check`, because it needs network. The four values are in step by reading.
- **Line length.** The new prose lines are all within 120 characters. Longer lines in the file are table rows or earlier text.
- **Skill cases.** `agent-packages/AGENTS.md` says a skill change re-runs the cases under `research/<package>/cases/`. `research/change-description-authoring/` has no `cases/` directory, and the commit message says so. Nothing is owed.

## Item 4: names by content, not by position

- None. New text refers to sections by number, as the file already does, and to rules by content (the Translation, Discussion, Symptom and Alternatives items).

## Item 5: the failure report (analogue: does each rule have a detection)

- Each new rule has a §8 item: Symptom, Alternatives, Translation and Discussion. Translation's detection (delete and compare to the diff) catches the rule, with the Finding 5 gap.
- The "derived, not observed" rule is reached by Symptom's "traced in the code and marked as derived". The "(§2)" pointer is missing from the Translation item's second half only; this is cosmetic.

## Item 6: what the writer says it verified

- The commit message reports blind-draft counts per rule.
- It says the current open-question rule and the What-slot example were not re-run.
- The What-slot example is the part that fails Finding 1, and it is the part the message says was not re-run. That fits.
- No exemplar and bad case are named in the change for the Translation rule, only a rate ("persists in about one draft in two").

## Item 7: siblings of the change

- **Packages that carry this skill.** `git grep` finds no other package that copies it. The mentions are cross-references (`docs-page-authoring`, `problem-report-authoring`, the style packages). None restates the changed rules.
- **Set sizes.** No sentence counts the slots or the checklist items.
- **Consistency within the skill.** The Slot 2 skip condition, the changelog row 3 and §8 Symptom all use the new "audit or code reading" wording. The commit-body *Fixed* examples near line 487 were not changed, and I did not check them against the rule beyond a read.
- **Finding 2 above** is the one sibling gap: the commit-body shape has no place for the open question.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The What-slot *After* example puts the outcome in prose, translates ("it sends directly"), and its commentary says sentence 1 gives the `ensureOpen()` reason when sentence 2 does | Substantive | `SKILL.md` ~349 | Drop the outcome clause from sentence 1, state only the reason, remove "it sends directly", and rewrite the sentence after the example to match. Re-run the example against the Translation check. |
| 2 | The open-question rule names a Scope slot the commit body lacks | Taste | `SKILL.md` ~458 | Add a clause for the commit-body case. |
| 4 | "Over fifteen" drafts does not reconcile with the per-rule counts | Taste | commit message | Say how the 15 is made up. |
| 5 | Translation check can delete the only reason-stating sentence | Taste | `SKILL.md` §8 | Add "keep the sentence that states the reason". |
| — | "where a user did not observe it" for the audit rule | Taste | `SKILL.md` ~90 | Optional clause. |

Finding 3 is churn and I'm leaving it out of the table.

I did not run `make check`, `make check-descriptions` or any blind drafts. I did not fetch the pull request the drafts were written for. I did not load the repository's `apm-authoring` skill, and I did not review the wording for style beyond places where a sentence reads wrongly.
