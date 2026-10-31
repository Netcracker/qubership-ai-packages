I'm writing the report now. I read the diff, the skill, and the surrounding sections of `SKILL.md`, and I ran the drift script, which found nothing to parse.

# Final review: `d79c43d..HEAD` (4f69810), change-description-authoring 1.4.0

**Inputs.**
- There was no separate task statement, so the claimed cases come from the commit message only.
- No previous report exists.
- This change has no code, so I used the §2a analogues throughout.
- I ran `comment-drift.py d79c43d HEAD` and it produced no output.
- I loaded `english-developer-style`. `apm-authoring` is not among the three allowed skills, so I did not load it.

## Item 1: comments consistent with each other (analogue: statements one file makes about another)
- **Section references.** The §2, §5 and §7 pointers resolve. The §7 bullet points to "§2, the What slot", and the Symptom, Translation, Alternatives and Discussion checklist items point to §2 and §3.
- **Slot 2 and the changelog.** The slot 2 skip cell and the changelog row 3 both say the same thing for an audit-found defect: name what found it, or give the condition alone.
- **README.** Its new bullets match the SKILL rules.
- **Finding 1 (substantive).** The new What-slot "After" example fails the rule it illustrates, and it contradicts the commit message.
  - The second sentence is `with the pool open from startup it sends directly`. The reviewer recovers that from one hunk (`sendDirect`), which is the rule's own `Y now calls Z` translation. Only the clause `used sendWithRetry only to reopen a closed pool` is the reason.
  - The first sentence puts an outcome in prose: `a caller that runs before startup completes fails at once`. The commit message says the example "no longer puts an outcome in prose", and the paragraph after the example sends that outcome to a `User-visible changes` line.
  - A reader would copy the pattern and keep both.
- **Finding 2 (taste).** Slot 2 says "name what found it and end the sentence there". Two paragraphs later it allows a traced, derived consequence as its own sentence. These are compatible once "sentence" is read as "the sentence about the finding", but a reader could take them as conflicting. My preference is "end there unless a traced consequence follows, marked as derived".
- No comment narrates the change.

## Item 2: claimed cases covered (analogue: sections that handle each claim; detection per rule)

| Claim in commit message | Where handled |
| --- | --- |
| Slot 2: describe an audit-found defect by what found it | Slot 2 text and its Before/After example, the changelog row 3, and the checklist Symptom item |
| Derived consequences are traced to the caller and marked as derived | Slot 2 paragraph and the checklist Symptom item |
| "Say so" kept for a defect with no symptom by construction | Slot 2 text, the skip cell, and the checklist |
| What slot: hunk-recoverable sentences are translation, with an identifier exception | Slot 2 prose, the §5 pointer, the §7 bullet, and the checklist Translation item |
| §2 asks for "what changed that the diff does not show" | Present in "What each paragraph must earn" |
| Rejected alternatives: mechanism is a fact about merged code | Alternatives paragraph and checklist |
| Open questions: answered, kept in Scope, or dropped | Scope paragraph, the Scope table cell, and the Discussion checklist item |

- **Command lines.** The changed files tell no one to run a command, so there are none to list.
- **Unclaimed hunks.** The 1.3.0→1.4.0 bump in `apm.yml`, the package `apm.yml` and `marketplace.json` is not claimed by any sentence of the message. This is taste. It follows the repo's per-change bump convention, which I did not check against history, and one clause would claim it.
- **Finding 3 (taste).** The `(measured: three of three drafts repeated as open a question the code answered)` parenthetical now sits under the new open-question rule. The commit message says those drafts ran against an earlier rule ("answer from the code or drop it"). The measurement supports the problem, not the current wording. I would phrase it as "under the earlier wording".

