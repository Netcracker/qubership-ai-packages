# Final review: `d79c43d..HEAD` (4f69810)

**Claimed cases.** There is no separate task statement, so the claimed cases come from the commit message alone.

**Change type.** The change has no code: it edits a skill, a package README, and version entries. Each item below uses the §2a analogue. I did not run the drift script because there are no members to parse.

**Skills.** I read `final-review/SKILL.md` in full. I did not load `english-developer-style` or `apm-authoring`, and I did not check wording for style alone.

**Previous report.** None exists.

## Item 1: comments consistent with the code and with each other (analogue: statements about other parts of the repository)

- **Finding A (substantive).** The *After* example in `SKILL.md` ("What" slot, around lines 354–360) breaks the rule it illustrates.
  - Its second sentence is "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly." A reviewer recovers that from the one hunk that swaps `sendWithRetry` for `sendDirect`.
  - The new "Translation" checklist item says to delete such a sentence. The skill's own example therefore fails its own check (§2a, "What the writer says it verified"; `apm-authoring` *One canonical example per concern*).
  - The sentence after the example, "The removed `ensureOpen()` calls are gone from the text…", comments on the example. It does not state a rule.
- **Finding B (substantive).** The new rule is not applied everywhere the symptom is asked for.
  - The PR-description table, "Why" slot (line 195), still asks for "the symptom" with no audit clause.
  - The rule was added to the commit-body table (line 81, "Slot 2"), the checklist, and the changelog row (line 475). The checklist and "Slot 2" text say "(§2)", so a reader of the PR template gets no hint of it.
  - The *Before/After* example sits under the commit-body slots, not the PR section.
- **Finding C (taste).** The PR "What" row (line 196) still says "The behavioral change, not the changed files". The commit message says "§2 asks for 'what changed that the diff does not show'", which only the prose at line 288 carries. The two are compatible, so this is optional.
- **Checks that passed.**
  - The README additions match the skill's new rules.
  - The version strings agree across `marketplace.json`, root `apm.yml`, and the package `apm.yml`: all three read 1.4.0.
  - `make check` and `make check-descriptions` pass. The check output was tail-truncated, but it showed no errors.
  - The instructions file has no matches for "symptom", "open", "translat", "hunk", or "alternative", so it needs no sync.
  - No sentence narrates the change ("now", "no longer") outside the examples.
  - The `Not changed:` / `User-visible:` references from the earlier commit are unaffected.

## Item 2: claimed cases covered (analogue: rules that have a detection)

The commit claims these rules, each with a detection:

| Claim | Rule text | Detection |
| --- | --- | --- |
| Slot 2: audit-found defect | lines 81, 91–96 | checklist "Symptom" |
| Derived consequence traced and marked | line 99 onward | checklist "Symptom" (second question) |
| What slot: translation | lines 342–360 | checklist "Translation" |
| Public identifier named once | same | none |
| Rejected alternative stated as a fact about merged code | line 369 onward | checklist "Alternatives" |
| Open questions | line 458 onward | checklist "Discussion" |
| §7 pointer | line 763 | n/a |

- The "public identifier named once" exception has no checklist line. The "Translation" item says "delete each sentence… where the diff still says it, leave it deleted", which would delete the identifier sentence. The exception and the checklist item conflict. **Finding D (substantive).** The request is to add "except a public identifier (§5)" to the "Translation" item.
- The commit message says the *Translation* examples avoid the PR the drafts were written for. That claim holds.
- There are no commands the change tells anyone to run, so the command-line half of this item is **none**.
- Every hunk maps to a sentence in the commit message, including the version bumps and the README. **none** for orphan hunks.

## Item 3: boundaries, partitions, and the negative control

- **Evidence.** The commit message reports the draft evidence ("fifteen blind Opus drafts…") and admits two untested pieces. These are the current open-question rule and the What-slot example.
- **Finding E (substantive).** The new *After* example (Finding A) is one of the untested pieces, and it fails the rule, which a re-run of the checklist would have caught. The request is to apply the "Translation" checklist to both examples before merge.
- **Negative control for the Translation rule, tested by hand.** I used a one-line fix.
  - The rule, followed literally, still makes the writer write a "What" slot and run the deletion check.
  - The skill already ends it in §7 ("When to write nothing"), so this row is not a finding.
