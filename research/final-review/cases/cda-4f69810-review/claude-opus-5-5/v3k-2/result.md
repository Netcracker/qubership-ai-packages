I found no blocking defect, but there are eight substantive requests. The commit adds three rules to the `change-description-authoring` skill (audit-found defects, hunk translation in the What slot, open questions). In several places the checklist or the README states those rules differently from the rule text, so an agent checking against §8 would reach a different result. The most consequential: the What slot's own *After* example breaks the "not restated in slot 2" rule (line 231), and the Translation checklist item deletes the identifier sentence the new rule says to keep.

# Final review: `d79c43d..4f69810`, "stop drafts from inventing symptoms and translating hunks"

**Inputs.** There was no task statement. The claimed cases come from the commit message alone. The change has no code: it touches a skill, a package README, and three version manifests. So the form was filled through the §2a analogues, with `english-developer-style` and `apm-authoring` loaded. `apm-authoring` came from the repository's package copy, because it is not one of the three skills I was given. The drift script was not run, because the change has no members to parse. There was no previous report. Paths below are relative to `agent-packages/change-description-authoring/`, with `SKILL.md` meaning `.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

*Analogue used: statements one file makes about another, and worked examples against their own rules.*

- **The What-slot *After* example breaks the rule stated a few lines earlier (`SKILL.md:353`).** The example says "a caller that runs before startup completes fails at once instead of opening the pool on demand".
  - That is what the caller observes, plus the condition. The paragraph under it (`:357-359`) calls it an outcome that belongs under "User-visible changes".
  - `:231` says "A fact stated in slot 3 is not restated in slot 2".
  - The commit message also says the example "no longer puts an outcome in prose". That holds for the `IllegalStateException` text but not for the behavior.
  - An agent that copies the canonical example restates the outcome in prose.
- **The README drops the exception the skill keeps (`README.md:29`).** It says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen".
  - `SKILL.md:98-101` allows a consequence derived from the code, once it is traced to the caller and marked as derived. That is a prediction.
  - A reader who knows the package from its README would cut a sentence the skill permits.
- **The Translation checklist contradicts the rule it checks (`SKILL.md:826`).** It says "delete each sentence… where the diff still says it, leave it deleted". The rule has two differences:
  - The rule (`:342`) is about sentences recoverable from *one hunk*. The checklist covers anything the diff says, which includes a synthesis across hunks.
  - The rule exempts a public identifier that is added, removed or renamed (`:345-347`). Under the checklist, the sentence naming a renamed system property is still in the diff, so it gets deleted.
  - The commit message says drafters check against §8, not §2, so this checklist wording is what agents will apply.
- No sentence narrates the change ("now", "no longer") outside a measured note. Cross-references `§2, slot 2`, `§5` and `§7` resolve to the right sections. The measured counts at `:100-101` and `:464` match the commit message.
- Formatting (taste): `:463` is a stray short line, "wanted. Leave", in the middle of a paragraph.

## Item 2: claimed cases covered

| Claim (commit message) | Section that handles it | Detection (§8) |
| --- | --- | --- |
| Slot 2: an audit-found defect is described by what found it | `:91-95` | Symptom item, `:803-806` |
| Changelog names only the condition | table row 3, `:475` | **none**: the Changelog item at `:842` still lists "symptom" without qualification |
| Derived consequence only when traced and marked as derived | `:98-101` | Symptom item |
| "Say so" kept for a defect with no symptom by construction | `:95-97`, table `:81` | Symptom item |
| What slot: a one-hunk sentence is translation; public identifier named once | `:342-347`, example `:350-359` | Translation item, which differs from the rule (Item 1) |
| §7 points to the What-slot rule | `:763-764` | n/a |
| §2 asks for "what changed that the diff does not show" | `:288` | n/a |
| Rejected alternative stated as a fact about the merged code | `:370-374` | Alternatives item, `:832-833` |
| Open questions answered, kept in Scope, or dropped | `:458-464`, table `:199` | Discussion item, `:834-837` |
| Slot 2 and What rules each carry a bad and a good example | `:92-93`, `:350-355` | n/a |
| "This skill has no cases under research/" | Verified: `research/change-description-authoring/` has phase files but no `cases/` directory, unlike three sibling research directories | n/a |

- **The changelog rule has no checklist item.** The commit says "each fix … has a checklist item". `:842` asks for "symptom" in every entry, which pushes the writer to invent one for an audit-found defect.
- **Commands.** The changed files add no commands.
- **An unclaimed hunk.** The version bump 1.3.0 → 1.4.0 in `apm.yml`, the root `apm.yml` and `.claude-plugin/marketplace.json` has no sentence in the commit message. The two previous commits in this package each carry "Version 1.x.0 to 1.y.0".

## Item 3: boundaries, partitions, and the negative control

*Analogue used: the genres and situations the change claims, and the instructions table.*

- **Partitions with no evidence.** All the evidence comes from drafts of *one PR description*. So the commit-body slot 2 and the changelog's "condition alone" rule were never exercised. The commit message itself says the current open-question rule and the rewritten What example were not re-run.
- **Two rules conflict on the same input.**
  - `:461` puts a question only a maintainer can settle "in the Scope slot".
  - In a repository where §4 rule 5 applies, the description is the commit body: it takes the body's slots, which have no Scope slot, and must "keep reviewer-only content out of it" (`:600+`, rule 5).
  - The open-question rule has no clause for that case, so a question addressed to the maintainer ends up in the permanent commit.
