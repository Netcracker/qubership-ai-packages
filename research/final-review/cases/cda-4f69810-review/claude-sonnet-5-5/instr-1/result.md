I've finished reading the change and the two skills, so I'm writing the report now.

# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.** There was no separate task statement, so item 2 uses the claimed cases from the commit message only.

**Change type.** The change has no code. It edits one skill (`SKILL.md`), its README, and three version fields, so I used the §2a analogues throughout. I loaded `apm-authoring` and `english-developer-style` from the given directory. `comment-drift.py` was not run in any useful way: it parsed nothing in Markdown or YAML, so there was nothing to list.

There is no previous report, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about each other. I found two problems.

- **Example contradicts its rule (substantive).** `SKILL.md:354-359`, the What-slot *After* example, opens with "so a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome stated in prose. The sentence two lines below says the same outcome belongs on its own `User-visible changes` line. The commit message says the example "no longer puts an outcome in prose", which is false for the file as committed. A drafter copying the example repeats the outcome in two places.
- **Explanatory paragraph after the example (taste).** `SKILL.md:357-359` follows the example with a paragraph on what the example leaves out. `apm-authoring` rule 2 and its pitfall "An example followed by 'do not copy this part'" apply. Prefer cutting the paragraph, or keeping only the pointer to the User-visible line.

Cross-references and counts check out:
- `§5` for identifiers and `§7` for the "No paraphrase of the diff" rule both point to the right sections.
- "Five slots" and "six slots" are unchanged and still correct.
- The Slot 2 skip condition, the changelog part 3, and the §8 Symptom item all carry the audit and code-reading clause consistently.
- The README sentences match the new rules.
- I found no `now` or `no longer` narration in the added rule text.

## Item 2: claimed cases covered

Analogue: for each claim, the section that handles it and how a reader can detect whether a text obeys it.

| Claimed case (commit message) | Where handled | Detection |
| --- | --- | --- |
| Audit-found defect described by what found it | Slot 2 prose (`:93-96`), skip cell (`:81`), changelog part 3 (`:475`) | §8 Symptom (`:803-806`) |
| Derived consequence traced and marked as derived | `:98-101` | §8 Symptom |
| Hunk translation cut | What slot (`:342-359`), §7 (`:763`) | §8 Translation item |
| Public identifier named once | `:346-348` | None. Translation says to delete a sentence that the diff still says, and a public identifier would be cut by it. |
| Rejected alternative stated as a fact about merged code | `:369-372` | §8 Alternatives |
| Open question answered, kept in Scope, or dropped | `:458-464`, Scope row | §8 Discussion |

- **Public-identifier exception has no detection (substantive).** `SKILL.md:346-348` and §8 Translation (`:826`). The §8 Translation item says to delete each sentence the diff still says. It never mentions the public-identifier exception. A checking agent deletes the sentence naming the flag, which is exactly what the exception forbids. Add the exception to that checklist line.

No commands are told to be run, except that `git log -S` is already in `apm-authoring`.

Every hunk belongs to a sentence of the commit message. The version bump in `marketplace.json`, the package `apm.yml`, and the root `apm.yml` is consistent across all three. The commit message does not mention the bump. That is a minor omission only, since other commits in the series do the same.

## Item 3: boundaries, partitions, and negative control

Analogue: the claimed genres and the negative control. The added-instructions table follows.

Partitions the change claims:
- audit-found defect;
- defect with no symptom by construction;
- derived consequence;
- question answered by code;
- question only a maintainer can settle;
- question not bearing on the change.

Evidence: the commit message reports measurements for the symptom, obstacle, and open-question rules. For the others it says plainly that they were not re-run:
- the current open-question wording;
- the What-slot example;
- research cases.

That is stated honestly, so it is not a finding.

**State left by the earlier version.** No installed-state concern applies. The package is only text.

