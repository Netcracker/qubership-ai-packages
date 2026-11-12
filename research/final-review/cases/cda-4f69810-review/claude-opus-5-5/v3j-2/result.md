# Final review: `d79c43d..4f69810`, the change-description-authoring skill 1.3.0 → 1.4.0

**Inputs.** I was given no task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), the package README, and the three version fields. The form is filled through the §2a analogues. The drift script ran (`comment-drift.py d79c43d HEAD`, exit 0). It printed nothing, because there are no code members to parse. The skills loaded were `english-developer-style` from the directory I was given and `apm-authoring` from this repository, in place of a doc-comment skill. The repository's `apm-authoring` has no rule called *Fix a bad output where the rule stops*, so that citation in final-review §2a could not be checked against it. There is no previous report, so this is round one.

Below, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

Analogue used: statements one file makes about another file or about itself, and worked examples.

- **The What-slot *After* puts an outcome in prose.** `SKILL.md:353` says: "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is what a caller sees and under what condition, which is the content of the User-visible changes slot.
  - `SKILL.md:231` says "A fact stated in slot 3 is not restated in slot 2". The text right after the example (`:358-360`) also sends the `IllegalStateException` to User-visible changes.
  - The commit message says the example "no longer puts an outcome in prose", which is false.
  - A reader copying the exemplar learns to state the outcome twice.
- **The *After*'s second sentence has the shape the rule rejects.** `SKILL.md:354-355` ends with "with the pool open from startup it sends directly". That is a hunk (`sendWithRetry` → `sendDirect`) behind a lead-in that states a reason. It is the same shape as the *Before*'s "With the pool opened at startup, the lazy ensureOpen() calls are removed".
  - `:342-344` says this is translation "even under a lead-in that states a reason".
  - The reader cannot tell whether the rule applies per clause or per sentence. The checklist (`:826`) tests per sentence, which this sentence passes.
- **The rule cuts the skill's own PR exemplar.** `SKILL.md:254` reads "The orphan sync is requeued with backoff on failure instead of being dropped." That is one hunk.
  - The new rule (`:342`), `§7` (`:763`), and the Translation checklist item (`:826`) all delete it.
  - The What row of the table (`:196`) asks for "The behavioral change".
  - For a fix whose behavioral change is a single hunk, the two rules contradict each other. Nothing says the one sentence that states the behavioral change stays.
