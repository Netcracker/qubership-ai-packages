I've read the whole diff and run the checks, and I'm now writing the report. The change is a skill edit, so I used the no-code analogues in §2a.

# Final review: `d79c43d..HEAD` (commit 4f69810)

**Inputs.** There is no task statement. The claimed cases come from the commit message alone, so item 2 rests on that. This is the first report over this change.

**Skills loaded.** I read `final-review` and skimmed `english-developer-style`, as the form allows. This is not a code change, so I did not load `test-authoring` or a doc-comment skill. I did not read `apm-authoring` and cite no rules from it. The report does not apply `english-developer-style`.

**Drift script.** I ran it and it printed nothing, because it does not parse Markdown or YAML. The analogue used is a manual check of every statement the changed files make about each other.

## Item 1: comments consistent with the code and with each other (analogue: cross-statements)

- **Finding (substantive).** `SKILL.md:353-359`, the What-slot *After* example, breaks the rule it illustrates, in two ways.
  - Its second sentence reads "with the pool open from startup it sends directly". That is "Y now calls Z", which the new rule at lines 342-347 calls translation "even under a lead-in that states a reason". The reviewer recovers it from the one `sendWithRetry` → `sendDirect` hunk.
  - Its first sentence puts an outcome in prose: "a caller that runs before startup completes fails at once". The note under the example says that outcome is the `IllegalStateException` and belongs under "User-visible changes". The skill also says "A fact stated in slot 3 is not restated in slot 2" (about line 222).
  - A reader who copies the exemplar reproduces both defects. The commit message says the example "no longer puts an outcome in prose", and that is false of the text.
  - The note under the example also says the first sentence "says why they are no longer needed". The first sentence gives the startup change and an outcome, not why the `ensureOpen()` calls became unnecessary.
- Other cross-references check out. §5 is "Trailers and the identifiers a reader greps", §7 is "When to write nothing", and the checklist is §8. Pointers to "§2, slot 2" and "§2, the What slot" resolve.
- Slot 2's skip cell (line 81), the Slot 2 prose (lines 90-96), the changelog row 3 and the checklist Symptom item agree. No other place says "has not been seen" or "no symptom" in a way that conflicts.
- Narration of the change (`now`, `no longer`, `used to`): none in the added prose. The *Before* examples use "now" deliberately as the bad case.
- The README bullets say the same as the skill, with one gap. The README says a hunk sentence "is cut even when it carries a decision; its reason stays", and omits the skill's exception for a public identifier. I label this taste.

## Item 2: claimed cases covered

Claims from the commit message, each with the section that handles it:

| Claim | Where handled | Detection |
| --- | --- | --- |
| Slot 2: an audit or code-reading defect is described by what found it | Lines 81, 90-96 | Checklist Symptom (lines 802-806) |
| Slot 2: a derived consequence is traced and marked as derived | Lines 98-101 | Checklist Symptom |
| "Say so" kept for a defect with no symptom by construction | Lines 81, 94-96 | Checklist Symptom |
| Changelog entry names the condition alone for an audit-found defect | Changelog row 3 | **None** (see below) |
| What slot: hunk sentences are translation; identifiers are named once | Lines 342-347 | Checklist Translation |
| §7 points to the What-slot rule | Lines 760-763 | Pointer present |
| §2 asks for "what changed that the diff does not show" | Line 288 | Present |
| Rejected alternatives: mechanism is a fact about the merged code; a removed obstacle is a step taken | Lines 368-372 | Checklist Alternatives |
| Open questions: answered, kept in Scope, or dropped | Scope row, lines 458-465 | Checklist Discussion |
| Checklist: Symptom and Alternatives extended, Discussion and Translation added | §8 | Present |

- **Finding (taste).** The changelog-entry change has no example, and the only changelog *After* example is unchanged. The checklist Symptom item does not mention changelog entries either. Nothing lets a reader tell whether a changelog entry for an audit-found defect obeys the rule.
- Every hunk belongs to a sentence of the commit message. The version bumps to 1.4.0 in `apm.yml` (package and root) and in `marketplace.json` are not mentioned in the message, but they follow the repository's pattern for a minor bump. I noted this and did not file it.
- The commit message reports measurements, and they are not backed by anything in the repository. The text says "measured: two of two drafts", and the commit gives "none of two" for the final symptom wording. Two drafts is a thin basis, and the commit says as much. The skill text states "three of three" in the Discussion rule, which matches the commit. I did not ask for more; the figures are the writer's to state.
- No command lines are given in the changed files.

## Item 3: boundaries, partitions, negative control (analogue: genres, modes, situations)

