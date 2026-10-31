## Final review of `d79c43d..HEAD` (commit `4f69810`)

**Inputs.**
- The change is one commit that edits a skill, its README, and three version entries. It has no code.
- No task statement was handed over. I took the claimed cases from the commit message and answered item 2 from it alone.
- There is no previous report for this change.
- I loaded `apm-authoring`. I only grepped `english-developer-style`, so the wording pass was not done.
- The drift script (`comment-drift.py`) printed nothing. The change has no members for it to parse.
- Each item uses the analogue from §2a.

### Item 1: comments consistent with the code and with each other
Analogue: statements the changed files make about each other, and the worked examples.

- **Finding (substantive).** The What-slot *After* at `SKILL.md:353-358` fails the rule the same commit adds.
  - Its second sentence is "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly." That is a `Y now calls Z` sentence recovered from one hunk, under a lead-in that gives the reason. Line 346 says a reason does not exempt such a sentence.
  - The first sentence states the caller's outcome in prose ("fails at once instead of opening the pool on demand"). The paragraph after the example then puts the same fact under "User-visible changes", and slot 3 says a fact stated there is not restated in slot 2.
  - The commit message says the What-slot example "no longer puts an outcome in prose". The text does.
  - A drafter copies the example, because `apm-authoring` rule 2 says agents copy examples.
- **Finding (substantive).** `SKILL.md:188` is the pull-request Why row. It still reads "The problem, the symptom, the condition that reaches it" and has no `Skip when` column. The commit-body slot 2 row was changed for audit-found defects, and this row was not. The row it parallels now says one thing and this row says another about the same fact. The prose at line 190 ("no skip condition") is true only if the row carries the same exception.
- No sentence narrates the change with `now` or `no longer` outside a regression-test comment.
- **Taste.** `SKILL.md:462-464` has a stray short line break ("wanted. Leave" / "a question out…"). It is cosmetic.

### Item 2: claimed cases covered
Claims taken from the commit message only.

| Claim | Where handled |
| --- | --- |
| Slot 2: audit-found defect described by what found it, sentence ends there | `SKILL.md:81`, `:91-96` |
| Changelog entry names the condition alone | `:475` |
| Derived consequence traced to the caller and marked derived | `:99-102` |
| What slot: one-hunk sentence is translation; public identifier named once | `:342-348` |
| §7 points to this rule | `:763` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected-alternative mechanism stated as a fact about the merged code | `:371-373` |
| Open-question rule, with the maintainer question kept in Scope | `:458-465`, `:196` |
| Checklist: Symptom, Alternatives, Discussion, Translation | `:803-840` |
| Bad and good example in the slot 2 and What rules | `:92-94`, `:350-358` |

- **Commands:** the change tells the reader to run none.
- **Hunks no sentence claims.**
  - Version bumps 1.3.0 → 1.4.0 in `apm.yml`, the package `apm.yml`, and `marketplace.json`.
  - The README bullets.
  - Neither is mentioned in the message. Earlier commits in this series bump the same way, so this is a minor omission, not a request.
- **Finding (substantive).** The commit says "This skill has no cases under research/, so none were re-run." `research/change-description-authoring/` exists, with phase 1 to 4 prompts and results. It may be a study of the skill's design and not cases. The sentence should say that, or the cases should be named.

### Item 3: boundaries, partitions, and the negative control
Analogue: the claimed situations, the negative control, and the evidence.

