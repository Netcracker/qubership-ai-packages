## Final review: `d79c43d..HEAD` (commit `4f69810`)

**Scope and inputs.** The change is one commit, `4f69810`, and it touches only Markdown and manifests: the `change-description-authoring` SKILL.md, its README, two `apm.yml` files, and `.claude-plugin/marketplace.json`. There is no code. The task statement was not handed over separately, so the claimed cases come from the commit message, as the skill asks. No previous report exists, so §4's table is omitted. Loaded: `apm-authoring` (the authoring skill for an APM skill) and `english-developer-style`. `test-authoring` was not loaded because the change has no tests. I ran `comment-drift.py d79c43d… HEAD`; it printed nothing, since it parses no Markdown, so the items below use the §2a analogues. I did not look for or run the repository's registration gate; the version agreement was checked by reading.

### Item 1: comments consistent with the code and with each other
Analogue: statements the file makes about its own rules, its cross-references, and its examples.

- **S1 (substantive).** `SKILL.md:91-93` says that where "reading the code or an audit found the defect, name what found it and end the sentence there." A defect an audit found and a user also observed, with a quoted log line in the issue, then loses its observed symptom. That conflicts with slot 2's "what a person outside the code observes" and with the checklist's literal requirement. The changelog row at `SKILL.md:475` has the same condition-alone gap. Request: limit the condition to "where no symptom was observed", or require the observed literal alongside what found it.
- **S2 (substantive).** The new public-identifier exception at `SKILL.md:345-347` ("name it once") conflicts with the checklist item at `SKILL.md:826-827`: "where the diff still says it, leave it deleted." A reader who follows the checklist deletes the one sentence the body requires. Request: add "except a public identifier the change adds, removes, or renames (§2)" to the checklist item.
- **S3 (substantive).** `agent-packages/change-description-authoring/README.md:26-27` says a sentence the reviewer recovers from one hunk "is cut." That is false for the identifier case in S2. Request: add the same exception, or point at §2.
- **S4 (substantive).** The example at `SKILL.md:349-359` is followed by a gloss: "The removed `ensureOpen()` calls are gone from the text…". That is a caveat saying what the example leaves out. apm-authoring rule 2 says "an example that needs a caveat after it teaches what the caveat forbids." Request: drop the gloss, or show the common case without the removal.

Other comments checked and consistent: the §-references (§2, §3, §4, §5, §7, §8) resolve to the right sections; the changelog row now agrees with slot 2; the §7 pointer matches the What-slot rule; the README bullets on rejected alternatives, audit findings, and open questions match the SKILL text.

### Item 2: claimed cases covered
Claimed cases from the commit message, with their detection in the §8 checklist:
1. Audit-found defect ends at what found it: `Symptom` item. Covered, but see S1.
2. Derived consequence traced and marked derived: `Symptom` item.
3. Changelog gives the condition alone for an audit-found defect: **no checklist item** (S6).
4. "Say so" kept for no symptom by construction: `Symptom` item.
5. What-slot translation rule: `Translation` item. Conflicts with the identifier exception (S2).
6. Public identifier named once: **no checklist item** (S2).
7. §2 "what changed that the diff does not show": no separate check, and §2 itself carries the rule.
8. Rejected alternatives as merged-code facts: `Alternatives` item.
9. Open questions answered, kept, or dropped: `Discussion` item.

Command lines: none in the changed files, so none to list.

Hunks against sentences: the version bump (1.3.0 to 1.4.0) appears in `apm.yml:2`, `apm.yml:168`, and `.claude-plugin/marketplace.json:291`. No sentence of the commit message claims it. It is also against apm-authoring's Versions section: "Bump that when the contract changes… not on every prose edit."
- **S5 (substantive).** Drop the bumps, or name the contract change in the commit message and say what run checks it.

