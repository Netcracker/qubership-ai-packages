## Final review: `d79c43d..HEAD` (commit 4f69810, change-description-authoring 1.3.0 → 1.4.0)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message, as the skill allows. I read the whole diff. The drift script (`comment-drift.py d79c43d… HEAD`) printed nothing, because the change is Markdown and has no parseable members. I loaded `english-developer-style` as the developer-style skill. I did not load `test-authoring` because the change has no tests. The artifact's authoring skill, `apm-authoring`, is not in the skills directory I was given, so I could not load it. Its rules are used here only as the final-review skill cites them. No previous report exists for this change. No files were changed and nothing was committed.

**Checks run.** `scripts/check-skill-descriptions.py` passes (27 skills within 1020 characters). `apm pack --check-versions --check-clean --dry-run` exits 0 with "Version alignment OK". The new prose lines are within 120 characters. Table rows exceed 120, as the existing ones already do.

### Item 1: comments consistent with the code and with each other

Checked the Impact-and-trigger row (line 81) against the slot-2 paragraph (90–101), the changelog row (475) against slot 2, the Scope row (199) against the open-question paragraph (458–465), and the §7 pointer (762–763) against the What-slot paragraph. These agree with each other. The README bullet at line 26 repeats the "one hunk" wording that finding 2 disputes. The one wording problem is taste (finding 8). Narration: none in a comment. The `now` in the What-slot example describes a pull request, not code. **Finding 2 and finding 8.**

### Item 2: claimed cases covered

Claims taken from the commit message:

| Claim | Where it lives | Checked by |
| --- | --- | --- |
| Audit or code-reading defect names what found it | slot 2, 90–96 | checklist, Symptom, 803 |
| Derived consequence traced and marked | slot 2, 98–101 | checklist, Symptom, 803 |
| "Say so" kept for no symptom by construction | slot 2, 95–96; table line 81 | checklist, Symptom |
| Translation sentence cut; public identifier named once | 342–356 | checklist, Translation, 826; **identifier exception missing (finding 1)** |
| "What changed that the diff does not show" | 288 | none needed |
| Rejected alternative stated as merged-code fact | 370–372 | checklist, Alternatives, 832 |
| Open question answered, or kept for a maintainer | 458–465; Scope row 199 | checklist, Discussion |
| Changelog names the condition alone for audit-found defect | changelog row 475 | **no checklist line (finding 4)** |

No commands are added by this change, so the command-line sub-item is `none`.

Hunks against claims: the version bump in three manifests and the README bullets are claimed by no sentence of the message (findings 5 and 6). Every SKILL.md hunk maps to a claim.

**Findings 1–7.**

### Item 3: boundaries, partitions, and the negative control

This is a skill, so the instruction table is below. Each row's input and ending clause were checked against the text.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect names what found it (slot 2) | A production defect with a logged line | the logged line and its trigger | "Where reading the code or an audit found the defect" — ends, no finding |
| Derived consequence only after tracing (slot 2) | An untraced "might hang" | the untraced claim, unless the rule stops it | "earns a sentence only after it is traced" — ends, no finding |
| Translation cut (What slot) | "used sendWithRetry only to reopen a closed pool", a reason | the reason, which should stay | The rule's scope is "one hunk"; the checklist says "the diff" — **conflict (finding 2)** |
| Public identifier named once (What slot) | an internal `ensureOpen()` | nothing; the rule does not reach it | Exception at 344–347, not carried into the checklist — **finding 1** |
| Open question (Scope) | a question the code answers | the answer | "Where the code … answers it" — ends, no finding |
| Changelog condition-alone (row 475) | a production defect with a symptom | the symptom literal | Its own condition — ends, but the rule has no checklist item (**finding 4**) |

The What-slot worked example (352–355) also breaks the translation test, which is finding 3.

### Item 3a: level, placement, and the environment

The rules sit in the same SKILL.md as their siblings, and the checklist is the detection. Both gates pass, as listed above. The version fields agree across the three manifests (1.4.0). The root `apm.yml` version (1.2.0) is the repository's own and is untouched.

### Item 4: names by content

`(§2, slot 2)` at line 475 is an ordinal where the table names the slot "Impact and trigger". **Finding 9.** Otherwise none.

### Item 5: the failure report

Every new checklist item detects its rule, with two exceptions. Translation detects a restatement of the diff, but not the identifier exception or the "one hunk" scope (findings 1 and 2). The changelog condition-alone rule has no detection (finding 4).

### Item 6: what the writer says it verified

The commit states its evidence: blind drafts, the defects they showed, the arms, and that the open-question rule and the What-slot example were not re-run. The bad cases are named. The worked example does not pass the new translation test (finding 3). The subject claims "translating hunks" is stopped, but the body says it "persists in about one draft in two" (finding 7). I did not run the drafts, per the form.

### Item 7: siblings

`docs-page-authoring`, `problem-report-authoring`, `test-authoring`, and `english-developer-style` name this skill without section numbers. None of them restates the changed rules. No member was added to a set. The "five slots" and "six slots" counts are unchanged. No vendored copy of this skill exists in the repository.

### Findings

| # | Label | File and line | Finding | Change requested |
| --- | --- | --- | --- | --- |
| 1 | substantive | SKILL.md:826–827 | The Translation checklist omits the public-identifier exception stated at 344–347. A checklist run deletes the only mention of a new flag or property, which the rule says to name once. | Add "except a public identifier the change adds, removes, or renames, named once (§2)". |
| 2 | substantive | SKILL.md:342–343; README.md:26; SKILL.md:826–827 | The rule says "recovers from one hunk"; the checklist says "where the diff still says it". A sentence drawn from two hunks is cut by one test and kept by the other. | Use "from the diff" in the rule and in README line 26. |
| 3 | substantive | SKILL.md:352–355 | The After example's second sentence joins a reason ("used sendWithRetry only to reopen a closed pool") to an edit ("it sends directly"). The checklist test deletes it whole, and the reason goes with it. | Split the reason into its own sentence. |
| 4 | substantive | SKILL.md:475 and 842–843 | The changelog's condition-alone rule for audit-found defects has no checklist line. The Changelog item checks only "symptom", so the rule is not reached. | Add to the Changelog item: "for a defect an audit or a code reading found, is the condition alone (§2)?" |
| 5 | substantive | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168` | The 1.3.0 → 1.4.0 bump is claimed by no sentence in the message. Earlier commits to this package state their bumps in the message. | Add a sentence claiming the bump. |
| 6 | substantive | README.md:23–33 | The README bullets are a new claim surface, and no sentence of the message names the README. | Add a sentence claiming the README update. |
| 7 | substantive | commit subject | "stop drafts from … translating hunks" conflicts with the body's "persists in about one draft in two". | Reword the subject to "reduce". This is a pre-merge fix, so amend HEAD. |
| 8 | taste | SKILL.md:81 | The Skip-when cell mixes a skip condition with a writing instruction ("for a defect an audit … found, the body names what found it"). It reads as an exception to skipping. | Move the clause out; the slot-2 paragraph already states it. |
| 9 | taste | SKILL.md:475 | "(§2, slot 2)" is an ordinal where the table names the slot. | "(§2, the Impact and trigger slot)". |

### What this review did not check

- I did not run the blind drafts, the classifier script, or the `apm-authoring` rules. The authoring skill was not in the skills directory.
- Prose style (Item 4 wording beyond cross-references) was not reviewed, per the form.
- The line break in the open-question paragraph (`wanted. Leave`) is churn and is not reported.
