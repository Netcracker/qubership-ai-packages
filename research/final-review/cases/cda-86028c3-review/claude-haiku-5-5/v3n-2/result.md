## Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit 86028c3)

**Claims source.** No task statement was handed over, so the claimed cases come from the commit message of 86028c3 and the test-case READMEs it adds. There is no previous report, so §4 does not apply.

**Drift script.** Not run. The change touches no code member, so there is nothing for it to parse.

**Analogues.** This is a skill and research change, so each item uses the §2a analogue. The skills loaded from the given directory are `apm-authoring` and `english-developer-style`. The doc-comment skill does not apply.

### Item 1: comments consistent with the code and with each other

Analogue: statements the changed skill makes about its own rules, the other sections, and the cited cases.

- The lead rule (`SKILL.md:234-241`), the slot 1 sentence (`:86-88`), the checklist "Breaks" line (`:849-852`), the README bullet, and the slot 3 table cell agree on the non-major case.
- Conflicts and ambiguities are listed as findings F1 to F3 below.
- The §8 checklist and the README bullet agree with the rule. The worked *After* example (`:262-300`) has no break, so it is still correct.

### Item 2: claimed cases covered

Analogue: each claim in the commit message and the case READMEs, against the case that exercises it.

- Lead when the release is not a major: checks 1 to 3 in `pgjdbc-4367-breaks`, all four rule runs pass (`opus/result.md`, `opus/result-2.md`, `haiku/result.md`, `haiku/result-2.md`).
- "Breaks" as result shape and as an extended failure: checks 2 and 3, verified by grep for `getUpdateCount` and `-1` in each run.
- Red evidence on the base commit: `opus/baseline/result.md` and `haiku/baseline/result.md` fail the lead, result-shape, and Scope checks as the table says.
- No break gives no section: `pgjdbc-4392-no-break`, all four runs. No "Breaking changes" heading appears.
- The skill-tree ids match the claim. Rule runs use `4798053…`, which is `HEAD:…/change-description-authoring`. Baseline runs use `1f020ce…`, which is the parent tree.
- Word counts in the table match `wc -w`.
- Uncovered claims are listed in F4.
- Hunks: the version bump is not claimed by any sentence of the message (F5).

### Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the release kinds and the break kinds the rule names. The negative control is `pgjdbc-4392-no-break`.

- Partitions with no run: a major target, an unknown release, and a `BREAKING CHANGE:` or `!` trailer. See F4.
- The commit-body and rule-5 path has no run, F4.
- Pre-existing state: none. The skill's output has no earlier-version state to meet.

**Added instructions** (SKILL.md lines; a rule is one row only if it has a sub-clause that changes its output):
- Added instructions: 7, no rows.
- Not findings: `:234`, `:255`.

### Item 3a: level, placement, and the environment

- The rule sits in the pull request description section of the right skill. Its README bullet and checklist item are consistent.
- Registration: `apm.yml:2`, `apm.yml:168`, and `.claude-plugin/marketplace.json:291` all say 1.5.0.
- `make check` (apm pack dry run, `--check-versions --check-clean`) exits 0 and lists `change-description-authoring 1.5.0 [matches]`.
- `make check-descriptions` reports all 27 skill descriptions within 1020 characters.
- The `make test` target does not run the research cases, so the cases are run only by hand.

### Item 4: names by content, not by position

- `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:25` uses "Checks 1 to 3" and "4 to 6". Each check has a named content label in bold.
- `pgjdbc-4367-breaks/README.md:49` uses "The first" and "The second" for draft versions of the rule.

### Item 5: the failure report

None. The change adds no assertions. The case checks state what each result shows.

### Item 6: what the writer says it verified

- The red runs on the base tree exist for both models. The control has no base run, which is not needed for a control that only shows a section does not appear.
- The major branch and the unknown-release branch have no evidence, as stated under F4.

### Item 7: siblings of the change

- The sites that carry the same symptom are the description, the commit body, and the README bullet. The changelog's `**Breaking:**` marking is a different rule, sorted within categories. Its defect does not apply, so there is no sibling finding.
- Other skills that name `change-description-authoring` (`english-developer-style`, `docs-page-authoring`, `problem-report-authoring`, `test-authoring`) only delegate to it. None restates the break rule.
- The apm-authoring rule "Fix a bad output where the rule stops" is met: the lead has an end condition, and the 4392 control covers the input where it must not fire.

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | "The lead stays … that body opens with its breaks" presumes a lead that a major release does not have. A major puts breaks after Why (`:254-255`), so a squash-copied body would open with breaks while the description opens with Why. | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:258-260` | Say the body opens with breaks only where the description leads. In a major, the body keeps problem first. |
| F2 | Two rules send the same kind of item to different slots. An extended failure "goes with the breaks, not in the Scope slot" (`:239`). A compatibility break a maintainer must decide stays in Scope as a question (`:488-491`). Opus `pgjdbc-4367-breaks/opus/result-2.md` kept `grant insert` in Scope, which is what the Scope rule allows. | substantive | `SKILL.md:239` vs `SKILL.md:488-491` | State which slot a break takes when its intent is open, for example the break in slot 3 and the question in Scope, and make both sentences say it. |
| F3 | "the trailer decides, and it is written whatever the description does" does not say which way the trailer points. A reader can take it as forcing a major, which suppresses the lead, or as forcing the lead. | substantive | `SKILL.md:247-248` | Name the outcome: "A `BREAKING CHANGE:` trailer or `!` makes the next release a major, so the breaks stay in slot 3." |
| F4 | Claimed branches with no run: the major target and the unknown-release target (`:234`, `:254-255`, and the commit message "unless … a major"); the trailer branch; the squash-copied body (`:257-260`); and three of five break kinds named in the commit (removed option, changed default, changed error code). | substantive | `SKILL.md:234-260`; commit 86028c3 message | Add a case with a major target (for example `gradle.properties` at 43.0.0) and one with no version information, and one squash-copy run. Add a removed-option or changed-default case, or drop those kinds from the claim. |
| F5 | Unclaimed hunk: the version bump 1.4.0 to 1.5.0. No sentence of the commit message mentions it. | substantive | `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168`; `.claude-plugin/marketplace.json:291` | Add a sentence to the commit message that claims the bump and says why the contract changed, or move the bump to its own commit. |
| F6 | The case READMEs quote a rule that is not in the skill: "A break leads the description where the next release from the target branch promises compatibility". The committed heading reads "unless the next release from the target branch is a major". The runs used the committed tree, so only the citation is wrong. | substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8`; `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading, or link its line. |
| F7 | The commit message says the runs were "on Opus and Haiku (effort high)". The case README says "Haiku ran at effort `high`; Opus at the session's default." | substantive | commit 86028c3 message, line 23; `research/.../pgjdbc-4367-breaks/README.md:33-34` | Correct the message (amend, since it is unpushed) or the README sentence. |
| F8 | Ordinals where the checks and versions have content names. | taste | `research/.../pgjdbc-4367-breaks/README.md:25`, `:49` | Name the checks and the draft versions by their content. Expect this to be declined without discussion. |

**Churn:** none.

**Not checked:** the research runs were not re-run, since there is no model access offline. The result files were checked only for the facts the table cites (headings, `-1`, word counts, tree ids). `make test` was not run. markdownlint and Vale are not installed here. The English prose was not proofread beyond the sentences that read wrongly.
