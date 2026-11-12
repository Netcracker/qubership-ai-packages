# Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message alone. The commit's class comments do not apply, since a skill has no tests. There is no previous report. The drift script ran with exit 0 and printed nothing, since the change has no code members. I loaded `english-developer-style` and `apm-authoring` from the given path and read the diff whole. I read the unchanged sections only where a changed line cites them.

**Analogue used.** The change is a skill plus a README and version entries, so every item uses its §2a analogue.

## Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about other sections, files, or the repository.

- Finding 1 (substantive): the trigger "found by reading the code or an audit" overrides the symptom in the same sentence (see Finding 1 below).
- Finding 2 (substantive): the changelog row's "(§2, slot 2)" citation points to a rule that does not say "the condition alone" (see below).
- Finding 3 (substantive): "named once" for public identifiers conflicts with slot 4's exact-text rule, and the scope of "once" is unclear (see below).
- Finding 4 (substantive): the §8 Translation item and the What-slot rule test different things (see below).
- Finding 5: the README, the version triple, and the cross-references to §2, §5, and §7 agree with the skill text.
- Finding 6 (substantive): the What-slot example is followed by a caveat (see below).

## Item 2: claimed cases covered

Analogue: the claimed cases are the rules the commit names, and each rule's detection is the §8 item that checks it.

- Slot 2 audit-found rule (`:92–94`): detected by the Symptom item (`:805`). The detection does not cover the observed-symptom case (Finding 1).
- Derived consequence traced and marked derived: detected by the Symptom item. Covered.
- "Say so" kept for a defect with no symptom by construction (`:94–96`): detected by the Symptom item. Covered.
- Changelog row 3 "condition alone" (`:475`): no detection of its own. The Symptom item names the body only. Finding 2 covers the citation.
- What-slot translation (`:342–343`): detected by the Translation item (`:826`). The two disagree (Finding 4).
- Public identifier named once (`:345–347`): **no detection** (Finding 3).
- Rejected alternatives, mechanism as a fact about merged code, and obstacle removed: detected by the Alternatives item. Covered.
- Open questions answered, kept as Scope questions, or dropped: detected by the Discussion item. Covered as detection, not measured (Finding 7).
- The §7 "same test, sentence by sentence" bullet: covered by the Translation item.

Commands: the change adds no command lines, so none to list. Hunks: the three version bumps and the README have no sentence in the commit message that claims them (Finding 5).

## Item 3: boundaries, partitions, and the negative control

Analogue: partitions are the trigger cases (audit-found, code-read, observed, no symptom). The negative control is the table of added instructions in §2a.

- The audit-found partition has no control for a defect that is both audit-found and observed (Finding 1).
- The open-question rule has three branches (answered by code, maintainer-only, does not bear). Only the first two have examples, and none has a measured run on the current wording (Finding 7).
- The table of added instructions is below. Counted by rule, the change adds or widens about twenty instructions. Two of them have an input their own rule does not serve.
- Pre-existing state, limits, and replaced mechanisms: none apply.

