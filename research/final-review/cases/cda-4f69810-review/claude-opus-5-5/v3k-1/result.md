I reviewed `d79c43d..HEAD` (one commit, `4f69810`), and it needs another pass before merge. I found 11 substantive findings and 2 matters of taste. The worst problem is that two of the skill's own worked examples break the rules this commit adds. Three rules also lack a clause where they stop: the new changelog rule drops the error text the skill elsewhere calls essential, the Translation checklist line deletes the public names the rule says to keep, and the open-question rule can push a reviewer-only question into the permanent commit.

# Final review: `d79c43d..HEAD`

**What was reviewed.** The change touches only a skill package (`SKILL.md`, `README.md`) and version strings, so I filled the form through the §2a analogues for "a change with no code". `SKILL.md` below means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

**Inputs.** There was no task statement. I took the claimed cases from the commit message alone, as the skill allows. There is no previous report of this form for this change. I loaded `english-developer-style` (from the given folder) and `apm-authoring` (the repo copy under `agent-packages/`). I ran `comment-drift.py d79c43d HEAD`; it printed nothing and exited 0, as expected, since the change has no code members to parse.

## Item 1: comments consistent with the code and with each other
*Analogue: every statement one changed file makes about another file or about itself, including the worked examples.*

- **Substantive – the older PR example breaks the new Translation rule.** The new rule (`SKILL.md:341-347`) and checklist (`:826`) cut any sentence the reviewer can recover from one hunk. The What paragraph of the existing *After* example (`SKILL.md:254-255`), "The orphan sync is requeued with backoff on failure instead of being dropped", is exactly such a sentence. Following the rule leaves the canonical example with only the rejected alternative, and the What slot's own job ("the behavioral change", `:196`) is gone. The skill now contradicts itself, and the clause it needs is the one the Translation row would carry.
- **Substantive – the new What-slot example puts an outcome in prose.** The *After* at `SKILL.md:353` says "a caller that runs before startup completes fails at once". The explanation at `:357-359` calls that same failure an outcome that belongs under "User-visible changes", and `:231` says a fact in that slot is not restated in the What slot. The commit message claims the example "no longer puts an outcome in prose", which is not the case. A drafting agent copying the example writes the failure twice.
- **Substantive – the README over-states the skill.** `README.md:28-30` says an audit-found defect gets "neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` does allow a traced consequence, marked as derived. A reader of the README expects a flat ban that the skill does not impose.
- No sentence narrates the change ("now", "no longer") outside a measured note. The §7 pointer to the What slot (`:763-764`) and the "§2 asks for what changed that the diff does not show" claim (`:288`) both hold.

## Item 2: claimed cases covered
*Analogue: each claim in the commit message against the section that handles it, plus every hunk against a claim.*

| Claim in the commit message | Where it is handled |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:81`, `:91-96`, checklist `:803-806` |
| Changelog entry names the condition alone | `:475` |
| A derived consequence is written only when traced and marked as derived | `:98-101`, `:804` |
| "Say so" kept for a defect with no symptom by construction | `:94-96`, `:81` |
| What slot: one-hunk sentences are translation, public identifier named once | `:341-359` |
| §7 points to this rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternatives: mechanism as a fact about merged code; an obstacle the change removes is a step it took | `:370-374`, `:836-837` |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, `:199`, `:838-841` |
| Checklist: Symptom and Alternatives extended, Discussion and Translation added | `:803`, `:826`, `:836`, `:838` |
| Slot 2 and What slot carry a bad and a good example | `:92-93`, `:349-355` |
| "This skill has no cases under research/" | True: `research/change-description-authoring/` has no `cases/` folder, unlike `blackbox-test-design` and `problem-report-authoring`. |

- **Commands the change tells someone to run:** none added.
- **Substantive – two hunks no sentence claims.**
  - The version bump from 1.3.0 to 1.4.0 in `apm.yml:168`, the package `apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The three previous commits on this package each stated their bump in a sentence ("Version 1.2.0 to 1.3.0").
  - The two `README.md` bullets (`:26-32`).
  
  The fix is one sentence in the message that claims both.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the genres and situations the change claims as partitions; the table of added instructions as the negative control.*

- **Substantive – the trials cover only one of the three artifacts.** The audit rule claims three: commit body, PR description, and changelog entry. The trial was "blind drafts of one pull request description". The commit body (`:91-96`) and the changelog entry (`:475`) have no evidence at all.
- **Substantive – no noise input was checked.** No trial used an input where the added rule is noise and checked that the output did not grow. Examples: a defect with an observed log line, where the audit rule must not fire; a change with no open questions, where the Discussion item must add nothing. This is also the control §2a asks for.

I counted 7 added or widened instructions: slot-2 audit rule, derived consequence, changelog condition-alone, Translation rule with its identifier exception (`:288` is the same concern), alternatives mechanism, open questions, and the checklist lines that restate them.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:475` "the condition alone" | An audit-found defect a regression test later reproduced, emitting a literal error | A changelog entry with no diagnostic; R3's grep misses it, against §3 `:511-512` | "unless a test or a run has reproduced the symptom" |
| `:461` "keep it in the Scope slot" | A squash repo with "title and description" (§4 rule 5), with a maintainer-only compatibility question | The open question lands in the permanent commit body, against `:609-610` "keep reviewer-only content out" | "; under §4 rule 5, ask it in a review comment instead" |

The Translation instruction gets no row: Item 1's orphan-sync finding and Item 5's identifier finding cover it.

Not findings: `:98` "The change is not a fix"; `:369` "when a reviewer would propose it"; `:91` "Where reading the code or an audit found".

## Item 3a: level, placement, and the environment
- `make check` (the marketplace gate) exits 0. `make check-descriptions` passes: "all 27 skill descriptions are within 1020 characters".
- The layout matches the sibling packages, and the umbrella `qubership-repo-essentials` uses the package by path, with no version to bump.
- No new sentence reads as generic tutorial text.
- **Taste – no slot for the answer.** The open-question rule (`:458`) sits under `#### Scope`, but its "give the answer and its evidence" branch names no slot. An agent may put answered questions in Scope.

