# Final review: `d79c43d..4f69810`, change-description-authoring 1.4.0

There was no separate task statement. The claimed cases come from the commit message alone, and there are no test class comments.

This change has no code: it edits a skill (`SKILL.md`), its package README, and three version fields. Each item below therefore uses the analogue in final-review §2a. I loaded `english-developer-style` from the given skills directory. I read the repository's `apm-authoring` conventions through `agent-packages/AGENTS.md` instead of loading that skill. I did not run `comment-drift.py`: the change has no code members for it to parse. There is no previous report, so there is no carry-over table.

## Item 1: comments consistent with the code and with each other
**Analogue used:** the statements one changed file makes about another, and the skill's statements about its own examples.

- **README vs SKILL on derived consequences.** `README.md:28-29` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code once it is traced to the caller and marked as derived, and the Symptom checklist item (`SKILL.md:803-806`) accepts one. A README reader would think the skill forbids derived consequences.
- **The What-slot *After* puts an outcome in prose.** The commit message says the example "no longer puts an outcome in prose". Its first sentence still does (`SKILL.md:353-354`): "a caller that runs before startup completes fails at once instead of opening the pool on demand". The text under it (`:357-359`) assigns that same outcome to "User-visible changes". That contradicts "A fact stated in slot 3 is not restated in slot 2" (`SKILL.md:231`). Someone copying the exemplar writes the outcome twice.
- Checked and true:
  - §7 now points to the What-slot rule (`SKILL.md:763-764`).
  - §2 says "what changed that the diff does not show" (`:288`).
  - The slot-2 table cell, the prose and the checklist all use "by construction".
  - The Scope table row (`:199`) matches the open-question paragraph (`:458-465`).
  - The changelog part 3 row cites the slot-2 rule correctly.

## Item 2: claimed cases covered
**Analogue used:** each claim in the commit message, matched to the section that handles it and the checklist item that detects it.

