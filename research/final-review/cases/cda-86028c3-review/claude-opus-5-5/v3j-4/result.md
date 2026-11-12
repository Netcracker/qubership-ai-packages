# Final review: `4f69810..86028c3` (one commit, change-description-authoring 1.4.0 → 1.5.0)

There was no task statement, so the claimed cases come from the commit message alone. This change has no code: a skill, a package README, version bumps, and research cases. I filled the form with the §2a analogues. I didn't run the drift script, because it parses code members and these files have none. Skills loaded: `english-developer-style`, plus `test-authoring` as named. `apm-authoring` was not loaded, because I was told not to load copies outside the provided directory. Its rules are not cited.

## Item 1: comments consistent with the code and with each other
*Analogue used: statements one file makes about another.*

- **The case READMEs quote a rule that doesn't exist.** `cases/pgjdbc-4367-breaks/README.md:7` and `cases/pgjdbc-4392-no-break/README.md:6` both quote "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". A reader who searches the skill for the quoted sentence finds nothing.
- **The release-tool sentence reads two ways.** `SKILL.md:247-248` says "the trailer decides, and it is written whatever the description does". It doesn't say what the trailer decides. One reading: a `!` or `BREAKING CHANGE:` makes the next release a major, so the breaks stay in slot 3. That cancels the lead in every release-please or semantic-release repository on a 1.x line, even though the rule's own reason still holds there (the reviewer's first decision is whether to accept a major bump). The other reading: the trailer only marks the version and the lead still applies.
- **The leading break lines get no label in a commit body.** `SKILL.md:257-260` (with `:86`) says that under §4 rule 5 the body "opens with its breaks and then its problem". It doesn't say how those lines are labeled. §2 says `User-visible:` is "what R4 and R5 search for", and §4 rule 5 bodies carry no headings (`:856-857`). So the leading breaks either lose the label or the body gets two `User-visible:` paragraphs.
- Checked and consistent: the slot-3 table cell at `:198`, the Problem checklist line at `:831`, §7 "no section for an absent concern", the changelog's in-place `**Breaking:**` rule in §3 (a different artifact), and `english-us-developer-style` §7, which routes ordering to this skill. The skill-tree ids match: `47980534` is `HEAD:<skill>` and `1f020ce5` is `HEAD~1:<skill>`.

## Item 2: claimed cases covered
*Analogue used: the section that handles each claim, and the case run that exercises it.*

| Claimed case (commit message) | Section | Run that exercises it |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `:234`, `:252` | `pgjdbc-4367-breaks`, 4 runs (target is 42.7.x) |
| Breaks stay in slot 3 when the next release is a major | `:254-255` | none |
| Release read from the version file | `:244-246` | 4367 (`gradle.properties`) |
| Release read from the milestone or branch name | `:245-246` | none |
| Breaks lead when nothing says which release it is | `:248-250` | none |
| Break kinds: new failure, result shape, extended failure | `:234-241` | 4367 checks 1–3 |
| Break kinds: removed option, changed default, changed error code | `:236-238` | none (definition only) |
| Commit body keeps the problem first, breaks first under `User-visible:` | `:257-258` | none (both prompts ask only for a PR description) |
| Squash copies the description, so the lead stays | `:258-260` | none (both prompts state a merge model where rule 5 doesn't apply) |
| A change with no break grows no section | `:255-256` | `pgjdbc-4392-no-break`, 4 runs |

**Commands in the change:**
- `cases/pgjdbc-4367-breaks/README.md:28-29` says to copy the skill "with `git archive <rev> agent-packages/…`". `git archive` writes a tar stream to stdout, so this command copies nothing. The form `agent-packages/AGENTS.md:42` prescribes, `git archive … | tar -x -C <dir> --strip-components=<depth>`, does copy it. No script runs either form, unlike `research/blackbox-test-design/cases/run-case.sh`.
- The same paragraph names `english-developer-style` from `agent-packages/english-us-developer-style` with no revision.

**Hunks no sentence claims:** the version bumps in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2` and `.claude-plugin/marketplace.json:291`. Earlier commits on this package stated theirs ("Version 1.2.0 to 1.3.0.").

## Item 3: boundaries, partitions, and the negative control
*Analogue used: partitions are the modes the change claims. The control is `pgjdbc-4392-no-break` plus the table below.*

- **Only one mode of five has a run.** The trials cover the patch-release PR description in a repository where §4 rule 5 doesn't apply. These claimed modes have no evidence: a major target, an unknown release, the commit-body form, the rule-5 body that leads with breaks, and a release-tool trailer.
- **The control does its job for "no break".** All four runs show no lead and no heading.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "the trailer decides" | release-please repo at 1.4.2, change with a break and `!` | Why first, breaks buried in slot 3; reviewer meets the major bump last | "the trailer sets the version; the breaks lead unless the branch already plans a major" |
| `:258` "the lead stays" | squash "title and description" repo, patch release, one break and one new error | unlabeled break lines at the top, or two `User-visible:` paragraphs | "under a `User-visible:` label of their own, the other outcomes in slot 4" |

Not findings: `:254` "Where the next release is a major", `:255` "A change with no break", `:240` "a failure that now succeeds".

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, and whether the repository's offline gates pass.*

None. The rule sits in §2 next to slot 3, which it amends. Its checklist line is in §8, and the package README bullet sits beside the slot bullets. The cases are under `research/<package>/cases/`, as `agent-packages/AGENTS.md:35` asks. Results: `make check` exited 0 (versions aligned, marketplace clean). `make check-descriptions` reported "ok: all 27 skill descriptions are within 1020 characters". The new `result*.md` and `prompt.md` files match the `FILTER_REGEX_EXCLUDE` pattern in `.github/super-linter.env`.

## Item 4: names by content, not by position

None. The case names, check names ("Lead", "Result shape", "Fix out"), and section references name things by content. "Three versions of the rule" in the 4367 README tells each version apart by what it contained.

## Item 5: the failure report
*Analogue used: whether the checklist reaches each rule, and whether each detection detects the rule.*

- **The checklist doesn't catch the miss the trials recorded.** The commit message reports that one Opus run in four left the extended failure (`grant insert`) in Scope. The Breaks checklist line (`:849-852`) asks only whether the description opens with the break lines. The Scope line (`:877`) asks whether gaps are named as intentional. Nothing asks whether a failure extended to inputs that worked before was left in Scope, so a self-review passes `opus/result-2.md`.

## Item 6: what the writer says it verified

- The red run is stated: both baseline runs on `1f020ce5` fail checks 1–3, and the rule runs pass them except for `opus/result-2.md` on check 3.
- **The control has no baseline arm.** Its outputs are 241–256 words against the 209-word draft. Nothing shows whether the rule caused any of that growth, which the form asks for when a rule is added after a bad output.
- I didn't check the cost figures in the 4367 README (Opus 5.5 at $4 per million, Haiku 5.5 at $0.10). They also disagree in order of magnitude with `agent-packages/AGENTS.md`, which says "about a dollar" per Opus run.

## Item 7: siblings of the change

- **The list of heading names misses the new heading.** `SKILL.md:300-301` lists `Why`, `What`, `User-visible changes`, `How to verify`, and `Scope` as "one set that matches the slots", but not `Breaking changes`, which `:252` now prescribes.
- Other places that list or route to the skill: the package README (updated), the research README file list (updated), marketplace and `apm.yml` descriptions (scope unchanged, so no edit needed), and both `english-*-developer-style` §7 copies (they route to this skill and are consistent). No sentence still gives a stale count.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule heading that isn't in the skill | substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed heading "…unless the next release from the target branch is a major" |
| "The trailer decides" reads two ways and can cancel the lead whenever a break triggers a major bump | substantive | `SKILL.md:247-248` | Say what the trailer decides, e.g. "the trailer sets the version; the breaks lead unless the branch already plans a major" |
| A rule-5 body that leads with breaks has no label for those lines | substantive | `SKILL.md:258-260`, `:86` | Add the label clause, e.g. "under a `User-visible:` label of their own" |
| Major, unknown-release, commit-body, rule-5 and trailer modes have no run | substantive | `research/change-description-authoring/cases/` | A case for at least the major target and the rule-5 body, or a sentence in the commit message saying they are untested |
| Checklist doesn't detect an extended failure left in Scope, the miss the trials recorded | substantive | `SKILL.md:849-852` | Add "is no failure extended to inputs that worked before left in Scope?" |
| `Running it` command copies nothing: `git archive` without `\| tar -x` | substantive | `cases/pgjdbc-4367-breaks/README.md:28-29` | Use the AGENTS.md pipeline, and pin the revision of the style skill |
| Control has no baseline arm, so the growth isn't attributed | substantive | `cases/pgjdbc-4392-no-break/README.md:20-24` | Run the control on `1f020ce5` and compare word counts |
| Version bump not claimed in the commit message | substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." as earlier commits did |
| `Breaking changes` missing from the list of heading names | substantive | `SKILL.md:300-301` | Add it to the set, conditional on a break |

Not checked: markdownlint on the two case READMEs (no offline linter run), `make test` (no change under `tests/` or the scripts it runs), whether the pgjdbc PRs and comment link say what the READMEs claim (no network), the model prices in the 4367 README, and a pass over the prose for style alone.
