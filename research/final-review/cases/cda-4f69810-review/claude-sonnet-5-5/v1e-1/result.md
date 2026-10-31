# Final review: `d79c43d..HEAD` (commit 4f69810)

**Inputs.** The diff is one commit that touches only skill text, a README, and version strings. There is no separate task statement, so the claimed cases come from the commit message alone. I read the diff in full. This is a change with no code, so I used the §2a analogues and did not run the drift script, because it has nothing to parse. I read `final-review` and the Claude-side `english-developer-style` skill. I did not load `test-authoring`, since the change has no tests. `apm-authoring` and `docs-page-authoring` are not among the three permitted skills, so their rules are not cited. I ran `make check` and `make check-descriptions`; both pass.

## Item 1: comments consistent with the code and with each other

The analogue is every statement one file makes about another place, plus every count and cross-reference.

- **Substantive: the commit message says "This skill has no cases under research/."** `agent-packages/AGENTS.md:35` defines regression cases as `research/<package>/cases/<case>/`. `research/change-description-authoring/` exists but has no `cases/` directory. So the sentence is literally true. It does not say whether the drafting runs should have been recorded as cases, which is the convention for other packages (`blackbox-test-design`, `problem-report-authoring`).
- **Substantive: the slot 2 "Skip when" cell (SKILL.md:81) is ambiguous.** It reads: "…the defect has no symptom by construction, and the body says so in one clause; for a defect an audit or a code reading found, the body names what found it."
  - The first branch says to skip and write one clause. The second says to name the finder. A reader cannot tell whether slot 2 is skipped or filled for an audit-found defect.
  - The prose at lines 90–96 says to fill it with the finder's name, and that sentence ends the slot.
  - The cell should say which.
- **Substantive: the two "answered, kept open, or left out" rules do not agree on where an unanswerable question goes.**
  - Scope table row 5 says a maintainer-only question goes in the Scope slot.
  - The new paragraph at SKILL.md:458 repeats this. It sits under `#### Scope`, so that placement matches the row.
  - Not checked: whether the commit-body Scope variant (§2 commit body) and §8 "Scope" item (still "every gap named as intentional…") accept a question. §8 "Scope" says every gap is named as intentional, which a maintainer-only open question is not.
  - The Scope checklist item is in conflict with the new Discussion item. This is a taste-level finding unless a maintainer agrees.
- **Taste: SKILL.md:~459 has a stray line break.** A paragraph has "Leave" alone on a line, followed by "a question out only when…". It renders fine in Markdown, but it signals an edit left behind.
- **Churn, not reported:** the hunk of `README.md` is consistent with the SKILL.md edits.
- **Consistent with the code:**
  - Version `1.4.0` agrees across the package `apm.yml`, the root `apm.yml`, and `marketplace.json`. No `1.3.0` remains.
  - The "§7 points to this rule" claim holds: the hunk at the "No paraphrase of the diff" line sits in §7 and cites "§2, the What slot".
  - The "§5" reference for public identifiers exists.
- **Narration of the change:** the new text does not narrate (`now`, `no longer`) except inside the worked "After" example, where it describes a behavior of the example code. This is acceptable.

## Item 2: claimed cases covered

Claimed cases from the commit message, each with the section that handles it:

| Claim | Handled by |
| --- | --- |
| Slot 2: an audit-found defect is described by its finder, and the sentence ends there | SKILL.md:92–96, with a Before/After; checklist "Symptom" (line ~805) |
| Changelog entry for an audit-found defect names the condition alone | Changelog table row 3 (line 475) |
| A derived consequence is written only when traced to a caller and marked derived | SKILL.md:98–101; checklist "Symptom" |
| "Say so" is kept for a defect with no symptom by construction | SKILL.md:94–96 |
| What slot: a sentence recoverable from one hunk is translation, even under a lead-in with a reason | SKILL.md:~342; Before/After; checklist "Translation" |
| A public identifier is named once | SKILL.md:~345 |
| §2 asks for "what changed that the diff does not show" | SKILL.md:~288 |
| Rejected alternatives: mechanism stated as a fact about the merged code; an obstacle the change removes is a step it took | SKILL.md:~369–373; checklist "Alternatives" |
| Open questions: answered, or kept in Scope with decision and evidence, or dropped only when irrelevant | SKILL.md:~458; checklist "Discussion" |
| Slot 2 and What slot carry a bad and a good example | Both do |
| Checklist: Symptom and Alternatives extended, Discussion and Translation added | All four present |

