Final review of `d79c43d..HEAD` (commit `4f69810`), a no-code change that edits one skill, its README, and three version entries. I applied §2a: each item is read through its analogue, and the drift script (`comment-drift.py d79c43d HEAD`) printed nothing because no code changed. There is no separate task statement, so the claimed cases come from the commit message alone. I loaded `english-developer-style`. The skills `apm-authoring` and `docs-page-authoring` are not in the permitted directory, so I did not load them.

## Item 1: comments consistent with the code and with each other
Analogue used: statements the changed files make about each other.
- **Section references.** `§2, slot 2`, `§2, the What slot`, `§7`, `§5`, and `§3` all resolve. The commit-body bullet that now says "(§2, the What slot)" sits in §7, "When to write nothing", as the commit message says.
- **Counts.** The "Six slots" and "Five slots" counts are unchanged and still true. No sentence counts the checklist items.
- **Finding A (substantive).** The new audit and code-reading rule reaches the commit-body slot 2 and the changelog row 3, but not the pull request description's Why slot (`SKILL.md:195`; also `:319` and `:246`).
  - That slot says "The problem, the symptom, the condition that reaches it" and "has no skip condition".
  - The commit message says drafts invented symptoms in a *pull request description*, so this is the artifact the defect was seen in.
  - A drafter filling the Why slot reads a rule that demands a symptom, and the slot 2 exception is in another section.
  - Request: add the audit and code-reading clause to the Why slot's "Answers" cell, or point it at slot 2.
- **Finding B (substantive).** The new What-slot *After* example (`SKILL.md:~355`) states a caller-visible outcome in prose: "a caller that runs before startup completes fails at once instead of opening the pool on demand".
  - The paragraph right after it says the early caller's `IllegalStateException` "is an outcome, and it goes on its own line under 'User-visible changes'".
  - The commit message says this example "no longer puts an outcome in prose", and the example does exactly that.
  - Request: drop that clause from the example's first sentence, or reword it as the reason only ("the pool opens at startup, so the lazy open is gone").
- **Finding C (taste).** "An audit of the retry paths found this." has "this" with no antecedent in the example. A short noun phrase would fix it.
- No comment narrates the change.

## Item 2: claimed cases covered
Analogue used: the section that handles each claim, and the checklist item that detects it.

| Claimed case | Rule | Detection in the checklist |
| --- | --- | --- |
| Symptom for an audit-found defect | slot 2 and the changelog row | Symptom item |
| Derived consequence marked as derived | slot 2 paragraph | Symptom item |
| Hunk translation | What slot, §7 bullet | new Translation item |
| Public identifier named once | What slot | covered by the Translation item's "leave it deleted", but see Finding D |
| Rejected-alternative mechanism | "Rejected alternatives" paragraph | Alternatives item |
| Open questions | Scope paragraph and Scope table cell | new Discussion item |
| "Say so" kept for no-symptom-by-construction | slot 2 | Symptom item |

- **Finding D (taste).** The Translation checklist item says "delete each sentence ... where the diff still says it, leave it deleted". That conflicts with the exception that a public identifier is named once even though the diff shows it. The rule itself carves the exception out, so a drafter following only the checklist could delete the identifier. Add "except a public identifier (§2)" to the item.
- **Commands.** The changed files tell the reader to run no commands.
- **Hunk-to-claim.** The version bumps (1.3.0 to 1.4.0 in `apm.yml`, the package `apm.yml`, and `marketplace.json`) are not in the message. Earlier commits (`d79c43d`, `985bf80`) bump the same three files, so this follows convention. Label: taste.
- Every other hunk belongs to a sentence of the message.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the situations the rules cover and the control cases.
- **Partitions.** The changes cover an audit-found defect, an observed symptom, a no-symptom-by-construction defect, a retold obstacle, and an answerable versus maintainer-only question. Each has a stated treatment.
- **Evidence from drafts.** The commit message gives drafts for the symptom, obstacle, and question rules. It does not say that any draft exercised a no-symptom-by-construction defect, so the "say so" branch has no control.
- **Finding E (taste).** Add one control: a leak with no symptom, checking that the draft still says so.
- **Added-instruction table.** The non-serving input is chosen inside each instruction's own condition.

