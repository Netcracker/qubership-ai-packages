## Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Setup.** The change is an instruction file: a skill (`SKILL.md`), its README, and version entries in three manifests. No code or tests changed, so §2a's analogues apply. I used the commit message as the claim source. There was no separate task statement and no previous report, so §4's table is empty.

**Skills loaded.** `english-developer-style` from the given skills directory. `apm-authoring`, which §2a names for a skill package, is not in that directory, so I could not load it and used §2a's own analogues instead. `test-authoring` was not loaded because the change has no tests.

**Mechanical checks run.**
- Drift script (`comment-drift.py d79c43d HEAD`): no output, since no code member moved.
- `make check` (`apm pack --check-versions --check-clean --dry-run`): exit 0, "Version alignment OK".
- `scripts/check-skill-descriptions.py`: OK.
- `research/change-description-authoring/check-classifier-target-ref.sh`: exit 0; `bash -n` and `shellcheck` clean.
- The tree is still clean. `make check` wrote its log to `…/T/tmp.OXuDSJC8Dr/make-check.out`, outside the repository.

### Item 1: comments consistent with the code and with each other

Findings: S1 and the cross-reference in S3.

Checked and consistent: the slot-2 table row against the slot-2 paragraph (`SKILL.md:81`, `:90–101`); the README bullets against the rules; §2's "what changed that the diff does not show" (`:285`); the §6 "No paraphrase" line (`:764`) against the What-slot rule (`:342`); the Rejected-alternatives paragraph (`:369`) against §8 Alternatives.

### Item 2: claimed cases covered

| Claim in the commit | Detection in the checklist (§8) |
| --- | --- |
| Audit-found defect ends at what found it (`:92`) | Symptom item (`:803–806`) |
| Changelog names the condition alone for an audit-found defect (`:475`) | **none**, see S3 |
| Traced consequence stated as derived (`:98`) | Symptom item |
| "Say so" only for a defect with no symptom by construction | Symptom item |
| Translation rule with identifier exception (`:342–347`) | Translation item (`:826`), which contradicts the exception, see S2 |
| Mechanism as a fact about the merged code | Alternatives item |
| Open questions answered, kept, or left out (`:458`) | Discussion item |

The commit says "each fix … has a checklist item". That holds for every fix except the changelog row (S3) and the identifier exception (S2).

Hunks against claims: every hunk maps to a claim except the version bump (S4). The README hunk restates the rules, so I did not count it.

### Item 3: boundaries, partitions, and the negative control

Table for the added instructions (§2a):

| Instruction | Input it does not serve | What an agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, … end the sentence there" (`:91–93`) | A code-read defect whose consequence is traced to a caller | Stops before the traced consequence | None. The next paragraph permits it (S1) |
| "Delete each sentence of the What slot … leave it deleted" (`:826`) | A change that adds a public flag | Deletes the sentence naming the flag, so the flag appears nowhere | None. The exception at `:346` is not in the checklist (S2) |
| "A consequence … earns a sentence only after it is traced" (`:98`) | A leak with nothing logged | Nothing traced, so nothing written | Own condition; not a finding |
| "Name it once" (`:346`) | A renamed method used in six files | Named once in the What slot | Own clause; not a finding |
| "Leave a question out only when it does not bear on this change" (`:463`) | An unrelated future question | Left out | Own clause; not a finding |

Other partitions: the arms of the code-reading/audit and observed-symptom split leave a defect found by a failing test unnamed. A test failure is an observed symptom, so the rule still reaches it. Not a finding.

The negative control is the table: its rows with no ending clause are S1 and S2. Settings, limits, and pre-existing state do not apply to this skill.

### Item 3a: level, placement, and the environment

The rules sit in the right places: slot 2 for symptom rules, the What-slot section for translation, and §8 for checklist items. The repository gates listed above pass. The version bumps match across `apm.yml` and `marketplace.json`. Not a finding.

### Item 4: names by content, not by position

T1 only. The new changelog row refers to "(§2, slot 2)" (`:475`). The slot is named "Impact and trigger" in the table at `:81`.

### Item 5: the failure report

No finding beyond S3. The Symptom, Alternatives, and Discussion items each detect the rule they are attached to.

### Item 6: what the writer says it verified

The commit states its evidence: fifteen blind drafts, with the before and after counts. It also states that the current open-question rule and the What-slot example were not re-run (S5). The slot-2 and What-slot rules each have a named before/after. The open-question rule has none.

Applying the rules to the change's own examples: the What-slot After example keeps "it sends directly", which is the edit the diff shows (T2). The changelog row has no example (S3).

### Item 7: siblings of the change

I searched the other packages for the rule's wording (`has not been seen`, `say so`, `no symptom`, `audit found`, `open question`). No sibling restates the slot-2 or open-question rule. `docs-page-authoring` and `problem-report-authoring` only name this skill as the owner of change descriptions. The slot-count sentences are unchanged.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| S1. Slot 2 says a code-read defect "ends there", but the next paragraph allows a traced consequence for the same defect. A reader cannot tell which applies. | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:91–101` | Scope the "end there" rule to the case with no traced consequence, or say the traced consequence follows the finding. Make the checklist at `:805–806` match. |
| S2. The Translation checklist deletes every What-slot sentence whose content the diff shows. That removes the public-identifier sentence the rule at `:345–347` keeps. | substantive | `SKILL.md:826` against `:345–347` | Add the exception to the checklist item: "unless it names a public identifier the change adds, removes, or renames, which is named once". |
| S3. The changelog rule "for a defect an audit or a code reading found, the condition alone" has no checklist item, despite the commit's claim. Its cross-reference "(§2, slot 2)" points to a paragraph that says nothing about changelogs. | substantive | `SKILL.md:475`; the Changelog checklist item at `:842` | Add a clause to the changelog checklist item for an audit-found defect. Point the reference at the rule that states it. |
| S4. The 1.3.0 → 1.4.0 bump in `marketplace.json`, root `apm.yml`, and the package `apm.yml` is not claimed by any sentence of the commit message. `make check` passes, and earlier feat commits bumped the same files. | substantive (by the form; low stakes) | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Add one sentence to the body that says the package goes to 1.4.0. |
| S5. The open-question rule has no named exemplar and no bad case. The commit says it was not re-run against the current wording. | substantive | `SKILL.md:458–465` | Name an exemplar and a bad case for the rule, as slot 2 and the What slot do, and run them. |
| T1. The changelog cross-reference "slot 2" is an ordinal where "Impact and trigger" is available. | taste (I prefer the name) | `SKILL.md:475` | Use "(§2, Impact and trigger)". |
| T2. The What-slot After example keeps "with the pool open from startup it sends directly", the edit the diff shows. The deletion test in the rule would cut it. | taste (I prefer the reason alone) | `SKILL.md:354–355` | End the sentence at the reason, or leave it as is. |
| T3. The slot-2 "Skip when" column carries an instruction for a defect that is not skipped. A reader could take it as a skip condition. | taste | `SKILL.md:81` | Move the audit clause out of that column. |

No churn was reported.

### What the review did not check

I did not run the full `make test` suite, and I did not run the blind-draft trial, so the commit's measurements are unverified. I did not verify the claim "no cases under research/" beyond listing the directory, which holds phase documents and the gate script and no blind-draft cases. I did not load `apm-authoring`, which §2a names, because it is not in the skills directory I was given.
