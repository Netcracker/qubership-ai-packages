**Final review of `d79c43d..HEAD`, one commit: 4f69810, `change-description-authoring` 1.3.0 → 1.4.0.**

The change touches only a skill and its package metadata, so I used the §2a analogues. The drift script was not run: there are no members to parse.

- **No task statement.** I took the claimed cases from the commit message.
- **Skills loaded.** Only `english-developer-style` was loaded. `apm-authoring` is not among the three permitted skills, so I did not cite its rules by name.
- **No previous report.** There is none, so there is no §4 opening table.

### Item 1: comments consistent with each other (analogue: statements one file makes about itself or another)

Cross-references checked, all resolve:
- "§2, slot 2" points to the commit-body slot table, `SKILL.md:81`.
- "§5" points to the identifiers section, line 662.
- "§7 points to this rule" is true: the added "In a description, the same test applies sentence by sentence (§2, the What slot)" is in the §7 anti-pattern list.
- "§2 asks for 'what changed that the diff does not show'" is true: the wording is at `SKILL.md:288`.
- The version is 1.4.0 in all four places: `marketplace.json`, root `apm.yml`, the package `apm.yml` and the commit. The old "1.3.0" hits elsewhere are other packages.
- The README summary matches the new rules.

Findings:
- **F1, substantive, the worked What-slot example breaks its own rule (`SKILL.md:~351-355`).**
  - The rule says a sentence recoverable from one hunk is translation, even under a reason.
  - The *After* example keeps "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly". That sentence is the `sendWithRetry` → `sendDirect` hunk, with a reason attached.
  - The prose after the example says only the `ensureOpen()` hunk is gone from the text.
  - The identifiers in it are not public identifiers, so the "name it once" exception does not apply.
  - An agent copying the example gets the translation back. The commit message itself says translation "persists in about one draft in two".
  - Request: rewrite the second sentence to carry only the reason, for example "the retry only existed to reopen a closed pool, and the pool can no longer be closed". Alternatively, mark that sentence in the follow-up prose as the one the Translation checklist item would delete.
- **F2, substantive, the derived-consequence paragraph reopens the ban (`SKILL.md:~92-103`).**
  - The slot 2 text says "A predicted failure is not known".
  - The next paragraph says a derived consequence "earns a sentence" once traced.
  - The commit message says the previous ban on one wording was evaded by synonyms. The two paragraphs now read in opposite directions with no tie-breaker.
  - The specifics (consequence traced to a caller, marked as derived) are enough for a reader to follow. What is missing is a clause saying that, for an audit-found defect, the traced consequence is not written either. As written, the "derived" path is the way back to the failure sentence the rule exists to stop.
  - Request: add "and not for a defect an audit found, where the sentence ends at what found it".
- **F3, taste, the Why row of the PR-description table (`SKILL.md:~192`).** It still says "The problem, the symptom, the condition that reaches it", with no pointer to the audit exception. The drafts that motivated the change were PR descriptions. The pointer already exists indirectly: "Slots 1 and 2 are the commit body's slots 1 to 3".
- **F4, churn-level, wrapping.** The Scope rule leaves "Leave" alone on a short line (`SKILL.md:~461`). It is not worth a request.

### Item 2: claimed cases covered (analogue: the section that handles each claim, and a detection for it)

