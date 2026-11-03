# Final review of `4f69810..HEAD` (86028c3, a skill change)

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill package (`change-description-authoring` SKILL.md and README), bumps versions, and adds research cases. I used the §2a analogues for every item. I did not run the drift script, because there are no members for it to parse. I loaded `english-developer-style` from the given directory. `apm-authoring` is not among the three skills I was allowed to load, so I did not apply its rules. There is no previous report.

## Item 1: comments consistent with the code and with each other
Analogue used: statements one changed file makes about another.
- **Finding.** `research/.../pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". The `skill-tree` ids (`4798053…`) match HEAD's skill tree, so the runs used the committed wording and the quote is left over from an earlier draft. A reader would test the cases against a rule that doesn't exist.
- **Finding.** SKILL.md:844-846 is an unchanged checklist line ("Caller"). It still asks for every outcome "under 'User-visible changes', breaks first". The new rule (:252-254) and the next checklist line (:849-851) say the breaks lead the description and slot 3 keeps "only the other outcomes". An agent working through the checklist gets two opposite instructions in a row.
- The commit message says Opus and Haiku ran at "(effort high)". The case README:30 says Haiku ran at `high` and Opus at the session default. This is taste.
- Checked and consistent: the cross-references §4 rule 5, §5 (the `BREAKING CHANGE:` row at :706) and §7 (:787); SKILL.md:86, :198 and :310 against the new rule; the package README summary; the research README listing for `cases/` and its date; the skill-tree ids (HEAD → `4798053`, base 4f69810 → `1f020ce`); and every claim in the results tables, which I re-read against the eight result files. I did not fetch the cited maintainer comment (`#issuecomment-6079358908`) because there is no network.

## Item 2: claimed cases covered
| Claim (commit message) | Section | Evidence |
| --- | --- | --- |
| The description leads with the breaks unless the next release is a major | :234, :252 | 4367 patch arm, 4/4 runs pass |
| The next release is read from the version file, milestone, or branch name | :245-247 | only the version file is exercised (`gradle.properties`) |
| Breaks lead where nothing says which release it is | :248-250 | none |
| The definition of a break: new failure, return value or result shape, removed option, default, error code, extended failure | :234-241 | new failure, result shape, and extended failure are exercised; the other three are not |
| The commit body keeps the problem first, with the breaks as the first `User-visible:` lines | :257-258 | none: both cases draft only a PR description |
| Under squash, the lead stays in the body | :258-260, :86 | none |
| A change with no break gets no section | :255 | 4392 control, 4/4 runs |
| The run counts, "three of four", and "one Opus run left it" | case README | verified: `opus/result-2.md` keeps `grant insert` in Scope |

Commands: the only command in the changed files is the `./gradlew` line quoted from the pgjdbc draft. It is case input, not something the change tells anyone to run, so no runner is owed.

Hunks: the version bumps from 1.4.0 to 1.5.0 in three files are the package's own release bump. Each of the three earlier commits to this package makes the same bump, and `make check` passes. Every other hunk is covered by a sentence of the commit message.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the situations the change claims, plus the table of added instructions.
- **Finding (substantive).** The "unless the next release is a major" arm in the title has no evidence. Both cases target the same 42.7.x `master`. The no-break control tests the "no break" partition, not the "major" one. There is also no case for an unknown release, the commit-body arm, or the squash ("title and description") arm.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "the trailer decides" | a release-please repo, a fix that breaks a call | it doesn't know which way it decides; read literally, the trailer forces a major, so there's no lead even though the reviewer must accept that major | "the trailer makes the next release a major, and the breaks still lead" (or the opposite, stated) |
| `:252` "under a `Breaking changes` heading where the description has headings" | a repo whose template has its own breaking-change section lower down | a new top heading above the template, with the template's section duplicated or left empty | "where the template has a section for breaks, that section moves to the top" |
| `:258` "Where §4 rule 5 makes the description the commit body, the lead stays" | squash "title and description", the description written under a `Breaking changes` heading | a permanent body whose breaks carry no `User-visible:` label for R4 or R5 to grep | "written as the body's first `User-visible:` lines" |

Not findings: `:255` "neither the lead nor an empty", `:254` "the breaks stay first in slot 3".

## Item 3a: level, placement, and the environment
None. The cases sit under `research/<pkg>/cases/`, which matches `research/blackbox-test-design/cases`. The result and prompt files match `FILTER_REGEX_EXCLUDE`, which I checked against all 26 changed paths. These offline gates pass: `make check` (dry run, version check), `make check-descriptions` ("all 27 skill descriptions are within 1020 characters") and `tests/marketplace_roundtrip.sh` (PASS).

## Item 4: names by content, not by position
None. Slot numbers are labels the skill defines in its tables. The case checks are named in the table headers ("Lead (1)"). "The first … the second" (case README:47) refers to unnamed drafts that are not stored.

## Item 5: the failure report
- **Finding (substantive).** The checklist line "Breaks" (:849-851) checks the lead's position but not what counts as a break. The baseline failed on exactly that, leaving the result shape in slot 3 and the extended failure in Scope, and the committed rule still fails it in `opus/result-2.md`. The checklist line therefore detects a weaker property than the rule it is attached to. The request is to add "including a different result shape and a failure extended to inputs that worked before, none left in Scope".

## Item 6: what the writer says it verified
The exemplar and the bad case are both present: on the baselines, checks 1 to 3 fail and the rule arm passes them. The noise case is present too (4392). However, its growth is measured only against the author's draft (209 words → 241-256). There is no run on 4f69810, so whether the rule made output grow on an input where it is noise is not shown. **Finding (substantive):** run the control on the base skill as well.

## Item 7: siblings of the change
Within the file, the checklist sibling at :845 is filed under item 1. Outside the package, the only other mentions are changelog guidance (`english-*-developer-style` :570, which defers to this skill) and the Russian changelog examples. Neither concerns the order inside a PR description. The package README is the routing surface, and it is updated. The skill's `description` frontmatter needs no change, since the scope did not widen.

## Findings
| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| Both case READMEs quote a rule wording ("promises compatibility") that the skill doesn't contain | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed heading at SKILL.md:234 |
| The "Caller" checklist line still puts every outcome, breaks first, under "User-visible changes" | Substantive | SKILL.md:845 | Add "except breaks that lead the description (below)" |
| The major, unknown-release, commit-body, and squash arms have no case | Substantive | `research/.../cases/` | At least a run with a major target (for example `43.0.0-SNAPSHOT`) showing no lead |
| "The trailer decides" names no outcome | Substantive | SKILL.md:247 | State which way it decides |
| No clause for a template that already has a breaking-change section | Substantive | SKILL.md:252 | The clause in the item 3 table |
| Under rule 5, the lead's lines are not tied to the `User-visible:` label | Substantive | SKILL.md:258 | The clause in the item 3 table |
| The "Breaks" checklist line doesn't detect misclassified breaks | Substantive | SKILL.md:849 | Name the result shape and the extended failure |
| The control has no baseline run, so its growth is unmeasured | Substantive | `cases/pgjdbc-4392-no-break/README.md:22` | Run the control on 4f69810 |
| The commit message's "(effort high)" seems to cover Opus too | Taste | commit message | Say "Haiku at effort high" |
| 0.x versions: whether a minor bump counts as a major is not addressed | Taste | SKILL.md:243 | One clause, if wanted |

This review did not re-run the model trials, fetch the cited pgjdbc comment or check the README's token prices (no network), apply `apm-authoring` (not available), or make a pass over the prose for style alone.
