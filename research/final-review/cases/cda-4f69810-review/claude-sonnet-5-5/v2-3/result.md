Reviewing `d79c43d..HEAD` (one commit, `4f69810`). **No task statement was handed over.** I took the claimed cases from the commit message and answered Item 2 from it alone.

This change has no code: it edits a skill, a README, version metadata and a marketplace entry. I used the §2a analogues and did not run the drift script, because it has no members to parse. I did not load `apm-authoring` or `docs-page-authoring`, since only the three listed skills were allowed. I read `english-developer-style` only far enough to confirm its scope. `make check` (pack with version and clean check, dry run) and `make check-descriptions` both ran offline and passed.

There is no previous report, so no round-over-round table.

## Item 1: statements consistent with each other
Analogue: statements the changed files make about each other (section references, counts, repeated descriptions).
- The section references resolve: `§5` is Trailers and identifiers, `§2, slot 2` is the commit-body slot table, and `§2, the What slot` is the PR "What each paragraph must earn" part.
- The version `1.4.0` agrees across `apm.yml`, the package `apm.yml` and `marketplace.json:291`.
- The skill's `description` field and the marketplace description are unchanged, so they still agree.
- **Finding A (substantive), `SKILL.md` What-slot After example (~l.350).** The commit message says the What-slot example "no longer puts an outcome in prose". The After sentence still says a caller before startup "fails at once instead of opening the pool on demand". The paragraph right after it says that same failure is an outcome that goes on its own `User-visible` line.
  - The example therefore contradicts the rule it sits under (a fact stated in slot 3 is not restated in slot 2, l.~127).
  - A reader copies the After's shape, so drafts will keep the outcome in prose.
- **Finding B (taste), same example.** The paragraph after the example tells the reader what the After left out ("The removed `ensureOpen()` calls are gone from the text…"). `apm-authoring` treats an example followed by a "what not to copy" sentence as a contradiction. I read this one as explaining the example rather than disowning it, so I did not rate it substantive.
- The After's second sentence ("with the pool open from startup it sends directly") is close to the "`Y` now calls `Z`" form the rule bans. It survives only because of its reason clause, `used sendWithRetry only to reopen a closed pool`. I left it, since the rule allows a reason.
- The new Before/After for slot 2 has no narrating `now` or `no longer`. The only "now" is inside the quoted Before example, which is allowed.

## Item 2: claimed cases covered
Claimed cases and the section that handles each:

| Claim | Handled by | Detection |
| --- | --- | --- |
| Audit or code-reading defect is described by what found it | slot 2 text and skip cell; changelog part 3 | checklist "Symptom" |
| Derived consequence is traced to the caller and marked derived | new paragraph after slot 2 | checklist "Symptom" |
| Hunk translation is cut; public identifiers are named once | What slot, with Before/After | checklist "Translation"; §7 pointer present |
| Rejected-alternative mechanism is a fact about merged code | "approach you tried" paragraph | checklist "Alternatives" |
| Open questions are answered, kept in Scope, or dropped | new Scope paragraph and Scope table cell | checklist "Discussion" |

- **Commands:** the change tells the reader to run none.
- **Hunks vs. claims:** every hunk maps to a sentence of the commit message. The README bullets and the three version bumps map to the version line and the rule list. The marketplace bump is the registration entry.
- **Finding C (substantive), Translation checklist item.** It says to "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". The rule's exception, that a public identifier is named once, is not in the checklist item.
  - A drafter applying only the checklist (the commit message says drafts check against §8) will delete the system-property or flag sentence that readers search for.
  - Request: add `except a public identifier the change adds, removes, or renames (§5)` to the item.
- **Finding D (substantive), PR Why slot, l.195.** It still says only "the problem, the symptom, the condition that reaches it".
  - The audit-found rule lives in the commit-body slot 2 and in the checklist, but the drafts that exposed the defect were pull request descriptions, and the PR table is the one they write from.
  - Request: add `for an audit-found defect, what found it (§2, slot 2)` to the Why cell, or confirm that the pointer through the "commit body's slots 1 to 3" sentence is intended.

## Item 3: boundaries, partitions, and the negative control
Analogue: the genres and situations claimed, the negative control, and the table of added instructions. Pre-existing state does not apply, because the change only replaces text in a skill. No setting reaches a new consumer, no mechanism is replaced, and no limit is set.

Evidence in the commit message: 15 blind drafts. The earlier-version drafts show the failure. The final wording was tried on two drafts for the symptom rule, four for the obstacle rule and four for the question rule. Two partitions are stated as unrun: the current open-question rule and the current What-slot example. The "translation persists in about one draft in two" result is stated openly. The skill has no `research/` cases, and the commit says so.

