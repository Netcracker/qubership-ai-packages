# Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Scope and inputs.** The change is one commit that edits `SKILL.md`, `README.md`, and three version entries. It has no code and no tests. The claimed cases come from the commit message alone, since no task statement was handed over and there are no test class comments. No previous report exists, so §4's table is omitted. The drift script (`comment-drift.py d79c43d… HEAD`) ran and printed nothing, because no code members changed. Its analogue is the §2a reading below. Skills: `final-review` was read in full, and `english-developer-style` was loaded from the given directory. `apm-authoring` is not in that directory, so it was not loaded. Its rule names are not checked here, and I used `final-review` §2a and the file's own rules instead. `test-authoring` does not apply, since there are no tests. Offline gates: `make check` exits 0 with "Version alignment OK", and `make check-descriptions` reports 27 descriptions within the limit.

## Item 1: comments consistent with the code and with each other

Checked: the §7 pointer to the What-slot rule (line 763), the §2 reference to "what changed that the diff does not show" (287–289), the `(§5)` and `(§2, slot 2)` references, and the examples against their rules. The "now" and "no longer" wording appears only inside the quoted examples. Finding S2 is the one statement that reads wrongly.

Outside the change, not charged: §7a (around line 769) cites `english-developer-style` §7 for three rules. The diagnostic-literal rule is §5 there, and the decision test and the causal-link rule are not in §7 at all.

## Item 2: claimed cases covered

| Claim | Where | Detection |
|---|---|---|
| Audit or code-reading defect described by what found it; changelog names the condition alone | 92–93; 475 | Symptom item, 803–806 (see S3) |
| Derived consequence traced to the caller and marked as derived | 98–101 | Symptom item |
| "Say so" kept for no symptom by construction | 94–96 | Symptom item (see S2) |
| Bad and good example for slot 2 and the What slot | 92–93; 349–359 | — |
| Translation; public identifier named once; §7 points here | 342–347; 762–764 | Translation item only (see S1) |
| Rejected alternative: mechanism as a fact about merged code; removed obstacle is a step taken | 371–373 | Alternatives item, 832–834 |
| Open question answered, kept in Scope, or dropped | 458–465; PR row 5 at 199 | Discussion item, 835–838 |
| Checklist gains Discussion and Translation items | 826–827; 835–838 | — |

Hunks: the three version-entry changes are claimed by no sentence (T1). The README bullets restate the rules that the message claims, so they are covered. The change adds no command lines, so the command check is `none`.

## Item 3: boundaries, partitions, negative control

The partitions are the discovery modes (audit, observed failure, no symptom by construction), the question types, and the derived consequence. The observed-failure partition has no rule text, which is S3. The negative control is the table in §2a below. Pre-existing state: `none`, since nothing persistent is replaced. Limits: `none`.

## Item 3a: level, placement, environment

Placement fits: the rules sit in §2's slots and paragraphs, and §8 is the checklist. The version entries in the three files agree, and `make check` passes. Finding S5 concerns placement of one rule.

## Item 4: names by content

T2 (ordinal in the changelog row). Everything else is named by content.

## Item 5: failure report

Two rules lack a full detection. The Translation item detects a weaker property than the rule (S1). The stated-absence ban has no detection (S2).

## Item 6: what the writer says it verified

The writer states measurements and discloses that the final open-question rule and the What-slot example were not re-run. The new instructions were added after bad outputs, and no input where they are noise is reported (S6). The What-slot After example also keeps a hunk clause (T3). I did not run any drafts.

## Item 7: siblings

Checked: the §7 pointer, the README mirror, the marketplace description (still accurate), and the checklist items. Missed siblings are S4 and S5. The examples' identifiers (`QueryExecutor`, `ensureOpen`) appear nowhere else in the repo, so the commit's "avoid the pull request" claim cannot be checked here.

## §2a table: instructions the change adds or widens