- The commit's trial numbers cover four defects: predicted symptom, "none seen", retold obstacle, repeated open question. Hunk translation "persists in about one draft in two", and the commit says so.
- The rewritten open-question rule and the What-slot example were not re-run, and the commit says so. Those two are the partitions with no evidence.
- Not measured at all: the checklist items added in this commit, and the changelog part 3 change.
- No input in the trials was an audit-found defect that also has an observed symptom. See the table.
- Added instructions: 7. The rows below are the ones that fire where the item is noise or wrong. The other three are the Scope question clause, the changelog part 3 clause, and the two checklist lines.
- Not findings: `:353-358` is filed under item 1 and not repeated here. The Translation checklist item at `:826` ends for a non-description input, because it says "What slot".

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "Where reading the code or an audit found the defect, name what found it and end the sentence there" | audit found it, and the issue also has a user's stack trace | "An audit found this." The quoted diagnostic is dropped. | "only where no symptom has been observed" |
| `:99` "A consequence derived from the code earns a sentence only after it is traced" | a defect with an observed symptom | a derived-consequence paragraph beside the observed one | "only where the defect has no observed symptom" |
| `:342` "a sentence whose content the reviewer recovers from one hunk is translation" | a one-line fix whose single What sentence is the hunk | an empty What slot, against "Why has no skip condition" and the slot table | "absent when the Why sentence already states the behavior" |
| `:458` "answered, kept open, or left out" | a pull request with no review thread | a Scope sentence saying no questions remain | "only where the discussion left one" |

### Item 3a: level, placement, and the environment
- The rules sit in the existing file, beside the sibling rules. There is no new file.
- `check-skill-descriptions.py` passes: "ok: all 27 skill descriptions within 1020 characters". The skill description is unchanged.
- I did not run `make check` (the version and clean-pack gate). It needs `uvx` and the network. The three version bumps are consistent with each other by inspection.

### Item 4: names by content, not by position
None. The new references are `§2`, `§5`, `§7`, `slot 2`, and `the What slot`. These are section numbers and slot numbers already used throughout the file. The new checklist items are named by content.

### Item 5: the failure report
Analogue: the rules' detection.
- **Finding (taste).** The new checklist items are reachable, and the Translation item is a usable detector (delete a sentence, check the diff). The Symptom item ("quoted from an observation, or traced and marked as derived") has no way to tell a derived sentence from an observed one except the "marked" wording. That is acceptable. I prefer a sentence form for the mark, but this will be declined without discussion.

### Item 6: what the writer says it verified
The commit gives fifteen blind drafts with counts, and says what was not re-run. It does not name an exemplar and a bad case for each of the new rules. Re-applying the rule to its own example shows that the *After* of `:353` fails the rule (see item 1). That is a rewrite failing the change's own worked example. The commit's trial of the example did not catch it. For the added "Discussion" instruction, the commit has no check on an input where it is noise, such as a change with no review thread.

### Item 7: siblings of the change
- **The Why row** (`:188`) is covered in item 1.
- **Other readers of the set:**
  - `merge-model.md:24,38,51,63` and README `:73` say "problem, symptom, approach" for the first commit's body. This conflicts with the new rule for an audit-found defect. Each should say "symptom, where there is one".
  - `research/change-description-authoring/README.md:65` describes the changelog parts as "verbatim symptom and trigger", also without the exception.
  - `§7b` item 5 lists "symptom dropped" as a finding. After this change, dropping the symptom is the right output for an audit-found defect. The list should carry that exception.
- **Set size:** no sentence counts the slots or the checklist items. The new checklist items are listed.
- **Hits for `apm-authoring` rule 4:** each new rule has a checklist line. The commit message says this is deliberate.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| What-slot *After* translates a hunk and restates the outcome in prose | Substantive | `SKILL.md:353-358` | Cut the `QueryExecutor.execute` sentence. Keep the reason, and move "fails at once" to the outcome line. |
| Why row not updated for audit-found defects | Substantive | `SKILL.md:188` | Add the same exception as `:81`. |
| Siblings still say "symptom" unconditionally | Substantive | `merge-model.md:24,38,51,63`; README `:73`; `SKILL.md:790-791` | Add "where there is one", or point to `:91`. |
| "No cases under research/" is unclear against an existing `research/change-description-authoring/` | Substantive | commit message | Say what the directory holds. |
| Audit-found rule drops an observed symptom | Substantive | `SKILL.md:91` | Limit the instruction to a defect with no observed symptom. |
| Version bump and README hunks unclaimed | Taste | commit message | Add one sentence. |
| Stray line break | Taste | `SKILL.md:462-464` | Re-wrap. |

I did not run `make check`, the suite, or the drafting trials. I did not do a wording pass for style.