## Item 3: boundaries, partitions, negative control (analogue: genres, situations, the table of added instructions)
- **Partitions.** The partitions are an audit-found defect, a code-reading-found defect, a symptom-free defect, and an observed defect.
- **Control.** The control is the observed defect, which still gets a quoted literal.
- **Missing run.** There is no run on a case where the change is noise (a change with no audit and no open question). The commit says no `research/` cases exist for this skill, so none were re-run.
- **Prior state.** Not applicable. This is a text package with no persisted state.
- **Limits and replaced mechanisms.** Not applicable.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found: name what found it, end the sentence | An audit found it and a user also reproduced it | `An audit found this.`, dropping the observed symptom and its literal | "unless the failure was also observed; then slot 2 quotes it" |
| Derived consequence: trace it, mark it derived | A defect whose trace ends before any caller | Nothing | Ended by the text: "earns a sentence only after it is traced to the point where a caller sees it" |
| Translation: cut a hunk-recoverable What sentence | A one-hunk fix | The What slot is empty | Ended by slot 3's skip: "The problem statement makes the approach obvious" |
| Identifier exception: name a public identifier once | An identifier the Why slot already names | A second mention in What | "once, in whichever slot names it first" |
| Alternative stated as a fact about merged code | No alternative a reviewer would propose | Nothing | Ended by the text: "earns its sentence only where a reader would propose it" |
| Open question: keep a maintainer-only question in Scope | A commit body, which has no Scope slot | Unspecified | Not addressed by the text |

- **Finding 4 (taste).** The first row's input is not ended by the artifact, and the row could be read as dropping an observed symptom. Add the clause "unless the failure was also observed".
- **Finding 5 (taste).** The Scope-slot rule does not say where a maintainer-only question goes in a commit body.
- **Not findings:** "Derived consequence", ended by "only after it is traced to the point where a caller sees it". "Translation" on a one-hunk fix, ended by slot 3's skip condition. "Rejected alternative", ended by "earns its sentence only where a reader would propose it".

## Item 3a: level, placement, environment (analogue: file placement and gate)
- The rules sit in the existing SKILL sections and the README, matching the siblings.
- The registration entries are the version bumps in `apm.yml`, the package `apm.yml` and `marketplace.json`, which agree at 1.4.0.
- I did not run `make check`, the gate that checks that alignment. It needs `uvx` and network access, so the alignment is by inspection only.
- `make check-descriptions` is not relevant because the frontmatter is unchanged.

## Item 4: names by content, not by position
None. The new text cites `§` numbers, as the rest of the skill does. No new heading or case refers to something by its ordinal.

## Item 5: the failure report (analogue: detection per rule)
- Every new rule has a checklist line: Symptom, Translation, Alternatives and Discussion.
- The Translation detection ("delete each sentence … where the diff still says it, leave it deleted") detects the translation rule itself, not a weaker property.
- The identifier exception is not reached by that checklist item. This is minor, and it falls under finding 1's fix.

## Item 6: what the writer says it verified
- The commit states blind-draft counts before and after each rule.
- It discloses that the current open-question rule and the What-slot example were not re-run, and that hunk translation "persists in about one draft in two".
- It gives no pass/fail pair on the example text itself. Under finding 1 the example fails its own rule, so that pair is the missing evidence.
- I did not rerun anything.

## Item 7: siblings of the change
- **Version string.** `git grep 1.3.0` finds no remaining stale mention for this package.
- **Package sentences.** `docs-page-authoring/README.md`, `problem-report-authoring` and the `english-*-developer-style` skills only name the package. None restates the symptom or Scope rules.
- **Counts.** "Six slots" and "Five slots" are unchanged because no slot was added.
- **Symptom wording.** Commit-body slot 2 (line ~123, ~136) only refers to slot 2 and carries no separate absence rule, so no stale "say so" remains.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The What-slot "After" example keeps a hunk-recoverable clause (`it sends directly`) and states an outcome in prose (`fails at once`). It fails its own rule and contradicts the commit message. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` ~351-357 | Rewrite the After text so it carries only the reasons: the pool opens at startup, and `sendWithRetry` existed only to reopen a closed pool. Move the early-caller failure to the outcome line. |
| 2 | "End the sentence there" and "a derived consequence earns a sentence" read as conflicting. | Taste | same, ~91-101 | Say: end there unless a traced consequence follows, marked as derived. |
| 3 | The `(measured: three of three …)` parenthetical is attached to a rule other than the one measured. | Taste | same, ~458-465 | Say "under the earlier wording". |
| 4 | The audit-found rule can be read as dropping an observed symptom. | Taste | same, ~91-93 and the slot 2 skip cell | Add "unless the failure was also observed". |
| 5 | Commit bodies have no Scope slot for maintainer-only questions. | Taste | same, ~458 | Name where the question goes in a commit body, or say the rule is for descriptions only. |
| 6 | The version bump is not claimed by the message. | Taste | `apm.yml`, the package `apm.yml`, `.claude-plugin/marketplace.json` | One clause in the message. |

This review did not run `make check` or any suite, did not check the bump against the repo's history, did not read the `research/` directory, and did not pass over the prose for style alone.
