# Final review: `d79c43d..HEAD` (4f69810, `change-description-authoring` 1.3.0 → 1.4.0)

I wasn't given a task statement, so the claimed cases come from the commit message alone. This change has no code: it touches a skill, its README, and three manifest or index entries. I filled every item through the §2a analogues and loaded `apm-authoring` and `english-developer-style`. I did not run the drift script, because there are no members for it to parse. There is no earlier report to compare against.

## Item 1: comments consistent with the code and with each other
*Analogue used: statements each file makes about another file or about itself, including worked examples.*

1. **The What-slot *After* example puts an outcome in prose, although the commit message says it no longer does.** At `SKILL.md:353`, the *After* opens with "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is "what the caller observes and the condition", which is the definition of a slot 3 line. `:231` says "A fact stated in slot 3 is not restated in slot 2", and the caption at `:358` sends the same outcome to "User-visible changes". An agent copying the example writes the outcome twice (`apm-authoring` rule 2).
2. **The rule's own *After* can be read as breaking the rule.** At `:354-355`, the sentence "…used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly" is a reason followed by a hunk (`sendWithRetry` → `sendDirect`). `:342-344` says such a sentence is translation "even under a lead-in that states a reason". Read clause by clause, the example fails the rule. Read sentence by sentence, it passes because the reason is not in the diff. The text supports both readings.
3. **An unchanged example contradicts the new symptom rule.** `:295` holds up "`Inside the driver the defect is latent…`" as the conclusion to prefer. That is a claim that no failure occurs, it is not marked as derived, and "latent" is exactly the kind of synonym the commit says drafts used to get around a ban on a word. It contradicts `:93-94` ("neither is the absence of one") and `:98-101`.
4. **The audit rule is ambiguous when the defect was also reproduced.** `:91-93` says "name what found it and end the sentence there", and the skip cell at `:81` lists the audit case beside the skip conditions. For an audit-found defect that a regression test then reproduces (`:397`), one reading drops the reproduced diagnostic from slot 2. The other keeps it under "Is every symptom quoted from an observation" at `:803-804`.
5. **The open-question rule conflicts with the decision test.** `:464` says to leave a question out "only when it does not bear on this change". A question that bears on the change but whose answer changes no review decision is kept by `:464` and deleted by `:298` ("Delete a paragraph with no concrete decision").
6. **The README overstates the ban on predicted failures.** `README.md:29` says "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code once it is traced and marked as derived.
7. **The README's claim about evidence is false for the new rules.** `README.md:53` says the skill "carries no citations; the evidence stays in the research directory". The new measured parentheticals (`:100`, `:464`) and the fifteen-draft trial are not recorded under `research/change-description-authoring/`. The earlier commit 985bf80 did record its sources there.

No new text narrates the change itself ("now", "no longer") outside the examples.

## Item 2: claimed cases covered
*Analogue used: each claim in the commit message against the section that handles it.*

| Claim | Where it is handled |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:81`, `:91-93`, checklist `:803-806` |
| Changelog entry names the condition alone | `:475` |
| A derived consequence is traced to what the caller sees and marked as derived | `:98-101`, `:804` |
| "Say so" is kept for a defect with no symptom by construction | `:94-96`, `:806` |
| What slot: a sentence recoverable from one hunk is translation; a public identifier is named once | `:342-347` |
| §7 points to the rule | `:762-763` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternatives: the mechanism is a fact about the merged code; an obstacle the change removes is a step | `:370-374`, `:832-834` |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, `:199`, `:835-838` |
| New checklist items "Discussion" and "Translation" | `:826`, `:835` |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-355` |
| "The What-slot example … no longer puts an outcome in prose" | **False**; see Item 1, finding 1 |

The change adds no commands for anyone to run.

**Unclaimed hunks:**
- The version bump to 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`.
- The README hunk at `README.md:26-32`.

No sentence of the commit message claims either. The repository's earlier commits do: d79c43d says "Version 1.2.0 to 1.3.0" and "the package README lists the new slots".

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres the change claims are the partitions, and the added-instructions table is the negative control.*

**Partitions with no evidence:**
- The trial ran only on pull request descriptions. Commit body slot 2 (`:91`) and changelog part 3 (`:475`) are claimed but have no draft behind them.
- The current open-question rule and the rewritten What example were not re-run. The commit says this itself.
- The final symptom wording rests on two drafts.

There is no earlier state to worry about: this is a skill text, and the version moved consistently in all three places.

Added instructions: 6. One gets a row:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:475` "the condition alone" | An audit-found defect whose regression test (`:397`) reproduces an exception text | A changelog entry without the diagnostic the on-call engineer would grep for | "where no run has shown a diagnostic" |

Not findings: `:98`, `:345`, `:370`.

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, and the repository's own gate.*

