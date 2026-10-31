I've finished the evidence pass and am writing the report now.

# Final review: `4f69810..HEAD` (commit 86028c3)

**Inputs.** There is no task statement. The claimed cases come from the commit message, so item 2 is answered from it alone. The change has no code: it edits a skill, two package manifests, a package README, a research README, and two regression cases. Section 2a of the form applies, and the drift script was not run because there are no code members to parse. I loaded `english-developer-style` as the developer-style skill. There is no `docs-page-authoring` or `apm-authoring` skill in the supplied directory, so I judged the artifact rules from the form's own analogues. No previous report exists.

## Item 1: comments consistent with the code and with each other

Analogue used: statements one file makes about another, counts, section references, and rule names.

Checked:
- `§4 rule 5`, `§5`, `§7` and `§2` all exist. Rule 5 (line 637) is the squash/merge-commit rule.
- The new checklist item agrees with the new paragraphs.
- The three manifests all say 1.5.0.
- The `skill-tree` ids match `git rev-parse` for the skill directory at HEAD (`4798053…`) and at the base (`1f020ce…`).
- The commit message's run counts match the case README table.
- The word counts match `wc -w`, and the "Generated with Claude Code" claim matches the five files that contain it.

Findings:
- **Stale rule name.** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed heading is "unless the next release from the target branch is a major". The criterion differs: "promises compatibility" would also cover a minor release. A reader who searches the skill for the quoted text finds nothing. Locations: `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md` (intro paragraph) and `cases/pgjdbc-4392-no-break/README.md` (intro paragraph).
- **Ambiguous sentence.** SKILL.md ~line 247: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." It does not say what the trailer decides. One reading is that the release is now a major, so the lead is not owed. But the trailer is written because of the break, so on a tool-managed repository that reading would switch the rule off for every break. The other reading is that the trailer is owed in addition to the lead. The sentence needs a subject and an object.
- **Table row against paragraph.** The slot 3 table row says "Breaks first … ahead of slot 1 unless the next release is a major (below)". The last paragraph says "the breaks stay first in slot 3" for a major. The two agree. In a major release the heading and lead are dropped, but nothing says whether the `Breaking changes` heading is also dropped. I rate this taste.
- The skill adds no `now`/`no longer` narration.

## Item 2: claimed cases covered

Claims from the commit message, with the case that covers each:

| Claim | Covered by |
| --- | --- |
| Patch-release target leads with the breaks | `pgjdbc-4367-breaks` check 1 (`opus/result.md`, `haiku/result.md`, `haiku/result-2.md` pass; `opus/result-2.md` also passes check 1) |
| Result-shape change is a break | check 2 |
| Failure extended to later statements is a break, not Scope | check 3. One Opus run fails it, and the commit message says so. |
| A fix that now succeeds is not a break | check 4 |
| A change with no break grows no section | `pgjdbc-4392-no-break` checks 1 and 2 |
| Next release read from version file, milestone, or name | Only the version file and a missing milestone appear in the prompts |
| Unknown release: breaks lead | **none** |
| Major release: breaks stay first in slot 3, no lead | **none** |
| Commit body keeps the problem first, breaks as first `User-visible:` lines | **none** (both cases are PR descriptions) |
| Squash copies the description and the lead stays | **none** |
| Removed or renamed option, changed default, changed error code | **none** (only the return value, result shape, and a new failure are exercised) |

Commands the change tells someone to run: none. Hunk-to-claim check: the commit message does not claim the 1.4.0→1.5.0 bumps in `agent-packages/change-description-authoring/apm.yml`, root `apm.yml`, and `.claude-plugin/marketplace.json`. It also does not claim the new bullet in the package `README.md`, or the `cases/` line in `research/change-description-authoring/README.md`.

Findings:
- **Substantive.** Claimed arms without a case: the major-release arm, the unknown-release arm, and the commit-body and squash arms. The request is a case for each, or a sentence in the case README that says they are untested.
- **Substantive, small.** The version bump and the manifest/README hunks need one sentence in the commit message that claims them.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the genres and situations the change claims, and the control arm of each trial.

- **Negative control.** `pgjdbc-4392-no-break` is present and passes in 4 of 4 runs (2 Opus, 2 Haiku). It was run only with the rule. Without a baseline on `origin/main`, the claim "grows no section" has no comparison showing the rule is the cause. I rate this taste; it is a control, not a measurement of the rule.
- **Missing partitions.** The target branch is `master` at 42.7.14 with no milestone in both prompts. The boundary is the other side of "unless a major": a target at `…0.0`, a `release/N` branch name, and a `BREAKING CHANGE:` trailer. None has a run. This is the finding named under item 2.
- **Models.** Only Opus and Haiku ran. Sonnet is not tested, and the commit message does not claim it.
- **Sample size.** The rule moves `grant insert` out of Scope in 3 of 4 runs. The README states this honestly.
- **State left behind.** Not applicable. The skill replaces the earlier version and reads no persisted state.