- **Pre-existing state.** None applies: this is a skill text with no persisted format.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:92` "name what found it and end the sentence there", and `:475` "the condition alone" | audit-found defect that a later failing test reproduced, with a logged error | only "An audit found this"; changelog has no greppable diagnostic | "unless a run has since reproduced it; then quote what it printed" |
| `:342` "a sentence … recovers from one hunk … is translation" | one-line change of a default value that is the whole behavioral change | cuts the only statement of the behavior; conflicts with `:361` "Keep a specific value" | "except the behavioral change itself, stated as what callers get" |

Not findings: `:98` "only after it is traced", `:345` "is the exception: name it", `:371` "stated as a fact about", `:288` "that the diff does not show".

## Item 3a: level, placement, and the environment

None. The rules sit in the slot sections they modify, with checklist items in §8, matching how earlier versions laid out their rules.
- `make check` passed (rc=0; versions are aligned and the index is in sync).
- `make check-descriptions` passed: all 27 descriptions are within 1020 characters.
- The paired instruction file and the package `description:` are unchanged, which fits: the trigger surface did not widen.

## Item 4: names by content, not by position

None. The new text refers to sections and slots by number plus name ("§2, slot 2", "the What slot", "§4 rule 5"), as the rest of the file does. Its examples are named by content.

## Item 5: the failure report

*Analogue used: each detection checks the rule it is attached to.*

- **The Symptom item checks something weaker than the rule.** It asks "does the sentence end at what found it?" (`:805`). A draft that writes "An audit found this." followed by a separate sentence, "No failure has been observed.", passes it.
  - That is the exact failure the commit reports: five of ten drafts stated the absence, in four wordings.
  - The rule text at `:94` ("neither is the absence of one") covers it; the detection does not.
- **Two other detections differ from their rules.** The Translation item (Item 1) and the Changelog item (Item 2).
- **The new rules are all reached by the checklist.** Discussion, Alternatives and Symptom cover them.

## Item 6: what the writer says it verified

- **Stated.** For the slot-2, alternative and open-question rules, the commit names measured before/after counts from 15 blind Opus drafts, plus a bad and a good example for slot 2 and the What slot.
- **Not stated.**
  - The rewritten open-question rule and the rewritten What example were not re-run; the commit says so.
  - There is no noise-input check: no evidence that a description with no audit, no open question and no rejected alternative did not grow.
- **The rules re-applied to the change's own examples.**
  - Slot-2 *After*: passes.
  - What-slot *After*: passes Translation, but fails `:231` (Item 1).
  - The commit message's own claim "persists in about one draft in two" leaves the Translation rule's effect only partly shown.

## Item 7: siblings of the change

- **Places that list the package.** `apm.yml`, `marketplace.json` and the package `apm.yml` carry the new version, and no other file pins one. Package descriptions are unchanged, so the descriptions in `problem-report-authoring/README.md`, `docs-page-authoring/README.md` and the other packages that mention this one need no change.
- **The same defect elsewhere.** `problem-report-authoring/SKILL.md:90` requires "Open with the user-facing symptom" with no case for a defect an audit or a code reading found. An issue filed from an audit meets the same pressure to invent a symptom.
  - The change neither fixes this nor names it as a follow-up.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| What *After* example restates the outcome in slot 2, against "not restated in slot 2" | Substantive | `SKILL.md:353`, `:231` | Recast the first sentence as the boundary ("the pool opens at startup, not on first use") and leave the early-caller failure to the User-visible line; correct the commit-message claim |
| Translation checklist deletes what the diff says, so it also removes the exempt public identifier and cross-hunk syntheses | Substantive | `SKILL.md:826` | Say "recoverable from one hunk" and add "except a public identifier named once" |
| Symptom checklist passes a stated absence written as a separate sentence | Substantive | `SKILL.md:805` | Ask whether slot 2 says anything about failure beyond what found it, other than a traced, marked consequence |
| Changelog "condition alone" rule has no checklist item; `:842` still asks for a symptom in every entry | Substantive | `SKILL.md:475`, `:842` | Add "or the condition alone, for an audit-found defect" |
| A defect that was audit-found and later reproduced loses its observed diagnostic | Substantive | `SKILL.md:92`, `:475` | Clause: "unless a run has since reproduced it; then quote what it printed" |
| One-hunk translation rule cuts a one-line behavioral change; conflicts with "Keep a specific value" | Substantive | `SKILL.md:342`, `:361` | Clause: "except the behavioral change itself, stated as what callers get" |
| Maintainer-only question goes to the Scope slot even when the description is the commit body (§4 rule 5) | Substantive | `SKILL.md:461`, `:834-837` | Clause: "under §4 rule 5, in a review comment instead" |
| README rules out any predicted failure; the skill allows a traced, marked one | Substantive | `README.md:29` | Add "unless traced to the caller and marked as derived" |
| Version bump 1.3.0 → 1.4.0 in three files has no sentence in the commit message | Substantive | `apm.yml:2`, root `apm.yml:168`, `marketplace.json:291` | Add "Version 1.3.0 to 1.4.0." as in the two previous commits |
| Changelog and commit-body partitions, and the rewritten rules, have no draft evidence; no noise-input check | Substantive | commit message | A run on a changelog entry and on an input where the new items are noise, or a sentence that says these were not checked |
| `problem-report-authoring` opening rule meets the same audit-found case | Substantive | `problem-report-authoring/.../SKILL.md:90` | Fix it in this change, or name it as a follow-up in the message |
| Stray short line "wanted. Leave" | Taste | `SKILL.md:463` | Rewrap the paragraph |

Not checked: I did not re-run any blind drafts, did not do a pass over the wording for style alone, and did not run the round-trip `make test`.