### Item 3: boundaries, partitions, and the negative control
Added or widened instructions: 7 rows. The §7 pointer and the four checklist lines restate rows 4 to 7, so they get no row.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `SKILL.md:91-93` "name what found it and end the sentence there" | a defect a user reported with a log line, read by no audit | the quoted log line and its trigger | "Where reading the code or an audit found the defect" |
| `SKILL.md:98-101` derived consequence "earns a sentence only after it is traced" | a defect whose symptom an issue already quotes | the quoted symptom, not a derived one | "only after it is traced to what a caller sees" |
| `SKILL.md:475` changelog "the condition alone" | a defect a user reported with a log line | the literal and the condition | "for a defect an audit or a code reading found" |
| `SKILL.md:342-344` "translation" for a sentence the reviewer recovers from one hunk | a behavior the diff does not show, such as refusing calls before startup | the behavior sentence, kept | "the reviewer recovers from one hunk" |
| `SKILL.md:345-347` name a public identifier once | a change adding no public identifier | no identifier sentence | "A public identifier the change adds, removes, or renames" |
| `SKILL.md:369-373` rejected alternative as a merged-code fact | an alternative rejected for a fact still true after the change | that fact, in the present tense | "An obstacle the change itself removes is a step…" |
| `SKILL.md:458-465` open questions | a question the code already answers | the answer and its evidence | "Where the code, a test, or another source you verified answers it" |

Not findings: none. Partitions: the observed-symptom-plus-audit case is not covered by any example or evidence (S1).

### Item 3a: level, placement, and the environment
- The rules sit in the right sections: commit-body slot 2, the What slot, the changelog row, and the checklist.
- **T2 (taste).** The defect was seen in pull request descriptions, but the PR Why slot (`SKILL.md:195`) has no pointer to the audit rule. The checklist covers it. Label: taste. The reviewer prefers a one-line pointer, which is likely to be declined.

### Item 4: names by content, not by position
- **T1 (taste).** `SKILL.md:357`: "the first sentence says why…". Name the sentence by its content, such as "the sentence that gives the reason." Label: taste.

### Item 5: the failure report
- Every new rule needs a checklist detection. Two do not have one: the changelog condition-alone rule (S6) and the identifier-named-once rule (S2).
- **S6 (substantive).** The `Changelog` checklist item at `SKILL.md:842-843` lists category, observable change, symptom, reference, and compatibility. Add a check that an audit-found defect gives the condition alone, as §2 and §3 require.

### Item 6: what the writer says it verified
The commit message states that "the current open-question rule and the What-slot example… were not re-run," and that the skill has no `research/` cases. The evidence it does cite (blind drafts) covers the slot 2 and rejected-alternative wording, not these two.
- **S7 (substantive).** Run the open-question rule and the What-slot example on the current wording, or keep the commit message's disclosure as the only evidence for them.

### Item 7: siblings of the change
- No other copy of this skill exists in the repository (checked with `git grep` for its distinctive phrases). The `.agents/` copy of `english-developer-style` refers to this skill only by name.
- The version 1.4.0 agrees in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`.
- The §7 pointer and the README bullets both reflect the change, apart from S3.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| S1: audit-found rule drops an observed symptom | substantive | `SKILL.md:91-93`, `:475` | Limit the condition to "where no symptom was observed", or keep the literal beside what found it |
| S2: checklist deletes the identifier sentence the body requires | substantive | `SKILL.md:345-347` vs `:826-827` | Add the identifier exception to the Translation item |
| S3: README states the cut without the identifier exception | substantive | `README.md:26-27` | Add the exception, or point at §2 |
| S4: gloss after the What example teaches the omission | substantive | `SKILL.md:357-359` | Drop the gloss, or show the common case without the removal |
| S5: version bump not claimed, and against apm-authoring's Versions rule | substantive | `apm.yml:2`, `apm.yml:168`, `.claude-plugin/marketplace.json:291` | Drop the bumps, or claim the contract change and its run |
| S6: changelog condition-alone rule has no checklist detection | substantive | `SKILL.md:842-843` | Add a changelog check for audit-found defects |
| S7: open-question rule and What example not re-run | substantive | commit message | Run both on the current wording, or keep the disclosure |
| T1: "the first sentence" in the example | taste | `SKILL.md:357` | Name the sentence by its content |
| T2: PR Why slot has no pointer to the audit rule | taste | `SKILL.md:195` | Add a one-line pointer to the commit-body slot 2 rule |

Churn: none reported.

**Not checked:** the suite and the repository's registration gate were not run, since neither is applicable to a Markdown change and I did not look for the gate. Whether an agent following the rules produces the examples' outputs was not tested; S7 covers that.
