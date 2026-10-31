# Final review: `d79c43d..HEAD` (change-description-authoring 1.4.0)

**Inputs.** One commit, 4f69810. There is no separate task statement, so the claimed cases come from the commit message alone. Item 2 is answered from that message only. The skills loaded were `final-review` and `english-developer-style`. `apm-authoring` is not in the supplied skills directory, so its rules are not applied. The changed files are a skill, a README, manifests, and the marketplace JSON, so §2a applies. The drift script was not run because there are no members to parse. There is no previous report.

## Item 1: comments consistent (analogue: statements one file makes about another, counts, cross-references)

- **Finding (substantive).** `SKILL.md:81` and `:92-96` against the What-slot example (`:355-360`).
  - The commit message says the What-slot example "no longer puts an outcome in prose".
  - The "After" example opens with "a caller that runs before startup completes fails at once". That is a caller-observable outcome, written in slot 2.
  - The paragraph after it says the `IllegalStateException` "goes on its own line under User-visible changes".
  - `:228` says "A fact stated in slot 3 is not restated in slot 2".
  - The example therefore breaks the rule it sits under and the claim the commit makes about it.
- **Finding (taste).** `:93-96`.
  - "A predicted failure is not known, and neither is the absence of one" is followed three lines later by "a stated absence does not [look like an omission]".
  - The exception for a defect with no symptom by construction resolves it.
  - The leak example says "nothing logged", which is an observation, not a construction. Taste, so no request beyond noting it.
- Cross-references checked and resolving:
  - §2 (slots) and §3 (changelog parts) are real headings.
  - §5 is "Trailers and the identifiers a reader greps".
  - §7 and the §8 checklist exist.
  - Version 1.4.0 appears identically in `apm.yml` (root), the package `apm.yml`, and `marketplace.json`.
  - No remaining "1.3.0" for this package.
- No sentence narrates the change (`now`, `no longer`, `used to`) outside the Before/After examples, which are labeled.
- Formatting (churn, not reported as a request): a stray line wrap at `:461-462` ("wanted. Leave / a question").

## Item 2: claimed cases covered (analogue: section that handles each claim, plus detection)

| Claim in the commit message | Section | Detection |
| --- | --- | --- |
| Slot 2: audit or code-reading defect described by what found it; changelog gets the condition alone | `:81`, `:92-96`, `:475` | Checklist Symptom, `:803-806` |
| A derived consequence is written only after tracing to what a caller sees, and marked derived | `:98-101` | Checklist Symptom ("traced in the code and marked as derived") |
| "Say so" kept for a defect with no symptom by construction | `:94-96` | Checklist Symptom |
| What slot: a sentence recoverable from one hunk is translation; a public identifier is named once; §7 points to the rule; §2 says "what changed that the diff does not show" | `:288-289`, `:342-359`, `:763-764` | New Translation item, `:826`. The item omits the identifier exception (see Item 3 and the findings table). |
| Rejected alternatives: the mechanism is a fact about the merged code; an obstacle the change removes is a step it took | `:369-372` | Checklist Alternatives |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, Scope table row `:195` | New Discussion item |
| Bad and good example in the Slot 2 and What-slot rules | `:92-93`, `:353-359` | Examples present |
| No cases under `research/` to re-run | n/a | `research/change-description-authoring/` holds phase prompts and results, not cases. Consistent. |

- No commands are told to run, so there is no command-line claim to cover.
- Hunk-to-claim check:
  - The version bumps in four files belong to the "feat" claim.
  - The README bullet belongs to the three new rules.
  - The §7 hunk is claimed ("§7 points to this rule").
  - No unclaimed hunk.
- The measured figures ("fifteen drafts", "two of two", "three of three") cannot be checked from the repository. The figures given for the retold-obstacle and open-question tests add up to more than fifteen drafts, which implies shared drafts. This is stated, not refuted.

## Item 3: boundaries, partitions, negative control (analogue: genres and situations, plus the table of added instructions)

- **Finding (substantive).** The audit rule in slot 2 and the changelog part 3 has no clause for the partition where the audit-found defect was then reproduced and a symptom was observed. See table row 1.
- **Finding (substantive).** The Translation checklist item (`:826`) says to delete each What-slot sentence the diff still says. The rule it checks (`:342-348`) exempts a public identifier. An agent following the checklist deletes the identifier. See table row 3.
- Pre-existing state: package installed over 1.3.0. The change is additive, and no persisted format is involved. None.
- Values that now reach another consumer, limits, and replaced mechanisms: not applicable.

