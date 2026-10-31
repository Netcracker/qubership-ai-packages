# Final review: `d79c43d..HEAD`, one commit (`4f69810`)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message, as the skill allows. The change touches `SKILL.md`, `README.md`, the package `apm.yml`, the root `apm.yml`, and `marketplace.json`. It has no code, so `comment-drift.py` was not run. I used the analogues in §2a. I loaded `english-developer-style` and `apm-authoring` from the given skills directory. `test-authoring` was not loaded because the change has no tests. There is no previous report, so §4's table is empty.

**Gate.** `apm pack --check-versions --check-clean --dry-run` (the Makefile `check` flags) exited 0 with "Version alignment OK", and the working tree stayed clean.

Paths below are relative to `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/` unless they start with a repo path.

## Item 1: comments consistent with the code and with each other

Analogue: the statements the changed files make about each other and about the rules.

- **F1.** The What-slot After example (`SKILL.md:353-355`) states an outcome in prose ("fails at once"). Lines 357-359 say such an outcome goes on its own User-visible line. The commit message says the example "no longer puts an outcome in prose", which the file contradicts.
- **F2.** `README.md:26-27` says a cut sentence's "reason stays". The Translation checklist item (`:826-827`) deletes the whole sentence. See F2 in the table.
- **F3.** The slot-2 rule (`:81`, `:90-96`) is ambiguous for a defect an audit found that also has an observed symptom. The rule says to end at what found it, while the same slot says it carries what a person observes. See F3.

Consistent: the slot counts in `README.md:17`, the §7 pointer at `:763`, and the §5 cross-reference at `:684`, which supports the identifier rule.

## Item 2: claimed cases covered

Claimed cases from the commit message, each mapped to its rule and checklist item:

- Predicted failure from one missing call: `:90-96`, checklist Symptom `:803-806`. Covered.
- "No failure has been observed" wordings: `:94-96`. Covered.
- Hunk-listing sentences: `:342-347`, checklist `:826-827`. Covered in text; the checklist is wrong (F2).
- Rejected alternative answered by an obstacle the change removes: `:370-372`, checklist `:832-834`. Covered.
- Repeated open question: `:458-465`, checklist `:835-838`. Covered.
- "Say so" for an absent symptom: `:94-96`. Covered.
- "What changed" asked to list changes: `:288`. Covered.
- The identifier rule (`:345-347`): no checklist item, though the commit says each fix has one. See F5.

Commands: no command line is added or changed, so there is nothing to check.

Reverse direction (every hunk belongs to a claim): every hunk is claimed except the version bumps at `apm.yml:2`, root `apm.yml:168`, and `.claude-plugin/marketplace.json:291`. See F6.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the routes by which a defect is found (audit, code reading, observed symptom, no symptom by construction). The partition "audit-found, with an observed symptom" has no clause (F3). The change writes no persisted state, so the limits paragraph does not apply.

