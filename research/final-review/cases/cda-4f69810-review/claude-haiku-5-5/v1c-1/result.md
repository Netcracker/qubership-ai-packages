**Final review: commit `4f69810` (`d79c43d..HEAD`)**

**Scope and inputs.** The change is one commit, `4f69810`, which edits `change-description-authoring` and its version in three files. No task statement was handed over, so item 2's claimed cases come from the commit message alone. Its class-comment equivalent is the skill's own sections. This is a first review, so there is no previous report to open with. The drift script ran (`comment-drift.py d79c43d… HEAD`) and printed nothing: no code member changed, so there is nothing to tag. Analogues from §2a are used throughout. I loaded `final-review` and `english-developer-style` from the skills directory. `test-authoring` was not loaded because the change has no tests. `apm-authoring`, the artifact authoring skill, is not in that directory, so I checked the three rules it is cited for by grepping its repo copy (`agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`). The skill file is `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, cited below as `SKILL.md`.

**Item 1: comments consistent with the content and with each other.** Finding F1. The new trigger "Where reading the code or an audit found the defect, name what found it and end the sentence there" (`SKILL.md:91-92`) has no condition on a symptom having been observed. The §3 sentence at `SKILL.md:512` still says that omitting the symptom "costs R3 the whole entry". The new changelog row (`SKILL.md:475`) and the symptom checklist (`SKILL.md:803-806`) repeat the trigger. The new section references (§2, §7, "the What slot") resolve. Counts are unchanged.

**Item 2: claimed cases covered.** The commit claims four defects and a checklist item for each fix. Symptom, Alternatives, Discussion, and Translation exist. The identifier-named-once rule (`SKILL.md:345`) has no checklist item, which is F5. Every hunk except the version bumps belongs to a claim. The bumps are F4. The commit's claim that no research cases exist is consistent with `research/change-description-authoring/`, which holds phase documents and no case set. The change contains no command lines to check.

**Item 3: boundaries, partitions, control.** The partition the change claims but does not test is a defect with an observed symptom, which is where F1 fails. The request is a draft run on such a defect, checking that the reported exception survives. The commit's slot-2 measurement is two drafts on the final wording.

**Item 3a: level, placement, environment.** The file sits at `.apm/skills/<name>/SKILL.md`, the same layout as `apm-authoring`. The version is 1.4.0 in the package `apm.yml`, the root `apm.yml:168`, and `marketplace.json:291`. I did not run any repository registration gate.

**Item 4: names by content.** One ordinal reference, `(§2, slot 2)` at `SKILL.md:475`, which is taste (F6). The slot is named "Impact and trigger". Numbering is the file's convention throughout, so the finding is minor.

**Item 5: failure report.** The Translation checklist detects "the diff still says it" (`SKILL.md:826`), which is a different property from the rule it is attached to, "recovers from one hunk" (`SKILL.md:342`). That mismatch is F2. The other detections name what to look at.

**Item 6: what the writer says it verified.** Evidence is stated. Bad and good examples exist for slot 2 and the What slot. The commit states that the final-wording slot-2 run had two drafts, and that the open-question rule and the What-slot example were not re-run. That is a disclosed gap, not a finding. The What-slot example conflicts with its own rule, which is F3.

**Item 7: siblings.** The changelog row, the description table row, and the checklist were updated together. §3 at `SKILL.md:512` is the sibling that F1 reaches. §7a at `SKILL.md:794` already lists "symptom dropped" as a finding, so the new trigger also weakens that check. The prose counts of slots are unchanged. The three version lines agree.

**§2a table: instructions added or widened**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (`SKILL.md:91-92`) | A defect found by reading code that a user already reported with an exception or log line | The reported literal is dropped, and the sentence ends at "found by reading the code" | None. Needed: "…and no symptom has been observed; where one has, quote it" |
| "where the diff still says it, leave it deleted" (`SKILL.md:826`) | A behavior spread over several hunks, such as a new flag read in three files | The sentence naming the behavior is deleted, though the What rule keeps it | None. The criterion conflicts with the rule's "one hunk" |
| "A consequence derived from the code earns a sentence only after it is traced…" (`SKILL.md:98`) | A defect no caller ever sees | Nothing, since the trace fails | Covered by the rule's own trace condition. None |
| "Leave a question out only when it does not bear on this change" (`SKILL.md:464-465`) | A maintainer question that only looks related | Kept as a Scope question | Covered by the "does not bear" test. None |

**Findings**

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| F1. The slot-2 trigger drops an observed symptom. A defect found by code reading that was already reported with an exception or log line gets "found by reading the code" and loses the literal R3 greps for. | Substantive | `SKILL.md:91-92`; also `:475`, `:803-806`, `:512`, `:794` | Make the trigger "no symptom has been observed"; where one has, quote it. Apply the same condition to the changelog row and the symptom checklist. Run one draft on a defect with an observed exception. |
| F2. The Translation criterion disagrees with the rule. The rule says "recovers from one hunk" (`:342`); the checklist says "the diff still says it" (`:826`). A behavior spread over several hunks is kept by the rule and deleted by the checklist. | Substantive | `SKILL.md:342`, `:826` | Make the checklist say "recovers from one hunk", or make the rule match the checklist. |
| F3. The What-slot After example breaks its own rule. It keeps the edit, "with the pool open from startup it sends directly", where `:345` says to state the reason and not the edit. | Substantive | `SKILL.md:352-355` | Cut the edit clause and keep the reason, "QueryExecutor.execute used sendWithRetry only to reopen a closed pool". |
| F4. The version bump from 1.3.0 to 1.4.0 is unclaimed. No sentence in the commit message mentions it. The three hunks are `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168`, and `.claude-plugin/marketplace.json:291`. Previous feature commits bump the same three files, so the fix is one sentence, not a move. | Substantive (per the form's rule that any unclaimed hunk is a finding) | the three lines above | Add a commit-message sentence that claims the bump, or move it to its own change. |
| F5. The rule that a public identifier is named once (`SKILL.md:345`) has no checklist item and no detection. The commit says each fix has one. | Substantive | `SKILL.md:345`; checklist near `:826` | Add a checklist item: "Is each public identifier the change adds, removes, or renames named once in the What slot?" |
| F6. The changelog row cites "slot 2" by ordinal (`SKILL.md:475`). The slot has the name "Impact and trigger". | Taste (the file numbers its slots throughout, so this will likely be declined) | `SKILL.md:475` | Write "the Impact and trigger slot". |

**What this review did not check.** I did not run any test, build, or registration gate, and I did not re-run the drafting experiments or verify their measurements. The apm-authoring rules were checked only through grep of the repo copy. The English prose was checked only for the rules cited, not for a style pass.
