# Final review of 86028c3 (`4f69810..HEAD`)

**Scope.** One commit, `86028c3`. It changes a skill (`change-description-authoring` SKILL.md, its package README, versions), adds two regression cases under `research/change-description-authoring/cases/`, and updates the research README. There is no code and no test suite. No task statement was handed over, so the claimed cases come from the commit message, and the cases' own READMEs were used for what the runs were meant to show. No previous report exists, so §4's table is empty.

**Skills.** I loaded `english-developer-style` and `test-authoring` from the given skills directory. The artifact's authoring skill (`apm-authoring`) was not among the three handed over, so I did not load it. I used §2a with the change-description skill's own rules as the authoring reference.

**Drift script.** Run: `comment-drift.py 4f69810 HEAD` exited 0 with no output. The changed files are Markdown, so there are no members to list.

**Gate.** `apm pack --check-versions --check-clean --dry-run` with the local `apm` 0.26.0 exited 0 ("Version alignment OK"), and the tree stayed clean. The Makefile's uvx pin was not used.

## Item 1: comments consistent with the code and with each other

- **Stale rule title in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The rule is now SKILL.md:234, "A break leads the description unless the next release from the target branch is a major." A reader searching for the quoted sentence finds nothing, and the old condition is different. (substantive)
- **Commit message and README disagree on run conditions.** Commit `86028c3` says the 4367 cases ran "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says "Haiku ran at effort `high`; Opus at the session's default." (substantive)
- **Ordinal names.** `pgjdbc-4367-breaks/README.md:25`: "Checks 1 to 3 are the rule under test; 4 to 6 are the guard…". (taste, see Item 4)
- **Rule 5 is not updated.** SKILL.md:638 still says "shape it as §2's commit body", where §2 opens with the problem. The breaks-first exception is stated at SKILL.md:86-87 and 257-260 but not pointed to from rule 5. (taste)
- **Ambiguous trailer sentence.** SKILL.md:247-248, "the trailer decides, and it is written whatever the description does", does not say what the trailer decides. (taste)

The other comments I checked are consistent with the code: the §8 checklist (SKILL.md:849-852), the §7 "no empty section" rule, the package README bullet, and the word counts. I confirmed the word counts in the 4392 README (241, 251, 256, 249) and the 4367 table (756, 825, 792, 758, 779, 784) with `wc`.

## Item 2: claimed cases covered

| Claim (commit message) | Covered by | Finding |
|---|---|---|
| Lead when the next release is not a major | 4367 checks 1, all four runs | Major and unknown branches not run (below) |
| Result-shape break (`getUpdateCount()` → -1) | 4367 check 2, all four runs | none |
| Failure extended to later statements is a break | 4367 check 3, three of four runs | none |
| A fix is not a break | 4367 check 4, all four runs | none |
| No break means no lead and no section | 4392 checks 1-3, four runs | none |
| Commit body keeps the problem first; the lead stays under rule 5 | none | **S3** |
| Break kinds: removed option, changed default, changed error code | none | **S4** |

