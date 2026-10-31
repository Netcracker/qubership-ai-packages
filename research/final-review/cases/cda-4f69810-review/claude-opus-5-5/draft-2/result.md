# Final review of `d79c43d..4f69810`: the change-description-authoring update (version 1.4.0)

This change has no code. It edits one skill, its README, and three version entries, so I filled the form with the §2a analogues and loaded `apm-authoring` and `english-developer-style` alongside it. I ran the drift script with the base and head commits; it printed nothing because it has no code to parse. There was no task statement, so item 2 takes its claimed cases from the commit message alone.

The review found five substantive findings and two rows in the table of added instructions, plus two taste findings. The first two findings are contradictions between parts of the skill. I made no file changes and no commits.

## 1. Comments consistent with the code and with each other
Analogue: what one changed file says about another, the counts and section pointers, and the worked examples. I checked the pointers in the commit message ("§7 points to this rule", §2's "what changed that the diff does not show", the new checklist items Symptom, Alternatives, Discussion and Translation) against `SKILL.md`, and they hold. Two contradictions:

- **Slot 1 still asks for a predicted failure (`SKILL.md:87`).** Slot 1's model sentence is "Previously, when X happened, this caused Y, which resulted in Z". For a defect found by an audit, that asks for exactly what the new slot 2 rule at `:91-94` stops: a consequence Y and Z that nobody observed. A draft that obeys slot 2 can simply move the prediction into slot 1.
  - **Request:** give `:87` a condition: for a defect found by an audit or by reading the code, the problem and its condition only, as slot 2 says.
- **The README bans what the skill allows (`README.md:28-29`).** The README says such a defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101`, however, allows a consequence worked out from the code, once it is traced to what a caller sees and marked as derived.
  - **Request:** add that exception to the README sentence.

## 2. Claimed cases covered
The cases the commit message claims, each with the place that covers it:

| Claimed case | Where it is covered |
| --- | --- |
| Slot 2 names what found the defect and ends the sentence there | `:81` table, `:91-94`, checklist `:803-806` |
| Changelog entry gives the condition alone | `:475` |
| A derived consequence is traced and marked as derived | `:98-101` |
| "Say so" is kept for a defect with no symptom by construction | `:94-96` |
| A sentence recoverable from one hunk is translation; a public identifier is named once | `:342-359` |
| §7 points to that rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| A rejected alternative is a fact about the merged code | `:369-373`, checklist `:832-833` |
| Open questions are answered, kept for a maintainer, or left out | `:458-465`, Scope table `:199`, checklist Discussion |
| Each rule has a checklist item | Yes |

The version bump to 1.4.0 in three files belongs to the claimed change. The change adds no commands for anyone to run. No hunk falls outside the claim.

## 3. Boundaries, partitions, and the negative control
- **Only one of three artifacts was tested.** The trials used "blind drafts of one pull request description". Two of the new rules govern other artifacts and have no draft behind them: the commit-body slot 2 rule (`:91-101`) and the changelog "condition alone" (`:475`). Two branches the commit message itself says were not re-run also lack evidence: the open-question rule's branch that keeps a question for the maintainer, and the reworked What-slot example.
  - **Request:** run a blind draft of a commit body and of a changelog entry for a defect found by an audit, or state these gaps in the commit message.

The table of added instructions. Each row shows an input that meets the instruction's conditions but leaves out something a reader needs:

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:475` "for a defect an audit or a code reading found, the condition alone" | An audit-found defect whose new regression test reproduces it with an exception | The condition only; the exception class the on-call reader would search for is dropped | "unless a test or a report reproduces it; then quote the diagnostic" |
| `:92` "name what found it and end the sentence there" | The same input | "An audit of X found this."; the reproduced diagnostic is left out as not observed | "where no test or report reproduces the failure" |

Not findings: `:98`, `:342`, `:369`, `:458`.

## 3a. Level, placement, and the environment
The rules sit in the slot sections they govern, each with a checklist item, and the package layout is unchanged.

- `scripts/check-skill-descriptions.py` passed: all 27 descriptions are within 1020 characters.
- `research/change-description-authoring/check-classifier-target-ref.sh` passed all cases.
- I did not run `make check`, because it fetches `apm` through `uvx` and there is no network. Instead I checked by hand that 1.4.0 matches in `apm.yml`, the package's `apm.yml`, and `marketplace.json`.

No added sentence is generic tutorial advice. Finding: none.

## 4. Names by content, not by position
The new text refers to slots by the numbers and names their tables define ("slot 2", "the What slot", "(§2, slot 2)"). It adds no new references by position such as "above" or "below". Finding: none.

## 5. The failure report
- **The Translation check contradicts the rule it checks (`SKILL.md:826`).** It says: "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". A sentence naming a new public identifier (a system property, a flag) is always visible in the diff, so this check deletes the very sentence that `:345-347` says to keep.
  - **Request:** add "unless it names a public identifier the change adds, removes, or renames".

The other new checklist items check the rules they are attached to.

## 6. What the writer says it verified
The commit message gives counts of bad and good outputs per rule (2 of 2, then 5 of 10, then 0 of 2 for symptoms; 2 of 4 to 0 of 4 for retold obstacles; 3 of 3 to 0 of 4 for open questions). It also says that the rewritten open-question rule and the What-slot example were not re-run. Applying the rewritten rule to its own example shows a problem:

- **The What-slot *After* example breaks its own rule (`SKILL.md:354-355`).** It ends with "with the pool open from startup it sends directly". That is a reason in front of a hunk (`sendWithRetry` became `sendDirect`), which is the exact form `:342-344` calls translation "even under a lead-in that states a reason". An agent copies the example (`apm-authoring` rule 2).
  - **Request:** end that sentence at the reason, without the edit.

## 7. Siblings of the change
The places that list or route to this package are consistent:

- The version is aligned in all three places.
- `qubership-repo-essentials` uses a relative path with no version pin.
- The frontmatter description's scope did not change.
- No sibling package cites a section whose meaning changed.
- The commit-body form of the translation rule (§7) points to the new What-slot rule.

One taste finding: the rule that a rejected alternative must hold in the merged code (`:369-373`) appears only in the pull-request section. The commit body's slot 3 (`:103-106`) has no pointer to it, although the generic Alternatives checklist item reaches both.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Slot 1's model sentence asks for the predicted consequence that slot 2 now stops for an audit-found defect | Substantive | `SKILL.md:87` | 1 |
| README bans a predicted failure outright; the skill allows a traced, derived one | Substantive | `README.md:28` | 1 |
| Trials covered pull request descriptions only; the commit-body and changelog rules, the maintainer-question branch, and the new example have no draft | Substantive | `SKILL.md:91`, `:475` | 3 |
| The changelog's "condition alone" and slot 2's "end the sentence there" drop a diagnostic that a regression test reproduces | Substantive | table rows, `SKILL.md:475`, `:92` | 3 |
| The Translation check deletes the public-identifier sentence the rule keeps | Substantive | `SKILL.md:826` | 5 |
| The *After* example ends with a hunk behind a reason, the form the rule forbids | Substantive | `SKILL.md:355` | 6 |
| The merged-code rule for alternatives has no pointer from the commit body's slot 3 | Taste | `SKILL.md:103` | 7 |
| The commit message says the example "no longer puts an outcome in prose", but the *After* still states "fails at once" | Taste | `SKILL.md:353` | 1 |

Two checks could not be done: the drift script has no code to parse in this change, and `make check` needs network access, so I verified version alignment by hand instead.
