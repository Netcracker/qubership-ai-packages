# Final review: `d79c43d..4f69810` (one commit, `feat(change-description-authoring): stop drafts from inventing symptoms and translating hunks`)

I wasn't given a task statement, so item 2 takes its claimed cases from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), the package README, and three version fields. So I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring` (the repository's copy) in place of a doc-comment skill. I did not run the drift script, because the change has no members for it to parse. No earlier report of this form exists for this change.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement one changed file makes about another file, about the repository, or inside its own worked examples.

- **README contradicts SKILL on derived consequences.** The README hunk says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code, as long as it is traced to the caller and marked as derived, and the §8 Symptom item asks for exactly that ("traced in the code and marked as derived"). Someone reading the README would expect such a sentence to be banned, but the skill permits it.
- **The What-slot *After* example puts an outcome in prose.** At `SKILL.md:353-355` it says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is what the caller observes plus the condition, which is the content of a "User-visible changes" line. `SKILL.md:225` says "A fact stated in slot 3 is not restated in slot 2", and the commit message says the example "no longer puts an outcome in prose". Moving the exception class out of the sentence (`SKILL.md:357-359`) did not remove the outcome from it.
- I verified these and they hold: §7 points to the rule (`SKILL.md:762-764`); §2 now reads "what changed that the diff does not show" (`:288`); the Symptom, Alternatives, Discussion, and Translation checklist items match their rules; the Scope table cell matches the new Scope paragraph; the changelog row 3 cross-reference "(§2, slot 2)" points to the right place. The new text narrates no change.

## Item 2: claimed cases covered
Analogue used: each claim of the commit message against the section that handles it, plus every hunk against a claim.

| Claim | Where it is handled |
| --- | --- |
| Slot 2: audit or code-reading finding named, sentence ends there, with a bad and a good example | `SKILL.md:91-95`, table row `:81` |
| Changelog entry for an audit-found defect names the condition alone | `SKILL.md:475` |
| Derived consequence only when traced and marked as derived | `SKILL.md:98-101` |
| "Say so" kept for a defect with no symptom by construction | `SKILL.md:94-96` |
| Translation rule with "even under a lead-in"; public identifier named once; bad and good example | `SKILL.md:342-359` |
| §7 points to the translation rule; §2 asks for "what changed that the diff does not show" | `SKILL.md:762-764`, `:288` |
| Rejected alternative stated as a fact about the merged code; a removed obstacle is a step the change took | `SKILL.md:369-374` |
| Open questions: answered, kept in Scope, or dropped | `SKILL.md:458-465`, Scope row `:199` |
| Checklist: Symptom and Alternatives extended; Discussion and Translation added | `SKILL.md:803-806`, `:826-838` |
| "This skill has no cases under research/" | True: `research/change-description-authoring/` has phase files and no `cases/` (only `research/test-authoring/` has one) |

- **Commands:** none. No changed file tells a reader to run a command.
- **Hunks no sentence claims:**
  - The version bump from 1.3.0 to 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The two previous commits to this package each said "Version 1.x.0 to 1.y.0".
  - The README hunk. The previous commit said "the package README lists the new slots".
- **Rules with no detection:** none. Every new rule has a checklist item.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the artifacts the change claims (commit body, PR description, changelog entry), and the table of added instructions.

- **Untested partitions.** The trial covered only "drafts of one pull request description". The new rules for commit-body slot 2 (`SKILL.md:81, 91-101`) and changelog row 3 (`:475`) have no draft evidence.
- **Not re-run.** The commit message itself says the final open-question rule and the revised What-slot example were not re-run.
- Not applicable here: pre-existing state, a consumer newly reached by a setting, a replaced mechanism, limits.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it, end the sentence there; changelog gives "the condition alone" (`:91-95`, `:475`) | An audit found the defect, and it was later reproduced, or a user reported it, with a logged diagnostic | Slot 2 reads "An audit of X found this.", and the changelog entry drops the log line the on-call reader greps for. The slot-2 rule asking for the diagnostic (`:90-91`) says the opposite for the same input | "where no failure has been observed; an observed diagnostic is quoted as usual" |
| Translation: a sentence recoverable from one hunk is deleted, per the checklist (`:342-347`, `:826-827`) | A mostly mechanical change (a rename across 80 files) with one semantic hunk, where one sentence tells the reviewer which hunk carries the decision | The agent deletes the sentence, because the diff "still says it". This conflicts with "where to look" (`:290-291`) | "unless the sentence tells the reviewer which of many hunks carries the decision" |
| A question only a maintainer can settle is kept in the Scope slot (`:458-465`) | A description that becomes the commit body (§4 rule 5, squash or merge commit) | An open question such as "is this break intended?" ends up in permanent history and is stale once the maintainer answers | "where the description is not copied into the commit body; otherwise in a review comment" |

**Not findings:**
- Public identifier "named once": ended by "a public identifier the change adds, removes, or renames".
- The rejected-alternative rule: ended by "when a reviewer would propose it".
- Dropping a question: ended by "only when it does not bear on this change".
- "Say so" for no symptom: ended by "by construction".

