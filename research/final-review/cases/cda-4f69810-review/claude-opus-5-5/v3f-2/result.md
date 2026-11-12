# Final review: `d79c43d..4f69810`, "stop drafts from inventing symptoms and translating hunks"

There was no task statement, so I took the claimed cases from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), the package README, and three version fields. I filled the form using the analogues for a change with no code (§2a), and checked it against `english-developer-style` (the copy you supplied) and the repository's `apm-authoring`.

The drift script ran and printed nothing, because it parses no Markdown. No earlier report of this form exists for this change, so there is no table of carried-over findings.

## Item 1: comments consistent with the code and with each other
*Analogue used: what the changed files say about each other and about the repository.*

- **Substantive.** The *After* example at `SKILL.md:353-359` breaks a rule of the same skill. It says "a caller that runs before startup completes fails at once". The paragraph under it then sends that same outcome, as the `IllegalStateException` from `Pool.acquire()`, to its own line under "User-visible changes". Line 231 says "A fact stated in slot 3 is not restated in slot 2." So a reader who copies the example writes the outcome in both places. The commit message also claims the example "no longer puts an outcome in prose", and this sentence shows it still does.
- **Taste.** The new exception at lines 345-347 covers a public identifier that the change "adds, removes, or renames (a system property, a flag, an option)", and cites §5. But §5 (line ~694) says something broader: "The public identifier the change touches: option, flag, class, method". Take a public method whose behavior changes but whose name does not: §5 says to name it, and the new rule says not to.
- The other cross-statements match their targets:
  - The slot 2 table row (81) matches the prose at 91-101.
  - Changelog row 3 (475) matches "§2, slot 2".
  - The pointer at 763 matches the What-slot rule.
  - The Scope row (199) matches the rule at 458-465.
  - The README bullets match the skill.
  - The version is 1.4.0 in all three manifests.
  - None of the new text narrates the change, except "now gets" at 358, which describes the code's behavior and is fine.

## Item 2: claimed cases covered
*Analogue used: the section that handles each case the commit claims.*

| Claimed case | Section that handles it |
| --- | --- |
| Slot 2: a defect found by an audit or a code reading is described by what found it, and the sentence ends there | `SKILL.md:91-94` (before/after), table row 81, checklist 803-806 |
| Changelog entry names the condition alone | row 3 at 475; **no checklist item reaches it**: the Symptom item asks whether the sentence "end[s] at what found it", and the Changelog item at 842 does not mention it. The commit says each fix "has a checklist item". |
| A consequence derived from the code must be traced to what a caller sees and marked as derived | 98-101, checklist 804 |
| "Say so" kept for a defect with no symptom by construction | 94-96, 805 |
| What slot: a sentence recovered from one hunk is translation | 342-359, checklist "Translation" at 826 |
| A public identifier the change adds, removes, or renames is named once | 345-347 |
| §7 points to the What-slot rule | 763 |
| §2 asks for "what changed that the diff does not show" | 288 |
| Rejected alternative: the mechanism is a fact about the merged code | 370-373, checklist Alternatives 831-832 |
| Open questions: answered, kept open in Scope, or dropped | 458-465, Scope row 199, checklist Discussion 835 |
| Bad and good examples for the slot 2 and What-slot rules | 92-93, 349-355 |

- **Commands:** the changed files add no command line, so there is nothing to run.
- **Hunks no sentence claims (substantive):**
  - The version bump 1.3.0 → 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The previous commits claim theirs ("Version 1.2.0 to 1.3.0.").
  - The two new README bullets (`README.md:26-32`).

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres and situations the change claims; for this skill, the negative control is the table of added instructions below.*

**Partitions with no evidence (substantive).**
- Every trial drafted one pull request description from one source pull request.
- The commit-body slot 2 rule and the changelog row 3 rule were never tried; those are two of the three artifacts the change edits.
- The final open-question wording and the rewritten What-slot example were not re-run. The writer says so.

**Pre-existing state:** none. The package installs from a relative path and leaves no persisted state, so a version bump is all an upgrade meets.

**Table of added instructions.** I counted 9 instructions.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Slot 2 / changelog row 3: audit-found defect → name what found it; the changelog gives "the condition alone" | An audit found it, then a regression test reproduced it with an exact exception text | A changelog entry with no diagnostic, so the on-call reader's grep misses | "unless a run reproduced it; then quote what the run printed" |
| What slot: a sentence recovered from one hunk is translation | A one-hunk behavior change ("retries now back off exponentially") | A What slot with a reason and no stated behavior, against row 196's "The behavioral change" | "a sentence naming the behavior a caller sees is not translation" |
| Open question: answer it with evidence unless it does not bear on the change | An issue thread with many settled side questions, all touching the change | One answered question per paragraph, against the length rule and the decision question at 299 | "only where a reviewer would otherwise raise it again" |
| Checklist "Translation" | (detection for the What-slot rule) | Inherits the row above | (same clause) |

