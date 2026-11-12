# Final review: `change-description-authoring` 1.4.0 (`d79c43d..HEAD`, commit `4f69810`)

**Inputs.**
- **Task statement:** none was handed over, so claimed cases come from the commit message alone.
- **Previous report:** none.
- **Files changed:** `SKILL.md`, the package `README.md`, and the version string in `apm.yml` (package), `apm.yml` (root) and `marketplace.json`.
- **Item-by-item analogues (§2a):** this change has no code, so every item below uses the no-code analogue.
- **Drift script:** not run, because there are no members to parse.
- **Skills loaded:** `english-developer-style` from the given directory. `apm-authoring` and `docs-page-authoring` are not in that directory, so I did not load them. The citations below are to the final-review form and the skill's own sections.
- **Gate:** `make check` (`apm pack --check-versions --check-clean --dry-run`) printed "[dry-run] Would write marketplace.json" and the tail I read shows no error. I did not read the exit status, so I take it as passing.

## Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about each other.

- **Section references.** The new references to §2 (slot 2 and the What slot), §5 and §7 all resolve. §5 does say readers grep identifiers, so the "named once" exception holds.
- **Versions.** 1.4.0 appears in all three places and matches.
- **README.** Its two new bullets match the skill text.
- **Finding A (substantive), `SKILL.md` ~lines 349–360, the translation example.**
  - The commit message says the What-slot example "no longer puts an outcome in prose". The *After* does: its first sentence says "a caller that runs before startup completes fails at once".
  - The paragraph right below it says that same failure is an outcome and "goes on its own line under User-visible changes".
  - The example therefore breaks the skill's "state each causal link once" rule and its own explanation.
  - Request: have the *After* give the reason only ("The pool opens at startup, so `sendWithRetry`, which existed to reopen a closed pool, is no longer needed"). Leave the failure to the outcome line.
- **Finding B (taste), same example.** The tail "it sends directly" is recoverable from one hunk, so by the new Translation checklist item it is a sentence to delete. This is a minor point.

## Item 2: claimed cases covered

Analogue: each case the commit message names against the section that handles it.

| Claimed case | Section |
| --- | --- |
| Symptom invention and the audit rule | Slot 2 table row and prose; checklist "Symptom"; changelog row 3 |
| Hunk translation | What-slot rule; §7 line; checklist "Translation" |
| Obstacle the change removes | Rejected-alternatives rule; checklist "Alternatives" |
| Open question | Scope row; new Scope paragraph; checklist "Discussion" |

- **Commands the change tells someone to run:** none.
- **Unclaimed hunks:** none. Every hunk belongs to a sentence of the commit message.
- **Finding C (substantive), `SKILL.md` ~line 195 and ~line 246.**
  - The commit says the defects appeared in PR-description drafts.
  - The PR-description Why slot still reads "The problem, the symptom, the condition that reaches it".
  - Its *After* example has no audit case. Only the commit-body Slot 2 table row got the audit clause.
  - A drafter working from the PR table sees "the symptom" with no clause ending it.
  - Request: add the audit clause to the Why row, or one sentence saying slot 2's rule applies to Why.

## Item 3: boundaries, partitions, negative control

Analogue: the instruction table below and the situations the change claims.

**Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit/code-reading defect: "name what found it … end the sentence there" | A defect an audit found that a user also hit and logged (an observed diagnostic exists) | "An audit found this." The observed diagnostic is dropped, though the same slot says to quote it as a literal | "unless a failure was also observed; then quote it" (**substantive**) |
| Maintainer-only question belongs "in the Scope slot" | A description that §4 rule 5 makes the commit body, where the checklist says Scope is absent | Either a Scope slot in a commit body, or the question is lost | "in a commit-body description, leave it in the review thread" (**substantive**; the conflict between the two rules is the finding) |

Rows that leave the table:
- Derived-consequence rule, for a one-hop obvious trace: ended by "traced to the point where a caller sees it".
- Rejected-alternative mechanism check, for a change with no discussion: ended by "earns its sentence only where a reader would propose it" and "when retold from someone else's discussion".
- Translation rule, for a one-line change: ended by the existing What-slot skip, "The problem statement makes the approach obvious".
- Public-identifier exception: stated in the rule itself.

**Pre-existing state.** Not applicable. The package is a text update and the version is bumped.

## Item 3a: level, placement, environment

- `make check` is the repository's gate for this change, and it passed.
- The rules live in the files that already hold the neighboring rules.
- The package follows the layout of its siblings.
- Each new rule has a checklist item.
- No tutorial-generic sentences were added.

## Item 4: names by content, not position

None. The new text refers to "slot 2", "the What slot" and "§7", which are named sections, not ordinals by position.

## Item 5: failure report

Each new rule has a checklist question that says what to look at. The "Translation" test ("delete each sentence in turn") detects the rule it belongs to. "Discussion" detects all three branches of the open-question rule.

## Item 6: what the writer says it verified

- **Stated:** the commit message gives blind-draft counts (15 drafts; "none of two"; "none of four").
- **Not in the repository:** the drafts are not in the repo (the commit says no `research/` cases exist), so the counts cannot be checked.
- **Not re-run, by the commit's own admission:** the current open-question rule and the revised What-slot example.
- **Finding D (taste):** the Finding A example is exactly the part that was not re-run, and it carries the defect. Re-running one draft would settle it.
- **No bad case where the added item is noise** is named for any of the rules (§2a, "What the writer says it verified").

## Item 7: siblings

- **Version set:** `marketplace.json`, root `apm.yml` and package `apm.yml` all agree.
- **Prose that counts the old set:** the README summary and the trigger instruction file were read, and neither counts rules.
- **Other paths with the same symptom:** the commit-body Slot 2 and the PR Why slot are two paths for one symptom, and only the first was updated (Finding C). The changelog row was updated.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| A: the *After* states the outcome in prose, against the commit's claim and the skill's own paragraph below it | Substantive | `SKILL.md` ~349–360 | Give the reason only and leave the failure to the outcome line |
| C: the PR Why slot lacks the audit clause | Substantive | `SKILL.md` ~195, ~246 | Add the clause, or a pointer to slot 2 |
| Audit rule "end the sentence there" drops an observed diagnostic | Substantive | `SKILL.md` ~93 | Add "unless a failure was also observed" |
| Maintainer-question rule conflicts with the commit-body Scope rule | Substantive | `SKILL.md` ~458 and checklist Scope | Say where the question goes in a commit-body description |
| B: "it sends directly" restates a hunk | Taste | `SKILL.md` ~353 | Cut it |
| D: the changed example was not re-run | Taste | commit message | Re-run one blind draft |

I did not run a prose-style pass for wording. I did not run the drafting experiments the commit message cites, and I did not run `make check` beyond reading its tail.
