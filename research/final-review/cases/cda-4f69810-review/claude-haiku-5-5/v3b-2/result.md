# Final review: `d79c43d..HEAD` (commit 4f69810, change-description-authoring 1.3.0 → 1.4.0)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message alone (C1–C8 below). No previous report exists, so there is no §4 table. The change is Markdown only: `SKILL.md`, `README.md`, two `apm.yml` files, and the `marketplace.json` entry. There are no code members and no tests. I ran `comment-drift.py d79c43d… HEAD`; it printed nothing and exited 0, which is correct for a change with no members. I loaded `english-developer-style` and applied it to the new wording. I did not load `test-authoring` because the change has no tests. The `apm-authoring` skill that §2a names is not in the skills directory I was given, so I did not load it. Its rules are cited below only as the skill names them.

## Item 1: comments consistent with the code and with each other

Analogue used: statements the file makes about its own rules, its checklist, and its examples.

- The new What-slot rule says a sentence the reviewer recovers from one hunk is translation, "even under a lead-in that states a reason". Its own After example then writes "with the pool open from startup it sends directly" (line 355). That is the same pattern. **Finding F1.**
- The slot table's Skip-when cell for Slot 2 (line 81) now carries a requirement for audit-found defects, not a skip condition. A reader can take it as permission to omit the slot for those defects. **Finding F2.**
- The README's new bullets restate the three new rules and agree with the SKILL text. The `.instructions.md` trigger file restates no rule. No sibling file repeats the old "no observable symptom" wording; a repo-wide grep found none.

## Item 2: claimed cases covered

The commit message claims these cases. The "test" for each is its rule text plus a checklist item.

- **C1** Drafts invent symptoms: Slot 2 paragraph (lines 88–100), table row (line 81), §8 Symptom item. Covered.
- **C2** Drafts translate hunks: What-slot rule (lines 342–357), §7 pointer (line 763), §8 Translation item (line 826). Covered in text. The example fails the rule (F1), and the checklist omits an exception the rule states (F3).
- **C3** Rejected alternatives with a retold obstacle: Alternatives paragraph, §8 Alternatives item. Covered.
- **C4** Open questions repeated: paragraph at line 458, Scope row, §8 Discussion item. Covered.
- **C5** "Say so" misread as permission to state absence: Slot 2 closing sentence, §8 Symptom item. Covered.
- **C6** "What changed" asks for a list of changes: the "what changed that the diff does not show" wording (line 288). Covered.
- **C7** Changelog entry names "the condition alone" for audit-found defects: changelog row (line 475). **Not covered by any §8 item (F4).** The commit says "each fix … has a checklist item", which this breaks.
- **C8** "New Discussion and Translation items": present (lines 826 and the Discussion item). Covered.

Commands: the added lines contain no command the change tells a reader to run.

Hunks: every hunk is either a rule in the commit's sentences or a README restatement of them, except the three version bumps:
- `.claude-plugin/marketplace.json:291`
- `apm.yml:168`
- `agent-packages/change-description-authoring/apm.yml:2`

No sentence in the commit message claims them. **Finding F5.** The bump follows the repository's per-feature convention, and `make check` checks it (see 3a).

## Item 3: boundaries, partitions, and the negative control

Each rule's partitions are stated in its text: observed, derived, found by audit or reading, and no symptom by construction for Slot 2; answered by code, maintainer-only, and not bearing for open questions. No state persists between runs, so "pre-existing state" does not apply. The one defect here is F1, where the example breaks its own rule.

### §2a table: instructions the change adds or widens

Each row is an input where the instruction fires.

| Instruction | Input where it fires | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Slot 2: an audit-found defect is named by what found it, "and end the sentence there" (lines 90–93) | Retry-path defect found by audit; no failure seen | "An audit of the retry paths found this." | "end the sentence there". Ends it. None. |
| Slot 2: a derived consequence "earns a sentence only after it is traced" (line 98) | Lazy field read before startup; consequence traced to a caller | A sentence marked as derived | "only after it is traced to the point where a caller sees it". Ends it. None. |
| Slot 2: "say so" for no symptom by construction (lines 94–96) | Leak on an error path with nothing logged | "This path leaks; nothing is logged." | "by construction". Ends it. None. |
| What slot: a sentence recovered from one hunk is cut, "even under a lead-in that states a reason" (lines 342–344) | Pool change: the hunk swaps `sendWithRetry` for `sendDirect`; the reason is pool-open state | The example at line 355 keeps "with the pool open from startup it sends directly" | None. The rule says cut; the example keeps it. **F1.** |
| What slot: a public identifier is "named once" (lines 345–347) | New system property | Named once | "named once". Ends it. The checklist then deletes it (F3). |
| Rejected alternatives: "an obstacle the change removes is a step" | Reviewer proposes lazy `ensureOpen()`; the change removes the closed-pool obstacle | "The pool is open from startup, so lazy opening is not needed." | "an obstacle the change removes". Ends it. None. |
| Open question the code answers: give the answer, "do not repeat the question as open" (line 458 on) | "Does the pool close on fork?", answered by a test | The answer, with the test's name | "where … verified evidence answers it". Ends it. None. |
| Maintainer-only question: keep it in the Scope slot (line 458 on) | Whether a compatibility break is intended | A Scope-slot question with its decision and evidence | "only a maintainer can settle". Ends it. None. |
| Question that does not bear on the change: drop it (line 458 on) | "Should the wiki change?" on a code-only change | Nothing | "does not bear on this change". Ends it. None. |
| Changelog: audit-found defect gets "the condition alone" (line 475) | Changelog entry for an audit-found leak | The condition only | "the condition alone". Ends it, but no §8 item checks it (F4). |
| §7: descriptions get "the same test … sentence by sentence" (line 763) | PR What slot with a translation sentence | Deletes it | "where the diff still says it". Ends it. None. |
| §2: "what changed that the diff does not show" (line 288) | Rename that also changes behavior | The behavior change only | "that the diff does not show". Ends it. None. |