## Item 4: names by content, not by position
- **Taste – an ordinal reference.** `:357-358` says "the first sentence says why". Naming it by content ("the sentence on the pool opening at startup") would survive a reordering. It is two adjacent sentences, so the risk is small.
- The headings and § cross-references all refer by name or number of section, which is fine.

## Item 5: the failure report
*Analogue: does the checklist reach every new rule, and does each check detect that rule rather than a weaker one?*

- **Substantive – the Translation check is weaker than the rule.** The check (`:826`) deletes a sentence only "where the diff still says it". A sentence like "With the pool opened at startup, the lazy `ensureOpen()` calls are removed" survives that check, because the diff does not state the causal lead-in. Yet the rule (`:342-344`) says the lead-in does not exempt it. This fits the commit's own finding that translation "persists in about one draft in two", since the drafting agents say they check against §8.
- **Substantive – the Translation check drops the identifier exception.** The checklist line omits it, so an agent following it deletes the sentence naming a new system property, which `:345-347` says to keep.
- **Substantive – the Symptom check pushes the wrong text into changelogs.** The check (`:804-805`, "does the sentence end at what found it?") is the only check on the audit rule. Applied to a changelog entry, it asks for "An audit found…", where `:475` asks for the condition alone. The Changelog check (`:842`) never mentions that case.

## Item 6: what the writer says it verified
- **What the writer did state:** counts from 15 blind Opus drafts.
- **What the writer did not show:** the drafts and their inputs are not in the change. The writer also says outright that the current open-question rule and the What-slot example were not re-run.
- **Substantive – the rewritten rules fail the change's own examples.** I applied them to the examples by reading, without running anything. The rewritten What-slot rule fails both the new pool example (Item 1, outcome in prose) and the existing orphan-sync example (Item 1, Translation).
- **Substantive – no check for growth.** No noise input was tried, as Item 3 says.

## Item 7: siblings of the change
- Version strings match in all three places, the README covers the new rules, and the umbrella needs no edit.
- `english-developer-style` and `problem-report-authoring` contain no rule that contradicts the new ones (I searched for symptom, audit, paraphrase, and open-question wording).
- **Substantive – the rule was not added where the drafts were written.** The audit-found handling went into the commit-body slot 2 (`:81`) and the changelog (`:475`). The PR description's Why slot (`:195`, "The problem, the symptom, the condition that reaches it") still asks for a symptom. That is the slot the trial's drafting agents said they write from. It inherits the rule only through "Slots 1 and 2 are the commit body's slots 1 to 3" at `:204`.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The older PR *After* What paragraph breaks the new Translation rule | Substantive | `SKILL.md:254`, `:341` | Exempt the sentence that states the behavioral change (at what a caller sees), or rewrite the example to pass |
| The pool *After* states an outcome in prose that also goes under User-visible | Substantive | `SKILL.md:353`, `:231` | Drop "fails at once…" from the What sentence, or exempt it by name; fix the commit claim |
| The README says "neither a predicted failure", but the skill allows a traced, derived one | Substantive | `README.md:29` | Align with `SKILL.md:98-101` |
| Version bump and README hunks unclaimed in the commit message | Substantive | `apm.yml:168`, `README.md:26` | Add one sentence claiming both |
| Changelog "condition alone" drops a reproduced diagnostic | Substantive | `SKILL.md:475` | Add "unless a test or a run has reproduced the symptom" |
| Open question kept in Scope lands in git log under §4 rule 5 | Substantive | `SKILL.md:461` | Add "; under §4 rule 5, in a review comment instead" |
| Translation check misses the lead-in case | Substantive | `SKILL.md:826` | Add: a sentence whose only addition is a lead-in reason is cut down to the reason |
| Translation check omits the public-identifier exception | Substantive | `SKILL.md:826` | Add "except a public identifier the change adds, removes, or renames (named once)" |
| Symptom check asks changelog entries to name what found the defect | Substantive | `SKILL.md:804`, `:842` | Scope that clause to the commit body and description; add "condition alone" to the Changelog item |
| PR Why slot lacks the audit-found clause | Substantive | `SKILL.md:195` | Add the audit-found clause to the Why cell |
| Commit body and changelog partitions untested; no noise input; rewritten rules not re-run | Substantive | commit message | Run drafts for the commit body and changelog, plus one noise input each for the audit and Discussion rules; re-run the What-slot and open-question wording |
| Answered questions have no named slot | Taste | `SKILL.md:458` | Name the slot for the answer |
| "the first sentence" | Taste | `SKILL.md:357` | Refer to the sentence by its content |

This review did not run any drafting trials, did not run `make test` (the change touches no tested script), and did not do a style-only pass over the prose.
