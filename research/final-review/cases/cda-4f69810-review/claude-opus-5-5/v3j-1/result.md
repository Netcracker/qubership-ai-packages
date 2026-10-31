# Final review: `d79c43d..4f69810` (one commit, change-description-authoring 1.4.0)

I found nine problems that need fixing and two matters of taste. Five of the problems are statements that disagree with each other: the README, the commit message, the worked example, and the Translation checklist item each conflict with a rule in `SKILL.md`. A sixth is a detection the checklist never reaches. The other three are where a rule goes too far (an observed symptom, a leak an audit found, a squash that copies the description) and missing evidence that the rewritten rules work.

There was no task statement. I took the claimed cases from the commit message alone. There was no previous report, so the table of earlier findings is omitted.

**How I ran the form.** The change is a skill with no code, so I used the analogues in §2a and say under each item which one. I loaded `english-developer-style` from the handed-over copy. In place of a doc-comment skill I used `apm-authoring` from the repository's source package (`agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`). I ran `comment-drift.py d79c43d` and it printed nothing, because Markdown has no members for it to parse.

Paths below are relative to `agent-packages/change-description-authoring/`, and `SKILL.md` means `.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
*Analogue used: statements one changed file makes about another file or about the change.*

- **README contradicts the skill.** `README.md:28-30` says a defect an audit found is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code, once it has been traced to what a caller sees and is marked as derived. A reader of the README would think every consequence is banned.
- **The worked example contradicts the commit message and §2.**
  - The commit message says the What-slot example "no longer puts an outcome in prose".
  - The *After* at `SKILL.md:352-353` says "a caller that runs before startup completes fails at once". That is the same outcome the next paragraph (`:357-359`) sends to "User-visible changes".
  - `SKILL.md:226` says "A fact stated in slot 3 is not restated in slot 2". The example breaks that rule, and drafts copy the example.
- **The slot-2 row reads like a reason to skip the slot.** At `SKILL.md:81` the clause "for a defect an audit or a code reading found, the body names what found it" sits in the *Skip when* column, so it reads as a skip condition. The prose at `:91-93` fills the slot. Under Taste below, because both readings arrive at the same text.
- **No narrating words** (`now`, `no longer`) in the added text. The measured counts in the skill (`:100`, `:464`) match the commit message.

## Item 2: claimed cases covered
*Analogue used: the section that covers each claim, and the checklist line that detects it.*

| Claimed in the commit message | Section | Detection (§8) |
| --- | --- | --- |
| A defect found by an audit is described by what found it, and the sentence ends there | `:91-94` | Symptom `:804-805` |
| A changelog entry for it names the condition alone | `:475` | **none**: the Changelog item (`:842`) is unchanged, and the Symptom item asks for "what found it", which is the opposite |
| A derived consequence is traced to the caller and marked as derived | `:98-101` | Symptom `:803-804` |
| "Say so" kept for a defect with no symptom by construction | `:94-96` | Symptom `:805-806` |
| A sentence recovered from one hunk is translation | `:342-345` | Translation `:826` |
| A public identifier is named once | `:345-347` | **contradicted** by Translation (see Item 5) |
| §7 points to the rule | `:763-764` | n/a |
| §2 asks for "what changed that the diff does not show" | `:286` | Decision |
| Slot 2 and the What slot each have a bad and a good example | `:92-93`, `:349-355` | n/a |
| Alternatives: the mechanism is a fact about the merged code | `:370-373` | Alternatives `:832-834` |
| Open questions are answered, kept in Scope, or dropped | `:458-465`, `:199` | Discussion `:835-838` |

- **Commands:** the change adds no command lines. None.
- **Hunks no sentence claims:**
  - The README hunk (`README.md:26-32`). No sentence of the commit message claims it.
  - The version bump 1.3.0 → 1.4.0 in `apm.yml`, `../../apm.yml`, and `.claude-plugin/marketplace.json`. It is the repository's convention, and `make check --check-versions` enforces it, but no sentence claims it.

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the situations the rules claim, plus the table of added instructions.*

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "name what found it and end the sentence there" | An audit found the defect, and a reproducer since threw `SQLException: …` | "An audit found this." The diagnostic R3 greps for is dropped | "and no run has reproduced it; a run's output is quoted" |
| `:94` "no symptom by construction … say so" | An audit found a leak on an error path that logs nothing (the rule's own exemplar) | Two rules fire on the same input: end at the audit (`:91`), or state the absence (`:94`) | "whatever found it, where the code emits nothing a caller sees", or a stated precedence |
| `:458` "keep it in the Scope slot as a question" | A squash with "title and description" (§4 rule 5) | A maintainer-only question written into the permanent commit body | "under §4 rule 5, in a review comment instead" |

Not findings: `:98` "only after it is traced", `:370` "when a reviewer would propose it", `:286` "that the diff does not show", `:475` "the condition alone", `:763` "In a description".

**Partitions:** the trials covered only pull request descriptions. Commit bodies and changelog entries, which both claim the new slot-2 rule, have no evidence.

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, and the repository's gate.*

- Each rule sits in the section it governs: slot 2, the What paragraph, Alternatives, Scope, the changelog table, and §7/§8. No sentence reads like generic tutorial text.
- `make check` exited 0.
- `make check-descriptions` printed "ok: all 27 skill descriptions are within 1020 characters".
- None.

## Item 4: names by content, not by position
- **Ambiguous reference.** At `SKILL.md:475`, "(§2, slot 2)" in the changelog table could mean the commit body's slot 2 (Impact and trigger) or the pull request's slot 2 (What). `:763` already does this right with "the What slot". Requested: "(§2, Impact and trigger)".

## Item 5: the failure report
*Analogue used: whether each detection is reached by §8 and checks its own rule.*

- **The Translation item deletes what the rule keeps.**
  - `:826` says to delete each sentence of the What slot and leave it deleted where the diff still says it.
  - A sentence naming an added system property is in the diff, so the item deletes it.
  - The rule (`:345-347`) says to name that identifier once.
  - The item tests a stronger property than the rule.
- **One rule has no detection.** The changelog "condition alone" rule is not reached by any checklist item (see Item 2).
- The Symptom, Alternatives, and Discussion items each detect their own rule.

## Item 6: what the writer says it verified
*Analogue used: an exemplar the rules pass and a bad case they fail.*

- **Bad cases are stated:** 2/2 drafts predicted a failure before the rule, 5/10 under the word ban, 0/2 under the final wording; retold obstacles 2/4 → 0/4; open questions 3/3 → 0/4.
- **Gaps:**
  - The commit message says the rewritten open-question rule and the rewritten What-slot example were not re-run. §2a asks that a rewritten rule be applied again.
  - The final slot-2 wording rests on n=2.
  - No noise-input check is reported: for example, a fix with an observed stack trace, checked so that drafts neither add "found by …" nor drop the diagnostic.
  - Hunk translation is stated to persist in about one draft in two.

## Item 7: siblings of the change
*Analogue used: the places that list or route to the package.*

- The descriptions in `apm.yml`, `../../apm.yml`, and `marketplace.json` are unchanged, and the scope was not widened.
- The umbrella `qubership-repo-essentials/apm.yml:10` uses a relative path with no version pin.
- `english-developer-style` §7 (changelog module) defers which parts an entry carries to this skill, so the "condition alone" rule wins there.
- No set gained a member, and no count changed.
- None.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The *After* example puts the outcome "fails at once" in What-slot prose, against `:226` and the commit message's claim | Substantive | `SKILL.md:352-353` | Drop the outcome clause from the *After*; keep the reason |
| The Translation checklist deletes the public identifier the rule says to name once | Substantive | `SKILL.md:826` | Add "except a public identifier the change adds, removes, or renames (§2)" |
| The changelog "condition alone" rule has no checklist item, despite "each fix … has a checklist item" | Substantive | `SKILL.md:475`, `:842` | Add it to the Changelog or Symptom item |
| The README bans every predicted failure; the skill allows a derived consequence marked as such | Substantive | `README.md:28-30` | Say "an untraced prediction", or mention the derived case |
| An audit-found defect with an observed reproduction loses its diagnostic | Substantive | `SKILL.md:91-94` | Add "and no run has reproduced it" |
| The audit rule and the by-construction rule conflict on a leak an audit found, which is the rule's own exemplar | Substantive | `SKILL.md:91-96` | State which rule wins, or pick an exemplar no audit would find |
| A maintainer-only question goes to Scope even under §4 rule 5, where the description is the commit body | Substantive | `SKILL.md:458-463`, `:199` | Add "under §4 rule 5, in a review comment" |
| "(§2, slot 2)" is ambiguous between the commit body and the pull request description | Substantive | `SKILL.md:475` | Write "(§2, Impact and trigger)" |
| The rewritten open-question rule and What example were not re-run; there is no noise-input check | Substantive | commit message | Re-run both, and add one observed-symptom input |
| The version bump and the README hunk are claimed by no sentence | Taste | `apm.yml:2`, `README.md:26` | One sentence in the commit message |
| The audit clause sits in the *Skip when* column | Taste | `SKILL.md:81` | Move it to the *Answers* column |

I did not run any drafting trial, did not re-run the measurements, and did not do a style-only pass over the prose. `make check` and `make check-descriptions` were the only checks I ran.
