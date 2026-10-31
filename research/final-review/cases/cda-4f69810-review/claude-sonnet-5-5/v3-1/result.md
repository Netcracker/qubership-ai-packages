# Final review: `d79c43d..4f69810` (change-description-authoring 1.4.0)

**Inputs.** I had no task statement, so the claimed cases come from the commit message alone. This is a change with no code: it edits a skill, its README, and version fields. §2a applies and I used its analogues under every item. I did not run `comment-drift.py`, because there are no members to parse. I loaded `english-developer-style` from the given skills directory. I did not load `apm-authoring` or `docs-page-authoring`, because they are not among the three permitted copies. There is no previous report.

## Item 1: comments consistent with the code and with each other
*Analogue: statements the changed files make about each other and about the repository.*

- **Versions.** 1.3.0 → 1.4.0 appears in `agent-packages/change-description-authoring/apm.yml`, root `apm.yml:168`, and `.claude-plugin/marketplace.json:291`. All three agree, and no `1.3.0` for this package is left (`git grep`).
- **Cross-references.** "§7 points to this rule" holds: the added line at SKILL.md:~760 cites "§2, the What slot". The new `(§5)` for public identifiers matches the existing §5 trailers section.
- **Skip column vs prose.** The slot 2 skip cell (line 81), the slot 2 prose (lines 90-96), the changelog part 3, and the §8 Symptom item all say the same thing about audit-found defects. None of them contradicts another.
- **Finding A (substantive).** The new What-slot *After* example (SKILL.md ~352-355) puts an outcome in prose: "a caller that runs before startup completes fails at once instead of opening the pool on demand".
  - The sentence that follows says the early caller's `IllegalStateException` "is an outcome, and it goes on its own line".
  - Line 130 says outcomes are kept out of slot 3 paragraphs and put on their own line.
  - The commit message says the example "no longer puts an outcome in prose".
  - A reader of the example gets two places for the same outcome. A drafting agent copying the *After* will repeat the outcome in prose.
  - The request is to reword the first sentence to carry the reason only, for example "The pool opens at startup, so the on-demand opening is unnecessary."
- **Finding B (taste).** Lines 93-96 say "neither is the absence of one", and then "a stated absence does not [look like an omission]" for the by-construction case. Both are correct, because the second is scoped to by-construction defects. A reader skimming could take it as a contradiction. I would add "only" or "there" before the by-construction case. Expect this to be declined.
- **Narration.** There is no "now" or "no longer" narration of the change. The "now gets" in the example describes the example's code, not this change.

## Item 2: claimed cases covered
*Analogue: each claimed rule against the section that handles it, plus the check that detects it. The commit message is the only source.*

| Claim | Section that handles it | Checklist item |
| --- | --- | --- |
| Audit-found defect: name what found it | slot 2 prose + skip cell + changelog part 3 | Symptom |
| Derived consequence traced and marked as derived | slot 2, second paragraph | Symptom |
| "Say so" kept for no-symptom-by-construction | slot 2 prose | Symptom |
| What slot: hunk translation, identifiers named once | What-slot paragraph + Before/After | Translation; §7 pointer |
| Rejected alternative as a fact about merged code | alternatives paragraph | Alternatives |
| Open question answered, kept, or dropped | new Scope paragraph + Scope table cell | Discussion |
| §2 asks for "what changed that the diff does not show" | "A reviewer decides" paragraph | none, which is fine |

- **Commands.** The changed files tell the reader to run none.
- **Hunk-to-claim.** Every hunk belongs to a commit-message sentence, including the README paragraph and the version bumps.
- **Finding C (taste).** The commit message says "Over fifteen blind Opus drafts". Its own breakdown (2 + 10 + 2, then 4 and 3) cannot be reconciled with fifteen from the text. I could not check this. Counts and measured claims in the SKILL ("two of two", "three of three") do match the commit message.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the claimed situations, the negative control, and the state left by the earlier version.*

- **Instruction table.** The change adds or widens five instructions.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it and stop | A defect found by a failing test or a user report | — | "Where reading the code or an audit found the defect" |
| Trace a derived consequence and mark it | A defect whose symptom was observed and quoted | — | "A consequence derived from the code earns a sentence only after…" |
| Translation: delete What-slot sentences the diff already says | A change whose diff is unreadable, such as a generated file or a huge rename | A one-line What that tells the reviewer nothing | Not addressed by the text; it is the existing "diff" assumption, so taste |
| Name a public identifier once | A private identifier or a test name | — | "A public identifier the change adds, removes, or renames (a system property, a flag, an option)" |
| Open question: answer, keep in Scope, or drop | A change with no discussion or review thread | — | "A question the issue or the review left open" |

