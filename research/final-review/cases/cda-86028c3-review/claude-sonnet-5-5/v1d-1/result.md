# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

**Inputs.** I had no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it is a skill edit, a package README, version bumps, and `research/` cases. I used the §2a analogues under every item. I did not run the drift script because there are no members to parse. I loaded `english-developer-style` (wording) and read the skill under review. `apm-authoring` and `docs-page-authoring` are not among the three skills I was told to load, so I did not load them.

No previous report exists, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files)

- **Rule name quoted wrongly.** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". `pgjdbc-4367-breaks/README.md:8` cites "SKILL.md §2" for it. The skill's sentence at `SKILL.md:234` reads "A break leads the description unless the next release from the target branch is a major". The phrase a reader would grep for matches nothing in the skill. The same stale quote appears in `pgjdbc-4392-no-break/README.md:6`.
- **Squash-copy rule contradicts itself.**
  - `SKILL.md:310` still says "Under §4 rule 5 the description is the commit body and takes the body's shape instead", and `SKILL.md:637` says to "shape it as §2's commit body".
  - The new text at `SKILL.md:259-260` says that under rule 5 "the lead stays" and the body "opens with its breaks and then its problem".
  - The paragraph at `SKILL.md:257-260` also opens with "The commit body keeps its order, problem first".
  - Rule 5 and line 310 now give the opposite answer from §2 on what a squash-copied description opens with.
  - The reason given at `SKILL.md:257-258` is also reversed for that case. The label `User-visible:` is "what R4 and R5 search for", but breaks in the lead carry no label. A squash body that follows line 260 therefore has no `User-visible:` line for its breaks.
- **"The trailer decides" is ambiguous.** `SKILL.md:247-248` says "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does". Read literally, the trailer makes the next release a major, so the breaks would not need to lead. That defeats the patch-release premise of the paragraph. It could instead mean "the trailer is written regardless", which is a different claim. It needs one reading.
- **Research README is accurate.** The `cases/` line and the 2026-10-20 sentence match what exists. `README.md:25-27` in the case 4367 README matches the table: Opus `result-2` fails check 3, and the other three pass.
- **No narration.** I found none of `now`, `no longer`, or `used to` in the added skill text. The case READMEs' history of three rule versions is a research record, which is fine.

## Item 2: claimed cases covered (analogue: sections and cases that cover each claim)

| Claim in the commit message | Covered by |
| --- | --- |
| A break is defined as new failure, changed return value or shape, removed option, changed default or error code, or a failure extended to inputs that worked before | The 4367 case covers the result shape (check 2) and the extended failure (check 3). No case covers a removed option, a changed default, or a changed error code. |
| Breaks lead unless the next release is a major | 4367 (patch release, version file says 42.7.14) |
| "Read from its version file, milestone, or name" | Only the version file is exercised. The prompt says there is no milestone, and it names no maintenance branch. |
| "They lead where nothing says which release it is" | None. Both prompts give `pgjdbc.version=42.7.14`. |
| "A major release keeps breaks first in slot 3" | None |
| "The commit body keeps the problem first, with breaks as the first `User-visible:` lines" | None. Both prompts are PR descriptions, and the merge model is `plain 37` squash 3. |
| "Where squash copies the description into the commit, the lead stays" | None |
| "A change with no break grows no section" | `pgjdbc-4392-no-break`, checks 1 and 2 |
| "all four runs lead with the breaks and mark the result shape, three of four move the extended failure out of Scope" | Matches the table: Opus `result-2` is the one that fails check 3. |
| Run counts (two each with the rule, one each on origin/main, two each for the control) | Matches the files. The word counts in the READMEs match `wc`. The baselines' `skill-tree` (1f020ce) equals the tree at HEAD~1, and the other runs' (4798053) equals the tree at HEAD. |
| "Opus and Haiku (effort high)" | The case README says "Haiku ran at effort `high`; Opus at the session's default", and the 4392 README says "Haiku at effort `high`". The commit message gives high for both models. |

- **Hunks no sentence claims.**
  - The 1.4.0 to 1.5.0 bump in `agent-packages/change-description-authoring/apm.yml`, `apm.yml`, and `marketplace.json` is not mentioned in the commit message.
  - The new bullet in the package `README.md` is not mentioned either.
  - Both are conventional and consistent with each other, so I rate them taste.
- **Commands.** `git archive <rev> …` in the case README is a run recipe, not a configuration command. No CI job runs it, and none is owed.

## Item 3: boundaries, partitions, and the negative control

- **Partitions.**
  - The only target tested is a patch release that the version file shows as 42.7.14. The untested partitions are:
    - a major release;
    - an unknown release, where the skill says breaks lead;
    - a milestone or a maintenance branch name;
    - the squash-copy path.
  - These are claimed in the skill and the commit message. The skill says "a break read first in a major release costs a paragraph". A trial with the target set to a major would show whether the agent skips the lead there.
- **Negative control.** The no-break control (4392) sits on the same patch target, which is the right partition for it. A second control would be a break aimed at a major, where the lead must not appear. It is missing.
- **Baseline for the control.** The control has no `origin/main` run. That is acceptable for a control that should stay green. Without the baseline, though, the evidence does not show that the pre-change skill also passes it.
- **State left by an earlier version.** The skill is installed over 1.4.0, and no instruction conflict was tested. The slot 1 sentence and the checklist edits make the text consistent, but the squash contradiction in Item 1 is exactly that kind of conflict.

