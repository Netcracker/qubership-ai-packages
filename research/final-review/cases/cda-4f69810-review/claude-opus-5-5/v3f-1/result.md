# Final review: `d79c43d..4f69810`, one commit (change-description-authoring 1.4.0)

There was no separate task statement, so item 2 takes its claimed cases from the commit message alone. The change has no code: it touches a skill (`SKILL.md`), the package README, and three version fields. Every item below uses the §2a analogue. I did not run the drift script, because there are no members for it to parse. I loaded `english-developer-style` from the given directory and `apm-authoring` from `agent-packages/apm-authoring`. No previous report exists.

## Item 1: comments consistent with the code and with each other

Analogue used: statements one file makes about another, and the worked examples.

- **What-slot example against the slot 3 rule.** Line 231 says "A fact stated in slot 3 is not restated in slot 2." The *After* at 353–355 states "a caller that runs before startup completes fails at once instead of opening the pool on demand" in What-slot prose. Then 358–359 sends the same outcome (`IllegalStateException` from `Pool.acquire()` for an early caller) to "User-visible changes". The commit message also says the example "no longer puts an outcome in prose", which is false for its first sentence: only the exception class moved. A reader will copy the example and restate the outcome in both slots.
- **Slot 2 contradicts itself.** Lines 91–94 say "name what found it and end the sentence there" and "A predicted failure is not known". Line 98 then allows "a consequence derived from the code" once it is traced and marked as derived. The README (lines 28–29) settles the conflict one way, "with neither a predicted failure nor a claim that none was seen", and so drops the traced-consequence permission. A writer cannot tell whether an audit-found defect may carry a traced consequence.
- The checked cross-references hold:
  - "§7 points to this rule" holds at 763–764.
  - "§2 asks for 'what changed that the diff does not show'" holds at 288.
  - The Scope row at 199 matches 458–465.
  - Changelog part 3 at 475 matches slot 2.
  - No narration of the change (`now`, `no longer`) appears outside the examples.

## Item 2: claimed cases covered

Analogue used: claimed cases against the section that handles each and its checklist detection.

| Claim in the commit message | Section | Detection |
| --- | --- | --- |
| Audit or code-reading defect: name what found it, end the sentence | 81, 91–93 | Symptom at 803 |
| Changelog names the condition alone | 475 | **none**: Changelog at 842 asks for "symptom" |
| Derived consequence traced and marked derived | 98–101 | Symptom at 803 |
| "Say so" kept for no symptom by construction | 94–96 | Symptom at 803 |
| Hunk translation, even under a reason lead-in | 342–347 | Translation at 826 |
| Public identifier named once | 345–347 | **contradicted** by Translation at 826 (item 5) |
| §7 points here; §2 "does not show" | 763, 288 | n/a |
| Alternative is a fact about the merged code; a removed obstacle is a step | 370–373 | Alternatives at 832 |
| Open question answered, kept in Scope, or dropped | 199, 458–465 | Discussion at 835 |
| Bad and good example for slot 2 and the What slot | 92–93, 349–355 | n/a |