## Item 3a: level, placement, and the environment
Analogue used: where each rule lives, the layout against sibling packages, and the registration gate.

None. Each rule sits in the section it governs and the README follows the package layout. The version is 1.4.0 in all three registration files. `scripts/check-skill-descriptions.py` passes ("all 27 skill descriptions are within 1020 characters"). `make check` (`apm pack --check-versions`) needs `uvx` and the network, so I did not run it. No sentence reads as generic tutorial text.

## Item 4: names by content, not by position
Applied unchanged to the change's own headings, cross-references, and examples.

- `SKILL.md:357`: "the first sentence says why they are no longer needed" points at a sentence of the *After* example by its position. It could name it by content: "the sentence on opening the pool at startup".
- `SKILL.md:764`: "(§2, the What slot)" names a rule that sits under "What each paragraph must earn". No heading is called "What slot".

## Item 5: the failure report
Analogue used: whether each rule's detection is reached by the checklist, and whether the detection tests the rule.

None. Every new rule is reached by a §8 item. The Translation item ("delete each sentence … where the diff still says it, leave it deleted") detects the rule itself rather than a weaker property. Its over-reach is filed under item 3.

## Item 6: what the writer says it verified
Analogue used: an exemplar that passes, a bad case that fails, and re-application after a rewrite.

- **What is stated:** each arm reports bad-case counts (two of two, five of ten, three of three, two of four).
- **Re-application to the change's own examples:**
  - The slot-2 *After* passes the new rule.
  - The What *After* passes the translation test only because of its "used sendWithRetry only to reopen a closed pool" clause. It still restates an outcome (item 1).
- **Not stated:**
  - Any run on an input where a new item is noise, for example a fix with an observed diagnostic or a PR with no open question, with a check that the output did not grow.
  - A re-run of the final open-question rule and of the What example (the commit message says so itself).
- **Counts don't add up.** "Over fifteen blind Opus drafts" does not reconcile with the symptom arms as stated (2 + 10 + 2 = 14).

## Item 7: siblings of the change
Analogue used: the places that list or route to the package.

None.
- The marketplace and `apm.yml` descriptions are unchanged, and the scope did not widen, so the trigger surface is still correct.
- The `qubership-repo-essentials` umbrella pins the package by path.
- `references/merge-model.md` mentions "problem, symptom, approach" generically. The symptom slot now includes "what found it", so it isn't contradicted.
- `problem-report-authoring` has no rule about audit findings or predicted failures to align with (`grep` for audit/predicted/code reading found nothing).
- No member was added to a set.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| README bans a predicted failure outright; SKILL allows a traced, marked derived consequence | Substantive | `agent-packages/change-description-authoring/README.md:28-29`; `SKILL.md:98-101` | Make the README say "with a consequence only where it is traced to the caller and marked as derived" |
| What-slot *After* states a caller outcome in prose, against "not restated in slot 2" and against the commit's claim | Substantive | `SKILL.md:353-355` | Rewrite the first sentence as the reason (the pool opens at startup, so on-demand opening goes away) and leave the caller's failure to the User-visible line |
| Audit rule and changelog "condition alone" drop an observed diagnostic when an audit-found defect was later reproduced | Substantive | `SKILL.md:91-95`, `:475` | Add the clause "where no failure has been observed" |
| Translation checklist deletes a sentence that points the reviewer at the one semantic hunk in a large mechanical diff | Substantive | `SKILL.md:342-347`, `:826-827` | Add "unless it tells the reviewer which of many hunks carries the decision" |
| Maintainer-only question kept in Scope lands in permanent history under §4 rule 5 | Substantive | `SKILL.md:461-463`, Scope row `:199` | Add the clause that routes it to a review comment where the description becomes the commit body |
| Commit-body slot 2 and changelog row 3 rules have no draft evidence; the trial covered PR descriptions only | Substantive | commit message; `SKILL.md:81`, `:475` | Run drafts of a commit body and a changelog entry for an audit-found defect, or say in the message that these rules were not trialed |
| Final open-question rule and revised What example not re-run; no noise-input growth check | Substantive | commit message | A run of both on the bad case and on an input where they are noise, with word counts |
| Version bump and README hunk claimed by no sentence | Substantive | `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, `.claude-plugin/marketplace.json:291`, `README.md:26-32` | Add "Version 1.3.0 to 1.4.0; the package README lists the new rules." |
| "fifteen" drafts does not match the stated arms (14) | Taste | commit message | State how the fifteen split across arms |
| "the first sentence" names an example sentence by position | Taste | `SKILL.md:357` | Name it by content |
| "(§2, the What slot)" points at a heading that does not exist | Taste | `SKILL.md:764` | "(§2, *In the What slot, name the behavioral change*)" |

This review did not run `make check` or `make test`, because both need `uvx` and the network. It did not re-run any drafts, did not run the drift script (there is no code), and did not make a style-only pass over the prose.
