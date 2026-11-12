# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.** There is no task statement. The claimed cases come from the commit message of 4f69810 alone, as the skill allows. The change has no code: it edits a SKILL.md, a README, two `apm.yml` files and `marketplace.json`. So I used the §2a analogues and did not run the drift script, which has no members to parse. I loaded no doc-comment skill. I did not load `apm-authoring`, `docs-page-authoring`, `english-developer-style` or `test-authoring` either, because I judged this change on its facts, not its wording. I cited rules from the final-review skill only.

I did not run the suite or any trial, and I did not run the repository's registration gate.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files, counts, section references)

- The `§5` reference at SKILL.md:347 holds. §5 covers the identifiers a reader greps, and line 683 lists "the public identifier the change touches".
- The "§2, slot 2" reference at line 475 holds. The checklist's "(§2)" references hold too.
- **Finding 1 (substantive).** The new "After" example at SKILL.md:~350 breaks the rule it illustrates. Its second sentence is "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly." The rule just above says a sentence like "`Y now calls Z`" is translation, and that you state the reason, not the edit. "It sends directly" is the edit and is recoverable from one hunk. Only the clause "used … only to reopen a closed pool" carries the reason. Under the new checklist item "delete each sentence of the What slot in turn", the closing clause of this sentence would be deleted. §2a says an example that fails its own rule is a finding.
- **Finding 2 (substantive).** The audit/code-reading rule is added to commit-body slot 2 (line 81), to the changelog row (line 475) and to the checklist. It is not added to the PR-description Why slot (line 195). That slot reads "The problem, the symptom, the condition that reaches it" and has no audit variant. Line 217 says the Why slot becomes the commit body, so a description's Why slot can state a symptom where the commit body's slot 2 would name what found it. The request is a clause in the Why row, or a pointer to slot 2.
- **Finding 3 (taste).** In the open-question paragraph at ~line 458-465, the paragraph breaks lopsidedly ("is\nwanted. Leave\na question"). This is reflow churn only.
- The commit message says "This skill has no cases under research/". `research/change-description-authoring/` exists, with `phase1`–`phase4` prompts and results and a script. It may mean "no re-runnable cases", but as written it is ambiguous. This is taste: say "no re-runnable cases" or name the directory.
- Nothing narrates the change with "now", "no longer" or "used to" outside examples. The one "now gets" is in the worked example, as an outcome.

## Item 2: claimed cases covered

Each case comes from the commit message. The detection analogue is the checklist item.

| Claim | Where handled | Detection |
| --- | --- | --- |
| Slot 2 audit/code-reading rule, with a before/after | lines 81, 91-96 | Checklist "Symptom" |
| Derived consequence only when traced and marked | lines 98-101 | Checklist "Symptom" |
| Changelog names the condition alone | line 475 | None beyond the "Symptom" item, which names the commit-body case only |
| "Say so" kept for a defect with no symptom by construction | lines 81, 94-96 | Checklist "Symptom" |
| What slot: hunk translation, and a public identifier named once | ~lines 342-360 | Checklist "Translation" |
| §7 pointer and §2 "what changed that the diff does not show" | line 288 and ~line 763 | None needed |
| Rejected alternative stated as a fact about the merged code | ~lines 368-372 | Checklist "Alternatives" |
| Open questions: answered, kept in Scope, or dropped | ~lines 458-466, Scope row at line 262 | Checklist "Discussion" |
| New "Discussion" and "Translation" checklist items | lines 826-838 | n/a |

- **Finding 4 (taste).** The changelog-entry variant has no check of its own. The "Symptom" checklist item reads as a commit-body check, and the "Changelog" item at line 842 does not mention the audit case. The "Changelog" item at line 842 would be the place to add it.
- The commit message cites "Over fifteen blind Opus drafts" and gives per-rule counts: 2 + 10 + 2, 4, 4 and 3. I could not check these against any file in the change. The skill text repeats two of them ("two of two", "three of three"), and both match the commit message. They are the writer's evidence, not mine.
- No command lines are in the changed hunks.
- Every hunk belongs to a sentence of the commit message. The version bumps (1.3.0 to 1.4.0) are in `apm.yml`, the package `apm.yml` and `marketplace.json`, at three consistent lines. Other packages stay at their own versions.