| Claim | Section | Checklist detection |
| --- | --- | --- |
| Audit or code-reading defect: name what found it, end the sentence there | `:81`, `:90-94` | Symptom |
| Changelog entry: the condition alone | `:475` | Symptom asks whether "the sentence end[s] at what found it", which is the slot-2 rule. Nothing checks "condition alone", so a changelog line that names the audit, or a marked derived consequence, passes. **Finding.** |
| Derived consequence traced to the caller and marked as derived | `:98-101` | Symptom |
| "Say so" kept for no symptom by construction | `:94-96` | Symptom |
| What slot: one-hunk sentence is translation, even under a lead-in | `:342-344` | Translation (weaker than the rule; see Item 5) |
| Public identifier named once | `:345-347` | None. The Translation item works against it; see Item 5 |
| §7 points to the rule; §2 says "does not show" | `:763`, `:288` | — |
| Rejected alternative stated as a fact about the merged code; an obstacle the change removes is a step | `:370-373` | Alternatives |
| Open question answered, kept in Scope, or dropped | `:199`, `:458-465` | Discussion |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-355` | — |

- **Commands:** the changed files add no command lines.
- **Unclaimed hunks.** No sentence of the commit message claims:
  - the version bump 1.3.0 → 1.4.0 in `apm.yml:168`, `.claude-plugin/marketplace.json:291` and the package `apm.yml:2`. Earlier commits on this package say "Version 1.2.0 to 1.3.0.";
  - the two README "What it covers" hunks.

## Item 3: boundaries, partitions, and the negative control
**Analogue used:** the artifacts and situations the change claims, and the trials it reports.

- **Untested artifacts.** All the trials were "blind drafts of one pull request description". The change also rewrites the commit-body slot-2 rule (`:81`, `:90-101`) and changelog part 3 (`:475`). Those two artifacts have no trial evidence, and the commit message does not say so.
- **Audit-found, then reproduced.** `:92` says "end the sentence there". It does not say what happens when a regression test or a run then reproduces the failure, which makes the symptom observed. A writer could drop the reproduced diagnostic, the string R3 greps for. The checklist's "quoted from an observation" points the other way.
- **No negative control.** No draft with an observed, quoted symptom was run to show that the new slot-2 wording does not suppress a real diagnostic.
- **Pre-existing state:** none applies. This is a version bump of a text package with no persisted format.
- **Limits and replaced mechanisms:** none apply.

## Item 3a: level, placement, and the environment
**Analogue used:** where each rule lives, layout against sibling packages, and the repository's own gates.

None to report. The rules are in `SKILL.md`, the summary in the README, and the versions are aligned across three files. `make check` exits 0, with only the pre-existing `license:` warning. `make check-descriptions` reports "all 27 skill descriptions are within 1020 characters".

## Item 4: names by content, not by position
**Analogue used:** the change's own headings, cross-references, and case names.

None to report. "Slot 2" and "slot 3" are the IDs the skill's own tables define. "The first sentence" (`:357`) points at a two-sentence example directly above it. The new checklist items have names (Translation, Discussion).

## Item 5: the failure report
**Analogue used:** whether the checklist reaches every rule, and whether each detection checks the rule rather than something weaker.

- **Translation check is weaker than the rule.** The checklist says "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" (`SKILL.md:826-827`). That test misses the case the rule names: a hunk restated "under a lead-in that states a reason". Deleting such a sentence loses the reason, which the diff does not show, so the sentence is kept with its edit intact. The commit message reports translation persisting in about one draft in two, which is what this gap predicts.
- **Translation check conflicts with the identifier exception.** A sentence naming a newly added system property is recoverable from one hunk. The deletion test removes it, but `:345-347` says to keep it.
- **Changelog "condition alone"** has no detection (see Item 2).

## Item 6: what the writer says it verified
**Analogue used:** an exemplar that passes the rules and a bad case that fails them.

- The commit message gives counts over fifteen blind Opus drafts. It says plainly that the current open-question rule and the revised What-slot example were not re-run, and that the package has no `research/.../cases/`. I confirmed that only phase files exist there.
- **The flagship exemplar fails the new rule.** Applying the rewritten Translation test to the skill's existing PR exemplar fails it. "The orphan sync is requeued with backoff on failure instead of being dropped" (`SKILL.md:254-255`) is recoverable from one hunk, so the checklist deletes it. Yet it is exactly the "behavioral change" the What-slot table (`:196`) asks for. The rule never says whether the caller-facing behavioral change counts as translation.
- The What-slot *After* also fails §2 `:231` (see Item 1).
- The drafts behind the two new "measured:" claims (`:100`, `:464`) are not in the repository. The same is true of the skill's earlier measurements, so this is existing practice, not a new defect.

## Item 7: siblings of the change
**Analogue used:** index, marketplace, umbrella, and sibling cross-references.

None to report.
- The marketplace entry, the root `apm.yml` and the package `apm.yml` all carry 1.4.0, and `make check` confirms the index is in sync.
- The frontmatter description is unchanged and the scope was not widened.
- The instructions file lists no rules.
- I searched `english-*-developer-style` for symptom and open-question wording and found nothing that now conflicts. Its "a bug report is provenance" rule (`:466-470`) agrees with the change.
- No set gained a member, so no count is stale.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The Translation check deletes a sentence whose content the diff shows. That misses a hunk restated under a reason lead-in, the case the rule names, and it deletes the public identifier the rule keeps. | Substantive | `SKILL.md:826-827`, vs `:342-347` | Make the check flag any clause the diff shows, not only whole sentences, and make it exempt a public identifier named once. |
| 2 | The new rule makes the existing PR exemplar's What sentence ("requeued with backoff … instead of being dropped") count as translation, even though the slot table asks for the behavioral change. | Substantive | `SKILL.md:254-255`, `:196`, `:342` | Say whether the caller-facing behavioral change is exempt from the translation rule, and re-apply the rule to that exemplar. |
| 3 | The What-slot *After* states the outcome ("fails at once") in prose and then sends the same outcome to User-visible changes, which `:231` forbids. The commit message says the example no longer does this. | Substantive | `SKILL.md:353-359` | Rewrite the *After* so the prose gives only the reason, or say why this restatement is allowed. |
| 4 | The README says an audit-found defect gets "neither a predicted failure", but the skill allows a traced consequence marked as derived. | Substantive | `README.md:28-29` vs `SKILL.md:98-101` | Bring the README in line with the skill. |
| 5 | Changelog part 3, "the condition alone", has no checklist detection. The Symptom item checks the slot-2 form instead. | Substantive | `SKILL.md:475`, `:803-806` | Add the changelog variant to the Symptom or Changelog checklist item. |
| 6 | The slot-2 rule does not cover an audit-found defect later reproduced by a test or a run, so a writer may drop the observed diagnostic. | Substantive | `SKILL.md:92-94` | State that a reproduced diagnostic is quoted as observed. |
| 7 | The commit-body and changelog rules were changed with no trial on either artifact, and no observed-symptom control was run. The commit message does not mention either gap. | Substantive | commit message; `SKILL.md:81`, `:475` | Run those partitions, or say in the message that they were not run. |
| 8 | The version bump in three files and the README hunks are not claimed by any sentence of the commit message. | Substantive (trivial) | `apm.yml:168`, `marketplace.json:291`, package `apm.yml:2`, `README.md:26-32` | Add "Version 1.3.0 to 1.4.0." and a clause on the README to the message. |
| 9 | Putting the audit case in the slot-2 "Skip when" cell suggests slot 2 is skipped for an audit-found defect, while the prose makes "what found it" the slot's content. | Taste | `SKILL.md:81` | Move the audit clause into the "Answers" cell. |

The review did not re-run any drafts or check the commit message's trial counts against the drafts, which are not in the repository. It did not run `comment-drift.py` (there is no code to parse), and it did not review the prose for style.
