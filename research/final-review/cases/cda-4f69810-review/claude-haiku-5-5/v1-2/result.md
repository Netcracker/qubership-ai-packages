# Final review: `d79c43d..HEAD` (commit 4f69810)

**Setup.** The change is one commit, `4f69810 feat(change-description-authoring): stop drafts from inventing symptoms and translating hunks`. It has no code, so the form runs through its analogues (§2a). No task statement was handed over and I did not ask, so the claimed cases come from the commit message and the README hunk. No previous report exists.

**Skills read.** `final-review` (the form), `english-developer-style` (from the skills directory), and the artifact itself, `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, in full. The authoring skill for a skill package is `apm-authoring`, which is not in the skills directory. I used the repo copy and read only its rules 1 and 2 (lines 221–290). `test-authoring` was not loaded because there are no tests.

**Scripts.** `comment-drift.py d79c43d… HEAD` ran with exit 0 and printed nothing, because the diff has no code members. `make check` (apm version alignment, dry run) passed with exit 0, and `make check-descriptions` passed (27 descriptions within 1020 characters). The tree is still clean.

## Item 1: comments consistent with the code and with each other

Finding 1 is below. Rule 1 in the slot 2 paragraph (name what found a defect, then end the sentence) conflicts with the derived-consequence paragraph that follows it. The derived paragraph allows a traced consequence for any defect, and a defect found by code reading is exactly the case where a consequence is derived. The changelog row and the checklist follow only the first rule. Nothing else in the file contradicts another part. The wording checks found no em-dashes, double hyphens, clefts, or `currently` in the added lines, so there is nothing to report there.

## Item 2: claimed cases covered

The claims taken from the commit message are these:
- Audit or code-reading defects are described by what found them, and the changelog names the condition alone. This is at SKILL.md:90–96, changelog row 475, and checklist 803–806.
- A derived consequence is written only when traced and marked as derived (98–101).
- "Say so" is kept for a defect with no symptom by construction (94–96).
- A hunk-recovered sentence is cut, and a changed public identifier is named once (342–347, with the pointer at 762–764).
- A rejected alternative is stated as a fact about the merged code (369–382, checklist 832–834).
- An open question is answered, kept in Scope, or dropped (458–465, scope row 199, checklist 835–838, README 26–30).
- The Translation checklist item is at 826–827.

Each claim has a home in the text. The Translation item contradicts the identifier rule (finding 3).

Unclaimed hunks: the commit message does not mention the version bump in `agent-packages/change-description-authoring/apm.yml:2`, `.claude-plugin/marketplace.json:291`, or `apm.yml:168`. It also does not mention the README hunk at lines 26–32. Previous feature commits bumped the same three files, so the bump is probably deliberate, but no sentence claims it. Finding 4 covers both.

No command line was added.

## Item 3: boundaries, partitions, and the negative control

Every drafted case in the message is audit-found. No run covers a defect with an observed symptom, which is the control where slot 2 must still quote the literal. Nor does any run cover a defect with no symptom by construction. Finding 2 covers this.

**Table of added instructions:**

| Instruction | Input it does not serve | What the agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there." (SKILL.md:91–93) | An audit-found defect whose reproduction throws a literal exception | "An audit found this." R3 loses the string it greps for | "…; where a reproduction shows the symptom, quote the diagnostic as a literal" |
| "A consequence derived from the code earns a sentence only after it is traced…" (98–101) | A code-reading defect whose trace reaches no caller, such as a leak with nothing logged | Nothing, or an untraced consequence, depending on the reader | "…; where the trace reaches no caller, the no-symptom sentence above applies" |
| Translation checklist item (826–827) | A rename of a public flag whose sentence also carries the decision | The sentence is deleted with its identifier, and the reason goes too | "…except a public identifier the change adds, removes, or renames; keep the reason, rewritten" |
| "Name what changed that the diff does not show" (287–289), rejected-alternative rule (369–382), open-question rule (458–465) | None found | Output correct for the inputs I checked | none needed |

Item 3a: no test was added. The rules sit in the right sections (§2 slot rules, §3 changelog, §8 checklist). The gate runs offline and passes (`make check`, `make check-descriptions`).

## Item 4: names by content, not by position

One taste finding (finding 8): the What-slot example refers to "the first sentence" (357–358). The sentence is named by its position, though it could be named by its content.

## Item 5: the failure report

The Translation checklist item is the detection for the What-slot rule. It detects deletion of whole sentences, so it fires on reasons and identifiers that the rule says to keep. That is finding 3. The derived rule's detection ("traced in the code and marked as derived", 803–806) does match its rule.

## Item 6: what the writer says it verified

The message states its evidence. It also states that the current open-question rule and the What-slot example were not re-run, and that translation "persists in about one draft in two". The Translation checklist item shipped with no run at all. Finding 6 covers this. A taste note: the drafting counts in the message (14 symptom drafts, plus 4 and 7 in the other rows) cannot be reconciled to "over fifteen" without knowing which drafts overlap.

## Item 7: siblings of the change

No member was added to a set, so the set checks do not apply. No prose count of checklist items or slots changed. `git grep` finds no other copy of this skill and no slot or section-number reference that the change moved. Sibling skills cite the package by name only.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Slot 2 says a defect found by reading or audit "ends there", but the next paragraph allows a traced derived consequence for any defect. The changelog row and the checklist follow only the first rule. | Substantive | `SKILL.md:90–101`; `:475`; `:803–806` | Decide whether a traced, marked derived consequence may follow a defect found by reading or audit. State that the same way in slot 2, the changelog row, and the checklist. |
| 2 | Slot 2's "end the sentence there" drops an observed diagnostic when the defect was also found by audit. The partition where a symptom is observed has no run. | Substantive | `SKILL.md:91–93` | Add "where a reproduction shows the symptom, quote the diagnostic as a literal". Run one draft on an observed-symptom defect, and check that the literal survives. |
| 3 | The Translation checklist deletes any sentence the diff also says. That removes reasons and public identifiers, which the rule says to keep. README line 26–27 says "its reason stays". | Substantive | `SKILL.md:826–827` vs `:342–347`; `README.md:26–27` | "…where the diff still says it and the sentence is neither a reason nor a public identifier the change adds, removes, or renames; a reason is kept, rewritten as the reason." |
| 4 | The version bump 1.3.0 to 1.4.0 (three files) and the README hunk are not claimed by any sentence of the commit message. | Substantive (form rule: an unclaimed hunk is a finding) | `agent-packages/change-description-authoring/apm.yml:2`; `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `README.md:26–32` | Add a sentence to the commit message that claims the bump and the README summary, or move them to their own change. |
| 5 | The new rules and examples rest on drafts of earlier wording. Current open-question rule, the What-slot rule (persists in about one draft in two), and the Translation item have no run on their current wording. | Substantive | commit message, "not re-run" sentence; `SKILL.md:458–465`, `:342–359`, `:826–827` | One run of the current wording on the same drafts, reported with its count. |
| 6 | Drafting counts in the message do not reconcile to "over fifteen" without the overlap. | Taste | commit message | State the total number of drafts. |
| 7 | The "Skip when" cell for Impact carries a required action ("the body names what found it"). | Taste | `SKILL.md:81` | Move the action out of the skip cell. Expect this to be declined. |
| 8 | "The first sentence says why" refers to a sentence by position. | Taste | `SKILL.md:357–358` | Name the sentence by content, such as "the sentence that says the pool opens at startup". |

**Not checked:** I did not run the drafts or any Vale or English linter. I did not check the `research/change-description-authoring` directory for the message's "no cases" claim, and I did not check the commit message's draft counts against the drafts themselves. I used `/tmp` for one make output file and have deleted it.