- **S2. The release-name branches have no run.** The 4367 prompt's version file says `42.7.14`, and the latest release tag is `REL42.7.14`. The rule (SKILL.md:245-246) says to read the next release from the version file, but that file names the last release. So the case passes by inference, and the "major" and "unknown" branches are never run.
- **S3. The commit-body form has no run.** All runs are PR descriptions. No case produces a commit body, so "the breaks as the first `User-visible:` lines" and "that body opens with its breaks" (SKILL.md:257-260) have no evidence.
- **S4. Break kinds without a case.** The definition at SKILL.md:234-237 and the commit message name a removed option, a changed default, and a changed error code. No run exercises any of them.
- **S5. Unclaimed hunks.** The version bumps `1.4.0` → `1.5.0` in `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, and `apm.yml:168` are not claimed by any sentence in the commit message. The gate passes, and recent feature commits also touch `apm.yml`, so this looks like convention. It still needs a sentence in the commit body or its own commit. (substantive)

I also checked the commit's results against the result files: the lead, the result-shape line, the `grant insert` line, and the "no section" control all match the README table. The four runs with the rule are at tree `47980534…`, which is HEAD's skill tree. The baselines are at tree `1f020ce5…`, which is the base commit's skill tree.

## Item 3: boundaries, partitions, and the negative control

- **S2 (above)** is the missing partition: a break in a release named as a major, and a release nothing names.
- **Negative control.** The 4392 control has two runs per model and no origin/main run. Its base arm is trivially green because the base never leads, so the gap does not hide a defect. (taste)
- **Baselines.** One run per model supports "without the rule both models put Why first". (taste)
- **Pre-existing state, values users pass, limits, mechanism replacement:** not applicable. The change replaces no state or mechanism.

**§2a instruction table** (one row per added or widened instruction):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| "A break leads … unless the next release … is a major" (SKILL.md:234) | a break in a release named as a major | not run | "unless … is a major": present, untested (S2) |
| "A failure that now succeeds is a fix, not a break" (SKILL.md:240-241) | `create table begin …` no longer failing | stays out of the lead in all four runs | the rule's own clause; run confirms |
| "A change with no break has neither the lead nor an empty heading" (SKILL.md:255) | 4392 (no break) | no lead, no heading in all four runs | the rule's own clause; run confirms |
| Commit body keeps problem first; lead stays under rule 5 (SKILL.md:257-260) | a break in a commit body | not run | none; (S3) |
| "the trailer decides" for `BREAKING CHANGE:` (SKILL.md:247-248) | a change with that trailer | unclear which decision it makes | none; (taste) |

## Item 3a: level, placement, environment

- None of the new behavior is observable in one process; the observation is a model run, so no smallest-level test is owed.
- The case directories sit under `research/` and are registered in the research README.
- The repository's gate passes (see above). Markdownlint was not run; it is not installed and its config is not in the tree.
- Long lines: `pgjdbc-4367-breaks/README.md:17` is 121 characters. If the repo pins MD013 to 120, as the `markdown-line-length-120` skill it carries assumes, this fails. (taste; the pin could not be confirmed)

## Item 4: names by content

- Ordinals: `pgjdbc-4367-breaks/README.md:25` names checks by number. The same README's results table headers "Lead (1)" and "Result shape (2)" also use numbers. Naming them by content ("the lead, result-shape, and grant-insert checks") would be safer. (taste)
- Case IDs `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break` name content. The SKILL's slot numbers follow its own table. Nothing else.

## Item 5: the failure report

- The change has no assertions. The graded checks are hand-judged, which is covered under Item 6.
- The SKILL's own §8 checklist reaches the rule (SKILL.md:849-852). That line detects both the lead and the "no break" control. The commit-body rule has no checklist line.
- **none**

## Item 6: what the writer says it verified

- Evidence is present: the origin/main baselines for the failing arm, the control runs, and the final version of the rule (tree match).
- Gaps: S2 and S3, plus the one-run baselines (taste) and the missing control base arm (taste).
- Earlier drafts of the rule were run but not stored. The commit says so, which is honest.

## Item 7: siblings

- The package README bullet (`agent-packages/change-description-authoring/README.md:23-24`), the research README, and the version files are updated and consistent.
- The package's `instructions/` file and `references/merge-model.md` say nothing about slot order, so they need no change.
- Rule 5 (SKILL.md:638) is the one sibling not updated (taste).
- **S6** and **S7** below are sibling-level defects in the README and commit.
- **S7. The documented command does not copy files.** `pgjdbc-4367-breaks/README.md:29` says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". `git archive` writes a tar stream to stdout by default; `git archive HEAD README.md` emits a tar header and creates no files. The command needs `| tar -x -C <dir>`. The `agent-packages/english-us-developer-style` path it names exists. (substantive)

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| S1 | Quoted rule title no longer exists; it names a different condition | substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote SKILL.md:234 verbatim |
| S2 | Major and unknown release branches never run; version file names the last release, so "next release" is inferred | substantive | `cases/pgjdbc-4367-breaks/README.md`; SKILL.md:245-246, 252-254 | Run a case with a major next release (expect Why first) and one with no release signal; say what to read when the version file names the last release |
| S3 | Commit-body form (breaks first in `User-visible:`; lead stays under rule 5) has no run | substantive | SKILL.md:257-260; commit body | Run a commit-body case for 4367 |
| S4 | Removed option, changed default, changed error code claimed, not exercised | substantive | SKILL.md:234-237; commit body | One case per kind, or narrow the claim |
| S5 | Version bumps in three files not claimed by the commit | substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:2`; `apm.yml:168` | Claim the bump in the commit body, or split it |
| S6 | Commit says both models ran at effort high; README says Opus at default | substantive | commit `86028c3`; `cases/pgjdbc-4367-breaks/README.md:33` | Correct the commit message (amend) or the README |
| S7 | `git archive` documented without extraction; creates no files | substantive | `cases/pgjdbc-4367-breaks/README.md:29` | Pipe to `tar -x -C <dir>` |
| T1 | Ordinal names "Checks 1 to 3" and "Lead (1)" | taste | `cases/pgjdbc-4367-breaks/README.md:25` and results table | Name the checks by content |
| T2 | Rule 5 does not point to the breaks-first exception | taste | SKILL.md:638 | Add "(breaks first where §2 says)" |
| T3 | "The trailer decides" does not say what it decides | taste | SKILL.md:247-248 | Say it makes the next release a major |
| T4 | Control 4392 has no origin/main arm | taste | `cases/pgjdbc-4392-no-break/README.md` | Run it on the base, or say it has none |
| T5 | "Both models put Why first" rests on one run per model | taste | commit; `cases/pgjdbc-4367-breaks/README.md` | Say "in one run each" |
| T6 | 121-character line may fail MD013 at 120 | taste | `cases/pgjdbc-4367-breaks/README.md:17` | Wrap; the pin could not be confirmed |

No churn items were found.

## Not checked

- No network: the pgjdbc PRs #4367 and #4392, the maintainer's rewrite, and the cited prices (Opus $4/M, Haiku $0.10/M) were not verified. The 209-word draft count was not checked.
- Markdownlint and super-linter were not run.
- I read in full the 4367 results with the rule (Opus ×2, Haiku ×2), the 4367 baselines (Opus, Haiku), and the 4392 Opus control. The other three 4392 results were checked by word count, literal count, and a grep for break terms only. The results are the writer's to grade, and I did not re-grade them.
- No test suite exists in this change.
- The gate's output went to `/private/tmp/claude-501/gate.out` in the scratchpad. Nothing in the repository changed.
