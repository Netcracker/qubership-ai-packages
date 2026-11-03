# Final review: `d79c43d..HEAD` (`4f69810`)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message only (`git log d79c43d..HEAD`). The change touches one skill, its README, and three version fields. It contains no code, so I used the §2a analogues under every item. I did not run the drift script's analysis because there are no members to parse. It printed nothing on this range. I loaded `english-developer-style` from the given copy. I did not load `apm-authoring` because it is outside the three permitted skills, so rules cited from it below come from the text of `final-review`.

## Item 1: Comments consistent with the code and with each other

Analogue: statements one file makes about another, counts, cross-references, and the repeated descriptions.

- **Cross-references.** Checked all of them: `§2, slot 2` (changelog row 3), `§2, the What slot` (§7), `§5` (identifiers), `§7`, and `§2` for the checklist. All point to existing sections.
- **Version.** `1.4.0` appears in `marketplace.json`, the package `apm.yml`, and the root `apm.yml`. No `1.3.0` remains for this package. `make check` and `make check-descriptions` ran offline and passed; `make check` only dry-ran the marketplace write.
- **Slots.** The skill still says "Five slots", which matches.
- **Finding A (substantive), `SKILL.md:352-360`.** The commit message says the What-slot example "no longer puts an outcome in prose". The new *After* says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome in prose. The sentence under it says the `IllegalStateException` "is an outcome, and it goes on its own line". The example therefore breaks the rule it illustrates, and a drafter will copy the prose version.
- **Finding B (substantive), `SKILL.md:~826`.** The new checklist item reads "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". The rule it checks exempts a public identifier ("name it once, because readers search for the change by that string"). Deleting that sentence passes the checklist, so the checklist deletes what the rule keeps. The commit message says checklist items were added to match each rule, and this one drops the exception.

## Item 2: Claimed cases covered

Analogue: each claim is covered by the section that handles it. A rule's detection is its test.

| Claim in the commit message | Section | Detection |
| --- | --- | --- |
| Slot 2: an audit or code-reading finding is named by its finder, and the sentence ends there | Slot 2 table row, prose with before/after, changelog row 3 | Checklist "Symptom" |
| A derived consequence is written only when traced to a caller | Slot 2 prose | Checklist "Symptom" |
| "Say so" stays for a defect with no symptom by construction | Slot 2 | Checklist "Symptom" |
| What slot: a sentence recoverable from one hunk is translation | What-slot text with before/after; §7 | Checklist "Translation" (see Finding B) |
| A public identifier is named once | What-slot text | None |
| §2 asks for "what changed that the diff does not show" | Paragraph-earning text | None needed |
| A rejected alternative is stated as a fact about the merged code | Alternatives text | Checklist "Alternatives" |
| Open question: answered, kept in Scope with decision and evidence, or dropped | New paragraph, Scope row | Checklist "Discussion" |

- The identifier-once claim has no detection (see Finding B).
- **Commands.** None are added.
- **Hunks.** Every hunk maps to a sentence of the commit message. The README bullets and the three version bumps are claimed by the bump to 1.4.0 and the README's "What it covers" list. I found no unclaimed hunk.
- **Unverifiable counts.** The commit message says "over fifteen blind Opus drafts". Its own breakdown (2, then 10, then 2 for the symptom rule, plus 4 and 4 for the other two) does not sum to fifteen in any way I can verify. This is taste; I can't check it from the repository.

## Item 3: Boundaries, partitions, and the negative control

Analogue: partitions are the situations the change claims. The control is the statement of what does not apply.

**Table of added instructions**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found the defect "and end the sentence there" | A defect an audit found that a user also reported with a log line | "An audit found this." The observed diagnostic is dropped, although slot 2 and changelog row 3 otherwise demand it. The changelog row says "the condition alone". | "…and no one has observed it" (substantive) |
| A derived consequence only after tracing, marked as derived | None found; the slot-2 skip ("not a fix") ends the trivial cases | n/a | n/a |
| A hunk-recoverable What sentence is deleted | A one-hunk fix where the only What sentence is recoverable | An empty What slot, or a restated hunk that the checklist then deletes | "…where the description spans more than one hunk" (taste: the What slot has no skip clause and §7 covers "write nothing") |
| Rejected-alternative mechanism is stated as a fact about the merged code | n/a | n/a | n/a |
| A maintainer-only question stays in Scope | A description that becomes a commit body, which has no Scope slot | No home for the question | "…in a pull request description" (taste) |

Not findings: "name a rejected alternative" is ended by "where a reader would propose it". "Answer the question from the code" is ended by "only a maintainer can settle", plus the drop clause "does not bear on the change".

