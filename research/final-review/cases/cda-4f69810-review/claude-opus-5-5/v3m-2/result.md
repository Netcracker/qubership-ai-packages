# Final review: `d79c43d..4f69810`, one commit

**Inputs.** I had no separate task statement, so the claimed cases in item 2 come from the commit message alone. There is no previous report of this form for this change. The change has no code: it edits one skill, its README, and three version fields. I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring`. I ran `comment-drift.py d79c43d HEAD` anyway; it exited 0 and printed nothing, since it has no members to parse in Markdown or YAML.

In this report, `SKILL` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` at HEAD, and `README` means `agent-packages/change-description-authoring/README.md`.

## Item 1: comments consistent with the code and with each other

*Analogue used: statements the changed files make about each other and about the repository.*

1. **Two rules conflict on a defect an audit found that also has no symptom by construction.** `SKILL:92` says that where an audit found the defect, the body names what found it and ends the sentence there. `SKILL:94-96` says a defect with no symptom by construction (its own example is "a leak on an error path with nothing logged") gets that absence stated. A leak like that is exactly what an audit finds. For that input, one rule asks the writer to stop at what found it and the other asks them to state that nothing shows. The checklist at `SKILL:803-806` asks both questions and doesn't say which one wins.
2. **The Translation checklist item contradicts the public-identifier exception.** `SKILL:826` says to delete each sentence of the What slot in turn and leave it deleted where the diff still says it. `SKILL:345-347` says a public identifier the change adds or renames is named once, because readers search for it. The diff always shows a new property name, so the checklist deletes the one sentence the rule keeps.
3. **The What-slot example still puts an outcome in prose.** The commit message says the example "no longer puts an outcome in prose". The *After* at `SKILL:353` says "a caller that runs before startup completes fails at once instead of opening the pool on demand", which is something a caller observes. `SKILL:357-359` then sends the same outcome to "User-visible changes", and `SKILL:231` says a fact in slot 3 is not restated in slot 2.
4. **The README rules out what the skill allows.** `README:28-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL:98-101` allows a consequence derived from the code, if it is traced to the caller and marked as derived. The README is also stricter than the skill on the second half (see item 5, finding 1).
5. **Taste:** `SKILL:81` puts "for a defect an audit or a code reading found, the body names what found it" in the "Skip when" column. Prose at `SKILL:92` treats it as what slot 2 carries, not as a skip.

There are no narrating words (`now`, `no longer`) outside examples. The measured counts in the skill match the commit message: "two of two" at `SKILL:100` and "three of three" at `SKILL:464`.

## Item 2: claimed cases covered

*Analogue used: the section of the skill that handles each case the commit message claims.*

| Claimed case (commit message) | Section that handles it |
| --- | --- |
| Slot 2: name what found an audit-found defect, and end the sentence there | `SKILL:91-93`, `:81` |
| Changelog entry names the condition alone | `SKILL:475` |
| Derived consequence is traced to the caller and marked as derived | `SKILL:98-101` |
| "Say so" is kept for a defect with no symptom by construction | `SKILL:94-96` (conflicts with `:92`, item 1 finding 1) |
| What slot: one-hunk sentence is translation even under a lead-in that gives a reason | `SKILL:342-345` |
| A public identifier is named once | `SKILL:345-347` (contradicted by `:826`, item 1 finding 2) |
| §7 points to this rule | `SKILL:763-764` |
| §2 asks for "what changed that the diff does not show" | `SKILL:288` |
| Rejected alternatives: the mechanism is a fact about the merged code | `SKILL:370-373` |
| Open questions: answered, kept in Scope, or dropped | `SKILL:458-465`, `:199` |
| Checklist: Symptom, Alternatives, Discussion, Translation | `SKILL:803`, `:832`, `:835`, `:826` |
| Slot 2 and What slot each carry a bad and a good example | `SKILL:92-93`, `:349-355` |
| "Each fix … has a checklist item" | Not met for the changelog rule at `:475` (item 5, finding 2) |

**Commands:** none. The change adds no command line.

**Hunks that no sentence of the commit message claims:**
- The README bullets at `README:26-32`.
- The version bump from 1.3.0 to 1.4.0 in `apm.yml`, the package `apm.yml`, and `marketplace.json`. This follows the repository's usual pattern, and `make check` reports `1.4.0 [matches]`.

## Item 3: boundaries, partitions, and the negative control

*Analogue used: the genres and modes the skill claims, and the instructions table below.*