- **Added-instruction table:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found the audit-found defect | a defect an audit found that has a user-visible symptom reported in the issue | the symptom is dropped, because "end the sentence there" | none (**taste**: "where reading the code or an audit found the defect" does not say "and no report exists") |
| Trace a derived consequence "through every mechanism on the way" | a one-line fix with an obvious caller-visible failure | a tracing paragraph | "earns a sentence only after" ends it; the instruction applies only when a consequence is written |
| Public identifier named once | a renamed local variable | — | "public identifier… (a system property, a flag, an option)" |
| Question left open: keep it in Scope | a question the issue raised about an unrelated area | — | "Leave a question out only when it does not bear on this change" |
| Alternatives as facts about merged code | a change with no reviewer-proposable alternative | — | existing: "earns its sentence only where a reader would propose it" |

- **Pre-existing state.** None applies. The package is installed as a new version, and the roundtrip test checks versions and the index.

## Item 3a: level, placement, and the environment

- **Placement.** Rules sit in the same SKILL.md sections as their siblings. README bullets are in the same list.
- **Gate.** The repository's own gate (`make check`, `make check-descriptions`) ran offline and passed.

## Item 4: names by content, not by position

- **none** for the change's own text.
- The checklist uses names ("Symptom", "Translation"), not ordinals. "§2, slot 2" is a section reference, not a position.
- The new text names its measurements by content ("two of two drafts…", "three of three drafts…").

## Item 5: the failure report

- Each new rule has a detection, but the detections are weaker than the rules:
  - The "Alternatives" question "Is that mechanism a fact about the merged code, and not an obstacle the change itself removes?" asks for a judgment. It does not tell the reader what to check. This is the same defect the commit was about, and is **taste**.
  - "Discussion" has three questions and no way to see which fails. **taste**.
- The "Symptom" detection is reached by the checklist and detects the rule, not a weaker property. **none**.

## Item 6: what the writer says it verified

- **Evidence stated.** Draft counts: without a symptom rule, 2 of 2 predicted a failure; under a ban on the word, 5 of 10 stated "none seen"; under the final wording, 0 of 2 did. Retold obstacle: 2 of 4 drafts to 0 of 4. Open question: 3 of 3 to 0 of 4.
- **Weaknesses.**
  - The final wording was tested on two drafts only.
  - The "no longer evaded" claim rests on n=2.
  - Hunk translation "persists in about one draft in two", and the new example itself shows it.
  - The commit states that the research directory has no cases to re-run and that the open-question rule and What-slot example were not re-run. That is a disclosed gap.
- **Not stated.** No exemplar-and-bad-case pair exists. The report does not say that a draft with an unneeded item came out no longer (the noise case).

## Item 7: siblings of the change

- **The set** of "places that enumerate or route to the artifact": README (updated), `marketplace.json` (updated), root `apm.yml` (updated), `apm.lock.yaml` (no entry for this package), package `apm.yml` (updated).
- **Description mirrored in index and manifest.** Identical in `marketplace.json`, root `apm.yml`, and package `apm.yml`. The skill's description field was not changed, so it did not move with the widened scope. A widened scope not shown on the loading surface is the "classic miss", but the new rules narrow drafts. They do not widen what loads the skill.
- **Siblings of the rule.** Beyond the PR "Why" row in Finding B:
  - §7a/§7b contain nothing that contradicts the new rules.
  - The changelog "Fixed" examples (lines ~487–500) carry a symptom, so the audit rule does not apply to them.
  - "Package install over an earlier version" is not a concern for a skill.
- **Set counts.** No prose counts the checklist items.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| A | The *After* example's second sentence is a one-hunk translation and fails the new "Translation" check; the line below it comments on the example | substantive | `SKILL.md` ~354–360 | Cut "QueryExecutor.execute used sendWithRetry… sends directly" from the example, or replace it with a sentence the diff does not show; drop the "gone from the text" sentence |
| B | The PR "Why" row still asks for "the symptom" with no audit clause, unlike the commit-body row | substantive | `SKILL.md` 195 | Add "; for a defect an audit or a code reading found, what found it (§2, slot 2)" |
| D | The "public identifier named once" exception has no place in the "Translation" checklist item, which says to delete every hunk-recoverable sentence | substantive | `SKILL.md` ~826 | Add "except a public identifier (§5)" to the "Translation" item |
| E | The new example was not run through the new checklist; the commit says the What-slot example was not re-run | substantive | commit message | Run the "Translation" check on both examples and state it |
| F | The audit rule does not stop where an issue also reports a symptom someone observed | taste | `SKILL.md` 81, 91 | Add "and no observed symptom is reported" |
| C | The PR "What" row keeps "not the changed files" while the prose says "that the diff does not show" | taste | `SKILL.md` 196 | Align the row with line 288 |
| G | The "Alternatives" and "Discussion" checklist items are judgments with no stated evidence | taste | `SKILL.md` ~835–840 | None required |

**Not checked:** I did not run the blind drafts or any test suite, and I did not do a style-only pass over the prose.