**Negative-control inputs for the instructions the change adds** (the table below):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:98` "A consequence derived from the code earns a sentence only after it is traced" | a fix whose symptom is a quoted exception from the report | a "derived, not observed" label on a symptom that was observed | "only where the symptom came from the code and not from a report or a run" |
| `:342` "a sentence the reviewer recovers from one hunk is translation… state the reason for the decision" | a one-line fix | a reason sentence that only restates the commit subject | "only where the change makes more than one decision" |
| `:458` "answered, kept open, or left out" | a description with no open question | a Scope sentence about questions | "absent when the issue and review raise no question" |

Added instructions: 6 (fenced as 3 rows above). I filed three rows and did not row the others.

Not findings: `:93` (the audit rule is ended by its own condition, "named what found it and end the sentence there"); `:369` (the alternative rule is bounded by "where a reader would propose it", `:366`).

**Ambiguity (substantive, filed under item 1's rule).** Slot 2, `:93-96` and the skip cell `:81`. A defect "found by audit" with no symptom by construction (the leak example) satisfies both "name what found it and end there" and "say so". The text does not say which wins. Add: "when both apply, name what found it, then state that the defect has no symptom."

## Item 3a: level, placement, and environment

Analogue: right file, layout matching siblings, registration entries.

- Rules live in the one skill that owns them. The README summary was updated.
- The registration entries are consistent: `marketplace.json:291`, the package `apm.yml`, and the root `apm.yml:168`.
- `scripts/check-skill-descriptions.py` passes ("all 27 skill descriptions are within 1020 characters").
- Placement cosmetic (taste): `SKILL.md:462-464` has a reflow break ("wanted. Leave" / "a question…"). It is invisible when rendered but is a one-word orphan line in the source.
- Apm-authoring "Bump version when the contract changes, not on every prose edit": a minor bump for new rules is consistent with the series.

## Item 4: names by content

None. The new headings and bold lead-ins ("A question the issue or the review left open…") name content. No ordinals or positional references were added.

## Item 5: the failure report

Analogue: what a rule tells the reader to look at.

- Each of the new rules except the public-identifier exception has a checklist line (§8 Symptom, Translation, Alternatives, Discussion).
- Detection check on Translation: "delete each sentence in turn; where the diff still says it, leave it deleted" detects translation. It detects the weaker property "the diff says it", not "a reviewer recovers it from one hunk", and the two differ for a sentence carrying a reason. The rule says a reason is kept and the check's wording does not (taste; the finding above covers the exception).

## Item 6: what the writer says it verified

The commit states the measurements per rule and names the drafts' skill version (1.0.1). It also says what was not re-run. There is no named exemplar-and-bad-case pair. The 15-draft total ("Over fifteen blind Opus drafts") is not reconcilable with the per-rule counts it gives (2 + 10 + 2 + 4 + 4 + 3), and the drafts ran against 1.0.1, not the committed text. The writer's evidence is therefore partial, as it says itself.

The rewrite check from §2a, applying the new rules to the change's own worked example: the *After* example fails the outcome-in-prose rule (item 1 finding). That is the one place the rewrite does not pass its own example.

## Item 7: siblings of the change

Analogue: places that enumerate or route to the artifact.

- `.claude-plugin/marketplace.json` and `apm.yml` carry the new version. Sibling packages that cross-reference this skill (`docs-page-authoring/README.md:43`, `problem-report-authoring/README.md:81`, the two `english-*-developer-style` skills) refer to it by name only and are not affected.
- No sentence counts the slots or rules as before; I searched for the old counts and found none stale.
- The commit-body section (§2) and the pull request section (§2) each carry the symptom rule. The changelog section was updated too. All three paths are covered, and the checklist reaches all three.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| *After* example states an outcome in prose and then says it belongs on its own line; commit message claims otherwise | Substantive | `SKILL.md:354-359` | Rewrite the first sentence to state the reason only (the pool opens at startup, so `sendWithRetry` is unnecessary). Keep the outcome on the `User-visible changes` line. |
| Public-identifier exception has no checklist detection, and the Translation item contradicts it | Substantive | `SKILL.md:346-348`, `:826` | Add "except a public identifier the change adds, removes, or renames (§2)" to the Translation line. |
| Audit-found and no-symptom-by-construction both fire on the same defect | Substantive | `SKILL.md:81`, `:93-96` | State which wins when both apply. |
| Derived-consequence rule fires on defects whose symptom was observed | Substantive (row in item 3 table) | `SKILL.md:98` | Add "only where the symptom was not observed". |
| What-slot translation rule fires on a one-decision change | Substantive (row in item 3 table) | `SKILL.md:342` | Add "only where the change makes more than one decision". |
| Open-question rule fires where no question exists | Substantive (row in item 3 table) | `SKILL.md:458` | Add "absent when the issue and review raise no question". |
| Explanatory paragraph after the *After* example | Taste (prefer cutting) | `SKILL.md:357-359` | Cut it or reduce it to the pointer to the User-visible line. |
| Reflow break in the new Scope paragraph | Taste | `SKILL.md:462-464` | Rejoin the lines. |
| Commit message omits the version bump | Taste | commit 4f69810 | Mention it; low value. |

Not checked: I did not run the test or install-smoke suites, I did not re-run any blind drafts, and I did not verify the commit's draft counts. I did not review the prose for style beyond where it makes a sentence read wrongly.