Added instructions: 15. Rows are below; the Not-findings line names the instructions the artifact already ends for their inputs.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:826-827` checklist "Translation" | A What sentence giving the reason for an edit the diff shows, e.g. "`sendWithRetry` existed only to reopen a closed pool, and the pool is now open from startup" | Deletes the sentence, reason included | "where the diff still says it, leave it deleted". No clause keeps the reason, so this row is finding F2. |
| `:458-465` open-question rule | A question that bears on the change and that neither the code nor a maintainer settles, e.g. whether a retry storm recurs under production load | Drops it, or keeps it as an open Scope question | None for this branch. The rule names only "answered by the code" and "only a maintainer can settle". Finding F4. |

Not findings: `:98`, `:288`, `:763`.

## Item 3a: level, placement, and the environment

The rules sit where a reader looks: slot rules in §2 Commit body (`:80-96`), the What rule in §2 "What each paragraph must earn" (`:342-347`), and the checklist items in §8. The gate passes. The three version registrations agree at 1.4.0, but the bump itself is F6. The change adds no test, so there is no test level to check.

## Item 4: names by content, not by position

- **T1 (taste).** `SKILL.md:475` cites "(§2, slot 2)" by number where the slot has a name, "Impact and trigger". The example at `:357` also says "the first sentence". The file numbers its slots throughout, so the reviewer's preference is the name, and the request will likely be declined.

## Item 5: the failure report

Analogue: each rule's detection in the §8 checklist.

- The identifier rule has no detection (F5).
- The Translation item detects by deletion, which removes the reason clause that the rule keeps. The detection does not test the rule (F2).

## Item 6: what the writer says it verified

No red run or mutation verdict applies to a skill. The commit states that the current open-question rule and the What-slot example "were not re-run". The What-slot example also fails its own rule (F1), which the skill names as a finding. See F7.

## Item 7: siblings of the change

- Versions: the three registrations agree (checked by the gate). See F6.
- `README.md` agrees with the rule and contradicts the checklist (F2).
- `references/merge-model.md`, the trigger instruction file (unchanged), `docs-page-authoring`, and `english-developer-style` §7 contain no conflicting statement; I grepped them.
- No deployed copy of this skill is tracked, apart from `agent-packages/` and `research/`.
- No sentence counts the checklist items.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The What-slot After example states an outcome in prose, which the rule assigns to User-visible changes, and restates an edit the rule says to cut. The commit's claim that it "no longer puts an outcome in prose" is false. | substantive | `SKILL.md:353-355`, against `:342-344` and `:357-359` | Rewrite the After to keep only the reason ("`sendWithRetry` existed only to reopen a closed pool") and leave the outcome to the User-visible line. Or correct the commit claim. |
| F2 | The Translation checklist item deletes a sentence's reason with its edit. It contradicts the rule's "state the reason" and `README.md:27`, and its "diff still says it" is broader than the rule's "one hunk". | substantive | `SKILL.md:826-827`, against `:342-344`; `README.md:26-27` | Make the item cut only the clause the diff shows, keep the reason rewritten, and use the rule's one-hunk test. |
| F3 | For a defect an audit found that also has an observed symptom, "end the sentence at what found it" conflicts with "carry what a person observes". The Skip-when column also carries a requirement, not a skip condition. The changelog row repeats the ambiguity. | substantive | `SKILL.md:81`, `:90-96`, `:475`, `:803-806` | State that an observed symptom is quoted, and the end-at-finder rule applies only when none is observed. Move the audit requirement out of the Skip column. |
| F4 | The open-question rule has no branch for a question that bears on the change and is settled by neither the code nor a maintainer, e.g. one needing a production measurement. | substantive | `SKILL.md:458-465` | Add the branch: keep it in Scope with the measurement it needs, or give the outcome the rule requires. |
| F5 | The identifier rule ("name it once") has no §8 checklist item, though the commit says each fix has one. | substantive | `SKILL.md:345-347`; §8 at `:798-862` | Add a checklist item for public identifiers named once, or stop claiming every fix has one. |
| F6 | The version bump 1.3.0 → 1.4.0 in three files is claimed by no sentence. The series bumps the minor on every feat commit. `apm-authoring` says to bump on contract change, "not on every prose edit". | substantive | `apm.yml:2`; root `apm.yml:168`; `.claude-plugin/marketplace.json:291` | Name the bump in the commit message as a contract change (the new checklist items and the slot-2 condition), or move it to the release commit. |
| F7 | The final wording of the What rule, the open-question rule, and the Translation item has no run. The writer says so, and the What example fails its own rule (F1). | substantive | Commit message; `SKILL.md:342-359`, `:458-465`, `:826-827` | Run the final wording on the `sendWithRetry` input and on a bad draft, and state the results in the commit. |
| T1 | Slot numbers used as names: "(§2, slot 2)" and "the first sentence". | taste | `SKILL.md:475`, `:357` | Name the slot "Impact and trigger" and the sentence by its content. Expect this to be declined. |

## Not checked

- The drift script was not run, because the change has no code.
- The blind drafts behind the commit's numbers were not re-run, since that needs a model run.
- `make check` was run as `apm pack --check-versions --check-clean --dry-run` directly, with the Makefile's flags, not through `uvx`.
- The markdown linter and super-linter were not run.
- The research classifier script was not run; its bash block is unchanged.
- The test suite was not run.
- No file was changed and nothing was committed.