- **Commands:** none in the changed files.
- **Unclaimed hunks:** the version bump 1.3.0 → 1.4.0 in `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and `agent-packages/change-description-authoring/apm.yml:2`. No sentence of the message claims it. The previous commit's message did ("Version 1.2.0 to 1.3.0.").
- "This skill has no cases under research/" is true: `research/change-description-authoring/` holds phase prompts and results, not a `cases/` directory.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the genres and situations the change claims, and the instruction table.

- **Partitions without evidence.** The trial drafted one pull request description. The change also claims the commit body (row 81) and the changelog entry (row 475), and neither has evidence.
- **Negative control.** Item 6 covers the missing check on an input where the new rules are noise.
- **State from an earlier version:** none applies. An `apm install` replaces the skill text and leaves nothing behind.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it, end the sentence; changelog has the condition alone (91–93, 81, 475) | Audit-found defect whose regression test reproduces the exception | "An audit of X found this."; the exception text R3 greps disappears from the body and the changelog | "where no test, run, or report has since shown its symptom" |
| A sentence recoverable from one hunk is translation (342–347) | A dependency bump or a raised default, where the value decides compatibility | Deletes the sentence carrying the version; conflicts with "Keep a specific value" (361) | "…or a value the decision depends on (below)" |
| Keep a maintainer-only question in the Scope slot (458–463) | A description that §4 rule 5 makes the commit body | A review question left permanently in `git log`; conflicts with 267–269 "never in a description that … will copy into the commit body" | "or in a review comment where §4 rule 5 makes the description the commit body" |

Not findings:
- The traced derived consequence is ended by "earns a sentence only after it is traced to the point where a caller sees it".
- The rejected-alternative rule is ended by "An obstacle the change itself removes".
- "Say so" is ended by "no symptom by construction".

## Item 3a: level, placement, and the environment

- **Placement:** none. Each rule sits in the section it governs, the checklist items sit in §8, and the README feature list is updated in place.
- **Registration:** the version is aligned at 1.4.0 in all three manifests, checked by grep. I did not run the repository gate (`make check`, which runs `apm pack --check-versions`) because it runs through `uvx` and there is no network. The skill's `description:` is unchanged, so `check-descriptions` is unaffected.
- **Tutorial-level sentences:** none found.

## Item 4: names by content, not by position

- None substantive. The `slot 2` and `§2, slot 2` references follow the file's existing numbered-slot convention, defined by its tables.
- Taste: line 357 says "the first sentence says why". It could name the sentence ("the startup sentence").

## Item 5: the failure report

Analogue used: whether each rule's checklist detection detects that rule.

- **The Translation detection detects a weaker property than its rule.** Line 826 says "where the diff still says it, leave it deleted". That deletes the sentence naming a new public identifier, which 345–347 says to keep ("name it once"). Request: add "unless it names a public identifier the change adds, removes, or renames" to 826.
- **No detection reaches changelog part 3's "condition alone".** The Changelog checklist item at 842 still asks for "symptom".
- The Symptom, Alternatives, and Discussion items reach their rules.

## Item 6: what the writer says it verified

The message states the following:
- Measured counts for each defect, before and after.
- The drafts ran against 1.0.1, before the outcome-slot and length rules landed.
- The current open-question rule and the What-slot example were not re-run.

Missing:
- A run on the current text.
- An input where the added items are noise, with a check that the output did not grow. Examples: a fix reported by a user with an observed symptom, or a pull request with no open discussion.

The counts also don't add up: "Over fifteen blind Opus drafts", but the symptom arms total 2 + 10 + 2 = 14. They may overlap; the message does not say.

## Item 7: siblings of the change

Analogue used: places that list or point to this skill.

- **None.** The umbrella `qubership-repo-essentials` depends on `../change-description-authoring` with no version and a description that still holds.
- The cross-references in `english-*-developer-style`, `docs-page-authoring`, `problem-report-authoring`, and `test-authoring` name the skill's scope, which did not change.
- `problem-report-authoring` §6 (observed, inferred and marked) agrees with the new derived-consequence rule.
- No set gained a member, and no count sentence changed.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| What-slot *After* restates the early-caller failure that 358–359 sends to slot 3, against line 231; the commit message says the example has no outcome in prose | Substantive | SKILL.md:353–359, 231 | Make the *After* carry only what the diff and slot 3 do not, or say at 231 how the behavioral boundary in What differs from the outcome line |
| Slot 2 says "end the sentence there" and "A predicted failure is not known", then allows a traced derived consequence; README forbids any predicted failure | Substantive | SKILL.md:91–101; README.md:28–29 | One clause linking the two paragraphs (a traced consequence may follow in its own sentence), and the README aligned with it |
| Audit rule drops a symptom that a test or run later showed | Substantive | SKILL.md:81, 91–93, 475 | Add the clause "where no test, run, or report has since shown its symptom" |
| Translation checklist deletes the public identifier the rule keeps | Substantive | SKILL.md:826 vs 345–347 | Add the identifier exception to the checklist line |
| Translation rule conflicts with "Keep a specific value" on a version or threshold hunk | Substantive | SKILL.md:342–347 vs 361 | Add an exception for a value the decision depends on |
| Maintainer-only question kept in Scope conflicts with no reviewer content in a description that §4 rule 5 makes the commit body | Substantive | SKILL.md:458–463 vs 267–269 | Name where the question goes under §4 rule 5 |
| Changelog "condition alone" has no checklist detection, and the Changelog item asks for a symptom | Substantive | SKILL.md:475, 842 | Extend the Changelog checklist item |
| Evidence covers PR descriptions on 1.0.1 only; no commit-body or changelog drafts, no noise-input control, current open-question and example wording not run | Substantive | commit message | A run of the current text on a commit body and a changelog entry, plus one input where the new items are noise, with the word count compared |
| Version bump in three files claimed by no sentence | Substantive | marketplace.json:291, apm.yml:168, package apm.yml:2 | One sentence: "Version 1.3.0 to 1.4.0." |
| "Over fifteen" drafts, but the symptom arms total 14 | Taste | commit message | State how the drafts split across arms |
| Stray short line "wanted. Leave" | Taste | SKILL.md:463 | Rewrap the paragraph |
| "the first sentence" refers by ordinal | Taste | SKILL.md:357 | Name the sentence by its content |

Not checked: no draft was run against the skill, the `make check` and `make test` gates were not run (no network for `uvx`), the drift script was not run (no code), and the prose was not reviewed for style alone.
