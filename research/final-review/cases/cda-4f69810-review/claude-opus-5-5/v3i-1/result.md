# Final review: `d79c43d..4f69810` (one commit), change-description-authoring 1.3.0 to 1.4.0

There is no separate task statement. The claimed cases below come from the commit message alone. The change has no code: it touches a skill, its README, and three version fields. So the form was filled through the §2a analogues, and each item names the analogue it used. I did not run the drift script (`comment-drift.py`), because nothing in the change has members for it to parse.

Skills loaded: `english-developer-style` (the copy under the task's skills directory) and `apm-authoring` (the copy at `agent-packages/apm-authoring`, used in place of the doc-comment skill). I did not load `test-authoring`, because no test is involved.

## Item 1: comments consistent with the code and with each other
Analogue used: the statements each changed file makes about the others and about the repository.

- **The What-slot *After* example puts an outcome in prose** (`SKILL.md:353-355`). Its first sentence says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is the outcome which `SKILL.md:358-359` sends to "User-visible changes". It also breaks `SKILL.md:230`: "A fact stated in slot 3 is not restated in slot 2". The commit message claims the example "no longer puts an outcome in prose", and that claim is false.
- **The same example breaks its own translation rule** (`SKILL.md:354-355`). "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly" is a reason followed by `Y now calls Z`. The rule at `:342-345` names that shape as translation "even under a lead-in that states a reason". An agent copying the exemplar learns the defect the commit says still shows up in about one draft in two.
- **The README contradicts the skill on derived consequences** (`README.md:28-30`). The README says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` does allow a consequence traced in the code and marked as derived. A README reader would take that as banned.
- **The README says evidence lives in research/, but the new evidence doesn't** (`README.md` Contents). The README says the skill "carries no citations; the evidence stays in the research directory". The change adds two "measured:" claims (`SKILL.md:100`, `:464`), and the fifteen-draft trial behind them is not under `research/change-description-authoring/`. The previous evidence-bearing change of this kind added `phase4_merge_model.md` there.
- **The leak example no longer fits its category** (`SKILL.md:95-96`). The condition was narrowed from "no observable symptom" to "no symptom by construction", but the example stayed "a leak on an error path with nothing logged". A leak does have a symptom: memory or handle growth. A leak is also the typical audit finding, so the example now sits under both rules at once ("name what found it" and "say so").
- Taste: §5 (`:683`) asks to name any public identifier the change *touches*, including a class or method. The new exception (`:345-347`) covers only identifiers that are *added, removed, or renamed*, with property, flag, and option as examples. Both readings work.

## Item 2: claimed cases covered
Analogue used: the section that handles each claimed case.

| Claimed case (commit message) | Section |
| --- | --- |
| Slot 2: an audit or code-reading defect is described by what found it, and the sentence ends there | `SKILL.md:91-94`, table row `:81` |
| Changelog entry names the condition alone | `:475` |
| Derived consequence only when traced and marked as derived | `:98-101` |
| "Say so" kept for a defect with no symptom by construction | `:94-96` |
| What slot: a sentence recovered from one hunk is translation; public identifiers named once | `:342-359` |
| §7 points to the rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternatives: a fact about the merged code; an obstacle the change removes is a step | `:370-373` |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, Scope row `:199` |
| Checklist: Symptom and Alternatives extended; new Discussion and Translation items | `:803-806`, `:826-838` |
| Slot 2 and What-slot rules each carry a bad and a good example | `:92-93`, `:349-355` |

- Every claimed case has its section.
- The commit message runs no commands, and the change adds no runnable command lines.
- Reverse direction: no sentence of the commit message claims the version bump to 1.4.0 (`apm.yml:168`, `marketplace.json:291`, package `apm.yml:2`). The sibling commits d79c43d and 51b35c9 each say "Version 1.x.0 to 1.y.0." This is taste.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the claimed genres and situations, plus the table of added instructions.

- **Two of the three claimed artifacts have no evidence.** The trial drafted one pull request description. The commit-body slot 2 rule and the changelog part 3 rule changed with no draft of either.
- **The current wording was not tested.** The commit says the current open-question rule and the What-slot example were not re-run. The other rules ran against version 1.0.1 of the skill.
- There is no persisted state to check. The change is skill text installed over the earlier version, and nothing reads it as a format.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "name what found it and end the sentence there" | audit-found defect whose regression test reproduces the exception | "An audit found this", with the reproduced diagnostic dropped | "unless a run, test, or report has observed it; quote that" |
| `:475` changelog "the condition alone" | Security entry for an audit-found CVE | condition only, impact (e.g. code execution) omitted | "except a consequence traced and marked as derived (slot 2)" |
| `:342` "translation, even under a lead-in" | change whose whole content is one hunk (dependency bump) | an empty What slot | "where another sentence of the description states the change" |
| `:458` "keep it in the Scope slot as a question" | §4 rule 5 repository: the description becomes the commit body | an open maintainer question copied into `git log` | "under §4 rule 5, in a review comment instead" (conflicts with `:265-267`) |

Not findings: `:98`, ended by "only after it is traced to the point where a caller sees it"; `:288`, ended by "that the diff does not show"; `:370`, ended by "a step the change had to take".

## Item 3a: level, placement, and the environment
Analogue used: which file each rule lives in, and the repository's own gates.

- Each rule sits in its own section of `SKILL.md`, and the README is updated beside it. The layout matches the sibling packages.
- I ran `scripts/check-skill-descriptions.py`: "ok: all 27 skill descriptions are within 1020 characters".
- The version reads 1.4.0 in all three places.
- I did not run `make check` (`apm pack --check-versions`), because it needs `uvx` and the network.
- No added sentence is generic tutorial material. Each rule cites a failure mode specific to this skill.
- Answer: none.

## Item 4: names by content, not by position
Analogue used: unchanged, applied to the change's headings, cross-references, and case names.

- Taste: `:357` says "the first sentence says why". The startup sentence can be named by what it says.
- The slot numbers are names the skill's own tables define, so they are not position references.

## Item 5: the failure report
Analogue used: whether the checklist reaches each new rule, and whether each detection checks the rule it is attached to.

- **The Translation detection is weaker than its rule and contradicts its exception** (`:826-827`). "Where the diff still says it, leave it deleted" removes a sentence that names a public identifier the change adds, and `:345-347` exempts exactly that. It also tests "the diff" where the rule says "one hunk".
- Every other new rule is reached by the Symptom, Alternatives, or Discussion checklist item.

## Item 6: what the writer says it verified
Analogue used: an exemplar the rules pass and a bad case they fail, both named in the change.

- The commit reports counts over fifteen blind drafts, which is a red-then-green result for slot 2, the rejected alternative, and the open question.
- **The bad case is not named.** The commit says only that "the examples avoid the pull request the drafts were written for".
- **Neither the drafts nor the trial are in the repository.**
- **The current open-question wording and the rewritten What-slot example were not re-run.** The commit says so.
- **There is no input where the added items are noise**, so nothing shows that output did not grow there. A fix with an observed symptom, or a change with no open question, would be such an input.

## Item 7: siblings of the change
Analogue used: the places that list or route to the skill.

- The instructions trigger, the marketplace and root `apm.yml` descriptions, and the root README are unchanged, and the scope was not widened.
- The commit and pull request module in `english-developer-style` leaves this content to `change-description-authoring`. Its "state the observable defect or the violated contract" fits an audit-found defect.
- `problem-report-authoring` governs reports, not descriptions.
- No set gained a member, so no other list or count needed an update.
- Answer: none.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| *After* example states the outcome in prose, against `:230` and the commit's claim | Substantive | `SKILL.md:353-355` | Cut the "fails at once" clause and leave the outcome to "User-visible changes" |
| *After* example is a reason followed by `Y now calls Z`, the shape `:342` bans | Substantive | `SKILL.md:354-355` | Keep the reason ("used sendWithRetry only to reopen a closed pool") and drop "it sends directly" |
| Translation checklist deletes public identifiers and tests "the diff", not "one hunk" | Substantive | `SKILL.md:826-827` | Add "except a public identifier the change adds, removes, or renames"; match the rule's "one hunk" |
| README bans what `:98-101` permits | Substantive | `README.md:28-30` | Add "unless traced to the caller and marked as derived" |
| Measured claims have no evidence in research/, as the README promises | Substantive | `README.md` Contents; `SKILL.md:100`, `:464` | Add a research addendum with the drafts and the counts, or change the README sentence |
| Leak example no longer fits "no symptom by construction" | Substantive | `SKILL.md:95-96` | Pick an example with no symptom by construction, or keep "observable" |
| An observed reproduction of an audit-found defect is dropped | Substantive | `SKILL.md:91` | Clause from the instruction table above |
| Changelog "condition alone" drops a traced impact in a Security entry | Substantive | `SKILL.md:475` | Clause from the instruction table above |
| Open question kept in Scope is copied into `git log` under §4 rule 5 | Substantive | `SKILL.md:458-462`, `:199` | Clause from the instruction table above |
| Translation rule empties the What slot of a one-hunk change | Substantive | `SKILL.md:342` | Clause from the instruction table above |
| Commit body and changelog rules have no draft evidence; current wording and a noise input not run | Substantive | commit message | Re-run the current wording on one commit body, one changelog entry, and one noise input, and check that length did not grow |
| Version bump is not claimed in the commit message | Taste | `apm.yml:168` and two others | "Version 1.3.0 to 1.4.0.", as the sibling commits say |
| "the first sentence" refers by position | Taste | `SKILL.md:357` | Name the sentence by its content |
| "touches" in §5 versus "adds, removes, or renames" in the exception | Taste | `SKILL.md:345`, `:683` | Align the two scopes |

What this review did not check:
- It ran no drafts against the new wording.
- It did not run `make check` or `make test`, which need the network.
- It did not run the drift script, because the change has no code.
- It did not do a style-only pass over the prose.