- **Finding C (substantive), the audit-found-but-observed row above.** Slot 2 says "Where reading the code or an audit found the defect, name what found it and end the sentence there". That conflicts with the same slot's demand for a quoted diagnostic when users have seen one. A conflict between two rules is the finding (§2a step 3).
- **Negative controls in the evidence.** The commit message reports drafts only for inputs where each rule fires. Missing:
  - a symptomatic bug, to show the audit rule does not erase the symptom;
  - a one-hunk change, to show the What slot does not shrink to nothing;
  - a change with no open question, to show the output did not grow.

  See Item 6.

## Item 3a: Level, placement, and the environment

- **Placement.** All text sits in the existing sections and tables, and the README follows its sibling bullets.
- **Gate.** `make check` and `make check-descriptions` pass.
- **Finding D (taste), `SKILL.md:357-360`.** The paragraph after the example ("The removed `ensureOpen()` calls are gone from the text: the diff shows them…") is a sentence on what not to copy from the example. `final-review` §2a treats that as contradicting the "one canonical example" rule. The identifiers `ensureOpen`, `sendWithRetry`, and `QueryExecutor` are teaching props, so this is minor. I'd move the point into the rule text.

## Item 4: Names by content, not by position

Analogue: headings and cross-references. Nothing refers to a thing by ordinal; the numbered `§` references are the document's own section numbers. None.

## Item 5: The failure report

Analogue: what a rule tells the reader to look at, and whether its detection detects that rule.

- **Symptom, Alternatives, Discussion:** each detection matches its rule.
- **Translation:** weaker than its rule, because it lacks the identifier exception (Finding B).
- **Length checklist item:** still says outcome lines are left out of the count, which is consistent.

## Item 6: What the writer says it verified

- **Evidence stated.** The commit message reports blind drafts and honestly says the open-question rule and the What-slot example were not re-run, and that hunk translation "persists in about one draft in two".
- **Finding E (substantive).** There is no stated control arm, so the evidence covers only the "rule fires" cases. For the audit rule, the control is a bug with an observed symptom. For the translation rule, the control is a change where the What slot is short. For the open-question rule, the control is a change with no open question, where the output should not grow. `final-review` §2a asks for the "noise" input and a check that output did not grow.
- **The example.** The What-slot example was not run, and Finding A shows it breaks its own rule.

## Item 7: Siblings of the change

- **Version.** The three places that list it are all updated.
- **`1.3.0` elsewhere.** Only unrelated packages and a README tag example carry it.
- **Other mentions of the package.** `docs-page-authoring`, the style skills, and the rules files mention `change-description-authoring` by name only, with no counts or descriptions that would drift.
- **Same-concept sites in the skill:**
  - The PR **Why** slot (`SKILL.md:195`) still reads "the symptom". The audit rule lives in the commit-body slot 2 and the checklist, so a PR-description drafter may not apply it. Taste: add "(§2, slot 2)" to the Why row.
  - Line 319 ("The Why slot carries the symptom") has the same gap.
- **Research directory.** `research/change-description-authoring/` has no case files for the new rules. The commit says so.

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A: the What-slot *After* states an outcome in prose, contradicting the commit message and the note beneath it | substantive | `SKILL.md:352-360` | Remove "a caller that runs before startup completes fails at once…" from the example, or move it to a `User-visible:` line. Re-run the example. |
| B: the Translation checklist item lacks the public-identifier exception | substantive | `SKILL.md:~826` | Add "except a public identifier the change adds, removes, or renames (§2)". |
| C: "name what found it, end the sentence" conflicts with "quote the diagnostic" for an audit-found defect that was also observed | substantive | `SKILL.md:81, 92-96, 475` | Add "where no one has observed it" to the audit clause. |
| E: no control arm (observed-symptom bug, one-hunk change, change with no open question) | substantive | commit message and the research directory | Run and report one control draft per new rule. |
| D: a sentence on what not to copy follows the example | taste | `SKILL.md:357-360` | Move the point into the rule text. |
| Why row and line 319 do not point to the audit rule | taste | `SKILL.md:195, 319` | Add "(§2, slot 2)". |
| Open-question rule has no home in a commit-body-only description | taste | `SKILL.md:~455` | State where the question goes when there is no Scope slot. |
| "Over fifteen drafts" does not sum from the commit message's own figures | taste | commit message | State the arms and counts per rule. |

This review did not run the skill against any draft, did not re-run the blind drafts, did not run the full test suite, and did not check style or wording beyond sentences that read wrongly.
