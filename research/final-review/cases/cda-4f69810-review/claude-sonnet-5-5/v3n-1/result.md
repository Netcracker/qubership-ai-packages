# Final review: `d79c43d..HEAD` (4f69810, one commit)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message alone. This is a change with no code (§2a). The drift script printed nothing, because there are no members to parse, so it was not run for findings. Loaded skills: `apm-authoring` (read in part) and `english-developer-style` (not read; no wording pass was done, see the closing sentence). There is no previous report.

Claims taken from the commit message:
- Slot 2: a defect found by an audit or a code reading is described by what found it, and the sentence ends there.
- A changelog entry for such a defect names the condition alone.
- A consequence derived from the code is written only when traced to what a caller sees, and is marked as derived.
- "Say so" is kept only for a defect with no symptom by construction.
- What slot: a sentence recoverable from one hunk is translation. A public identifier is named once.
- Rejected alternative: the mechanism is a fact about the merged code, and an obstacle the change removes is a step it took.
- Open question: answered if the code settles it. Kept in the Scope slot if only a maintainer can settle it. Dropped only if it does not bear on the change.
- Checklist: Symptom and Alternatives are extended, and Discussion and Translation are new.
- "The slot 2 and What slot rules carry a bad and a good example."
- "The What-slot example no longer puts an outcome in prose."
- "This skill has no cases under research/."
- Version bumped to 1.4.0.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about itself, other files, and the version)
- **Consistent.** The 1.4.0 string agrees in `apm.yml:3` of the package, root `apm.yml:168`, and `marketplace.json:291`. The §2 and §3 cross-references in the new text resolve. The §5 reference for the identifier exception is right: §5 line 683 lists the public identifier. The new §7 pointer "§2, the What slot" is right.
- **Finding 1 (substantive).** The commit message says the What-slot example "no longer puts an outcome in prose". The After text (SKILL.md ~L350) opens "…so a caller that runs before startup completes fails at once instead of opening the pool on demand". That is the caller-observable outcome, stated in prose. The closing paragraph then says the outcome belongs on its own line under User-visible changes. The example therefore does the thing the rule next to it says belongs elsewhere. The commit message claim is also false as written.
- **Finding 2 (substantive).** The After's second sentence is "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly". Its tail, "it sends directly", is what the `sendDirect` hunk shows. The new rule calls such a sentence translation "even under a lead-in that states a reason". The skill's good example fails the skill's own Translation check, which deletes each What sentence the diff still says. A reader copies the example, so this is worse than a stray sentence. `apm-authoring` says an exemplar must pass its own rule.
- **Narration.** The new text has no `now`/`used to` narration outside examples. The *Before*/*After* labels are not narration.

## Item 2: claimed cases covered (analogue: sections that handle each claim; a rule's detection is its test)
| Claim | Section / detection |
| --- | --- |
| Audit-found defect | Slot 2 prose plus table, changelog row 3, checklist Symptom (new text) |
| Derived consequence | Slot 2 paragraph; checklist Symptom, "traced… derived" |
| No symptom by construction | Slot 2, table, checklist |
| Hunk translation | What slot; §7 pointer; checklist Translation |
| Identifier named once | What slot. The README summary omits this exception (see finding 4). |
| Rejected alternative as a fact about merged code | Rejected-alternatives paragraph; checklist Alternatives |
| Open question | Scope paragraph, Scope table row, checklist Discussion |
| Bad and good examples in slot 2 and What slot | Present |
| "No cases under research/" | See finding 3 |

- **Commands in changed files.** None are told to be run. `make check-descriptions` was run: all 27 descriptions within 1020 characters. The `pack --check` gate needs `apm` and was not run (see the closing sentence).
- **Hunk to claim.** Every hunk maps to a sentence of the commit message: the version bump in three files, the README bullet, the Scope table row, the §7 line, and the checklist. No unclaimed hunk.
- **Finding 3 (taste).** "This skill has no cases under research/" reads against `research/change-description-authoring/`, which exists. It holds the design audit trail, not draft cases. Say "no draft cases" to avoid the contradiction. This is a commit message point, not a file change.

## Item 3: boundaries, partitions, and negative control
- **Added instructions: 6, rows below.** The six are: slot 2 audit rule; derived-consequence rule; translation rule; rejected-alternative mechanism rule; open-question rule; identifier exception (a condition of the translation rule, not counted separately beyond that).

  | Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
  | --- | --- | --- | --- |
  | Open-question rule (L458) "kept in the Scope slot" | A commit body made from a description (§4 rule 5) | A question with no slot to sit in, since Scope is absent from a commit body | "in a commit body, put it in the body's last paragraph, or drop it" |

  The row's input comes from the skill's own text (the Scope-slot-absent-from-commit-body rule in the checklist, and the §4 rule 5 reference). Not findings: the translation rule on a feature with a new public flag (the identifier exception, L344, ends it), and the audit rule on a defect with an observed symptom (the rule's condition ends it).
- **Partitions.** The commit claims three genres and ran 15 blind drafts of one PR description. That leaves the commit-body and changelog partitions with no evidence, though the rule is added to both (slot 2 table, changelog row 3). The commit says the drafts ran against 1.0.1 and that the current open-question rule and the What example were not re-run. Those two are therefore the least-evidenced parts.
- **Pre-existing state.** Not applicable beyond the version number. No consumer pins 1.3.0 (`apm.lock.yaml` and `qubership-repo-essentials` have no pin).

## Item 3a: level, placement, and the environment
- **Placement.** The rules live in the SKILL.md sections their slots belong to, with the README and the checklist updated. This matches the sibling layout.
- **Registration.** Three version entries agree. The `make check` gate was not run (needs `apm`).
- **Finding 4 (taste).** The README bullet states the translation rule and omits the identifier exception, which the skill says to name once so readers can search for it. This is harmless because the README is a summary; I would add the clause. The new Scope-question sentence also has a stray hard wrap ("wanted. Leave" / "a question out…", ~L460), which is churn-level and not requested.
- **Any sentence a tutorial would carry unchanged?** None. All are platform-specific to the reader model.

## Item 4: names by content, not by position
- None. The new text uses "Before/After", "the Why slot", "the What slot", and "Slot 2". Slot numbers are the skill's own established scheme, not new ordinals.

## Item 5: the failure report
- **Detections.** Each new rule is reached by the §8 checklist: Symptom, Translation, Alternatives, Discussion. Each detects the rule rather than a weaker property, with one exception.
- **Finding 5 (taste).** The Translation check says "delete each What sentence in turn; where the diff still says it, leave it deleted". That detects the rule's core, but not the carve-out "name an identifier once". It is clear enough that a reader would apply the exception. Taste, no request.

## Item 6: what the writer says it verified
- The commit states the draft runs and counts. Over 15 drafts: 2/2 predicted a failure without a rule; 5/10 stated "none seen" under a word ban; 0/2 with the final wording; the retold obstacle went 2/4 to 0/4; the open question went 3/3 to 0/4; translation persists in about 1 of 2.
- It states the open-question rule and the What example were not re-run. It does not state an exemplar that passes the rewritten rules. **Finding 2 shows the new What-slot After fails the rule it demonstrates.** I did not run any drafts.

## Item 7: siblings of the change
- **Sites of the slot 2 skip condition.** Table row L81, checklist L803, changelog row L475. The PR-description Why slot (L195, "the problem, the symptom, the condition that reaches it") carries the symptom but has no pointer to the audit and derived-consequence rules. The commit's drafts were PR descriptions. They reach the rule only through "Slots 1 and 2 are the commit body's slots 1 to 3" (L201). The checklist Symptom item covers the gap, so this is taste.
- **Finding 6 (taste).** The Why row of the PR table could end with "(§2 slot 2 for a defect found by audit)".
- **Set size.** No sentence counts the checklist or slots as before; the slot counts (five, six) are unchanged.
- **Other paths with the same symptom.** The changelog entry has the matching condition-alone rule. The commit-body slot 2 `Skip when` cell has the rule. No other path found.

## Findings
| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | What-slot After puts the caller-visible outcome in prose; the commit message says it no longer does | substantive | SKILL.md ~L350 (After), commit message | Drop "fails at once instead of opening the pool on demand" from the After, or correct the commit message |
| 2 | After's second sentence ("it sends directly") is hunk translation, failing the Translation check beside it | substantive | SKILL.md ~L350–352 | Rewrite the After so every sentence survives the delete-and-check, then re-run the check on the new example |
| 3 | "no cases under research/" contradicts the existing `research/change-description-authoring/` | taste | commit message | Say "no draft cases" |
| 4 | README omits the identifier exception; stray hard wrap in the open-question paragraph | taste | README.md L26–27; SKILL.md ~L460 | Optional |
| 5 | Translation check does not mention the identifier exception | taste | SKILL.md ~L826 | Optional |
| 6 | PR-description Why row has no pointer to the audit and derived-consequence rules | taste | SKILL.md L195 | Optional |
| 7 | Open-question rule has no home in a commit body made from a description | substantive | SKILL.md ~L458 | Add a clause, as in the table row in Item 3 |

**Not checked.** I did not run `apm pack --check` or any draft over the rules. I did not read the full `english-developer-style` or the rest of `apm-authoring`, and I did not review wording for style. The drift script printed nothing because the change has no code.