| Claim in the commit message | Where handled | Detection |
| --- | --- | --- |
| Slot 2: audit-found defect described by what found it | Table row (line 81), prose (lines ~91-96), changelog row 3 | Checklist "Symptom" |
| Slot 2: "say so" kept for defects with no symptom by construction | Line 81 and ~94-96 | Checklist "Symptom" |
| Slot 2: derived consequence traced and marked as derived | Lines ~98-103 | Checklist "Symptom" |
| Slot 2: bad and good example | Present (*Before*/*After*) | n/a |
| What slot: hunk-recoverable sentence is translation | Lines ~342-359 | Checklist "Translation"; §7 |
| What slot: public identifier named once | Lines ~342-348 | **No checklist item**, see below |
| What slot: bad and good example | Present, but see F1 | n/a |
| Rejected alternatives: mechanism is a fact about merged code, and an obstacle the change removes is a step | Lines ~368-372 | Checklist "Alternatives" |
| Open questions: answered, kept in Scope, or dropped | Scope rule (~458-465) and Scope table row | Checklist "Discussion" |
| §7 points to the rule | Done | n/a |
| §2 says "what changed that the diff does not show" | Done | n/a |
| Checklist items Symptom, Alternatives, Discussion, Translation | All four present | n/a |

Findings:
- **F5, taste, the identifier exception has no checklist hook.** "Name a public identifier once" is a rule, but the Translation checklist item only deletes sentences. An agent applying "delete each What-slot sentence in turn" could drop the one sentence that names the property. Consider adding "except a public identifier the change adds, removes, or renames" to the item.
- **F6, substantive, the commit message makes a claim the repository contradicts.**
  - The message says "This skill has no cases under research/, so none were re-run."
  - `research/change-description-authoring/` exists, with a README and phase files, but no `cases/` or `trial/` directory. The sibling `research/problem-report-authoring/` has both.
  - So the statement is true only if "cases" means a `cases/` directory. It is better stated as "no case set under research/".
  - The fifteen-draft counts (2 + 10 + 2 for the symptom rule, 4 and 4 for the rest) cannot be checked from the repository. The drafts are not stored there. The skill body repeats two of the counts as "measured: …" and "three of three".
  - The commit message also says the final-wording symptom run was "none of two", and the open-question and What-slot examples were not re-run. The skill text does not carry that caveat.
  - Request: store the drafts, or reword the commit message so it does not assert counts nobody can recheck.

Commands the change tells someone to run: none.
Hunk-to-claim mapping: all five files map to the commit message. The README, the version bumps and the marketplace entry are covered by "feat" plus the 1.4.0 bump. The message does not mention the bump, but it is mechanical.

### Item 3: boundaries, partitions, negative control (analogue: genres, situations, trial control)

Table of added instructions (the skill-specific table):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A defect found by a user report that the code reading only confirmed | "A code reading found this", which hides the symptom the reporter had | The rule's "found by reading the code or an audit" already excludes it. A reporter-found defect is a different input. Not a finding |
| Same rule | A one-line fix where "what found it" is the author's own review | "A code review found this" | None stated. **F7, taste:** add "only where the finder is something a reader can open (an audit report, a named review)" |
| "A consequence derived from the code … only after it is traced … stated as derived" | A change with no symptom by construction | An invented "derived" consequence | Covered by the "no symptom by construction" row of the same slot. Not a finding |
| "A sentence whose content the reviewer recovers from one hunk is translation" | A one-hunk change where the entire What slot is the hunk | An empty What slot, which conflicts with the slot's "no skip condition" | None. **F8, substantive.** Add "keep the reason, and stop at it". The Why slot is still the first thing a one-hunk change needs, and the What slot's alternative-rejection sentence is mandatory only "where a reader would propose it" |
| "A question the issue left open is answered, kept open, or left out" | A change with no linked discussion | The agent invents a question to keep | Not applicable: "the issue or the review left open" is its own condition. Not a finding |
| Negative control for the trial | The thing that stayed noisy or too short | None: no input where the added items are noise is cited | **F9, substantive** (evidence, see Item 6) |

Partitions: the three new rules cover the symptom case, the audit case, the code-reading case and the no-symptom case. The *no-symptom-by-construction* partition has no example of its own. The changelog row names the rule only for audit-found defects, not for no-symptom ones; the existing row text covers it with "the defect has no observable symptom" being replaced, which is consistent.

Pre-existing state: an upgrade from 1.3.0 reads the new SKILL.md only. There is no persisted format. Not applicable.

### Item 3a: placement and level (analogue: which file each rule lives in, registration entries)

- The rules are placed in the same files as the siblings, and the package layout is unchanged.
- The registration entries (`marketplace.json`, root `apm.yml`, package `apm.yml`) all agree. I did not run the repository's gate, which was not specified for this review.
- **F10, taste.** The translation-and-identifier rule sits at the end of the "What each paragraph must earn" subsection, after the docs-section paragraph. It would read better beside "Keep a specific value where the decision depends on that value", where the equivalent exception already lives. This is a placement preference, not an error.

### Item 4: names by content (analogue: headings, cross-references, case names)

- The only added cross-references are "(§2, slot 2)", "(§2, the What slot)" and "(§5)", each named by section and slot, not by position.
- Nothing is called "above" or "below" in the added text, and there are no ordinals. The new checklist items are named by content: Translation, Discussion. None.

### Item 5: failure report (analogue: what the rule tells a reader to look at)

- **Symptom, Alternatives, Discussion, Translation** each have a checklist item.
- "Public identifier named once" and "the removed hunk is gone from the text" have no detection, as in F5.
- The Translation check ("delete each sentence in turn; where the diff still says it, leave it deleted") detects the property, not a weaker one. It does not detect the case where the sentence adds a reason, which is the part the rule allows. A reader cannot tell from the item that the reason must survive. Together with F1, I rate this **substantive**, as part of F1: add "keep the reason" to the item.

### Item 6: what the writer says it verified

- Stated evidence: draft counts (two of two predicted a failure without the rule; five of ten stated absence under the ban; none of two with the final wording; retold obstacle two of four → none of four; open question three of three → none of four; translation "persists in about one draft in two").
- The commit also states what was not re-run: the open-question rule and the What-slot example.
- **F9, substantive.** For the instructions that were added after a bad output, the report does not show the input where the added instruction is noise (a change with no audit, a one-hunk change, a change with no linked discussion) or a check that the output there did not grow. The commit message reports the positive arm only. The request is a run on one such input, with the word count before and after.
- The "fifteen" total does not follow from the per-rule counts; the rules were probably run on overlapping drafts, but the message does not say so.
- I did not run any suite. This review has no tests to run.

### Item 7: siblings of the change (analogue: places that enumerate or route to the artifact)

Searched for the skill's name and for both new rules across the repository.
- **Same-file siblings, checked:** the commit-body slot table, the changelog row, the PR-description Scope row, the §6 anti-pattern list, the §8 checklist, and the README summary. All carry the change, except F3 (the Why row) and F5.
- **Sibling skills:** `english-developer-style` (three copies) names `change-description-authoring` only as a router. `docs-page-authoring` cites the changelog entry rule by name; neither copy restates the symptom rule. I found nothing that contradicts the new text.
- **Set-size sentences:** nothing counts checklist items or slots in a way the four new items break. The Discussion and Translation items are additions to a list, and I found no "the N checks" count in prose. Slot counts were not changed.
- **The trigger file** (`.apm/instructions/change-description-authoring.instructions.md`) carries a description that decides whether the skill loads. The change widens the skill to audit-found defects and open questions; the trigger already says "the commit message, the pull request title or description, or the changelog entry", so it still loads. No finding.

### Findings

| # | Finding | Label | Location | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The What-slot *After* example keeps a sentence the same rule calls translation | Substantive | `SKILL.md` ~351-355 | Rewrite the sentence to carry only the reason, or say it is the one to delete |
| F2 | Derived-consequence paragraph reopens the ban on predicted failures | Substantive | `SKILL.md` ~92-103 | Add "and not for a defect an audit found" |
| F6 | Commit message says "no cases under research/", while `research/change-description-authoring/` exists, and the draft counts cannot be rechecked | Substantive | commit message | Reword, or store the drafts |
| F8 | Translation rule has no stop for a one-hunk change | Substantive | `SKILL.md` ~342 | Add "keep the reason, and stop at it" |
| F9 | No noise-input run for the added instructions | Substantive | commit message | One run on an input where the item is noise, with word counts |
| F5 | Identifier exception has no checklist hook; Translation item does not say to keep the reason | Taste | `SKILL.md` §8 | Add both to the Translation item |
| F3 | PR-description Why row has no pointer to the audit exception | Taste | `SKILL.md` ~192 | Add a pointer |
| F7 | "What found it" has no condition on the finder | Taste | `SKILL.md` ~91 | Add "only where the finder is something a reader can open" |
| F10 | Translation rule placement | Taste | `SKILL.md` ~342 | Move beside the "specific value" paragraph |

F4 was dropped as churn.

This review did not run the skill, the repository's gate, or any draft, and it did not check the draft counts or do a style-only pass over the prose.