- **The README misstates the derived-consequence rule.** `README.md:28-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a derived consequence once it is traced to the caller and marked as derived. A reader deciding from the README whether to load the skill gets a stricter rule than the skill states.
- **The audit rule ends a sentence, not the symptom.** `SKILL.md:91-92` ("end the sentence there") and the checklist (`:805`, "does the sentence end at what found it?") both stop at a sentence boundary.
  - The bad example (`:92-93`) becomes compliant if its semicolon is replaced by a period: "An audit found this. It has not been seen to fail."
  - The commit message itself reports that drafts evaded a rule naming a word by using a synonym. Evading a sentence boundary is the same move.
  - `:94`, "A predicted failure is not known, and neither is the absence of one", is a statement, not an instruction. It also sits uneasily with `:98`, which allows a traced prediction.
- Cross-references checked and accurate:
  - "§7 points to this rule" (`:763`).
  - §2 asks for "what changed that the diff does not show" (`:288`).
  - `(§5)` for searchable identifiers: §5 is "Trailers and the identifiers a reader greps".
  - `(§2, slot 2)` in changelog row 3.
  - "no cases under research/": `research/change-description-authoring/` holds only `phase*` files.
  - "version 1.0.1 … before the outcome slot and the length rules": the history goes 1.0.1 → 1.1.0 → 1.2.0 → 1.3.0. The rebase-and-merge rules in 1.1.0 also came later. The sentence leaves that out but does not contradict it.
- Taste: the PR Why row (`:195`) still asks for "the symptom" with no audit clause. Yet the drafts that showed the defect were PR descriptions. The rule reaches the PR only through "Slots 1 and 2 are the commit body's slots 1 to 3" (`:206`) and the checklist.

## Item 2: claimed cases covered

Claimed cases come from the commit message; there was no task statement. The coverage column gives the section that handles each case and, after the semicolon, the checklist item that detects it.

| Claimed case | Covered by |
| --- | --- |
| Slot 2: an audit or code-read defect is described by what found it, and the sentence ends there | `:81` (table), `:91-95`; Symptom `:803-806` |
| Its changelog entry names the condition alone | `:475`; Changelog `:841` (only "symptom" in general) |
| A derived consequence only when traced and marked as derived | `:98-101`; Symptom `:804-805` |
| "Say so" kept for a defect with no symptom by construction | `:94-96`; Symptom `:806` |
| Slot 2 has a bad and a good example | `:92-93` |
| What slot: a one-hunk sentence is translation, even under a reason lead-in | `:342-345`; Translation `:826` |
| A public identifier is named once | `:345-347`; **no checklist item** (see Item 5) |
| §7 points to the rule; §2 asks for "what changed that the diff does not show" | `:763`, `:288` |
| What slot has a bad and a good example | `:349-355`, with the defects in Item 1 |
| Rejected alternative is a fact about the merged code; an obstacle the change removes is a step | `:370-373`; Alternatives `:832-834` |
| Open question: answered where evidence settles it; a maintainer-only one kept in Scope with the decision it needs; dropped only when it does not bear on the change | `:458-464`, Scope row `:199`; Discussion `:835-838` |

- **Commands:** none in the changed text.
- **Hunks no sentence claims:** the three version bumps (`apm.yml:168`, `.claude-plugin/marketplace.json:291`, the package `apm.yml:2`) and the README hunk. The previous commit in this series claims both kinds ("the package README lists the new slots", "Version 1.2.0 to 1.3.0"); this one claims neither.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the genres and situations the change claims, and the instructions table.

- **Two of three claimed genres have no trial.** The change edits three genres: commit body slot 2 (`:81`, `:91`), the PR description (What, Scope, alternatives), and changelog part 3 (`:475`). The fifteen drafts were all PR descriptions of one pull request. The commit body and changelog partitions have no evidence.
- **The current wording was not tried.** By the commit's own account, the drafts ran against 1.0.1, not 1.3.0. The current open-question rule and the What example were not re-run. So the interaction with the outcome slot added in 1.3.0, which is where the first Item 1 finding lives, was never tried.
- **No negative control.** There is no input where the new items are noise (a fix with an observed, quoted symptom; a PR whose discussion has no open question) with a check that the output did not grow.

Added or widened instructions: eight are counted (slot-2 audit rule, derived-consequence rule, translation rule, identifier exception, merged-code alternative rule, obstacle rule, open-question rule, changelog condition-only rule). The checklist lines, the table restatements, `:288`, and `:763` restate them and get no rows of their own. The translation rule, the identifier exception, and the derived-consequence rule get no rows because Item 1 and Item 5 cover them.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "name what found it and end the sentence there" (and `:475`) | Audit-found defect that the new regression test reproduces, or that a user later reported | "An audit found this", dropping the `TRAP:` line R3 greps | "unless a test, a run, or a report observed it; then quote that" |
| `:371` "An obstacle the change itself removes is a step" | The obstacle comes with the alternative (lazy open needs a lock on every call) | Drops the one valid reason against the alternative | "where the alternative would have to remove it too, it stays a reason" |
| `:458` "keep it in the Scope slot as a question" | Squash-merge repo where §4 rule 5 makes the description the commit body | A permanent commit body with an open question, stale once decided | "outside a description §4 rule 5 makes a commit body; ask it in a review comment there" |

Not findings: `:458` "the issue or the review left open"; `:345` "a public identifier the change adds".

## Item 3a: level, placement, and the environment

`none`. Each rule sits in the section of the slot it governs: the open-question rule is under `#### Scope`, the translation rule is under "What each paragraph must earn", and each has a checklist line. Gates run:

- `make check` exited 0 (versions aligned, marketplace in sync).
- `scripts/check-skill-descriptions.py` printed "ok: all 27 skill descriptions are within 1020 characters".

No added sentence could appear unchanged in a generic tutorial; each one comes from a measured failure.

## Item 4: names by content, not by position

`none` substantive. Taste: `:358` refers to "the first sentence" of the adjacent *After*. It could say "the sentence on opening at startup" instead. New headings and cross-references are all by section number plus name, matching the rest of the file.

## Item 5: the failure report

Analogue used: whether the checklist reaches every rule, and whether each check detects the rule rather than a weaker property.

