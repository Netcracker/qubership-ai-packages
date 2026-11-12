I've finished the review. Nothing in the repository was changed: `git status` is clean, and the only file I wrote is a gate log in the scratchpad.

# Final review: `d79c43d..4f69810`

There was no separate task statement, so the claimed cases come from the commit message alone. The change contains no code. It edits a skill (`SKILL.md`), the package README, and the version entries in three manifests, so the form is filled through the §2a analogues. I loaded `english-developer-style` from the given directory. `apm-authoring`, the other skill §2a names, is not among the three I was allowed to load, so where it would be cited I cite final-review §2a instead.

I ran the drift script (`comment-drift.py d79c43d HEAD`). It printed nothing and exited 0, because it parses code members and this change has none. Its silence is not evidence either way.

## Item 1: comments consistent with the code and with each other
*Analogue used: what the changed files say about each other and about the skill.*

- **The What-slot *After* example breaks the skill's own rule.** At `SKILL.md:353-354` the example says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is a caller-visible outcome written as prose in the What slot. Lines 357-359 then send the same outcome (`IllegalStateException` from `Pool.acquire()`) to "User-visible changes", and `SKILL.md:231` says "A fact stated in slot 3 is not restated in slot 2." The commit message also claims the example "no longer puts an outcome in prose", which is false. An agent that copies the example will state the outcome twice.
- **The README is stricter than the skill.** `README.md` (new bullet) says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". But `SKILL.md:98-101` allows a derived consequence once it is traced to what a caller sees and marked as derived. Someone choosing the package from the README gets a rule the skill does not have.
- Everything else checks out:
  - The slot 2 table cell (`:81`) agrees with the slot 2 prose (`:91-96`).
  - The changelog part 3 cell (`:475`) agrees with the commit message.
  - §7 (`:762-764`) points to the What slot, as the commit message says.
  - §2's "what changed that the diff does not show" is at `:288`.
  - The Scope table row (`:199`) and the open-question paragraph (`:458-465`) agree.
  - The commit message says no cases exist under `research/change-description-authoring/`. That is true: it holds only the phase files from the earlier research.
  - The commit message says the drafts ran against version 1.0.1, before the length and outcome rules landed. The history of `apm.yml` confirms this (1.0.1 → 1.1.0 → 1.2.0 → 1.3.0).

## Item 2: claimed cases covered
*Analogue used: the section that handles each claim, and whether each hunk is claimed.*

| Claim in the commit message | Where the skill handles it |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:91-94`, table `:81` |
| Changelog: an audit-found defect gets the condition alone | `:475` |
| A derived consequence is written only when traced and marked as derived | `:98-101` |
| "Say so" is kept for a defect with no symptom by construction | `:94-96` |
| What slot: a sentence recovered from one hunk is translation, even under a reason; a public identifier is named once | `:342-347`, example `:349-359` |
| §7 points to the rule | `:762-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternative stated as a fact about the merged code; an obstacle the change removes is a step it took | `:370-373` |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, `:199` |
| Checklist: Symptom and Alternatives extended; new Translation and Discussion items | `:803-806`, `:832-838`, `:826-827` |

The change adds no commands to run.

**Hunks no sentence claims:**
- The version bump from 1.3.0 to 1.4.0 in `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json`. The previous commit claimed its bump with "Version 1.2.0 to 1.3.0."; this one says nothing.
- The new README bullets.

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres the change claims, and the table of added instructions below.*

**Partitions with no evidence.** The rules change three genres: the commit body (slot 2), the changelog entry (part 3), and the pull request description. The trial covers only pull request descriptions ("Blind drafts of one pull request description"). The commit body and the changelog entry have no evidence.

There is no pre-existing state to check: the package ships text only.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Slot 2: for an audit-found defect, name what found it and end the sentence there (`:91-94`) | An audit found the defect, and the new regression test then reproduced it on the base commit with a literal `IllegalStateException: pool is closed` | `An audit of the pool paths found this.` The reproduced diagnostic, which R3 greps for, is left out. The checklist question "is every symptom quoted from an observation" (`:804`) asks for the opposite on the same input | "…unless a run has since reproduced it; then quote what the run showed" |
| Changelog part 3: the condition alone for an audit-found defect (`:475`) | The same reproduced defect | A changelog entry with no diagnostic | The same clause, at `:475` |
| What slot: cut a sentence recovered from one hunk (`:342-345`) | A large diff whose deciding change is one hunk among many unrelated ones | The pointer to that hunk is cut, although `:289-290` asks that the reader "be able to tell … where to look" | "…unless the sentence tells the reviewer which hunk carries the decision" |
| Checklist Translation item (`:826-827`) | The change adds a public system property, `pool.eagerOpen` | The checklist deletes the sentence naming it because "the diff still says it". The rule at `:345-347` exempts public identifiers, and the commit message reports that drafting agents check against §8, not §2 | "…unless it names a public identifier the change adds, removes, or renames (§2)" |