No command lines appear in the changed files, so the command part of this item is `none`.

- **Substantive: the message claims a measurement for each rule, and the tallies do not reconcile.**
  - "Over fifteen blind Opus drafts" is followed by per-rule counts: 2 + 10 + 2 for the symptom rule, 4 for the obstacle, 3 + 4 for the open question. That sums to at least 25, unless the same drafts count in several rules.
  - The text does not say which. Either say how many drafts there were, or say that counts overlap.
- **Substantive: the final wording of the symptom rule was tested on two drafts** ("none of two did"). The two-draft sample is thin, but the message states it, so it is disclosed.
- **Churn, not reported:** the message already says the open-question rule and the What-slot example were not re-run.
- **Hunks with no claiming sentence:** none. The four version bumps are covered by the feature bump to 1.4.0. The README hunk is covered by "Each fix therefore says what to write".
- **Measured claims inside the skill:** SKILL.md:100 ("two of two drafts that predicted a symptom…") and SKILL.md:464 ("three of three drafts repeated as open a question the code answered") match the commit message's counts. The "measured" claim at line 129 is an earlier one and is not touched.

## Item 3: boundaries, partitions, and the negative control

The partitions are the genres the rules cover. I filled the table of added instructions for the instructions the change adds or widens.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A defect found by a user's bug report that was also confirmed by an audit | "An audit found this", which hides the observed symptom a reader needs | None stated. Add "and where no one has observed it", or "only where nothing was observed". |
| "A consequence derived from the code earns a sentence only after it is traced to the point where a caller sees it" | A trivial fix where the consequence is the obvious one-hop symptom (a null dereference on this input) | A traced-and-marked-derived paragraph for something every reader sees at once | "only where the chain has more than one hop" is missing. This is a taste finding, because the cost is length and not a wrong claim. |
| "A sentence whose content the reviewer recovers from one hunk is translation" | A one-line fix whose only description is the hunk's effect, for example a changed default | The What slot becomes empty, or a reason with no fact | SKILL.md:~342 says "state the reason for the decision". It ends the instruction there; the row is not a finding. |
| "A public identifier the change adds, removes, or renames is named once" | A rename of an identifier that is not user-facing: a private helper listed as a "public" flag by mistake | Names a private identifier | "public" in the instruction bounds it. Not a finding. |
| "An obstacle the change itself removes is a step the change had to take, not a reason against the alternative" | An obstacle that the change removes but that would still rule the alternative out after the change | The agent drops a valid reason for rejection | Reaches the check "mechanism… after the change", which handles it. Not a finding. |
| "A question the issue or the review left open is answered, kept open, or left out" | A question from the review that is a style preference, not a decision | A Scope-slot question about a preference | "only a maintainer can settle" bounds it. The "bear on this change" clause covers the rest. Not a finding. |

- **Substantive:** the first row. The instruction fires on "audit or code reading" findings, and an audit-found defect that was also observed in production loses its symptom.
  - The input is one readers will meet: a bug found by audit and later hit in the field.
  - The request is the clause "and nothing has been observed".
- **Taste:** the second row.
- **Negative control for the Translation rule:** the checklist item "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" can erase a sentence that states a reason and also restates the hunk. The rule says the reason stays, so the checklist should say "keep the reason".
- **State left by the earlier version:** packages are installed over an earlier version (1.3.0). The change adds rules and renames nothing, so an install over 1.3.0 needs no migration. I did not check that `apm.lock.yaml` has to change; it has no entry for this package (`grep` found none).

## Item 3a: level, placement, and the environment