| Instruction | Input it does not serve | What an agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "name what found it and end the sentence there" | A defect found by an audit that also had a user report with a quoted log line. | Only "An audit found this", dropping the report's diagnostic. | Slot 2 already requires the diagnostic quoted as a literal for an observed symptom, so this is covered by the neighboring text. Not a finding. |
| "A consequence derived from the code ... earns a sentence only after it is traced" | A one-line fix where the consequence is obvious. | A traced chain longer than the fix. | "only where a caller would otherwise misjudge the risk". Label: taste. |
| "a sentence the reviewer recovers from one hunk is translation" | A one-hunk change. | An empty What slot. | The What slot's "Skip when" already says the problem statement makes the approach obvious. Covered, not a finding. |
| "an obstacle the change removes is a step ... check the mechanism against the code after the change" | A change whose alternative was rejected on cost, with no obstacle. | A check that finds nothing; harmless. | None needed. |
| "a question ... is answered, kept open, or left out" | A change whose discussion held no questions. | Nothing. | "absent when the discussion left no question" is implied. |

Pre-existing state: none, since this is not an install or upgrade path. The setting-reach, replacement-mechanism, and limit paragraphs of this item do not apply.

## Item 3a: level, placement, and the environment
Analogue used: which file each rule lives in and the registration entries.
- The rules sit in `SKILL.md`. The README summary and the three version entries are updated consistently at 1.4.0, matching the previous bumps. I did not run the repository's gate.
- **Finding F (taste).** The new Scope-paragraph text has a stray line break (`Leave` / `a question`, `SKILL.md:~463`). The line wrap is a reflow leftover.

## Item 4: names by content, not by position
None. I checked the new headings and cross-references; all cite sections by content, though `§7` in the message is by number. That is the skill's own convention.

## Item 5: the failure report
Analogue used: what a rule tells the reader to look at, and whether a detection catches the rule.
- Each new rule has a checklist item, but see Finding D for the Translation item, which detects a stronger property than the rule states.
- The Discussion item matches the rule, and the Symptom item matches slot 2.

## Item 6: what the writer says it verified
The commit message states the evidence: the draft counts per rule, the version they ran against (1.0.1), and what was not re-run (the current open-question rule and the What-slot example). It also states that no cases under `research/` were re-run.
- The "no cases" statement is hard to check, because `research/change-description-authoring/` holds phase prompts and results, not cases.
- Finding B shows the unrun What-slot example fails the rule it illustrates. This is the cost of that gap.
- No mutation run is stated.

## Item 7: siblings of the change
- Searched for the "symptom" rule across `SKILL.md`. Sites that still demand a symptom without the audit clause are the PR Why slot (Finding A), `:136` ("the symptom string", minimum inline content, which is conditioned on an issue existing, so fine), and `:319` (the "State each causal link once" paragraph, which names the Why slot as carrying the symptom; same gap as Finding A).
- Sibling packages that cite this skill (`docs-page-authoring`, `test-authoring`, `problem-report-authoring`, `qubership-repo-essentials`) only name it and carry no copy of these rules.
- The set-size sibling check found nothing: no slot or option was added.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A: PR Why slot lacks the audit and code-reading clause | substantive | `SKILL.md:195`, `:319` | Add the clause to the Why slot, or point it at slot 2 |
| B: What-slot *After* example puts an outcome in prose | substantive | `SKILL.md` What slot example (~355) | Cut the "fails at once" clause from the example |
| C: "found this" has no antecedent | taste | `SKILL.md` slot 2 example | Use a noun phrase |
| D: Translation item conflicts with the identifier exception | taste | `SKILL.md` checklist Translation item | Add the exception |
| E: No control for the no-symptom branch | taste | commit message | One draft with a no-symptom defect |
| F: stray line break in the open-question paragraph | taste | `SKILL.md:~463` | Reflow |

This review did not run the repository's gate or any suite, did not rerun any draft, and did not check wording for style beyond the places where a sentence reads wrongly.
