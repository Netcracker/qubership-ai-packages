# Final review: `d79c43d..4f69810` (one commit, change-description-authoring 1.4.0)

**Inputs.** There was no task statement, so the claimed cases come from the commit message alone. This change has no code: it touches a skill, its README, and the version entries in `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json`. Each item below therefore uses the §2a analogue, and I loaded `apm-authoring` and `english-developer-style`. The drift script ran and printed nothing, because it finds no members to parse in Markdown or YAML. There was no previous report. Line numbers below refer to `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` unless another file is named.

## Item 1: comments consistent with the code and with each other
*Analogue: what the changed files say about each other and about the repository.*

- **A. The Translation checklist item cancels the identifier exception.** `:826` says to delete each sentence of the What slot that the diff still says. A sentence naming a renamed flag or system property is exactly such a sentence, so following `:826` removes it. But `:345-347` says that identifier is "the exception: name it once". A writer who follows `:826` deletes what `:346` says to keep.
- **B. The worked example contradicts its own note and the PR slot rule.** The *After* at `:353-354` says in the What slot that "a caller that runs before startup completes fails at once". `:357-359` then says that outcome "goes on its own line under User-visible changes", and `:231` says "A fact stated in slot 3 is not restated in slot 2". So the example shows the outcome both in What-slot prose and on a User-visible line. The commit message's claim that the example "no longer puts an outcome in prose" is false for the text as committed. An agent copies the example (`apm-authoring` rule 2).
- **C. The slot 2 trigger can be read two ways.** `:91-92` says "Where reading the code or an audit found the defect, name what found it and end the sentence there". In nearly every fix, someone reads the code to find the cause, including when a user reported the failure. Read literally, the rule fires on a reported failure with a stack trace and stops the sentence before the quoted diagnostic. That clashes with `:89-91` and with the Symptom checklist line. The intended condition looks like "where no failure was observed".
- **D. The open-question rule has no place to go under §4 rule 5.** `:458-464` says to keep a maintainer-only question "in the Scope slot". But `:281` and `:608-612` say that a description which becomes the commit body takes the body's shape (which has no Scope slot) and keeps reviewer-only content out. The text reads two ways: either the open question goes into permanent history, or it goes to a comment. The rule does not say which.
- Everything else checked consistent:
  - the slot 2 table cell `:81` against the prose at `:91-96`;
  - changelog row 3 at `:475` against slot 2;
  - §7 at `:762-764` against the What rule;
  - the PR Scope row `:199` against `:458`;
  - the README bullets against the skill;
  - the commit's statement that the drafts ran against 1.0.1, before the outcome and length rules (confirmed from the `apm.yml` history: 1.0.1 → 1.1.0 → 1.2.0 → 1.3.0);
  - the commit's statement that there are no cases under research/ (`research/change-description-authoring/` holds only phase files);
  - no sentence in the skill narrates the change.

## Item 2: claimed cases covered
*Analogue: each case the commit claims, against the section that handles it.*