Not findings:
- Derived consequence, ended by "earns a sentence only after it is traced to the point where a caller sees it".
- Rejected-alternative mechanism, ended by "earns its sentence only where a reader would propose it".
- Maintainer-only question in Scope, ended by "Where only a maintainer can answer it".
- The public-identifier exception, ended by "the change adds, removes, or renames".
- "What changed that the diff does not show" (288), which narrows the rule and adds no output.

All three rows are substantive.

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives and which gates the repository runs.*

- The rules sit in the slots they govern, and the layout matches the sibling packages.
- I ran `scripts/check-skill-descriptions.py` and it passed ("all 27 … within 1020 characters"). `marketplace.json` parses.
- I did not run `make check` (`apm pack --check-versions`), because it needs `uvx` and the network.
- **Taste:** the open-question rule sits under `#### Scope`, but its "answered" branch belongs in the Why or What slot, and the rule never says where the answer goes.
- No sentence is generic tutorial material.

## Item 4: names by content, not by position
- **Taste.** At `SKILL.md:357`, "the first sentence says why" points to the *After* by ordinal. A content name would survive edits: "the startup sentence".
- The `§2`/`§5`/`§7` references follow the skill's own numbered-heading convention, so they are not findings.

## Item 5: the failure report
*Analogue used: whether each rule's detection is reached by the checklist and detects the rule itself.*

- Symptom, Alternatives, Discussion, and Translation each reach their rule. Each detects the rule's own property, not a weaker one.
- The gap is the changelog row 3 rule: no checklist item detects it (see item 2).

## Item 6: what the writer says it verified
*Analogue used: an exemplar the rules pass and a bad case they fail, both named in the change.*

- The commit message reports draft counts against the bad cases: symptom 2/2 → 5/10 → 0/2, obstacle 2/4 → 0/4, open question 3/3 → 0/4, translation about 1 in 2.
- But the drafts, prompts, and source pull request are not in the repository. The message also omits the source pull request "on purpose", so no reader can re-run them.
- **Substantive:**
  - No input where the added items are noise is named, with a check that the output there did not grow. An example would be a fix with a reported stack trace, no audit, and no open questions.
  - The rewritten example and the final open-question rule were not re-run (the writer states this).

## Item 7: siblings of the change
*Analogue used: the places that list or route to this skill.*

- **Index and routing:** the marketplace entry, the root `apm.yml`, and the package README are updated. The umbrella `qubership-repo-essentials` pulls the package by relative path and has no pin. The `description:` is unchanged, so the trigger surface is unchanged.
- **Twin rules:**
  - `problem-report-authoring` already has the observed-versus-read rule (its Question 5 at line 274), so it needs no change.
  - `english-developer-style` (commit and changelog modules, lines 492-575) asks for the symptom "a reader will search for". That does not conflict with the audit rule.
- **Sibling slot (taste).** The pull request description's Why row (195) still asks for "the symptom" with no audit branch. The rule reaches it only through "Slots 1 and 2 are the commit body's slots 1 to 3" at 204. That matters because the defects this commit fixes came from pull request descriptions.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The *After* example states the early caller's failure in What prose and also sends it to User-visible, against "not restated in slot 2"; the commit message claims otherwise | Substantive | `SKILL.md:353-359`, 231 | Take the outcome out of the *After* (e.g. "The pool opens at startup, so no call path needs to open it on demand"), or narrow line 231 |
| Audit rule drops a diagnostic that a regression run reproduced | Substantive | `SKILL.md:91-94`, 475 | Add "unless a run reproduced it; then quote what it printed" |
| The What-slot translation rule removes the behavioral change of a one-hunk fix, against row 196 | Substantive | `SKILL.md:342-345` | Add "a sentence naming the behavior a caller sees is not translation" |
| The open-question rule asks for an answer to every bearing question, against the decision and length rules | Substantive | `SKILL.md:458-465`, 835 | Add "only where a reviewer would otherwise raise it again" |
| The changelog "condition alone" rule has no checklist item, though the commit claims every fix has one | Substantive | `SKILL.md:475`, 842 | Extend the Changelog or Symptom checklist item |
| Version bump and README bullets claimed by no sentence | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291`, `README.md:26-32` | Add "Version 1.3.0 to 1.4.0" and a README sentence to the commit message |
| Commit body and changelog partitions untried; final wording not re-run; no noise-input control | Substantive | commit message | Run the final wording on a commit body, a changelog entry, and a noise input with a length check, and name them in the change |
| The public-identifier exception is narrower than the §5 it cites | Taste | `SKILL.md:345-347` vs ~694 | Align with §5 or say why it differs |
| The open-question "answered" branch has no slot | Taste | `SKILL.md:458` | Name where the answer goes (Why or What) |
| Ordinal "the first sentence" | Taste | `SKILL.md:357` | "the startup sentence" |
| The pull request description's Why row has no audit branch | Taste | `SKILL.md:195` | Add the branch, or point to slot 2 |

The review did not run `make check` or `make test` (both need `uvx` and the network), did not re-run any drafting trial, and did not do a separate pass over the prose for style.