- **Negative controls for the open-question rule and the What example.** The commit message says openly that the final open-question rule and the What-slot example were not re-run. These are two instructions with no evidence in the change.
  - **Finding D (substantive).** Evidence is missing for the final open-question rule and the What-slot example. The request is a blind draft with each, or a sentence in the commit body accepting the gap. The disclosure in the commit message is honest, so this is a request and not a defect.
- **Previously deployed state.** None applies. The edit is to a skill text, and the version bump is the only upgrade surface.
- **Limits and replaced mechanisms.** None.

## Item 3a: level, placement, and the environment
*Analogue: which file holds each rule, layout against siblings, and the registration entries.*

- The rules sit in the single SKILL.md where the sibling rules live. The README gets the user-facing summary.
- I did not run `make check`, because it needs `uvx` and network access. A manual check of the version fields in `apm.yml` and `marketplace.json` shows they are in sync, and the SKILL `description` field is untouched. The description check is therefore not triggered.
- **Finding E (taste).** SKILL.md has a short, awkward wrap ("wanted. Leave" then a new line, in the open-question paragraph). It is cosmetic.

## Item 4: names by content, not by position
*Analogue: the change's own headings and cross-references.* None. The change's references are by section number (§2, §5, §7), which is the document's own convention. The new checklist items are named by content ("Translation", "Discussion").

## Item 5: the failure report
*Analogue: the detection each rule offers.*

- Symptom, Alternatives, Translation, and Discussion each end in a question a reader can answer from the text.
- The Translation check ("delete each sentence in turn") detects the rule it is attached to.
- **Gap.** The new instruction "identifier named once" has no detection of its own. Because the Translation item covers it only indirectly, I rate this taste.

## Item 6: what the writer says it verified
*Analogue: an exemplar that passes and a bad case that fails.*

- The commit gives measured drafts for the symptom rule (both predicted a failure without it, five of ten claimed absence under the ban, none of two with the final wording), the retold-obstacle rule (2/4 → 0/4), and the open-question rule (3/3 → 0/4).
- It also says hunk translation "persists in about one draft in two".
- The new *After* example is not stated to pass the new Translation check. By Finding A, it carries an outcome in prose.
- No input where the added item is noise is stated for any of the five instructions, such as a defect with an observed symptom. The table in item 3 supplies the rows, and the text of each rule ends it for that input.

## Item 7: siblings of the change
*Analogue: places that enumerate or route to the skill, and sets whose size changed.*

- **Skill index.** `apm.yml`, `marketplace.json`, and the package `apm.yml` are all updated.
- **Other references.** The other references to this skill in `english-developer-style`, `docs-page-authoring`, and the style instructions only name the skill. None of them states a rule this change alters.
- **README bullet.** It carries the new rules, so the README is in sync.
- **Counts.** The slot counts ("Five slots", "Six slots") are unchanged, and the new checklist items do not change any stated count. The commit message says "new Discussion and Translation items", and the checklist gained exactly those two.
- **Research directory.** `research/` was not touched. The commit states that this skill has no cases there.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| A | The *After* example puts an outcome in prose, which contradicts line 130, the following sentence, and the commit message | Substantive | SKILL.md ~352-355 | Reword the first sentence to carry the reason only, and leave the early caller's failure to the "User-visible changes" line |
| D | The final open-question rule and the What-slot example have no draft run | Substantive | commit body; SKILL.md Scope paragraph and What-slot example | A blind draft with each, or a sentence in the commit accepting the gap |
| B | "Neither is the absence of one" sits next to "a stated absence does not [look like an omission]" | Taste | SKILL.md 93-96 | Scope the second sentence to the by-construction case explicitly |
| C | "Over fifteen" drafts cannot be tallied from the commit's own breakdown | Taste | commit message | State the count per rule |
| E | Short wrap, "wanted. Leave" | Taste | SKILL.md open-question paragraph | Re-wrap |

**Not checked:** I did not run `make check` or any gate (no network), I did not run the drift script (no code), and the prose was not reviewed for style. The `apm-authoring` rules were not applied, since that copy was not among the three allowed. The claimed counts of blind drafts could not be verified.
