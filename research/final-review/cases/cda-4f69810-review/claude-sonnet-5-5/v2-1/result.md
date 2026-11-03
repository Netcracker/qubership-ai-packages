I'm checking the last open sibling question, whether the PR-description Why slot carries the audit rule. Then I'll write the report.

# Final review: `d79c43d..HEAD` (4f69810)

**Inputs and scope.** The task statement was not handed over, so item 2 takes its claimed cases from the commit message alone. The change has no code (a skill, a README, version metadata), so §2a applies and each item below reads its analogue. `comment-drift.py` was not run: the change has no members for it to parse. I loaded `english-developer-style` from the given skills directory. `apm-authoring` and `docs-page-authoring` were not among the three skills I was told to use, so I did not load them. There is no previous report.

## Item 1: comments consistent (analogue: statements about other files, counts, section references)
- Section references resolve. `§2`, `§5` and `§3` point to existing headings, and `§7` is the "No paraphrase of the diff" bullet.
- The slot-2 skip rule (SKILL.md:81), the prose (:90-100), the changelog row (:475) and the checklist (:803-806) agree on what to do for an audit-found defect.
- README bullets (:23-32) match the new rules.
- The version is 1.4.0 in `apm.yml`, `marketplace.json` and the package `apm.yml`. The `1.3.0` hits elsewhere belong to other packages.
- **Finding A (substantive).** The What-slot *After* example (SKILL.md:354-357) breaks the skill's own rules, and the commit message says it does not.
  - The commit message says the example "no longer puts an outcome in prose".
  - The first sentence of the *After* text says a caller before startup "fails at once instead of opening the pool on demand". That is an outcome stated in prose, and the next paragraph of the skill says it belongs on a `User-visible changes` line.
  - It is also a consequence derived from the code, stated without the "traced and marked as derived" qualification from the slot-2 rule.
  - The second sentence, "with the pool open from startup it sends directly", is what the Translation check deletes: the hunk `sendWithRetry` → `sendDirect` already shows it.
  - Applied to the skill's own worked example, the rewritten rules fail.
- **Finding B (taste).** The PR-description *Why* slot (:195) still reads "the problem, the symptom, the condition" with no audit clause. The audit rule lives in the commit-body slot 2 and the §8 checklist. The blind drafts were PR descriptions, so putting the clause in the slot's own row would match the lesson in the commit message, that a rule outside the row is not read. The checklist does catch it, so I am not asking for the change.

## Item 2: claimed cases covered
Cases claimed by the commit message, each with the section that handles it:
- Predicted failure: slot 2 prose (:90-100) and checklist Symptom.
- "No failure observed" wordings: same.
- Hunk-listing: the What-slot rule (:342-359) and the Translation item.
- Retold obstacle: :369-371 and checklist Alternatives.
- Open question the code answers: :458-465, Scope row, and checklist Discussion.
- Question only a maintainer can settle: the same.

Commands the change tells anyone to run: none. Every hunk belongs to a sentence of the commit message. This includes the version bumps, the README, and the `Skip when` edit.

The commit message states which parts were not re-run: the current open-question rule and the What-slot example. Finding A sits in the second of those.

## Item 3: boundaries, partitions, negative control (analogue: table of added instructions)

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found an audit-found defect, end the sentence | A defect an audit found that also has a reproduced, observed failure | "An audit found this." with the observed failure dropped | None directly. The slot-2 opening still says to quote what a person observes, so the observed symptom stays. Not a finding. |
| Trace a derived consequence to the caller, mark it as derived | A trivial one-hop consequence | An extra "derived" sentence | "earns a sentence only after it is traced", which already ends it. Not a finding. |
| Delete What-slot sentences the diff recovers | A one-hunk fix | An almost empty What slot | The exception for public identifiers, and Why/Verification carry the rest. Not a finding. |
| Keep a maintainer-only question in Scope | A question that does not bear on the change | Drops it | "Leave a question out only when it does not bear on this change". Not a finding. |

Partitions:
- The commit message reports no run for the final open-question wording and the What-slot example, only for earlier wordings.
- The README text for a defect found by audit does not mention the changelog case, which is minor.

## Item 3a: level and placement
Placement matches the siblings (SKILL.md, README, `apm.yml`, marketplace). I did not run the repository's gate. The commit says there are no cases under `research/` to re-run.

## Item 4: names by content
None. The new text uses no ordinals or "see below". `§` references and the "Slot 2" and "What slot" names are content-based.

## Item 5: failure report (analogue: what the detection tells the reader)
Every new rule has a checklist item (Symptom, Translation, Alternatives, Discussion). One gap: the Translation check ("delete each sentence; where the diff still says it, leave it deleted") detects hunk translation, which is the rule it is attached to. It cannot detect an outcome stated in prose, so it does not cover Finding A's second defect.

## Item 6: what the writer says it verified
The commit message states blind-draft counts. Hunk translation "persists in about one draft in two". The final What-slot example and open-question rule were not re-run. No exemplar-pass or bad-case-fail pair is named for the new rules, and no check shows output did not grow on an input where the item is noise.

## Item 7: siblings
- Everything that lists the package carries 1.4.0.
- The English style packages only cross-reference the skill by name.
- No sentence counts the slots or checklist items by number.
- The three PR description places that restate the audit rule are the Why slot (Finding B), the changelog row (updated) and the checklist (updated).

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A. The What-slot *After* example states an outcome in prose, an underived consequence, and a hunk-recoverable second sentence | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:354-357` | Rewrite the *After* so it passes the rule: state the reason only (for example, "`sendWithRetry` existed only to reopen a closed pool, which can no longer happen once the pool opens at startup"). Leave the early-caller failure to the following sentence about the `User-visible changes` line. Then run the Translation check on the example. |
| B. The PR-description Why slot carries no audit clause | taste | `SKILL.md:195` | Optionally add "for a defect an audit found, what found it" to the Why row, matching slot 2. |

This review did not run the repository's gate or any blind drafts, and it did not read any wording for style alone.