The table of added instructions follows. Each row quotes the instruction and fills the other columns from its text.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "for a defect an audit or a code reading found, the body names what found it" (line 81) | A defect found by an audit that also reproduced, so a real symptom exists | "An audit of the retry paths found this." The observed symptom is dropped, though R3 needs it | None. The condition does not cover a defect that an audit found and someone then observed. Request: add "and no symptom was observed" or "only where no observation exists". |
| "A consequence derived from the code earns a sentence only after it is traced to the point where a caller sees it" (lines 98-101) | A one-line fix whose consequence is obvious (a typo in an error message) | A tracing paragraph with "derived" labels for a trivial change | The text does not end it. Taste; no reader of the skill is likely to meet this. |
| "a sentence whose content the reviewer recovers from one hunk … is translation" (lines 342-347) | A one-hunk change where the hunk is the whole change (a flag default flipped) | The What slot is deleted and nothing remains but the reason | The Why slot and the "public identifier" exception partly cover it. Taste. |
| "name it once" for a public identifier (lines 345-347) | An identifier already named in the title and the Why slot | A third mention in What | "name it once" ends it, but the slot is unspecified. Taste. |
| "An obstacle the change itself removes is a step … not a reason against the alternative" (lines 368-372) | A change whose alternative is rejected for a reason that predates it and still holds | The writer may wrongly drop a real obstacle | "check the mechanism against the code after the change" ends it. No finding. |
| Open-question rule (lines 458-465): "answered, kept in Scope, or left out" | A question that a maintainer settled in the thread itself | A Scope entry for a question already closed | "Where … another source you verified answers it" ends it. No finding. |

- **Finding (substantive).** Row 1 above (audit-found defect that was also observed).
- **Finding (taste).** The commit admits that the current open-question rule and the What-slot example were not re-run. The example is the one found defective in item 1, so the unrun parts include the failing one. The final symptom wording has two drafts of evidence and the hunk-translation rule still fails in about half of drafts. I accept that these are stated limits.
- Pre-existing state: the skill is installed over version 1.3.0. The README, `apm.yml` and `marketplace.json` agree on 1.4.0. The frontmatter has no version, so nothing else holds one.

## Item 3a: level, placement, and the environment

- The new rules sit in the sections where the sibling rules for the same slot already live, so placement is right. The checklist gained its entries in §8 beside the existing ones.
- Registration: `apm.yml` and `marketplace.json` are updated together. `grep` for the old `1.3.0` finds only other packages. I did not run a gate script.
- Line length: added prose lines are within 120 columns. The few longer lines in the file are table rows or were already present.

## Item 4: names by content, not by position

none. The new headings and references use content ("the What slot", "slot 2", §5, §7, §8). "Slot 2" and "slot 3" are existing ordinals the skill itself defines as a table, so I did not file them.

## Item 5: the failure report (analogue: what the rule tells the reader to look at)

- **Finding (substantive, merged with item 1).** The Translation checklist item ("delete each sentence of the What slot in turn; where the diff still says it, leave it deleted") run on the *After* example deletes "with the pool open from startup it sends directly". The example fails its own detection.
- The Symptom item checks the rule it is attached to, and so do Alternatives and Discussion. No weaker property is detected.

## Item 6: what the writer says it verified

The commit carries blind-draft counts per defect (see item 2). It names no passing exemplar and failing bad case for each new rule. It states that the open-question rule and the What-slot example were not re-run, and that this skill has no cases under `research/`. So the rules' ability to fail is evidenced for the symptom and obstacle rules only, and the example in item 1 shows the gap. I did not run the suite or any drafts.

## Item 7: siblings of the change

- Places that list the skill: `.claude/rules/english-developer-style.md` and `.cursor/rules/english-developer-style.mdc` only name it. `docs-page-authoring` names it as owner of the changelog entry. None of them describe the changed rules, and none count slots or rules.
- The skill's own sibling sites for the symptom rule are the commit-body table (line 81), the Slot 2 prose, the changelog row 3, and the checklist. All were updated. The commit-body *Why*-equivalent in the pull-request table (line 195) says "The problem, the symptom, the condition that reaches it" and does not carry the audit-found exception. A pull-request description writer reading only that row gets the old rule. I label this substantive: the row for the artifact where the drafts were written says the opposite of the new rule.
- Searching the prose for the old size of the sets: "Five slots" and "Six slots" are unchanged and the counts still match their tables. No sentence counts the checklist.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The What-slot *After* example contains hunk translation ("it sends directly") and an outcome in prose ("fails at once"), against the rule and the Slot 2/3 no-restating rule | Substantive | `SKILL.md:353-359` | Rewrite *After* so every sentence passes the Translation check, and fix the note's claim about the first sentence |
| The pull-request Why row says "the symptom" with no audit-found exception | Substantive | `SKILL.md:195` | Add the same exception as lines 81 and 90-96 |
| Audit-found rule has no case for a defect that was also observed | Substantive | `SKILL.md:81` | Add a condition so an observed symptom is still quoted |
| Commit message says the example "no longer puts an outcome in prose", which is false of the text | Substantive | commit message | Correct the sentence when the example is fixed |
| No example or checklist detection for the changelog-entry change | Taste | `SKILL.md` changelog row 3, §8 | Add a short *After* line or extend Symptom to name changelog entries |
| README omits the public-identifier exception | Taste | `README.md` | Add the exception or leave it; both are right |

**Not checked.** I did not run any drafts, the repository's gates, or the drift script (it does not parse Markdown), and I did not review prose style beyond the places where a sentence reads wrongly.
