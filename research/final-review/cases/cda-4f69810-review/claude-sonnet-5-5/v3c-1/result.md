# Final review: `d79c43d..HEAD` (4f69810, change-description-authoring 1.4.0)

**Inputs.** I had no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill, its README, and version fields. That is the §2a analogue case, and I did not run the drift script because there are no members to parse. I read the diff in full and loaded `english-developer-style`. I did not load `apm-authoring` because it is not among the three allowed skills, so rule citations from it are missing. There is no previous report. `make check` (`apm pack --check-versions --check-clean --dry-run`) ran and ended in the dry-run write of `marketplace.json`. I did not see an error, but I only read the tail of the output.

## Item 1: Comments consistent with each other (analogue: statements the files make about each other)

- **Substantive:** the new What-slot example contradicts the commit message and its own closing paragraph.
  - `SKILL.md:352-355`: the *After* text says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome stated in prose.
  - `SKILL.md:357-359` then says the `IllegalStateException` is an outcome that "goes on its own line under 'User-visible changes'".
  - The commit message says the What-slot example "no longer puts an outcome in prose".
  - So the example breaks the skill's own rule that an outcome gets its own line. A drafting agent copies the good example, so the outcome in prose gets copied.
- **Taste:** the *After* example also holds the sentence "with the pool open from startup it sends directly". That is a hunk translation of `execute` switching to `sendDirect`. The reason is already given in the clause before the semicolon ("used sendWithRetry only to reopen a closed pool"). The checklist item "delete each sentence in turn; where the diff still says it, leave it deleted" would delete the tail.
- Slot 2's table row (`SKILL.md:81`), the prose (`SKILL.md:92-96`), the Symptom checklist (`SKILL.md:803-806`), and the changelog row (`SKILL.md:475`) agree. All four say "no symptom by construction".
- The first-sentence-of-slot-2 prose still says "the defect has no symptom (a leak…)" nowhere. I grepped for the old wording and found none.
- No sentence narrates the change ("now", "no longer") beyond the intended *Before/After* examples.

## Item 2: Claimed cases covered

The test for a rule is its detection. Detections are the §8 checklist items.

| Claim from the commit message | Section and checklist item |
| --- | --- |
| Slot 2: audit/code-reading finding | Slot 2 prose, table row, and Symptom checklist |
| Derived consequence traced and marked | Prose at `SKILL.md:98-101` and Symptom checklist |
| "Say so" kept for no symptom by construction | Slot 2 prose and Symptom checklist |
| What slot: hunk translation | `SKILL.md:342-359` and the new Translation item |
| Public identifier named once | `SKILL.md:345-347` (the Translation item does not mention it; see Item 5) |
| Alternatives: mechanism is a fact about merged code | Alternatives checklist item |
| Open questions: answered, kept in Scope, or dropped | `SKILL.md:458-465`, the Scope row, and the Discussion item |
| Changelog row | `SKILL.md:475` |
| §7 points to the What-slot rule | `SKILL.md:763-764` |
| §2 asks for "what changed that the diff does not show" | `SKILL.md:288` |

- No command line is told to run in the changed text, so the command sub-check has nothing to list.
- Hunk-to-claim check: every hunk is claimed except the three below.
  - README gained a sentence on "its reason stays" and on the three new rules. The commit message does not name the README, though the README mirrors the skill.
  - The version bump to 1.4.0 appears in four files and is not mentioned in the message.
  - Neither is a finding on its own. The commit message could name them in one sentence.

## Item 3: Boundaries, partitions, negative control (analogue: partitions the change claims)

**Partitions.** Four rules are claimed: symptom, translation, alternatives, and open questions.

- Evidence is stated for all four, with the counts in the commit message.
- The commit message itself says the final open-question rule and the What-slot example were not re-run. Both are rules this change adds, so they have no evidence.
- **Substantive:** the What-slot example is the one with the defect in Item 1. The fix is to repair the example, then run it again on a blind draft.
- The negative control is the audit/symptom row: a defect with a real, observed symptom keeps the quoted diagnostic. That case is covered by the unchanged slot 2 text.

**Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it, end the sentence | An audit finding that also has an observed symptom (a reporter saw it fail) | Writes only "An audit found this", dropping the reported symptom | Not ended. The text says "where reading the code or an audit found the defect". A symptom reported in the issue is not addressed. Taste. |
| Derived consequence only after tracing, marked derived | A change with no error paths (a rename) | Nothing: the rule fires only when a consequence is predicted | "A consequence derived from the code earns a sentence only after it is traced". Ended by its own condition. |
| What slot: cut a sentence recoverable from one hunk | A one-line change whose entire description is that hunk | An empty What slot | Slot 2 of the table says "behavioral change, not changed files". There is no explicit exemption for a trivial change. Taste. |
| Name a public identifier once | An identifier that appears only in test code | Names a test-only flag | Ended by "public identifier". Not a finding. |
| Alternative's obstacle must be a fact about merged code | A change that has no alternative a reviewer would propose | Writes no alternative | Ended by "a rejected alternative earns its sentence only where a reader would propose it". Not a finding. |
| Open question: answer, keep with decision, or drop | A description with no open questions | Nothing | Ended by "a question the issue or the review left open". Not a finding. |

## Item 3a: Level, placement, environment

- Each rule sits in the slot it governs. The checklist items are in the existing §8 list. The README entry matches the existing bullet style.
- `make check` reaches the dry-run write step without an error that I saw. I read the last 15 lines only.
- **Taste:** the commit message says drafts check against §8, but the new "identifier named once" exception has no §8 item. Per the commit message's own finding ("a rule that is not in the checklist is not checked"), it is the one new rule left unchecked. I would add a clause to the Translation item.

## Item 4: Names by content, not by position

- None. The new text refers to sections by number (`§2`, `§5`), which is the document's existing convention. The examples use content names.

## Item 5: The failure report (analogue: what the rule tells the reader to look at)

- The Translation item names its detection (delete each sentence in turn).
- The Discussion item and the Symptom item name theirs.
- **Taste:** the identifier exception, noted in Item 3a, has no detection.

## Item 6: What the writer says it verified

- Stated: fifteen blind Opus drafts, with counts per defect.
- The commit message states two gaps: the final open-question rule and the What-slot example were not re-run.
- The "*After*" example fails the change's own rule (Item 1), so the rewrite-both check fails on the change's own worked example.
- The commit message's "hunk translation persists in about one draft in two" is an accepted residual, stated.
- The sample is small for the final wording (two drafts, none stated the absence).

## Item 7: Siblings of the change

- **Version sites:** `agent-packages/change-description-authoring/apm.yml`, `apm.yml` (root), and `.claude-plugin/marketplace.json` are all at 1.4.0. `make check` includes `--check-versions`.
- `apm.lock.yaml` has no entry for the package.
- **Sibling skills:** no other skill in `agent-packages` restates the slot-2 rule. `docs-page-authoring` cross-references only for the changelog entry, which was updated at `SKILL.md:475`.
- **Old count:** I searched for sentences that count the set of rules. None changed.
- **Same-symptom paths:** the commit-body mirror of slot 2 is the Why slot, where the table row is "The problem, the symptom, the condition that reaches it" (`SKILL.md:195`). It has no audit-found clause, so a commit body written from the Why slot is not told to end the sentence at what found the defect.
  - **Substantive** only if the Why slot is meant to govern commit bodies; `SKILL.md:207` says a description becomes the commit body, so I file it as substantive.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| What-slot *After* example puts an outcome in prose, against its own paragraph and the commit message | Substantive | `SKILL.md:352-359` | Move the early-caller failure out of the *After* sentence into the "User-visible changes" line, then re-run a blind draft on the example. |
| Why slot (also the commit body) has no audit-found clause | Substantive | `SKILL.md:195` | Add the slot 2 clause, or say that the slot 2 rule governs the Why slot. |
| *After* example contains the translation tail "it sends directly" | Taste | `SKILL.md:355` | Drop the clause after the semicolon. |
| Public-identifier exception has no checklist item | Taste | `SKILL.md:826-827` | Add the exception to the Translation item. |
| Audit rule does not address a defect that also has a reported symptom | Taste | `SKILL.md:92-96` | Add a clause for a reported symptom. |
| README and version bumps not named in the commit message | Taste | commit message | One sentence naming them. |

This review did not run the test suite or the blind drafts, did not check wording for style alone, and did not load `apm-authoring`, so no rule from it is cited.