- **Placement:** the rules sit in the same SKILL.md sections as their siblings. The checklist items are in §8.
- **The gate the repository runs:** `make check` (versions and clean pack) and `make check-descriptions` both pass offline. The 1.4.0 bump agrees in three places.
- **Level:** no sentence in the additions is a tutorial sentence; each is tied to a measured defect.

## Item 4: names by content, not by position

- **None** in the new text, with one exception.
- **Taste:** the commit message says "first a failure predicted from one missing call… and after a ban on that". That is narration of the run order, and it belongs in a commit message.
- The new checklist items are named by content (Translation, Discussion).
- SKILL.md refers to "§2, slot 2" in the changelog row. That is a reference by ordinal. The slot has a name ("Impact and trigger"), so the reference is stale-prone. This is taste.

## Item 5: the failure report

- **Substantive: the Translation rule's detection is a deletion test with no stated failure.** "Delete each sentence in turn; where the diff still says it, leave it deleted." It does not say what the reviewer should look at when a sentence that the diff still shows has a decision attached.
- **None** for the other rules: the Symptom and Alternatives checklist items each name what to check.

## Item 6: what the writer says it verified

- The commit message states the evidence: blind drafts, before and after, with counts. It names what was not re-run (the open-question rule, the What-slot example) and what persists (hunk translation, about one draft in two).
- **Substantive:** no bad case is named for the open-question rule, and no check that the output did not grow on an input where the rule is noise (for example, a change with no open questions). Per §2a, an instruction added after a bad output needs that.
- The message does not say whether the new Before/After examples pass the rewritten rules. The What-slot "After" example: "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly." This is itself a reasoned sentence that a reviewer could recover from the hunk (`sendDirect` replaces `sendWithRetry`). It is borderline under the new Translation rule.

## Item 7: siblings of the change

- **Set members:** no member was added to a set. Slot numbering and counts ("Five slots", "Six slots") are unchanged.
- **Places that route to the skill:** the instruction file and the package README. The README was updated. `.apm/instructions/change-description-authoring.instructions.md` does not repeat the rules.
- **Substantive: the audit-found rule has a sibling in the commit-body slot description.** SKILL.md:123 ("The symptom a fix removes is slot 2's…") and the commit-body worked example at lines ~160–170 were not checked against the new rule. I read them: the `TRAP:` example is an observed symptom, so it stays consistent. Not a finding.
- **Other places that say "say so":** SKILL.md:94–96 is the only one.
- **The `research/` audit trail:** `research/change-description-authoring/` documents the pipeline. It does not describe these rules, which is acceptable for an audit trail, but the README claims "the skill itself is written in a later session from the phase-3 synthesis". That is a statement about the history, not about this change.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Slot 2 "Skip when" cell contradicts the prose on whether slot 2 is filled for an audit-found defect | Substantive | SKILL.md:81 | State that the slot is filled with the finder's name, and not skipped |
| "Name what found it and end there" erases an observed symptom where an audit-found defect was also seen | Substantive | SKILL.md:92 | Add the condition "where nothing was observed" |
| Draft counts in the commit message do not reconcile | Substantive | commit message | State the number of drafts and whether counts overlap |
| Commit message says no cases under `research/`, but no recording of the runs is offered | Substantive | commit message | Say whether the blind drafts will be recorded as `cases/`, or why not |
| No negative control for the open-question rule or the audit rule | Substantive | commit message | Name an input where the rule is noise and the output did not grow |
| Translation check has no failure text and conflicts with "its reason stays" | Substantive | SKILL.md §8 "Translation" | Say what to do with a sentence that restates the hunk and carries a reason |
| §8 "Scope" says every gap is "intentional", but the new rule allows an open maintainer question | Taste | SKILL.md §8 | Mention the question form |
| Reference by ordinal "§2, slot 2" | Taste | SKILL.md:475 | Name the slot ("Impact and trigger") |
| Stray line break before "a question out only when…" | Taste | SKILL.md:~459 | Rewrap |
| Derived-consequence rule fires on one-hop cases | Taste | SKILL.md:98 | Add "only where the chain has more than one hop" |

The review did not run the drafting experiments, did not check the example `After` sentences against a drafting agent, and did not pass over the prose for style alone.