- Each rule sits in the section it governs (slot 2 prose, What-each-paragraph-must-earn, Scope, the changelog table, §7, §8), and the package layout matches its siblings.
- `make check` (the marketplace gate, which checks that versions are aligned and in sync) ran offline and exited 0.
- No added sentence is generic tutorial material.
- Finding: none.

## Item 4: names by content, not by position
- **`:475` "(§2, slot 2)" is ambiguous.** §2 has three numbered tables. "Slot 2" is "Impact and trigger" in the commit body, "What" in the pull request description, and "The observable change" in the changelog table where this reference sits. A reader can land on the wrong one. Elsewhere the same change refers by content ("§2, the What slot" at `:763`).
- `:357-358` "the first sentence says why" points into a two-sentence example. This is taste.

## Item 5: the failure report
*Analogue used: whether each rule's checklist detection detects that rule.*

1. **The Translation check at `:826` tests a different property from the rule.** The check says "where the diff still says it, leave it deleted". The rule at `:342` is about content recoverable from *one hunk*. This goes wrong two ways:
   - It deletes the public-identifier sentence that `:345-347` says to keep, because the diff does show that identifier.
   - It keeps a "reason + hunk" sentence that the rule cuts, because the diff does not show the reason.
2. **The Symptom check contradicts the changelog rule.** `:805` asks "does the sentence end at what found it?". That pushes the changelog entry to name the audit, while `:475` asks for "the condition alone". No checklist item reaches `:475`'s form.

The other new rules are reached by the Symptom, Alternatives, and Discussion items.

## Item 6: what the writer says it verified
The commit reports bad cases failing and the final wording passing:

| Rule | Reported result |
| --- | --- |
| Symptom, before the change | 2 of 2 drafts predicted a failure |
| Symptom, under a ban on the word | 5 of 10 stated that none was seen |
| Symptom, final wording | 0 of 2 |
| Retold obstacle | 2 of 4 → 0 of 4 |
| Open question | 3 of 3 → 0 of 4 |

Gaps:
- Hunk translation still persists in about one draft in two, so that rule is not shown to work.
- None of these runs used the current open-question text or the current What example.
- There is no noise input: no check that a description of a defect with an observed symptom, or one with no open questions, did not grow under the new items.

## Item 7: siblings of the change
- `apm.yml`, `marketplace.json`, and the package `apm.yml` are all at 1.4.0, and the gate agrees.
- The umbrella `qubership-repo-essentials` depends on the package by relative path, so no pin needs changing.
- The skill's `description:` is unchanged, and its scope did not widen.
- I found no sentence that still counts the slots or parts as before ("Five slots", "Six slots", "Five parts" are all still correct).
- The overlapping rule in `english-developer-style` §7 ("state the observable defect…") is compatible with the change.
- `README.md:53` is covered under Item 1, finding 7.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| What *After* puts the early-caller outcome in prose; contradicts `:231` and the commit message | Substantive | `SKILL.md:353` | Open the *After* with the decision, and leave the outcome to the User-visible line only |
| Rule's own *After* reads as "reason + hunk", the shape `:342-344` forbids | Substantive | `SKILL.md:354-355` | Say whether the rule applies by sentence or by clause, and make the example pass under that reading |
| Translation check deletes public identifiers and keeps reason-led translations | Substantive | `SKILL.md:826` | Detect "recoverable from one hunk", and exempt public identifiers |
| `latent` example asserts absence of a failure, unmarked | Substantive | `SKILL.md:295` | Replace it with a conclusion that complies with `:93-101` |
| Audit rule is ambiguous for a defect a test reproduced | Substantive | `SKILL.md:81`, `:91-93` | Add "where no observation or reproduction shows a symptom" |
| Changelog "condition alone" drops a reproduced diagnostic | Substantive | `SKILL.md:475` | See the Item 3 row |
| Symptom check contradicts `:475` for changelog entries | Substantive | `SKILL.md:805` | Make the check give the changelog's condition-alone form |
| "(§2, slot 2)" is ambiguous across three tables | Substantive | `SKILL.md:475` | "(§2, commit body slot 2)" |
| Open-question keep rule conflicts with the decision test | Substantive | `SKILL.md:464` vs `:298` | Leave out a question whose answer changes no review decision |
| README says derived consequences are banned | Substantive | `README.md:29` | Allow a traced consequence that is marked as derived |
| README says the evidence is in `research/`; the new trial is not there | Substantive | `README.md:53` | Record the 15-draft trial under `research/change-description-authoring/`, or reword the claim |
| Version bump and README hunks are unclaimed by the commit message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291`, `README.md:26` | Add "Version 1.3.0 to 1.4.0; the README lists the new rules" |
| Commit body and changelog partitions and the current What/open-question text have no trial, and there is no noise input | Substantive | commit message | A run on those partitions, plus one input where the new items are noise |
| "the first sentence" refers by position | Taste | `SKILL.md:357` | Name the sentence by its content |

I did not run the test suite (`make test`) or the `verify-docs` target, which needs network; nothing was fetched; and I did not do a style-only pass over the prose.
