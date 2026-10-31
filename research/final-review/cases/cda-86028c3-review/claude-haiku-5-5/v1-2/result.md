## Final review: `4f6981065..HEAD` (one commit, `86028c3`)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message, the two case READMEs in `research/change-description-authoring/cases/`, and the rule text in `SKILL.md` §2. This is the first review of this change, so there is no previous report. The change touches only Markdown and manifests, so the code-oriented items are answered through the §2a analogues.

**Skills.** I read `final-review` in full and loaded `english-developer-style`. `test-authoring` does not apply because the change has no tests. `apm-authoring`, the authoring skill §2a names for a skill package, is not in the skills directory, so I did not load it and applied §2a directly.

**Drift script.** Run; no output, exit 0. It parses only Java, Kotlin, Groovy and Scala, and the change has none of those.

**Gate.** `make check` (offline dry run) exits 0. The version bump is aligned across the three manifests.

**Analogue used under each item:** the §2a wording for a skill, with the instruction table in §2a below.

### Item 1: comments consistent with the code and with each other (§2a: statements about other files)
Findings 1, 2 and 11. The rest is consistent: the §2, §4 rule 5, §5 and §7 cross-references resolve, and the package README bullet matches §2.

### Item 2: claimed cases covered (§2a: claimed cases and the artifact's own claims)
- Covered by a run on the committed skill tree: lead when the release is not a major, the result-shape break, the `grant insert` extended failure (3 of 4 runs), the fix-is-not-a-break case, and the no-lead control. Each has a red baseline on origin/main except the control.
- Claimed but not run: next release is a major, nothing says which release it is, milestone and maintenance-branch-name sources, the `BREAKING CHANGE:` trailer, the commit body's breaks-first order, and the §4 rule 5 lead (finding 5).
- Claims in the commit message that disagree with the case records: findings 3 and 4.
- Hunks no sentence claims: finding 7.

### Item 3: boundaries, partitions, negative control (§2a)
The major, unknown-release and trailer partitions have no run (finding 5). The control has no base-commit run, and its growth is unmeasured (finding 6). No pre-existing state is read or replaced, so that check is none.

### Item 3a: level, placement, environment (§2a)
The rule lives in §2 with a consistent summary in the package README. The registration entries pass `make check`. The research runs are model runs that CI does not execute: none.

### Item 4: names by content (§2a)
Finding 10. The case names `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break` are by content. No other ordinal references are new.

### Item 5: failure report (§2a: a rule's detection)
The Breaks checklist item (`SKILL.md:849`) checks only that the lead exists. It does not check the extended-failure clause, the commit-body breaks-first rule, or the trailer rule (finding 8). The §2a table row is finding 9.

### Item 6: what the writer says it verified (§2a)
Red evidence exists for the lead, result shape and `grant insert` (the baseline results on origin/main fail those checks). The control has no red or green evidence on the base, and the new release-branch branches have none at all (findings 5 and 6).

### Item 7: siblings (§2a)
No other copy of `change-description-authoring` exists in `.claude`, `.cursor` or `.agents`. The instructions file and `merge-model.md` do not mention the break rule, so they need no change. The changelog rule (`SKILL.md:543`, breaks marked in place) is a different surface and does not conflict.

### §2a instruction table

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`) | A behavior change in a private helper that no caller outside the repository reaches, on a patch release | A `Breaking changes` lead naming the helper | Add "…and stop where no caller of the public API reaches the changed behavior" |

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Both case READMEs quote a rule sentence ("…where the next release from the target branch promises compatibility") that `SKILL.md` no longer contains. The committed sentence reads "unless the next release … is a major". | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | Quote the committed sentence. |
| 2 | "Six slots, in order" contradicts slot 3's "ahead of slot 1 unless the next release is a major". | Substantive | `SKILL.md:192`, `SKILL.md:198` | Amend "in order" to name the break exception. |
| 3 | The commit message says "on Opus and Haiku (effort high)". The README says Opus ran at the session default and only Haiku at effort high. | Substantive | Commit `86028c3` body; `cases/pgjdbc-4367-breaks/README.md:33` | State the effort per model. |
| 4 | The commit message says the PR "targets a 42.7.x patch release". The case README says "because `master` ships 42.7.x patch releases", and the input prompt says "Target branch: `master`". | Substantive | Commit body; `cases/pgjdbc-4367-breaks/README.md:5`; `cases/pgjdbc-4367-breaks/prompt.md:10` | Make the commit message match the case input. |
| 5 | Unrun branches of the new rule: next release is a major (breaks stay first in slot 3); nothing says which release (breaks lead); milestone or maintenance-branch-name sources; the `BREAKING CHANGE:` trailer; the commit body's breaks-first order; the §4 rule 5 lead. No case covers a major release, an unknown release, or a commit body. | Substantive | `SKILL.md:243–260` | Add a run for each, or state in the commit message and rule that these are untested. |
| 6 | "The control grows no section in any run" is contradicted: three of four control results have `## User-visible changes`, which the draft lacks. The control has no base-commit run, so growth cannot be attributed to this rule, and word counts (241–256 against 209) have no base to compare. | Substantive | Commit body; `cases/pgjdbc-4392-no-break/opus/result.md:16`, `opus/result-2.md:16`, `haiku/result-2.md:16` | Run the control on origin/main and compare headings and word counts, or narrow the claim to "no Breaking section and no lead". |
| 7 | Version bumps to 1.5.0 in three manifests have no sentence in the commit message. The repo bumps in every feature commit, and `make check` passes. | Substantive | `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168` | Add one body sentence that claims the bump. |
| 8 | The checklist's Breaks item checks only the lead. It omits the extended-failure clause (the miss the commit message names), the commit body's breaks-first lines, and the trailer rule. | Substantive | `SKILL.md:849–852`; `SKILL.md:257–260`; `SKILL.md:247` | Add a checklist line for each. |
| 9 | Break definition has no caller bound for internal code, so a private-helper change draws a `Breaking changes` lead (§2a table). | Substantive | `SKILL.md:236–242` | Add the clause in the §2a table. |
| 10 | "Checks 1 to 3 are the rule under test; 4 to 6 are the guard" refers by ordinal; the checks have content names. | Taste | `cases/pgjdbc-4367-breaks/README.md:25` | Name the checks by content. |
| 11 | "the trailer decides" names the trailer as the actor, but a release tool does the bump. | Taste | `SKILL.md:247` | Name the release tool as the actor (english-developer-style §7). |
| 12 | Price and token figures ("$4 per million", "110000 to 115000 tokens") are not verifiable offline. | Taste | `cases/pgjdbc-4367-breaks/README.md:59–60` | Cite a source or drop. |

**Not checked.** I did not rerun any model case. I could not check the external claims (the pgjdbc#4367 maintainer rewrite and its 2026-08-23 date) because there is no network. I did not do a style pass beyond the form's items: some new sentences run past 30 words, which is a style question, not this review. I briefly wrote and deleted a file under `/tmp` while checking the gate; `git status` is clean and nothing in the repository was changed.