| Claimed case | Where it is handled |
| --- | --- |
| Slot 2: a defect found by audit or code reading names what found it, and the sentence ends there | `:91-94`, checklist `:803-806` (but see C) |
| Slot 2: a changelog entry for such a defect names the condition alone | `:475`; the Changelog checklist line `:842` does not reach it |
| Slot 2: a derived consequence is traced and marked as derived | `:98-101`, checklist `:804` |
| Slot 2: "say so" kept for a defect with no symptom by construction | `:94-96`, checklist `:806` |
| What slot: a hunk-level sentence is translation; a public identifier is named once | `:342-347`, checklist `:826` (but see A) |
| §7 points to the rule | `:762-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternative: stated as a fact about the merged code; a removed obstacle is a step | `:371-374`, checklist `:832-833` |
| Open questions: answered, kept in Scope, or dropped | `:458-464`, `:199`, checklist `:834-838` (but see D) |
| A bad and a good example for slot 2 and for the What slot | `:92-93`, `:349-355` (but see B) |

- **Commands the change tells someone to run:** none.
- **Hunks no sentence claims:** the version bumps 1.3.0 → 1.4.0 in the three version files, and the two README bullets. The previous commit (`d79c43d`) did state its bump ("Version 1.2.0 to 1.3.0."); this one does not.
- **Changelog checklist:** the "condition alone" case at `:475` has no item in the Changelog checklist line. The commit claims "each fix ... has a checklist item", and this fix lacks one.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the situations the change claims, with each new instruction's negative control below.*

The trial covered the PR description. The changelog rule at `:475` and the commit-body form of slot 2 have no draft evidence; the commit message mentions only PR-description drafts. The commit says the open-question rule and the What-slot example were not re-run, which is accurate.

Added instructions: 8, no rows.

Not findings: `:98`, `:105`, `:288`, `:371`, `:475`.

The inputs that would have produced rows were filed under item 1 instead, as conflicts or ambiguities: C (`:91`), A (`:342`/`:826`), and D (`:458`).

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, and the repository's own gate.*

- Each rule sits in the section it governs, and every checklist item sits in §8.
- `apm pack --check-versions --check-clean --dry-run` ran offline and reported no error.
- `scripts/check-skill-descriptions.py` printed "ok: all 27 skill descriptions are within 1020 characters".
- No added sentence is generic tutorial material.

## Item 4: names by content, not by position

- **E. An ambiguous section reference.** `:475` cites "(§2, slot 2)". §2 has two slot 2s: the commit body's *Impact and trigger* and the pull request's *What*. A reader can follow it to the wrong one. Elsewhere the change names slots by content, for example "(§2, the What slot)" at `:763`.

## Item 5: the failure report
*Analogue: does every rule's detection reach the §8 checklist, and does it detect that rule?*

- Every new rule except the changelog "condition alone" is reached by an item in §8.
- The Translation detection at `:826` detects a stronger property than the rule allows: it deletes identifier sentences too (finding A).

## Item 6: what the writer says it verified

- **What the commit states.** It names the bad case: blind drafts that predicted symptoms, translated hunks, retold obstacles, and repeated answered questions. It gives before and after counts, and it says what was not re-run. That much is stated evidence.
- **F. No noise-input check.** §2a asks that, for an instruction added after a bad output, the evidence include an input where the new item is noise, with a check that the output there did not grow. The commit reports none. An example is a description with no open question and no audit-found defect, run under the new Discussion and Symptom items.
- **Not reapplied.** The rewritten What-slot example was not re-run against its own rule, and finding B shows it now fails `:231`.

## Item 7: siblings of the change

- The README was updated. The marketplace and `apm.yml` descriptions are unchanged, and the skill's scope did not widen, so none was owed.
- `git grep` for the old "no observable symptom" wording across `agent-packages` and `docs` finds no other copy. That includes `english-*-developer-style`, `docs-page-authoring`, and `problem-report-authoring`.
- No set gained a member, so no count is stale.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| A. The Translation checklist deletes the identifier sentences that `:346` says to keep | Substantive | SKILL.md:826 | Add "except a sentence that names a public identifier the change adds, removes, or renames" |
| B. The *After* example restates in the What slot an outcome that the note and `:231` send to User-visible | Substantive | SKILL.md:353-354 | Remove "fails at once …" from the *After*, or show the outcome only on a User-visible line; fix the commit claim |
| C. "Where reading the code … found the defect" also fires on a reported failure | Substantive | SKILL.md:91-92 | Condition it: "Where no failure was observed and an audit or a code reading found the defect" |
| D. A maintainer-only question sent to the Scope slot has no place under §4 rule 5 | Substantive | SKILL.md:458-462 | Add "where the description stays on the platform; under §4 rule 5, in a comment" |
| E. "(§2, slot 2)" matches two slots | Substantive | SKILL.md:475 | Write "(§2, commit body, Impact and trigger)" |
| The changelog "condition alone" rule has no checklist item | Substantive | SKILL.md:842 | Add it to the Changelog checklist line |
| The version bumps and README bullets are claimed by no sentence | Substantive | apm.yml:168, README.md:26-32 | Add "Version 1.3.0 to 1.4.0." and a line for the README |
| F. No check on an input where the new items are noise | Substantive | commit message | Run one such draft, or state that none was run |
| The line break inside "Leave / a question out" | Taste | SKILL.md:463-464 | Reflow the paragraph; it renders correctly either way |

I did not run blind drafts against 1.4.0, did not run `make test` or `make verify-docs` (the latter needs the network), and did not do a style-only pass over the prose.