- **The Translation item (`:826`) contradicts the identifier exception.** It says "where the diff still says it, leave it deleted". It does not mention the exception (`:345`): a sentence naming an added system property or flag is said by the diff, so the item deletes it. The commit message reports that drafting agents check against §8, not §2, so they will drop the identifier the rule says to keep.
- **The Translation item detects less than the rule says.** It works per sentence, while the rule (`:343-344`) is about a clause behind a lead-in. This is the second Item 1 finding seen from the detection side.
- **The Symptom item (`:805`) detects less than the rule says.** It detects a sentence boundary, not the absence of a claim about the symptom (the fifth Item 1 finding).
- The Alternatives and Discussion items reach their rules as stated.

## Item 6: what the writer says it verified

- **Stated:** bad cases and counts for three of the four defects: the symptom (2/2, then 5/10, then 0/2), the obstacle (2/4 → 0/4), and the open question (3/3 → 0/4). Translation is reported as persisting in about one draft in two.
- **Not stated:**
  - A known-good exemplar that passes the rewritten rules. The skill's own `:254` exemplar now fails them (Item 1).
  - A re-run of the current open-question wording and the What example; the commit says this itself.
  - A noise input with a check that the output did not grow.
- The final symptom wording rests on two drafts.

## Item 7: siblings of the change

`none`.

- The version appears in `apm.yml`, `marketplace.json`, and the package `apm.yml`; all three moved together, and `make check` confirms it.
- The description and the instruction trigger are unchanged and still cover the scope.
- `git grep` for "audit", "no symptom", "predicted", and "derived" in `problem-report-authoring` and `docs-page-authoring` finds no parallel rule.
- The research mention (`research/change-description-authoring/phase3_result.md:457`) is history.
- No slot or part count changed: "Six slots", "Five slots", and "Five parts" still hold. The checklist gained Translation and Discussion, and no sentence counts its items.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| What *After* states the caller outcome in prose, against `:231` and the commit message's claim | Substantive | `SKILL.md:353` | Restate the first sentence as the reason (the pool opens at startup, so nothing opens it on demand). Leave "fails at once" to the User-visible line. |
| *After*'s "with the pool open from startup it sends directly" is a hunk behind a reason lead-in, the shape `:343` rejects | Substantive | `SKILL.md:354-355` | End the sentence at the reason, or say the rule applies per clause and make `:826` match. |
| The translation rule and its checklist item cut the PR exemplar's behavioral-change sentence, which the What row requires | Substantive | `SKILL.md:254`, `:342`, `:826` | Add a clause: the one sentence that states the behavioral change stays even when a single hunk carries it. |
| The Translation checklist item deletes the public-identifier sentence the rule keeps | Substantive | `SKILL.md:826` vs `:345` | Add "except a sentence naming a public identifier the change adds, removes, or renames" to the item. |
| The audit rule ends a sentence, not the claim, so "An audit found this. It has not been seen to fail." passes the rule and the checklist | Substantive | `SKILL.md:91-94`, `:805` | State what the slot leaves out: no statement of whether a failure was seen, and only a traced, marked derivation (`:98`). Check that in the checklist. |
| The audit rule drops a symptom that a test or a report did observe | Substantive | `SKILL.md:91`, `:475` | Add "unless a test, a run, or a report observed it; then quote that". |
| An obstacle inherent to the alternative is treated as not a reason against it | Substantive | `SKILL.md:371-372` | Add "where the alternative would have to remove it too, it stays a reason". |
| A maintainer question kept in Scope lands in a squash commit body | Substantive | `SKILL.md:458-462` | Exclude a description that §4 rule 5 makes a commit body, and route the question to a review comment. |
| README says no predicted failure; the skill allows a traced, derived one | Substantive | `README.md:28-30` | Align the README with `SKILL.md:98`. |
| Commit body and changelog partitions untried; the current open-question and What wording not re-run; no noise control | Substantive | commit message; `SKILL.md:81`, `:475` | Run drafts of a commit body and a changelog entry for an audit-found fix, and one no-op input (an observed symptom, no open question) to check the output does not grow. |
| Version bumps and the README hunk are not claimed by the message | Substantive | `apm.yml:168`, `marketplace.json:291`, package `apm.yml:2`, `README.md:26-32` | Add the two sentences the previous commit carried (the README update and "Version 1.3.0 to 1.4.0"). |
| PR Why row has no audit clause, although the drafts were PR descriptions | Taste | `SKILL.md:195` | Add "for an audit-found defect, what found it" to the row. |
| "the first sentence" refers to the example by position | Taste | `SKILL.md:358` | Name it by content. |

I did not run any draft trials, and I did not do a style pass over the prose for wording alone. I ran no test suite, because the change has none; the gates run were `make check`, the description-length check, and the drift script, which has nothing to parse in Markdown.