**Table of added instructions:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Defect found by an audit: name what found it and stop | A defect a user reported with a logged exception | "A reported exception was found…" (the symptom would be dropped) | Already ended: the rule is conditioned on "Where reading the code or an audit found the defect"; not a finding |
| Derived consequence only after tracing, marked as derived | A trivial change with an observed symptom | A "derived" label on an observed symptom | Already ended: it applies only to "a consequence derived from the code"; not a finding |
| Cut sentences recoverable from one hunk | A one-line fix whose What slot is a single sentence | An empty What slot | Not addressed. The Translation item deletes "each sentence", so a one-sentence What slot is deleted. Taste (**Finding E**): add `only where the slot keeps a sentence of reason` |
| Rejected-alternative mechanism is checked against the code after the change | A change with no alternative a reviewer would propose | Nothing; the rule opens with "earns a block, when a reviewer would propose it" | Already ended; not a finding |
| Open questions: answer, keep in Scope, or drop | A change with no issue discussion | Nothing; the rule needs a question "the issue or the review left open" | Already ended; not a finding |

## Item 3a: level, placement, and the environment
- Each rule sits in the section its slot belongs to, and the edits are in the single existing SKILL.md with no new files.
- Both gates passed: `make check` (the dry-run pack and version gate) and `make check-descriptions` (27 descriptions, all within the 1020-character limit).
- Of the claimed cases, the only one of five with no recorded run is the open-question rule as currently worded (its Scope cell and paragraph are in the diff).
- A sentence that could appear unchanged in any tutorial: none found.

## Item 4: names by content, not by position
None. References use section numbers and slot names (`§5`, "slot 2", "the What slot"). Section numbers can go stale, but that is the file's existing convention. The measured claims in the text ("two of two", "three of three") are counts of results, not positional names.

## Item 5: the failure report
Analogue: what a rule tells the reader to look at.
- Each new rule is reached by a checklist item: Symptom, Translation, Alternatives, Discussion. Findings C and D concern weaker detections.
- The Symptom item detects the stated rule: "does the sentence end at what found it?" is a direct test.
- The Translation item (delete each sentence in turn) is weaker than the rule, because it lacks the identifier exception (C).

## Item 6: what the writer says it verified
- The commit message states the drafts' counts per rule, which serve as the "bad case fails, good case passes" evidence for the symptom, alternatives and discussion rules.
- The What-slot rule is partly verified: translation persists in about one draft in two, and the current What-slot example was not re-run. That is stated.
- Rule 1 was verified by the "no failure observed" wording trial, but the check for noise (an input where the item is empty, with output not growing) is not stated. This is Finding E's partition and is taste.
- Apply the new rules to the change's own text: its commit message names the cause and the mechanism, and its sentences are not hunk translations. It states the evidence for each rule. No finding.

## Item 7: siblings of the change
- **Version surfaces:** `git grep` finds `1.4.0` in the same three places that carried `1.3.0`. The umbrella `qubership-repo-essentials/apm.yml` references `../change-description-authoring` by path with no version pin. `apm.lock.yaml` has no entry for this package. The one-hit `marketplace.json:57` `1.3.0` belongs to a different package.
- **Set added to:** the changelog slot 3, the commit-body slot 2, the PR Scope cell, the checklist and the README bullets all received the new rules. The PR Why slot did not (Finding D).
- **README:** the new bullet matches the skill's content. No sentence counts the rule list ("both", "two", "five rules") against the old size.
- **Other skills:** `english-developer-style` and `docs-page-authoring` only cross-reference the skill by name, so they need no update.
- **Rows that name several paths:** the Scope open-question paragraph names only "whether a compatibility break is intended" as its example of a maintainer-only question. That is an example, not a symptom, so there is no mismatch.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| A | What-slot After example states an outcome in prose that the next paragraph sends to `User-visible`; the commit says the example no longer does | Substantive | `SKILL.md` What-slot example, ~l.350 | Reword the After to give only the reason (`the pool opens at startup, so the lazy open is not needed`) and leave the failure to the `User-visible` line |
| C | Translation checklist item omits the identifier exception | Substantive | `SKILL.md` §8 Translation item, ~l.826 | Add the exception to the item |
| D | PR Why slot row has no audit-found clause; the drafts that exposed the defect were PR descriptions | Substantive | `SKILL.md:195` | Add the clause or a pointer to slot 2 |
| B | Paragraph after the example says what the After omits | Taste | `SKILL.md` after the example | Optional; fold into the first sentence of the example |
| E | Translation rule would empty a one-sentence What slot; no noise-case evidence | Taste | `SKILL.md` §8 | Add `only where the slot keeps a sentence of reason` |

This review did not run the blind-draft trials or re-run any instruction on new input. It did not check the full SKILL.md beyond the changed hunks and the places that reference them, and it did not review prose style, which is outside this form.
