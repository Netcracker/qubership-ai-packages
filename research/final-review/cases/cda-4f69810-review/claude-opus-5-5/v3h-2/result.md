# Final review: `d79c43d..HEAD` (commit 4f69810, change-description-authoring 1.4.0)

There was no task statement, so the claimed cases come from the commit message alone. This change has no code: it edits a skill (`SKILL.md`), the package README, and three version fields. I used the §2a analogues for every item below. I loaded `english-developer-style` (from the provided skills directory) and `apm-authoring` (from `agent-packages/apm-authoring`). I ran `comment-drift.py d79c43d HEAD` and it printed nothing, because it has no Markdown, YAML or JSON members to parse. The repository gate (`apm pack --check-versions --check-clean --dry-run`, the `marketplace.yml` validate job) passed: "Version alignment OK", "Marketplace working tree clean". `scripts/check-skill-descriptions.py` printed "ok: all 27 skill descriptions are within 1020 characters".

## Item 1: comments consistent with the code and with each other
*Analogue: statements one changed file makes about another, and the rules checked against each other and against the worked examples.*

- **The Translation checklist item contradicts the public-identifier exception.** `SKILL.md:826` says "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". `SKILL.md:345` says a public identifier the change adds, removes, or renames "is the exception: name it once". The diff always shows such an identifier, so an agent that checks against the checklist (which the commit message says drafting agents do) deletes the one sentence the rule keeps. The commit message claims the identifier rule, but no checklist item carries it, and the checklist item that exists asks for the opposite.
- **The README states a narrower rule than the skill.** `README.md:28-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code once it is traced to what a caller sees and marked as derived. A README reader concludes that derived consequences are banned.
- **The What-slot *After* example puts an outcome in prose.** At `SKILL.md:353` it reads "a caller that runs before startup completes fails at once". `SKILL.md:231` says "A fact stated in slot 3 is not restated in slot 2". `SKILL.md:358-359` then calls the early caller's failure "an outcome" that goes under "User-visible changes". The commit message says the example "no longer puts an outcome in prose". Only the exception class has moved; the outcome itself is still there. `SKILL.md:320` ("The What slot carries the new behavioral boundary") supports the reading that the sentence belongs, so the skill holds both rules and neither says which wins. This is substantive: either a clause separating the boundary in What from the observed text and class in slot 3, or a different *After*.
- Taste: `SKILL.md:462-463` breaks the line after "wanted. Leave". It renders the same and only looks odd in the source.
- Checked and consistent: the slot 2 table row against the slot 2 prose; the changelog row (`:475`) against "§2, slot 2"; §7 (`:763-764`) against the What slot; §2 "what changed that the diff does not show" (`:288`); the Scope table row (`:199`) against the open-question rule (`:458`); and the 1.0.1 → 1.4.0 version history the commit message cites (`git log` on `apm.yml` agrees).

## Item 2: claimed cases covered
*Analogue: each claim of the commit message mapped to the section that handles it, plus each hunk mapped to a claim.*

| Claim | Section |
| --- | --- |
| Slot 2: audit or code-reading defect described by what found it, sentence ends there | `:91-92`, table row `:81`, checklist `:803-806` |
| Changelog entry names the condition alone | `:475` |
| Derived consequence only when traced and marked derived | `:98-101`, checklist `:804-805` |
| "Say so" kept for no symptom by construction | `:94-96` |
| What slot: one-hunk sentence is translation even under a reason | `:342-345`, checklist `:826` |
| Public identifier named once | `:345-347`. **No checklist item, and the Translation item contradicts it (Item 1).** |
| §7 points to the rule; §2 asks for "what the diff does not show" | `:763-764`, `:288` |
| Rejected alternative is a fact about the merged code; a removed obstacle is a step | `:370-373`, checklist `:832-833` |
| Open questions: answered / kept in Scope / dropped | `:458-465`, Scope row `:199`, checklist `:835-838` |
| Bad and good example on slot 2 and the What slot | `:92-93`, `:349-355` |
| "Each fix … has a checklist item" | True for all except the public-identifier exception |

- No commands are introduced in the changed files.
- **Unclaimed hunks:** the version bumps 1.3.0 → 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The gate requires them, and the previous commit (d79c43d) claimed its bump in the message ("Version 1.2.0 to 1.3.0."). Taste.
- The detection for the slot 2 rule is the checklist line, so it has one.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the genres and modes the change claims, and the table of added instructions.*

**Partitions.** The rules cover three artifacts: the commit body (slot 2, `:81`, `:91`), the PR description, and the changelog (`:475`). The commit message says every trial used "drafts of one pull request description". So the commit body and the changelog entry have no evidence. The changelog's "condition alone" rule was never drafted against. Substantive.

**Pre-existing state.** `apm.lock.yaml` does not pin this package and there are no deployed copies under `.claude/`, `.agents/`, `.codex/` or `.cursor/`. Nothing to check.

**Added or widened instructions:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "name what found it and end the sentence there" | Audit-found defect that the new regression test reproduces with a literal exception | "An audit of X found this." The reproduced diagnostic R3 greps for is dropped | "unless a run reproduced it; then quote what it printed" |
| `:475` changelog "the condition alone" | Audit-found security fix whose traced impact decides upgrade urgency | The condition only, with no impact, even though the body states a traced consequence | "…or the derived consequence the body states (§2)" |
| `:342` translation, "even under a lead-in that states a reason" | Large diff where one hunk is where the reviewer should look first | Cuts the sentence pointing at it, against `:289-290` "where to look" | "except a pointer to the hunk the reviewer must judge first" |
| `:370` mechanism "stated as a fact about the merged code" | Alternative ruled out by an external constraint (platform behavior, protocol, third-party API) | Recasts it as a merged-code fact, or drops a valid rejection | "where the mechanism lies in this repository's code" |
| `:458` "give the answer and its evidence" | Issue thread with many questions the diff answers at a glance | An answer paragraph per question; the description grows | "a question a reviewer of this change would ask again" |

**Not findings:**
- `:98` derived consequence: ended for non-fixes by the slot 2 skip, "The change is not a fix".
- `:199` maintainer question: ended by "a question from the discussion that only a maintainer can settle" together with `:458`, "left open". A question already settled in review is not left open.
- `:288` "what changed that the diff does not show": ended by the What slot row `:196`, "The behavioral change, not the changed files".

## Item 3a: level, placement, and the environment
None. The rules sit in the sections they govern, and the checklist entries are in §8. The package layout matches its siblings. The registration entries (`apm.yml`, `marketplace.json`, package `apm.yml`) are the ones `apm pack --check-versions --check-clean` checks, and that gate passed offline. Every added sentence names this skill's slots or its measured drafts, so none could appear unchanged in a generic tutorial.

## Item 4: names by content, not by position
None. The new cross-references are by section and slot name ("§2, slot 2", "§2, the What slot", "the Scope slot"). There are no ordinals and nothing like "above" or "below".

## Item 5: the failure report
*Analogue: does each rule's detection reach the checklist and detect that rule.*

- **Public-identifier exception:** no checklist item, and `:826` detects the opposite (Item 1). Substantive.
- **Slot 2 detection (`:803-806`):** it asks "does the sentence end at what found it?". That detects the rule, but it also flags a reproduced diagnostic as a violation (the first row of the table above).
- **Remaining items:** "Translation", "Discussion" and the extended "Alternatives" each detect the rule they are attached to.

## Item 6: what the writer says it verified
*Analogue: an exemplar the rules pass and a bad case they fail, named in the change.*

The commit message reports measured red-to-green counts over fifteen blind drafts:
- symptom: 2/2 → 5/10 → 0/2
- obstacle: 2/4 → 0/4
- open question: 3/3 → 0/4
- translation: persists in about one draft in two

It also discloses three gaps:
- the drafts ran against 1.0.1;
- the current open-question rule and the revised What-slot example were not re-run;
- the final symptom wording rests on two drafts.

Gaps it does not state:
- **No noise-input check.** For instructions added after a bad output, §2a asks for an input where the added item is noise and a check that the output did not grow. None is stated: for example, a fix with an observed diagnostic, or an issue with no open questions.
- **The drafts are not in the repository.** Unlike `research/blackbox-test-design/cases`, the reported counts cannot be checked from the change.
- **The exemplars are consistent.** The rules pass the slot 2 *After* and fail its *Before*. The What-slot *After* passes Translation but conflicts with `:231` (Item 1).

## Item 7: siblings of the change
- I searched the other packages and docs for "no symptom", "observable symptom", "paraphrase of the diff", "open question" and "left open". No other package restates these rules. `problem-report-authoring` covers symptoms for issue reports, a different artifact, and does not conflict.
- The trigger instruction file needs no change.
- `.claude/rules` and `.agents/skills` only cross-reference the package by name.
- The skill's `description:` is unchanged and the scope did not widen.
- `qubership-repo-essentials/apm.yml:10` depends on the package by relative path, so it needs no edit.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Translation checklist deletes the public identifier the rule keeps | Substantive | `SKILL.md:826` vs `:345` | Add "except a public identifier the change adds, removes, or renames (§2)" to the item |
| Public-identifier exception has no checklist item, against "each fix has a checklist item" | Substantive | `SKILL.md:826` | Covered by the clause above |
| README bans the derived consequence the skill allows | Substantive | `README.md:28-30` vs `SKILL.md:98` | State "a consequence only when traced and marked derived" |
| What-slot *After* restates an outcome in prose; commit message says it does not | Substantive | `SKILL.md:353`, `:231`, `:320` | A clause separating the What boundary from slot 3's outcome line, or a different *After* |
| No evidence for the commit-body and changelog partitions; drafts were PR descriptions only | Substantive | `SKILL.md:81`, `:91`, `:475` | A drafting run on a commit body and a changelog entry, or the gap stated |
| "End the sentence there" drops a diagnostic a reproducing test observed | Substantive | `SKILL.md:91-92` | "unless a run reproduced it; then quote what it printed" |
| Changelog "condition alone" drops a traced consequence | Substantive | `SKILL.md:475` | "…or the derived consequence the body states" |
| Translation rule cuts the "where to look" pointer that `:289-290` asks for | Substantive | `SKILL.md:342` | "except a pointer to the hunk the reviewer must judge first" |
| Merged-code mechanism rule mishandles external constraints | Substantive | `SKILL.md:370-371` | "where the mechanism lies in this repository's code" |
| Open-question answers grow with every question the diff answers | Substantive | `SKILL.md:458-460` | "a question a reviewer of this change would ask again" |
| No noise-input check; drafts not in the repository | Substantive | commit message | One run on an input where the added items are noise, with output length compared |
| Version bumps not claimed in the message | Taste | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | "Version 1.3.0 to 1.4.0.", as in d79c43d |
| Stray line break "wanted. Leave" | Taste | `SKILL.md:462-463` | Reflow the paragraph |

This review did not run any drafting trial, did not re-derive the commit message's draft counts (the drafts are not in the repository), did not run `make verify-docs` or `install-smoke` (both need the network), and did not do a style-only pass over the prose.