Below the table, the rows that end by their own condition: the audit-found row, the derived-consequence row, the no-symptom row, the rejected-alternative row, the open-question rows, and the §7 and §2 rows.

## Item 3a: level, placement, and the environment

No tests exist, so the test-level question does not apply. The rules sit in the sections where their old versions sat. The repository gates run offline and both pass:
- `make check` (`apm pack --check-versions --check-clean --dry-run`): exit 0. The three version strings are consistent at 1.4.0.
- `make check-descriptions`: all 27 skill descriptions are within 1020 characters.

The tree was clean after both runs.

## Item 4: names by content, not by position

- The changelog row cites "(§2, slot 2)" (line 475). The content name, "Impact and trigger", is available and the file uses it elsewhere. **F7** (taste).

## Item 5: the failure report

- The Symptom and Alternatives checklist items detect what their rules say.
- The Translation item detects "the diff still says it". For a public identifier that is the wrong detection, because the rule says to name it once (F3).
- The changelog rule has no detection at all (F4).

## Item 6: what the writer says it verified

The commit states its evidence and states its limits. The drafts ran against version 1.0.1, before the outcome slot and length rules. The commit also says "the current open-question rule and the What-slot example … were not re-run." The shipped text therefore has no run on its final wording for those two rules. **F6.** I did not run drafts; the evidence is the writer's to supply.

## Item 7: siblings of the change

- No sibling restates the Slot 2 or What-slot rules, so there is nothing to conflict with.
- The `english-developer-style` copies under `.agents/`, `.claude/rules/`, and `.cursor/rules/` are unrelated to this change.
- The set-size check (counts such as "five slots", "six slots") is unchanged.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| **F1.** The What-slot example keeps a translated sentence under a reasoned lead-in, which the rule two lines above forbids. | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:355` | Drop "with the pool open from startup it sends directly". The first sentence already gives the reason, and the call change is in the diff. |
| **F2.** The Slot 2 Skip-when cell carries a requirement for audit-found defects. A reader can take it as a skip condition. | substantive | `SKILL.md:81` | Move "for a defect an audit or a code reading found, the body names what found it" out of the Skip-when cell. Lines 88–100 already say it. |
| **F3.** The Translation checklist item omits the public-identifier exception. Following it deletes a name the rule says to keep once. | substantive | `SKILL.md:826–827` against `SKILL.md:345–347` | Add "except a public identifier the change adds, removes, or renames, which is named once (§2)". |
| **F4.** The changelog "condition alone" rule has no checklist item. | substantive | `SKILL.md:475`; §8 Changelog item at `SKILL.md:842–843` | Add to the Changelog item: "for a defect an audit or a code reading found, does the entry give the condition alone?" |
| **F5.** The three version bumps have no claiming sentence in the commit message. `make check` passes with them. | substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Add a commit-message sentence that claims the bump and cites `make check`, or move the bump to its own change. |
| **F6.** The commit says the final open-question rule and the What-slot example were not re-run, so the shipped wording has no run. | substantive | `SKILL.md:458` (open-question paragraph) and `SKILL.md:342–357` (What-slot rule) | Run the drafts on the final text, or state in the commit that these two rules are unmeasured. |
| **F7.** "(§2, slot 2)" is a positional reference where the slot has a content name. | taste | `SKILL.md:475` | Write "(§2, Impact and trigger slot)". Expect this to be declined. |

**Not checked:** I did not run any drafts, so the behavioral claims behind F6 are unverified. The `apm-authoring` rules named in §2a were not loaded. I did not evaluate the prose beyond the points above; a pass over the wording for style alone is not part of this review.
