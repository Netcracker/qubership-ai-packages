## Final review: `d79c43d..HEAD` (`4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message alone. The change has no code, so the §2a analogues apply. The drift script printed nothing, since the change has no code members. The skill tool could not resolve `english-developer-style` by name, so I read its file at the given path. `test-authoring` was read and does not bear on a change with no tests. The authoring skill for a skill package (`apm-authoring`) is not among the three provided, so I applied the form's analogues without it. No previous report exists, so §4's table is omitted. Line numbers are in `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` unless a file is named.

### Item 1: comments consistent with the code and with each other
Analogue used: every statement the changed files make about another section, file, or document. Section references (§2, §3, §4, §5, §7, §8) resolve. The §7 pointer to the What-slot rule is real (line 762). The Scope-slot row (line 199) agrees with the Discussion rule (lines 458–465).
Finding 2: the Translation checklist item (line 826) contradicts the public-identifier exception in the What-slot rule (lines 344–346).

### Item 2: claimed cases covered
Analogue used: the claims in the commit message, each checked against its rule and its checklist item. Covered: predicted and stated symptoms (slot 2 rule, Symptom item); derived consequences (same item); hunk translation (rule at 342, Translation item, except the identifier exception); rejected alternatives (Alternatives item); open questions (Discussion item); "say so" kept for a defect with no symptom by construction (slot 2 rule); the What-slot "what changed" wording (§2 Why paragraph). Not covered: the identifier exception (finding 2), the audit branch in the changelog row (finding 4), and the PR Why slot (finding 1).
Command lines: the change adds none.
Hunks: every hunk belongs to a claim except the version bump (finding 5).

### Item 3: boundaries, partitions, and the negative control
Analogue used: partitions are the defect kinds the commit claims (predicted, audited, derived, no symptom). The evidence covers one pull-request description, and the commit says so. A defect that is both audited and observed has no stated control (finding 9). Pre-existing state: none. The package is replaced by a later version with no persisted format, so no state is met.

### Item 3a: level, placement, and the environment
Analogue used: where each rule lives and whether the registration matches. The rules live in the canonical SKILL.md, the README summarizes them, and the checklist is in §8. Versions read 1.4.0 in `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, and `apm.yml:168`. `make check-descriptions` was not run, since the frontmatter description is unchanged. `make check` needs `uvx` and the network, so it was not run.

### Item 4: names by content, not by position
Finding 8: the new changelog row cites "slot 2" where the slot has a name, "Impact and trigger".

### Item 5: the failure report (checklist reach)
Analogue used: each rule that has a detection must be reached by the checklist. The Symptom, Alternatives, and Discussion items reach their rules. Not reached: the identifier exception (finding 2) and the changelog audit row (finding 4). The commit says "each fix has a checklist item", so that claim is false for these two.

### Item 6: what the writer says it verified
The commit states its evidence: over fifteen Opus drafts on 1.0.1, before the outcome slot and length rules landed. It also says the current open-question rule and the What-slot example were not re-run. Slot 2 has a bad and a good example. The Discussion rule has none (finding 7). The What-slot example fails the Outcome rule it is meant to exemplify (finding 3), and the commit says it does not.

### Item 7: siblings of the change
The PR-description Why row (line 195) and the §4 sentence "The Why slot carries the symptom" (line 319) still demand a symptom with no audit or no-symptom branch (finding 1). The README bullet omits the identifier exception (finding 6). The member-of-a-set check does not apply, since no set gains a member.

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The PR-description Why slot still asks for "the symptom", with no audit-found or no-symptom branch, so an audit-found defect is pushed back into predicting one. | substantive | SKILL.md:195, :319 | Add slot 2's audit and no-symptom branch to the Why row and to line 319, or cross-refer to slot 2 by name. |
| 2 | The Translation checklist says to delete any What-slot sentence the diff still shows. That deletes the public-identifier sentence the rule at 344–346 requires ("name it once"). The checklist does not mention the exception. | substantive | SKILL.md:826–827 (rule 342–346) | Add the identifier exception to the checklist item. |
| 3 | The What-slot After example says "a caller … fails at once", an outcome in prose. The Outcome rule puts outcomes on their own User-visible line. The commit says the example "no longer puts an outcome in prose", which is false. | substantive | SKILL.md:353 | Cut "fails at once" from the What example and keep it for the User-visible line. Correct the commit's claim before merge. |
| 4 | The new audit branch of the changelog row has no checklist item. The changelog checklist does not mention it, and the commit says every fix has one. | substantive | SKILL.md:475; checklist at :842–843 | Add the audit branch to the changelog checklist item. |
| 5 | Version bump 1.3.0 → 1.4.0 in three files. No sentence of the commit message claims it. | substantive | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168` | Add a sentence to the commit message that claims the bump, or move it to a release commit. |
| 6 | The README says a sentence recovered from one hunk "is cut even when it carries a decision", with no identifier exception. A reader can cut the sentence that names a public flag. | substantive | `agent-packages/change-description-authoring/README.md:26` | Add "except a public identifier the change adds, removes, or renames". |
| 7 | The open-question rule has no bad and good exemplar in the change. The "measured" figure cites the earlier rule, and the commit says the current wording was not re-run. | substantive | SKILL.md:458–465 | Add a bad case and a good case beside the rule, or run them. |
| 8 | The changelog row cites "slot 2" for a slot that has a name. | taste | SKILL.md:475 | Write "(§2, Impact and trigger)". |
| 9 | "End the sentence there" for an audit-found defect can be read as dropping an observed failure that the same defect also has. | taste | SKILL.md:92–93 | State that an observed failure gets its own sentence. I prefer this reading. |

Churn: none reported.

**Not checked:** the drafts were not re-run, `make check` and `make check-descriptions` were not run, and no `apm-authoring` skill was loaded, so the skill-package analogues are my own reading of the form.