Table of added or widened instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| 1. "Where reading the code or an audit found the defect, name what found it and end the sentence there" (`:91-93`; also `:81`, `:475`) | A defect an audit found and the author then reproduced, with an observed exception or log line | Drops the observed diagnostic, which R3 greps for, and writes only "An audit of X found this" | "only where no symptom was observed; a symptom you reproduced is quoted as in the rest of this slot" |
| 2. "A consequence derived from the code earns a sentence only after it is traced…and is stated as derived" (`:98-101`) | A defect with a symptom already observed | Marks an observed symptom "derived", or adds a trace nobody needs | The text already ends it: "derived, not observed" scopes it to derivation. Not a finding. |
| 3. "Translation: delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" (`:826`) | The sentence that names a new system property, flag, or option once | Deletes it, although `:342-348` and §5 require it | "except a public identifier the change adds, removes, or renames (§2)" |
| 4. "Keep it in the Scope slot as a question…" (`:458-465`) | A change whose description is a commit body of the five-slot shape. Scope is a slot of the pull request description only. | Invents a Scope paragraph in a commit body | `:458` sits under the pull-request Scope heading, which defines it. The scoping is implicit but present. Not a finding. |
| 5. "An obstacle the change itself removes is a step the change had to take, not a reason against the alternative" (`:369-370`) | A change with no rejected alternative | Nothing; it is conditioned by "where a reviewer would propose it". | Already ends it. Not a finding. |

## Item 3a: level, placement, environment

- Layout matches the sibling rules: the open-question rule is under Scope, the translation rule under What, and the Slot 2 rule under Slot 2.
- Registration entries match.
- Gate run: `scripts/check-skill-descriptions.py` printed `ok: all 27 skill descriptions are within 1020 characters`.
- None otherwise.

## Item 4: names by content

- None. The new text cites "the What slot", "slot 2", and "§2/§5/§7" by content or section.

## Item 5: failure report

- Each new rule has a checklist item (Symptom, Translation, Alternatives, Discussion).
- Each item detects its rule, except Translation. It detects a stronger property than the rule states, because it lacks the identifier exception. This is the Item 3 finding.

## Item 6: what the writer says it verified

- The commit message states blind-draft counts before and after.
- It also states what was not re-run: the current open-question rule and the What-slot example.
- Not stated: a noise input for the added items. Examples are a one-line fix with no What-slot content, a description with no open question, and a change with an observed symptom. This is the same gap as table row 1.
- Evidence is described but not attached; I did not run anything to supply it.

## Item 7: siblings

- Package siblings checked:
  - The README bullet is updated.
  - The umbrella `qubership-repo-essentials` depends by path and has no version pin.
  - The `english-developer-style` copies, `docs-page-authoring`, `problem-report-authoring`, and `test-authoring` only cross-reference the package by name.
- Digit and word counts of the slots ("Five slots", "Six slots", "five parts") are unchanged, because no slot was added.
- The commit-body table (slot 2, `:81`) and the changelog row (`:475`) were updated. The pull-request description's Why slot (`:197`) is not changed and is reached through "§2, slot 2". Acceptable.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The audit rule drops an observed symptom for a defect that was audit-found and then reproduced. No noise or partition run is stated. | Substantive | `SKILL.md:91-93`, `:81`, `:475` | Add a clause such as "only where no symptom was observed", and run it on an audit-found defect that was reproduced. |
| 2 | The What-slot "After" example states an outcome in prose, against `:228` and the commit's claim. | Substantive | `SKILL.md:355-360` | Move the failing-early-caller sentence out of the example, or end the example at the reason for the decision and leave the outcome to the User-visible line. |
| 3 | The Translation checklist item lacks the public-identifier exception, so it checks a stronger property than the rule. | Substantive | `SKILL.md:826` vs `:342-348` | Add "except a public identifier the change adds, removes, or renames". |
| 4 | "Neither is the absence of one" versus "a stated absence does not [look like an omission]". The leak example says "nothing logged". | Taste | `SKILL.md:93-96` | Optional: say "no symptom by construction" in both places. |

**Not checked:** the blind-draft counts and the "persists in about one draft in two" claim, which were not rerun and cannot be verified from the repository. No wording or style pass was done. `apm-authoring` was not available, so its rules are not applied. The drift script was not run. The suite was not run beyond `check-skill-descriptions.py`.