- **Two of the three claimed genres have no evidence.** The skill covers commit bodies, PR descriptions, and changelog entries. All fifteen drafts were PR descriptions. The slot-2 rule (`SKILL:91`) is written for the commit body, and the changelog rule (`SKILL:475`) is new, so both were never exercised. **Substantive.**
- **One open-question branch has no evidence.** The "kept open for a maintainer" branch was never run, and the commit message says so.
- There is no state a previous install leaves behind that matters here: a skill text replaces the old one. No limits or replaced mechanism are involved.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:475` "for a defect an audit … found, the condition alone" | An audit-found defect whose regression test reproduces the `TRAP:` assertion (the skill's own example at `:156`) | A changelog entry with no diagnostic text for R3 to grep | "unless a test or a report has since shown the diagnostic" |
| `:461` "keep it in the Scope slot as a question" | Squash with "title and description" (§4 rule 5, `:608`) | A maintainer's open question written permanently into the commit body | "where the description stays on the platform; under §4 rule 5, in a review comment" |

Not findings: `:98`, `:370`, `:763`.

## Item 3a: level, placement, and the environment

*Analogue used: where each rule lives, and the repository's own gate.*

None. Every rule sits in its slot section, with a matching checklist line where one exists. `make check` passed offline (exit 0, `change-description-authoring 1.4.0 [matches]`), and so did `make check-descriptions` ("all 27 skill descriptions are within 1020 characters"). No added sentence is generic tutorial material.

## Item 4: names by content, not by position

- **The changelog row cites "slot 2" by number.** `SKILL:475` cites `(§2, slot 2)`. §2 holds three numbered tables, and in the PR description table slot 2 is "What". The changelog table that contains the citation has its own part 2. The checklist elsewhere names slots by content, as in `(§2, the What slot)`. The request is `(§2, Impact and trigger)`. **Substantive.**
- No other new reference uses a position.

## Item 5: the failure report

*Analogue used: whether each rule's checklist line detects that rule.*

1. **The Symptom check passes the very output the commit message set out to stop.** `SKILL:805` asks "does the sentence end at what found it?". That passes `An audit of the retry paths found this. No failure has been observed.`, which is the "none was seen" wording the commit message describes. The ban on it lives only in the statement at `SKILL:94`, and only the README says it outright. The request is a check that no sentence in the slot states either a predicted failure or the absence of one. **Substantive.**
2. **The changelog rule has no checklist line.** The Changelog item at `SKILL:842` is unchanged, and the Symptom item asks about the body only. That leaves `SKILL:475` unchecked, which is the gap the commit message says each fix closes.
3. Item 1 finding 2 also counts here: the Translation check detects the opposite of the identifier exception.

## Item 6: what the writer says it verified

The commit message reports fifteen blind Opus drafts, with before-and-after counts per defect. It says honestly that the drafts ran against version 1.0.1, and that the current open-question rule and the What-slot example were not re-run.

What is missing:
- None of the drafts is named in the change or kept under `research/change-description-authoring/`. So neither an exemplar the rules pass nor a bad case they fail can be checked.
- Nothing shows that output stayed the same length on an input where the new items are noise, such as a feature change with no defect and no open question.
- The final symptom wording rests on "none of two".

**Substantive:** name or commit the bad drafts and one noise-input draft, or say they can't be shared.

## Item 7: siblings of the change

- **A sibling skill has the same gap.** `problem-report-authoring` (`SKILL.md:90`) tells the writer to "open with the user-facing symptom". A report of an audit-found defect meets the same pressure to invent a symptom. The request is to apply the rule there too, or name it as follow-up. **Substantive.**
- I checked these and found nothing to change:
  - The trigger file.
  - `references/merge-model.md`, which has no slot text.
  - The `english-developer-style` copies; their §7 provenance rule is consistent.
  - The other `*-authoring` skills, where "rejected alternative" refers to doc comments, a different rule.
- The marketplace and index entries carry the matching version.
- No new member was added to a set, so there are no counts to update.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The rule for audit-found defects conflicts with "say so" for a defect with no symptom by construction | Substantive | `SKILL:92`, `:94` | State which rule wins when a defect is both |
| The Translation check deletes the public identifier the exception keeps | Substantive | `SKILL:826` vs `:345` | Add "except a public identifier (§2)" to the check |
| The What *After* example restates an outcome in prose, against the commit's claim and `:231` | Substantive | `SKILL:353` | Drop "fails at once…" from the What sentence |
| The README forbids any predicted failure; the skill allows a traced one marked as derived | Substantive | `README:28-30` | Align the README with `SKILL:98` |
| The Symptom check passes an absence claim written in the next sentence | Substantive | `SKILL:805` | Check that the slot states neither a prediction nor an absence |
| The changelog "condition alone" rule has no checklist line | Substantive | `SKILL:475`, `:842` | Add it to the Changelog item |
| `(§2, slot 2)` is ambiguous across three tables | Substantive | `SKILL:475` | `(§2, Impact and trigger)` |
| The changelog rule drops a diagnostic that a test has since reproduced | Substantive | `SKILL:475` | See table row `:475` |
| A maintainer question in Scope lands in the commit body under §4 rule 5 | Substantive | `SKILL:461` | See table row `:461` |
| Commit body and changelog genres have no draft evidence | Substantive | `SKILL:91`, `:475` | Run drafts of a commit body and a changelog entry, or say they were not run |
| No exemplar, bad case, or noise-input check is named in the change | Substantive | commit message | Name or commit the drafts, or say why not |
| `problem-report-authoring` has the same invented-symptom gap | Substantive | `problem-report-authoring/…/SKILL.md:90` | Fix it there or name it as follow-up |
| The README hunk and the version bump are not claimed in the commit message | Taste | `README:26-32`, the three `apm.yml` and `marketplace.json` fields | One sentence claiming them |
| The audit-found case sits in the "Skip when" column | Taste | `SKILL:81` | Move it to the "Answers" column |

**Not checked:** I did not re-run any blind drafts, did not run `make test` or `install-smoke`, and did not review the prose for style alone.