### Table of added instructions

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release from the target branch is a major" | A repository with no versioning, such as a docs repo or a tool without releases | Opens with a Breaking changes lead for a behavior change nobody consumes as a release | The skill ends it only for "a change with no break". "Where nothing says which release it is, the breaks lead" fires here. Suggest "…, and a repository that makes no releases has no lead". |
| "A failure the change extends to inputs that worked before is a break … it goes with the breaks, not in the Scope slot" | A fix that extends a failure to an input of a kind the released version never accepted, such as a new feature input that was rejected before | Marks a new feature's rejection as a break | "inputs that worked before" ends it. Quoted, so no finding. |
| "after at most a short paragraph that says which code breaks" | A single break that the break line already names completely | A paragraph repeating the line | `SKILL.md:252-253`'s "at most" permits skipping it, so no finding. |
| "The commit body keeps its order … that body opens with its breaks and then its problem" | A squash-copied description, per Item 1 | Two incompatible orders for the same text | None. This is the finding above. |

## Item 3a: level, placement, and the environment

- The files are placed beside their siblings: `cases/` under `research/change-description-authoring/`, and the plugin edits are in the package directory.
- The repository's registration entries are the three version fields, all at 1.5.0. I did not run a gate, because none was named.
- `README.md` in the package states the rule without the major exception's consequence for slot 3. This is fine.

## Item 4: names by content, not by position

`result-2.md` and `result.md` in all four `<model>` directories distinguish runs by ordinal. The case READMEs refer to them as "both Opus runs" and "one of two Opus runs" with no content name. Taste: name them by rule version or by what differs, since run 2 differs from run 1 only by chance.

## Item 5: the failure report

The checks in the case READMEs state what a failure looks like ("fails: Why first", "fails: in Scope"). I found no weaker detection and no check not reached by the table. Check 4 of the 4367 case ("the fix is not a break") does not say how a reader tells a fix from a break written as a lead item. Taste.

## Item 6: what the writer says it verified

The 4367 case has red runs on the pre-change skill (both models' baselines fail checks 1 to 3) and green runs on the new skill. That is the evidence for the rule, and it is stated in the commit message. The unverified part is the rewording "after review" mentioned in the README. The final text passed 3 of 4 on check 3, so the extended-failure sentence is not reliable, and the commit message says so. A run of the Item 1 squash contradiction is absent because no such trial was run.

## Item 7: siblings of the change

- `git grep -n "Breaking changes\|Breaks first\|User-visible:"` finds sites in the skill that I read: the slot 3 row (`SKILL.md:198`), the changelog rule (`SKILL.md:543`, "marked in place and sorted first within their category"), the §4 rule 5 text (`SKILL.md:637`), the checklist (`SKILL.md:845-851`), and §7 (`SKILL.md:785`). Only `SKILL.md:637` and `SKILL.md:310` conflict with the new text.
- **Changelog.** The changelog rule at `SKILL.md:543` is unchanged and consistent: it sorts breaks first within a category. The description-level lead does not conflict with it.
- **Skill front matter.** The `description:` in the skill's front matter lists what the skill governs and does not mention the break rule. This is not the classic miss, because the scope widened within an existing topic.
- **Mentions of the version.** The old version 1.4.0 appears nowhere else (`grep` over `docs`, `README.md`, `apm.lock.yaml`).
- **Other skills.** `english-developer-style` and `test-authoring` do not cross-reference this rule.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | §4 rule 5 and `SKILL.md:310` say a squash-copied description takes the commit body's shape, but the new text says the lead stays. The `User-visible:` search rationale does not hold for lead breaks. | Substantive | `SKILL.md:257-260`, `SKILL.md:310`, `SKILL.md:637` | Pick one order for the squash-copied body. Update rule 5 and line 310 to match, or limit the new text to the PR description. |
| 2 | The case READMEs quote the rule under its old name, "…where the next release … promises compatibility", and cite "§2". | Substantive | `pgjdbc-4367-breaks/README.md:8`, `pgjdbc-4392-no-break/README.md:6` | Quote the rule as it reads at `SKILL.md:234`. |
| 3 | The "unless the next release is a major" exception and "nothing says which release it is" are claimed in the commit message and the skill, and no trial covers them. Both prompts are patch releases from the version file. | Substantive | Commit message, `SKILL.md:234-255`, both case prompts | Add one case with a major target, expecting breaks first in slot 3 and no lead. Add one with an unknown release. |
| 4 | "The trailer decides, and it is written whatever the description does" has two readings. The first reading makes the release a major and lifts the lead. | Substantive | `SKILL.md:247-248` | Say what the trailer decides: that the release is a major, so the lead lifts, or that the trailer is written regardless. |
| 5 | The commit says Opus and Haiku both ran at effort high. The 4367 README says Opus ran at the session default. | Substantive | `pgjdbc-4367-breaks/README.md` ("Running it"), commit message | Correct whichever is wrong. |
| 6 | The squash-copy path is claimed, and both prompts use a PR description with `plain 37`. | Substantive | Commit message, prompts | Covered by the case in finding 3 or a separate one. |
| 7 | The version bump and package README bullet have no claiming sentence. | Taste | `apm.yml`, `marketplace.json`, package `README.md` | Add half a sentence to the commit message. |
| 8 | `result-2.md` names runs by ordinal. | Taste | `cases/*/*/result-2.md` | Name runs by content. |
| 9 | The no-break control has no baseline run and no major-target control. | Taste | `pgjdbc-4392-no-break/README.md` | Add one baseline run of the control on `origin/main`. |

**Not checked:** I did not run the suite, any trial, or any lint. I did not read the full result files line by line, only their headings, word counts, and the Opus `result-2` lead. I made no pass over the prose for style alone.