| Instruction (line) | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (92–93) | A reported defect whose failure a user saw, then located by reading the code | "Found by reading the code." The observed failure is dropped | None. Needs "where no one has seen it fail" (S3) |
| "…a stated absence does not [look like an omission]" (94–96) | A predicted defect, not yet observed | "It has not been seen to fail" or "no failure was observed" | None. Needs "an absence of observed failure is never stated" (S2) |
| "Delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" (826–827) | A sentence naming a public flag the change adds | The sentence is deleted and the flag name is lost | §2's exception (345–347) is not in this item (S1) |
| "A consequence … earns a sentence only after it is traced to the point where a caller sees it" (98–101) | An internal leak nobody observes | Nothing is written | Its own condition. Not a finding |
| "Leave a question out only when it does not bear on this change" (458–465) | A review question the code answers | The answer, with evidence | "Answered by the code." Not a finding |
| "An obstacle the change removes is a step it took" (371–373) | An alternative rejected for a constraint that still holds | The constraint, stated as a fact about merged code | The mechanism check. Not a finding |
| "In a description, the same test applies sentence by sentence" (763–764) | A one-hunk change | The What slot reduced to its reason | The test itself. Not a finding |

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| S1 | The Translation item deletes a sentence that names a public identifier, which §2 requires to be kept named once. The exception has no detection. | Substantive | `SKILL.md` 826–827 vs 342–347 | Add "except a public identifier the change adds, removes, or renames, which is named once (§2)" to the Translation item and to the checklist. |
| S2 | "A stated absence does not [look like an omission]" reads as licence to write "has not been seen to fail", the misreading the commit message names. No checklist item bans it. | Substantive | `SKILL.md` 94–96; checklist 803–806 | Limit the absence to "no symptom by construction", and add "an absence of observed failure is never stated" to the Symptom item. |
| S3 | The audit trigger "found the defect" also fires for a reported defect with an observed failure, located afterwards by reading the code. The observed symptom is then dropped. | Substantive | `SKILL.md` 92; checklist 805–806; 475 | Trigger on "and no one has seen it fail", and keep a reported failure as the Impact sentence. |
| S4 | The PR description's Why row asks for "the symptom" and has no pointer to the audit rule. The changelog row has one; the PR row does not, though the drafts were PR descriptions. | Substantive | `SKILL.md` 195 | Add "for a defect an audit or code reading found, name what found it, not a predicted symptom (commit body, slot 2)". |
| S5 | The commit body's slot 3 asks for "why not" for alternatives, but the rule against retold obstacles lives only in the PR's What section. | Substantive | `SKILL.md` 82; 371–373 | Add a pointer in the slot 3 row, or one sentence in the body rules. |
| S6 | The added rules were written after bad outputs. No run checks that the new items do not appear where they are noise. The writer discloses that the current open-question rule and the What example were not re-run. | Substantive | Commit message; `SKILL.md` 458–465 | Run one blind draft on a change with no defect and no open question, and report whether the new items appear. Not runnable here. |
| T1 | Version bumps 1.3.0 → 1.4.0 in `.claude-plugin/marketplace.json`, the package `apm.yml`, and the root `apm.yml` are claimed by no sentence. The three prior commits bump the same way, and `make check` passes. | Taste | Commit message | One line naming the bump as the per-change version, checked by `make check`. |
| T2 | "(§2, slot 2)" refers to a slot by ordinal. | Taste | `SKILL.md` 475 | Use "(§2, Impact and trigger)". |
| T3 | The What-slot After example's second clause ends on the edit the hunk shows ("it sends directly"). | Taste | `SKILL.md` 354–355 | Drop the clause, or keep it as the example's point. |
| T4 | The slot 2 "Skip when" cell carries a non-skip instruction for audit-found defects. | Taste | `SKILL.md` 81 | Move that clause out of the "Skip when" cell. |

Churn: none reported.

**Not checked:** no drafts were run, so the measured claims are unverified. The `english-developer-style` wording was checked only where it changes a reading. `apm-authoring` was not loaded, so its rule names are unchecked. The examples' origin is unverified. The `make` gates run offline. Nothing in the repository was changed, and I did not commit.
