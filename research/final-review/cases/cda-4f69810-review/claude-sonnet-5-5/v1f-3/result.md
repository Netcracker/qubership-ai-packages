I'm checking the last details, and the review is nearly done. Here is the report.

# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.** There is no separate task statement, so item 2 is answered from the commit message alone. The change has no code. It edits one skill, its README, and the version in three registries, so §2a applies and each item below is read through its analogue. The drift script ran and printed nothing, because there are no members to parse. I loaded `english-developer-style` from the given skills directory. `apm-authoring` is not in that directory, so I did not load it. There is no previous report.

## Item 1: comments consistent with the code and with each other (analogue: statements across files)
- **Version, three places.** `apm.yml`, `agent-packages/.../apm.yml`, and `marketplace.json` all say 1.4.0. The description text is unchanged in all three. Consistent.
- **Section references.**
  - `§2, the What slot`, `§5`, `§3` and `§4 rule 5` resolve to real text.
  - `(§2, slot 2)` in changelog row 3 does not resolve to what it cites. Finding 3.
- **README bullet.** "its reason stays" matches the SKILL text.
- **Worked example against its own rule.** Finding 1.
- **Checklist against §2.** Finding 2.
- **Narration.** The new text does not narrate the change (`now`, `no longer`). The `Before`/`After` samples are labeled examples, not history.
- **Slot 2 table row.** The "Skip when" cell is consistent with the slot 2 body.

## Item 2: claimed cases covered
The claims below come from the commit message. The test of a rule is its detection (checklist item).

| Claimed case | Covering section or checklist item |
| --- | --- |
| Slot 2: audit or code-reading defect is described by what found it | Slot 2 body and `Before`/`After`. Checklist Symptom. |
| Changelog entry names the condition alone | Row 3, but its pointer `(§2, slot 2)` leads nowhere. Finding 3. |
| Derived consequence traced and marked as derived | The new paragraph after slot 2. Checklist Symptom. |
| What slot: no hunk translation | Rule and example. Checklist Translation. |
| Public identifier named once | §2 only. The checklist does not carry it. Finding 2. |
| Rejected alternative stated as a fact about the merged code | Checklist Alternatives. |
| Open question answered, kept in Scope, or dropped | Rule, Scope row, Discussion item. Finding 4 on the commit-body case. |
| `User-visible:` outcome stays out of the What slot | Example prose. Finding 1. |

- **Commands.** The change tells no one to run a command.
- **Hunks against the commit message.** Every hunk belongs to a sentence of the message. The README hunk and the version bumps are claimed implicitly by "feat" and the 1.4.0 bump. The message never mentions the bump. I treat this as taste, because the bump follows the repository pattern.
- **Wrap artifact.** The line break in `Leave\na question out only when…` in the new Scope paragraph is a reflow leftover. It is churn, so I am not reporting it.

## Item 3: boundaries, partitions, negative control
This item carries the table of added instructions.

| Instruction (quoted) | Input it does not serve | What an agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there." | An audit-found defect that a user also reported, with a quoted stack trace | "An audit found this." The quoted symptom R3 greps for is dropped. | "…and no one has observed it fail; an observed symptom is quoted as before". Finding 5. |
| "A consequence derived from the code earns a sentence only after it is traced to the point where a caller sees it…" | A trace that leaves the repository (a library or server behavior) | A "derived" sentence resting on an unverified step | "…and where the trace leaves the repository, stop at the last verified step". Taste. |
| "a sentence whose content the reviewer recovers from one hunk … is translation" with checklist "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" | A sentence that names a public flag or property | The checklist deletes it, though §2 says to name it once. | "except a public identifier the change adds, removes, or renames". Finding 2. |
| "[Alternative's] mechanism … stated as a fact about the merged code" | An alternative ruled out by a constraint outside the code, such as a supported platform version or a policy | The agent drops it or invents a code mechanism. | "or a constraint the repository states". Taste, since the earlier text already said "mechanism or measurement". |
| "…keep it in the Scope slot as a question…" | A description that §4 rule 5 makes a commit body, which has no Scope slot | The agent adds a Scope section to a commit body, or drops the question. | "in a commit body, put it in a closing paragraph". Finding 4. |
| "Leave a question out only when it does not bear on this change" | A question the reviewer already resolved in the thread | The reviewer's resolution is repeated as an answer. Harmless. | None needed. |

- **Partitions the drafts covered.** The measured drafts cover audit-found defects and one pull request. Defects with an observed symptom, non-fix changes, and the commit-body shape have no evidence. Item 6 repeats this.

