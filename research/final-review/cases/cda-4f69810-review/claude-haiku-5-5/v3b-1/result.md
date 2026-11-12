# Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Scope and inputs.** One commit, no code. It edits one skill (`agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`), its README, and three version fields. Per §2a the form applies through analogues. The task statement was not handed over, so item 2's claims come from the commit message alone, and the class-comment and task-statement inputs do not apply. No previous report exists, so there is no §4 table. The drift script was not run because no source code changed. Loaded: `english-developer-style` from the skills directory. `apm-authoring` is not in that directory, so I did not load it; the rule names I cite from it are as the form quotes them.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| §8 Translation checklist says to delete every What-slot sentence the diff still states. §2 says to keep the reason as its own sentence and to name public identifiers once. Applied literally, the checklist drops the reason the rule keeps, and drops the identifier the rule keeps. | substantive | `SKILL.md:826-827` vs `342-347` | Rewrite the item: delete the edit, keep its reason, and name a public identifier once. |
| The audit trigger "Where reading the code or an audit found the defect" has no condition that the symptom was unobserved. A defect reported with an exception, then located by reading the code, is "found by reading the code", so its observed symptom is dropped. R3 then loses the grep string. | substantive | `SKILL.md:90-92`; also the table row at `:81` and changelog part 3 at `:475` | Make the trigger "where no one observed the symptom". |
| The What-slot After example fails its own rule. "with the pool open from startup it sends directly" is the edit the hunk shows (`sendDirect` for `sendWithRetry`). The §8 deletion test would cut it. | substantive | `SKILL.md:353-355` | Cut that clause and keep "used sendWithRetry only to reopen a closed pool" as the reason. |
| The version bump 1.3.0 → 1.4.0 in three files is a hunk no sentence of the commit message claims. Earlier feat commits (`d79c43d`, `51b35c9`, `985bf80`) bump the same way, so it is the convention. | substantive (form rule, one-line fix) | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168` | One sentence in the commit body naming the bump. |
| The open-question rule was rewritten and not re-run, per the commit's own statement, and it has no bad/good example. | substantive | `SKILL.md:458-465` | A blind draft run against that wording with a bad case, or a bad/good example in the rule. |
| The paste-ready merge-model block still lists "symptom" as a required element of every commit body. An agent following it predicts a symptom for an audit-found defect, the case this commit targets. | substantive (sibling not updated) | `references/merge-model.md:24, 38, 51, 63` | Add "or what found it, where no symptom was observed" at those four places. |
| The Skip-when cell for slot 2 carries a requirement ("the body names what found it"), so an audit-found defect can read as skipped. | taste | `SKILL.md:81` | Move the requirement out of the skip column. |
| "(§2, slot 2)" refers by ordinal where the slot has a name. | taste | `SKILL.md:475` | "(§2, the Impact and trigger slot)". |
| The README summary of the translation rule omits the public-identifier exception. | taste | `README.md:25-27` | Add "public identifiers excepted". |

Taste findings are offered, not requested. Churn was not reported.

## Items

**1. Comments consistent with code and each other.** Analogue: statements the changed files make about other files. Cross-references resolve: §8 exists, §7 points to the What slot, §5 names identifiers, and §2 "what changed that the diff does not show" is present. The conflicts are S1 (checklist against rule) and T3 (README). Also the check that a rule's own examples obey it found the After example (S3).

**2. Claimed cases covered.** Each claim in the commit message has a rule and a checklist line:
- Audit-found defect ends at what found it: slot 2, `:90-96`, and changelog part 3. Trigger finding S2.
- Derived consequence traced and marked derived: `:98-101`; checklist `:803-806`.
- "Say so" only for no symptom by construction: `:94-96`.
- Translation cut, reason kept: `:342-347`; checklist conflicts (S1).
- Public identifier named once: `:345-347`; §5 `:683-685`.
- Rejected alternative as merged-code fact; obstacle removed is a step: `:369-373`; checklist `:832-834`.
- Open question answered, maintainer-only to Scope, dropped only if off-topic: `:458-465`; Scope row `:199`; checklist `:835-838`.

Commands: the added text has none to run. Hunks: every hunk is claimed except the version bump (S4). The README hunks are claimed by the summary sentence.

**3. Boundaries, partitions, negative control.** The instruction table below. Pre-existing state: the rules read no state an earlier version wrote, so none applies.

**3a. Level and placement.** Rules sit in their slots, with checklist lines and a README summary, as the siblings do. The skill-description gate (`scripts/check-skill-descriptions.py`) could not run because PyYAML is missing and there is no network. The frontmatter is unchanged by this diff, so the gate is not affected.

**4. Names by content.** One ordinal, T2. No new headings or case names.

**5. Failure report.** Every rule with a detection is reached by a checklist line, except the identifier exception, which S1 covers.

**6. What the writer says it verified.** The commit states its drafts, and that the open-question rule and the What-slot example were not re-run. The What-slot example also fails its own rule (S3). The open-question rule needs a run (S5).

**7. Siblings.** The three version fields agree at 1.4.0, but the bump is unclaimed (S4). The README is updated. The merge-model block is stale (S6). The instructions file names only the trigger, so it needs no change. The counts of slots and parts are unchanged.

### Instruction table (§2a)

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Slot 2: audit or code-reading defect ends at what found it | Bug reported with an exception, then located by reading the code | "Found by reading the code.", trace dropped | None; the trigger fires. **S2** |
| Slot 2: derived consequence only after tracing | Missing call with a later catch in the code | Traces the catch, writes nothing | "only after it is traced" |
| Slot 2: "say so" for no symptom by construction | Leak on an error path with nothing logged | States the absence | Holds |
| What slot: translation cut, reason kept | The pool change, following the After example | Keeps the edit clause as well | The example itself fails. **S3** |
| What slot: public identifier named once | Private helper removed | Does not name it | Holds (scope is public) |
| Rejected alternative: fact about merged code | Alternative rejected for an obstacle the change removed | States the mechanism as a fact | Holds |
| Open question: answered from code, or Scope if maintainer-only | Question only a maintainer answers | Scope entry | Holds; untested. **S5** |
| Changelog: audit-found defect gives the condition alone | Same as row 2 | Condition only | Same as row 2. **S2** |
| §8 Translation checklist | What-slot sentence carrying a reason | Deletes it | Conflicts with the rule. **S1** |

The Symptom, Alternatives, and Discussion checklist lines restate the rows above, so they are not separate instructions.

## Not checked

The drift script did not run (no code changed). The skill-description gate did not run (PyYAML missing, no network). `apm-authoring` was not loaded. The blind-draft numbers in the commit message were not verified, and I did not re-run any draft. No test suite applies to this change. I did not check the `research/` directory.