**Not findings:**
- The derived-consequence rule ends itself with "only after it is traced to the point where a caller sees it".
- The rejected-alternative mechanism ends at "An obstacle the change itself removes", and the rule only narrows what may be written.
- The open-question rule ends at "A question the issue or the review left open". A question the maintainer already answered in the thread is not open.

## Item 3a: level, placement, and the environment
None. Each rule sits in the section it governs: slot 2, What, alternatives, Scope, the changelog table, and §8. `make check` passed offline ("Version alignment OK"), and `scripts/check-skill-descriptions.py` passed ("all 27 skill descriptions are within 1020 characters"). I found no sentence that could appear unchanged in a general tutorial on the topic.

## Item 4: names by content, not by position
None. The new cross-references name their target by content ("§2, the What slot"). "Slot 2" and "part 3" are the skill's existing numbered slots, defined in its own tables.

## Item 5: the failure report
*Analogue used: every rule with a detection is reached by the checklist, and each detection checks the rule rather than a weaker or stronger property.*

- Every new rule has a checklist item: Symptom, Translation, Alternatives, and Discussion.
- **One detection checks a different property than its rule.** The Translation item checks "where the diff still says it", with no public-identifier exception and no "from one hunk" condition. The finding is already filed under item 3, Translation row.

## Item 6: what the writer says it verified
- The commit message reports counts from fifteen blind drafts on one pull request: before the change, with a ban on the word, and with the final wording. It also states that hunk translation persists in about one draft in two.
- Those runs used version 1.0.1 plus the candidate rules. The commit message says the current open-question rule and the What-slot example were not re-run, but in fact no rule was run against the text as shipped on top of 1.3.0.
- No exemplar or bad case is committed. The bad cases appear only as quoted fragments.
- No input was run where the new items are noise, such as a reported bug with an observed diagnostic, to check that the output did not grow.

## Item 7: siblings of the change
None, apart from the README finding under item 1.
- The package README is updated.
- The marketplace and manifest descriptions are unchanged, which is right: the skill's frontmatter description and scope did not widen.
- The instructions file needs no change.
- The new rules agree with `english-developer-style` §7, "A bug report is provenance too".
- `problem-report-authoring` requires an observation (`SKILL.md:63`). That is a different artifact, and it does not share this defect.
- No sentence counts the checklist items or the slots in a way that changed: "Six slots" still holds. The Scope slot gained a fourth kind of content, but `:210-212` still describes slot 5 as answering "the two questions" (taste).

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The What-slot *After* example states a caller outcome in prose, against `:231` and the commit message's claim | Substantive | `SKILL.md:353-354` | Make the first sentence give only the reason, e.g. "The pool opens at startup, so no call path has to open it on demand." Leave the outcome to the User-visible line |
| The audit-found rule drops a symptom a later run reproduced, and conflicts with the Symptom checklist question | Substantive | `SKILL.md:91-94`, `:475` | Add the clause: "unless a run has since reproduced it; then quote what the run showed" |
| The Translation checklist item has no public-identifier exception, and agents check against §8 | Substantive | `SKILL.md:826-827` | Add "unless it names a public identifier the change adds, removes, or renames" |
| The translation rule cuts the pointer to the deciding hunk in a large diff, against "where to look" at `:289-290` | Substantive | `SKILL.md:342-345` | Add a clause that keeps a sentence telling the reviewer which hunk carries the decision |
| The README bans derived consequences that the skill allows | Substantive | `README.md`, new bullet "A defect that an audit found…" | Say "with no failure predicted unless it is traced to what a caller sees and marked as derived" |
| The version bump and the README hunks are unclaimed by the commit message | Substantive | the three manifests, `README.md` | Add "Version 1.3.0 to 1.4.0." and a sentence on the README |
| The commit body and changelog partitions have no trial | Substantive | commit message | Run one commit-body draft and one changelog draft on an audit-found defect, or say in the message that they were not run |
| No run used the shipped text, and no noise input was checked for growth | Substantive | commit message | Re-run on 1.4.0 against the PR used, plus one input with an observed diagnostic, and report the word count against 1.3.0 |
| Slot 5's "the two questions" leaves out the maintainer-question content added to it | Taste | `SKILL.md:210-212` | Mention the maintainer question, or leave it as is |

I did not re-run any drafts, did not run `make test` or `make verify-docs` (the latter needs the network), did not fetch any cited source, and did not do a separate wording-only pass over the prose.