## Item 3a: level, placement, environment
- **Placement.** The rules sit in the sections where the sibling rules live: slot 2, "What each paragraph must earn", Scope, and the checklist. The description-length gate `scripts/check-skill-descriptions.py` passes (27 descriptions within 1020 characters). The frontmatter description is unchanged.
- **Generic sentences.** None found. Each new sentence encodes a measured failure.

## Item 4: names by content, not position
None. The new text refers to slots by name. The numbered slots (`slot 2`) are the skill's own fixed numbering, which the file already uses everywhere.

## Item 5: the failure report
- **Detection of each rule.** The new checklist items Symptom, Translation, Alternatives, and Discussion detect what they name.
- **Weaker property.** The Translation detection is weaker than its rule. It lacks the identifier exception and the "reason stays" half. See finding 2.

## Item 6: what the writer says it verified
The commit message states the draft counts: two of two predicted a failure, five of ten stated an absence, and none of two did under the final wording. The retold obstacle went from two of four to none of four. The open question went from three of three to none of four. It also states what was not re-run: the current open-question rule, the What-slot example, and any `research/` case.

- **Small samples.** The "none of two" and "none of four" samples are small.
- **Untested rewrites.** The translation rule and its example are not shown to pass, and the commit message itself says translation "persists in about one draft in two". The example fails the rule (finding 1), which is consistent with that.
- **Drafts count.** "Fifteen blind drafts" does not match the sum of the per-rule counts (2+10+2+4+4+3+4). Some drafts may serve several rules, but the message does not say so. Taste.
- **Not run.** I did not run the suite or the drafts.

## Item 7: siblings of the change
- **Surfaces that list the skill.** The surfaces that route to or pin the skill are `marketplace.json`, root `apm.yml`, the package `apm.yml`, and the README. Other packages cite the skill by name only, with no version or content claim (`english-*-developer-style`, `docs-page-authoring`, `test-authoring`, `problem-report-authoring`, `qubership-repo-essentials` with a local path). None needs a change.
- **Counts.** No sentence counts the slots or rules differently from before. The slot count of five and six is unchanged.
- **Other paths with the same symptom.** The commit-body variant of the open-question rule is finding 4. The changelog variant of the audit rule is finding 3.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The new What-slot `After` states an outcome in prose ("a caller that runs before startup completes fails at once instead of opening the pool on demand"). The next paragraph says that outcome goes on its own `User-visible changes` line, and slot 3 says it is "not restated in slot 2". The `After` also ends "it sends directly", which a reviewer recovers from one hunk (the new Translation check). The rule's own example fails the rule. | Substantive | `SKILL.md` ~l.350-358 (the `After` paragraph) | Remove the outcome clause from the `After`, or the "sends directly" clause. Re-apply the Translation check to the example. |
| 2 | Checklist Translation says to delete every sentence "where the diff still says it". That deletes the public-identifier sentence that §2 says to name once, and it does not say that the reason stays. | Substantive | `SKILL.md` ~l.826 (Translation item) | Add "except a public identifier the change adds, removes, or renames (§2)", and "keep the reason". |
| 3 | Changelog row 3 says "(§2, slot 2)" for "the condition alone". Slot 2's text never says what a changelog entry carries. The commit message says it does. | Substantive | `SKILL.md` l.475 and l.88-96 | Add one sentence to slot 2 on the changelog entry for such a defect, or drop the pointer. |
| 4 | The open-question rule and the Discussion item put the maintainer question in the "Scope slot". A description that §4 rule 5 makes a commit body has no Scope slot (checklist Scope item says so). The question then has nowhere to go. | Substantive | `SKILL.md` l.458-464 and l.834-838 | Say where the question goes in a commit body, or say that the rule applies to a separate description only. |
| 5 | "end the sentence there" for an audit-found defect would drop a symptom someone observed and reported. | Substantive | `SKILL.md` l.90-96 and the slot 2 table cell | Add "where no one has observed it fail" to the rule and to the table's skip cell. |
| 6 | The version bump is not claimed by a sentence of the commit message. | Taste | `apm.yml`, `marketplace.json` | Add a clause "1.3.0 to 1.4.0 (new rules)". |
| 7 | Rejected-alternative mechanism "as a fact about the merged code" excludes constraints outside the code, such as a supported version or a policy. | Taste | `SKILL.md` ~l.370 | Allow "or a constraint the repository states". |
| 8 | Trace-leaves-repository clause missing from the derived-consequence rule. | Taste | `SKILL.md` ~l.99-101 | "…and stop at the last verified step". |

**Not checked.** I did not run the suite or any blind draft (so the effect of the new rules is as stated by the writer, not seen by me). I did not run link, markdown, or CI jobs. I did not load `apm-authoring` because it is not in the given skills directory, so rules from it were not applied. The prose-style pass was not done beyond wording that makes a sentence read wrongly.