## Item 3: boundaries, partitions, negative control (with the added-instruction table)

The partitions for the audit rule are:
- Defect observed.
- Defect found by an audit or a code reading.
- Defect with no symptom by construction.
- Consequence derived from the code.

All four are written. The commit message reports no trial of the final open-question rule or of the What-slot example. It says so itself. The README claim "dropped only when it does not bear" is as written in the SKILL.md.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "name what found it and end the sentence there" | A defect a user reported, with a logged diagnostic | Slot 2 holds the quoted diagnostic. The instruction is conditioned on "reading the code or an audit found the defect", so it does not apply. | The condition itself |
| "A consequence derived from the code earns a sentence only after it is traced to the point where a caller sees it" | A defect with no consequence at all | The agent might write nothing, or "no failure is traced". | "Where the defect has no symptom by construction, say so" covers it; the line 94 sentence also says a stated absence of a symptom is not known. **Weak:** an audit-found defect whose trace shows no caller-visible effect has no instruction. A draft may restate "no failure" there. Request: add "…and if the trace reaches no caller, write nothing about a consequence". Taste. |
| "a sentence whose content the reviewer recovers from one hunk is translation" | A one-hunk fix where the single sentence is the reason | The agent deletes it. | "state the reason for the decision, not the edit" ends it. |
| "A question … only a maintainer can answer … keep it in the Scope slot" | A commit body (no Scope slot) or a description with no open question | The Scope slot only exists in the PR description. A commit body has no home for it. **Weak:** the rule says nothing for a commit body. Taste. | None |

## Item 3a: level, placement, environment

- The rules sit in the section each slot belongs to. The checklist items sit where the other items do.
- The registration entries (`apm.yml`, `marketplace.json`, package `apm.yml`) agree. The repository's own gate was not run (see the last sentence).

## Item 4: names by content, not position

- None. The new labels are "Translation" and "Discussion". The *Before:*/*After:* examples are labelled by role. I did not check the one phrase "the final wording" in the commit message for staleness.

## Item 5: the failure report

- The new checklist items name a check and an action ("delete each sentence … leave it deleted"; "does the description give the answer"). The "Translation" item reaches its rule. The "Symptom" item reaches the audit rule, but not the changelog row 3 variant (finding 4).

## Item 6: what the writer says it verified

- The commit message states the trial evidence, per rule, and says what was not re-run: the current open-question rule and the What-slot example. The What-slot example is the one that fails its own rule (finding 1), which fits it having been un-re-run.
- No red/green pair is named for the changelog variant.

## Item 7: siblings

- Other places that list the skill's description or version: `apm.yml`, `.claude-plugin/marketplace.json` and the package `apm.yml` (all updated). The README is updated. `research/change-description-authoring/README.md` and `.lycheeignore` name the package but do not restate the changed rules; I did not read them in full.
- Sets the change grows: the PR-description slot list (finding 2) and the checklist (two items added). No sentence still counts the checklist by number.
- Prose that counts slots: "Five slots" (commit body) and "Six slots" (description) are unchanged, and the change adds no slot.

## Findings

| # | Finding | Label | Where | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The "After" example in the What slot keeps "it sends directly", the translation the rule bans | Substantive | SKILL.md, What slot, ~lines 350-353 | End the sentence at "used `sendWithRetry` only to reopen a closed pool", or give the reason without the edit. |
| 2 | The audit/code-reading rule is missing from the PR-description Why slot, which becomes the commit body | Substantive | SKILL.md:195 (Why row), vs 81 | Add the audit clause to the Why row, or point it to slot 2. |
| 3 | The changelog variant has no checklist coverage of its own | Taste | SKILL.md:842 | Add the audit case to the "Changelog" item. |
| 4 | No instruction for an audit-found defect whose trace reaches no caller; none for open questions in a commit body | Taste | SKILL.md:98-101, ~458-466 | Add one ending clause each, if wanted. |
| 5 | Commit message "no cases under research/" is ambiguous given `research/change-description-authoring/` exists | Taste | commit message | Say "no re-runnable cases". |
| 6 | Ragged reflow in the open-question paragraph | Taste | SKILL.md ~458-466 | Reflow. |

This review did not run the repository's registration gate, the suite, or any drafting trial, and did not do a style pass over the prose.