Table of instructions the change adds or widens:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release is a major" | A repository with no versioning (a docs-only repo or an internal tool) where "released version" has no meaning | A `Breaking changes` lead for a changed default that nobody consumes as a release | Already ended by "A change with no break has neither the lead nor an empty heading (§7)" only if the change has no break. For a repo with no release, "where nothing says which release it is, the breaks lead" fires. Not addressed, so taste: the request is "only where the repository publishes releases". |
| "A failure extended to inputs that worked before is a break … it goes with the breaks, not in Scope" | A failure that existed before for every input, where the change only changes the message text | A break line for the changed message | Ended by "a changed error code for a failure a caller may catch", which scopes message changes. Not a finding. |
| "Where nothing says which release it is, the breaks lead" | A pull request whose description carries no break | Nothing | Ended by "A change with no break has neither the lead nor an empty heading". Not a finding. |
| "Commit body keeps problem first, breaks as first `User-visible:` lines" | A commit with no break | Nothing | Ended by "A change with no break grows no section". Not a finding. |

## Item 3a: level, placement, and the environment

Analogue used: which file each rule lives in, and whether the layout matches the siblings.
- The rule sits in the PR-description section of the skill, with the commit-body consequence beside it.
- The checklist item was added in §8. The package README was updated.
- The trigger file `instructions/change-description-authoring.instructions.md` was not changed, and the rule does not widen the trigger.
- The description in the manifests did not change.
- The case layout (`prompt.md`, per-model results, `skill-tree`) follows one structure across both cases. The repository's gate was not run.
- **Taste.** `cases/pgjdbc-4367-breaks/README.md` has one line over 120 characters (121), in check 3. The repository has a `markdown-line-length-120` skill.

## Item 4: names by content, not by position

- **Taste.** `result.md` / `result-2.md` name runs by ordinal. The content is the same prompt run twice, so the ordinal is accurate. The README table does say which file is which.
- **Taste.** The case README says "The first, without the sentence … The second, with that sentence" for three rule versions that are not stored. A reader cannot tell which is which from the text. The two versions could be named by their content, for example "the draft without the extended-failure sentence".
- The checks are numbered 1 to 6, and the README refers to them as "checks 1 to 3". This is stable within the file, so no finding.

## Item 5: the failure report

Analogue used: what a rule tells the reader to look at, and whether each detection detects its rule.
- Checks 1 to 3 each name a concrete string to look for (`getUpdateCount()` at `-1`, `grant insert on t to bob`), and checks 4 to 6 guard against the rule costing facts.
- The control's three checks name the literals `{d\t'1999-01-09'}` and `syntax error at or near "{"`.
- Check 1 ("opens … before the Why slot") can be satisfied by a one-line compatibility statement. It does not require the break lines themselves. Check 2 and 3 catch that case in practice. Taste.

## Item 6: what the writer says it verified

The red/green evidence is stated: baseline runs on the prior skill tree for 4367 on both models, two runs each with the rule, and the control. The mutation verdict is not applicable. The earlier rule drafts are "summarized in the case README, not stored", so the Opus claims about them cannot be re-checked. The commit message says so. The suite and the cases were not re-run.

## Item 7: siblings of the change

- Manifest set: `apm.yml`, `marketplace.json`, and the package `apm.yml` all moved to 1.5.0. A search for the package name in the repo's other manifests found no other listing.
- The changelog section of the skill ("Breaking changes are marked in place and sorted first within their category") is unchanged and compatible.
- Within the skill, line 83 (commit body) and line 226 (outcome slot) both say breaks come first, and they now agree with the new paragraph.
- The package README bullet omits the squash exception (the lead stays when the description becomes the body). Taste.

## Findings

| # | Finding | Label | File and line | Request |
| --- | --- | --- | --- | --- |
| 1 | Both case READMEs quote the rule as "promises compatibility". The heading says "unless … is a major". | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md` (intro); `cases/pgjdbc-4392-no-break/README.md` (intro) | Quote the heading as committed. |
| 2 | "the trailer decides" has no stated object, and one reading switches the rule off for tool-managed repositories. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` ~line 247 | Say what the trailer decides: for example, that the release is treated as a major, and that the trailer is written in addition to any lead. |
| 3 | The major, unknown-release, commit-body, and squash arms have no case. | Substantive | commit message; both case READMEs | Add a case per arm, or state in the README that they are untested. |
| 4 | The version bumps, package README bullet, and research README line are not claimed by any sentence of the commit message. | Substantive (small) | `apm.yml`, `.claude-plugin/marketplace.json`, `agent-packages/change-description-authoring/{apm.yml,README.md}`, `research/change-description-authoring/README.md` | Add one sentence to the message that claims them. |
| 5 | "Where nothing says which release it is, the breaks lead" fires for a repository that publishes no releases. | Taste | SKILL.md ~line 249 | Add "in a repository that publishes releases". |
| 6 | The control has no baseline run on `origin/main`. | Taste | `cases/pgjdbc-4392-no-break/README.md`, Results | Add one baseline run per model, or say none was run. |
| 7 | Ordinal names: `result-2.md`, "the first … the second" rule versions. | Taste | `cases/pgjdbc-4367-breaks/README.md`, Results | Name the versions by content. |
| 8 | Line 121 characters in check 3. | Taste | `cases/pgjdbc-4367-breaks/README.md`, check 3 | Re-wrap. |
| 9 | The package README bullet omits the squash exception. | Taste | `agent-packages/change-description-authoring/README.md` | Add a clause, or leave it. |

The review did not run the repository's gates or the cases, did not check the pgjdbc pull request links (no network), and did not do a style pass over the prose beyond sentences that read wrongly.