**Table of instructions with a non-served input**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:92` "Where reading the code or an audit found the defect, name what found it and end the sentence there" | An audit-found defect that a user reported with a log line | "An audit found this." with the log line dropped | "only where no symptom has been observed" |
| `:475` changelog row 3 "for a defect an audit or a code reading found, the condition alone (§2, slot 2)" | The same defect, with the log line in the report | The condition with the grep target gone. The cited slot 2 says to name the finding instead. | "only where no symptom has been observed" |

Not findings: `:94–96` (the "say so" clause ends it), `:462–463` (the "does not bear" clause ends it).

## Item 3a: level, placement, and the environment

Analogue: the rules sit in the right file. The README mirrors the skill, and the §8 detections sit in the same file. The registration entries are the ones the repository's gates check.

- `apm pack --check-versions --check-clean --dry-run` exits 0, so the three 1.4.0 entries agree and `marketplace.json` matches what `apm.yml` produces.
- `scripts/check-skill-descriptions.py` exits 0.
- `research/change-description-authoring/check-classifier-target-ref.sh` exits 0. Section 4 is unchanged, so this is not evidence for the change.

## Item 4: names by content, not by position

Analogue: unchanged. Applied to headings, cross-references, and case names.

- Taste (Finding 8): the What-slot caveat says "the first sentence says why" (`:358`), and the changelog row and slot 2 cross-reference refer to "slot 2" by position. Each could be named by content.

## Item 5: the failure report

Analogue: each rule's detection must detect that rule.

- The Public identifier rule has no detection, so its failure report is empty (Finding 3).
- The changelog row's citation tells a reader to look at a rule that says something else (Finding 2).
- The Symptom and Translation detections check their own rules. Finding 4 is the one mismatch.

## Item 6: what the writer says it verified

Analogue: the good and bad cases the change names. The worked examples and the commit's measurements carry them.

- The symptom rule's final wording has two drafts behind it. The commit states this.
- The commit discloses that the current open-question rule and the What-slot example were not re-run, and that hunk translation "persists in about one draft in two" (Finding 7).
- I did not run the drafting experiment, since the evidence is the writer's to state.

## Item 7: siblings of the change

Analogue: the places that list the skill or its counts.

- The README bullets match the skill rules.
- The three version entries are aligned at 1.4.0.
- "Five slots" and "Six slots" are still correct.
- The §2, §5, and §7 cross-references point where they say.
- The `research/` documents name the skill and do not cite the changed rules.
- The other `1.3.0` hit is an unrelated package, `qubership-user-essentials`.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The audit or code-reading trigger drops the observed symptom. An audit-found defect that a user reported is written as "An audit found this." with the log line gone. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:81, :92–94, :805` | Scope the trigger to a defect with no observed symptom. Where a symptom is observed, quote it and let the audit sentence follow. |
| 2 | The changelog row cites "(§2, slot 2)" for "the condition alone", but slot 2 says "name what found it and end the sentence there". | Substantive | `SKILL.md:475` | State the changelog variant in the changelog row only, and fix the citation to the rule it means. |
| 3 | "A public identifier … is named once" has no §8 detection. It also conflicts with slot 4's exact-text rule for the exception class, and it does not say whether "once" means per description or per paragraph. | Substantive | `SKILL.md:345–347`; `:83`; §8 Caller item | Add a §8 item. State the scope of "once", and the exception for the slot 4 `User-visible:` line. |
| 4 | The Translation item deletes "where the diff still says it". The rule keeps a sentence "recovered from one hunk". A sentence spread over two hunks is deleted by the checklist and kept by the rule. | Substantive | `SKILL.md:342–343` and `:826–827` | Make the item and the rule use the same test. |
| 5 | Three version bumps (`.claude-plugin/marketplace.json:291`, `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:3`) and the README (`README.md:23–33`) are not claimed by any sentence of the commit message. `apm-authoring` says to bump only when the contract changes. | Substantive | as listed | Add a sentence to the commit that claims the bump and states the contract change, and one that claims the README. Otherwise move the bump to its own change. |
| 6 | The What-slot example is followed by a caveat about which calls are gone, which `apm-authoring` §2 forbids. | Substantive | `SKILL.md:357–359` | Fold the reason into the rule above, or cut the caveat so the example stands alone. |
| 7 | The open-question rule has no evidence on its final wording. The three branches have one measured run at most, and the commit says the current rule and the What example were not re-run. | Substantive | `SKILL.md:458–466`; commit message | Run one draft per branch on the current wording, or state in the commit that the figures belong to the earlier rule. |
| 8 | "the first sentence says why" names a sentence by position, and "slot 2" names a slot by number where the slot has a name. | Taste | `SKILL.md:358`; `:475` | Name the sentence by its content and the slot by its name. Expect this to be declined. |

## What the review did not check

I did not run any drafting experiment, so the measured figures in the commit are unverified. I read the whole diff but not the full `SKILL.md`, only the sections the changed lines cite.
