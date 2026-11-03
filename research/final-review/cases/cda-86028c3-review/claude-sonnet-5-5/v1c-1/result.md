I'm drafting the report now. I've read the diff, the case READMEs and prompts, and the result files, and I've checked the skill-tree ids against the git trees.

# Final review: `4f69810..HEAD` (86028c3, change-description-authoring: breaks lead the description)

**Inputs.** There is no task statement, so the claimed cases come from the commit message only. This is a change with no code, so I used the §2a analogues. I did not run the drift script, because there are no members to parse. I applied `english-developer-style` only where a sentence reads wrongly. I did not load `apm-authoring`, because it is not among the three skills I was told to use. No previous report exists.

## Item 1: Comments consistent with the code and with each other
The analogue is the statements the files make about each other.

- **Stale quoted rule name (substantive).** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". They point at "SKILL.md §2". The SKILL heading is "A break leads the description unless the next release from the target branch is a major". The meaning differs too: "promises compatibility" does not obviously cover the unknown-release case that the SKILL says leads. See `cases/pgjdbc-4367-breaks/README.md:6-7` and `cases/pgjdbc-4392-no-break/README.md:6-7`.
- **Contradiction within SKILL.md (substantive).** The sentence "Under §4 rule 5 the description is the commit body and takes the body's shape instead" sits at about line 310 of `SKILL.md`. The new text at lines 257-260 says that when rule 5 applies, "the lead stays" and the body opens with its breaks and then its problem. The unchanged sentence makes a reader apply the body's problem-first shape. The new paragraph is unreachable from it.
- **Slot 1 "opens the body" (taste).** The new sentence at line 86 reconciles this for a rule-5 body. Slot 3's table row still says "ahead of slot 1", while the commit-body slot table says slot 1 opens. This is readable but needs two cross-references.
- **Label lost in a rule-5 body (substantive).** Lines 257-260 say the commit body keeps breaks as the first `User-visible:` lines "because the label is what R4 and R5 search for". The rule-5 case says only that "the lead stays". It does not say whether the breaks in that body also carry `User-visible:`. If they are in a `Breaking changes` section and not under the label, the grep the paragraph just justified misses them.
- **Narrating the change.** None. The case READMEs carry dated run history, which belongs to them.
- **Numbers.** Word counts, skill-tree ids and run counts all match the files. I recounted with `wc -w`, and `git rev-parse` confirms 4798053 at HEAD and 1f020ce for the baseline.

## Item 2: Claimed cases covered
Claimed in the commit message:

| Claim | Covered by |
| --- | --- |
| Break leads in a patch release | `4367-breaks` check 1: opus `result.md`, `result-2.md`, haiku `result.md`, `result-2.md` |
| Result shape is a break | check 2 |
| Extended failure is a break | check 3: 3 of 4 pass, and `opus/result-2.md` fails, as stated |
| Fix is not a break | check 4 |
| Break lines are not repeated | check 5 |
| Literals are kept | check 6 |
| No section when nothing breaks | `4392-no-break`, 4 runs |
| Baseline puts Why first | the two `baseline/result.md` files |
| Release read from version file, milestone, or branch name | **no case** |
| Major release: breaks stay first in slot 3 | **no case** |
| Release unknown: breaks lead | **no case** |
| Release tool and `BREAKING CHANGE:` trailer decide | **no case** |
| Squash copies the description: the lead stays, and the body opens with breaks then problem | **no case** |
| Commit body keeps problem first, with breaks as the first `User-visible:` lines | **no case** (the cases only produce pull request descriptions) |

Both prompts use the same repository facts (`master`, 42.7.14, no milestone). Every case is therefore a patch release.

- **Missing partitions (substantive).** The major-release and unknown-release arms of the rule, and the rule-5 and commit-body paths, have no run. Only the patch-release lead is shown. The commit message calls 4392 a "negative control", but it varies the change, not the release.
- **Commands.** None in the diff.
- **Hunks against claims.** The version bumps 1.4.0 → 1.5.0 in `apm.yml`, `.claude-plugin/marketplace.json` and the package `apm.yml`, the package README bullet, and the research README hunk are not in any sentence of the commit message, except that the two cases are. Taste, since a bump with a feature commit is routine. I ask for one sentence.
- **Effort setting.** The commit message says "on Opus and Haiku (effort high)". The case README says Haiku ran at `high` and Opus at the session's default, so the commit message overstates.

## Item 3: Boundaries, partitions, negative control
This item is the analogue for a skill, together with the table of added instructions.

| Instruction | Input it does not serve | What an agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release … is a major" | a change that breaks nothing | nothing; "A change with no break has neither the lead nor an empty heading" is stated, and 4392 shows it | already ended by that text |
| "Where nothing says which release it is, the breaks lead" | a repository with no version signal and a change with no break | no lead, by the same sentence | already ended |
| "a failure the change extends to inputs that worked before is a break … not in Scope" | a rejection of input that already failed in the same way on the same inputs | possibly a break line for an unchanged outcome; "inputs that worked before" bounds it | already ended |
| "under a `Breaking changes` heading where the description has headings, after at most a short paragraph" | a description of one paragraph with no headings | the lead sentence with no heading, as the clause allows | already ended |
| "Where the next release is a major, the breaks stay first in slot 3" | a major with no break | nothing | already ended |

Substantive: the instruction that a failure extended to inputs that worked before leads. It moved the case in only 3 of 4 runs, and the README says so honestly. That is evidence of a weak instruction, not a missing clause.

**Pre-existing state.** Descriptions already written with breaks in slot 3 are untouched by this change. The version bump is the only state that carries over. None.

## Item 3a: Level, placement, environment
- **Case layout (none).** It follows the existing pattern: `README.md`, `prompt.md`, `<model>/result*.md` and `skill-tree`.
- **Markdown lint (not run).** Case result files may be pasted as raw output. The research README says result files are excluded from markdownlint, but the case READMEs and prompts are not checked here.
- **Repository gate (not run).** The repository gate for registration entries (the version in `apm.yml` against `marketplace.json`) was not run. The three version strings agree on 1.5.0 by inspection.

## Item 4: Names by content, not position
- **`result-2.md` (taste).** The file name is ordinal ("second run"). The README rows name them by path, so nothing is lost, and the runs differ only by sampling.
- **"Three versions of the rule" / "the first … the second"** in the README is an ordinal reference to drafts that are not stored. The note is acknowledged in the commit. Taste.
- **Other names (none).** Case directory names are by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`).

## Item 5: Failure report
The analogue is what a failed check tells a reader.

- **Detection (none).** Each check lists the literal or the structure to look for, so a reader can tell whether a result passes.
- **Weaker property (substantive).** Check 1 says "before the Why slot", which `haiku/result-2.md` passes at line 1, but a lead that is long still passes. "At most a short paragraph" has no measure. A lead of three paragraphs passes.
- **Hand-graded results.** The table's pass and fail verdicts are by hand. No script reproduces them.

## Item 6: What the writer says it verified
- **Baseline (stated).** The commit message shows a red arm: both baseline runs fail checks 1-3. A rewritten rule was run, and the README says the committed wording gives 3 of 4.
- **Stored runs against the final skill (partly).** The final skill tree is the one in `skill-tree`, which matches HEAD. Results for the two earlier drafts are not stored, and the commit says so.
- **No sibling noise check.** The 4392 control shows the added rule costs nothing on a no-break change. The commit body states it.
- **The final wording was rerun?** Yes: tree ids match, so the committed text is the text that ran. Good.

## Item 7: Siblings
Places that enumerate or route to the rule:

- **Checked and updated.** The slot-3 table row, the Problem checklist line, a new Breaks checklist line, the package README bullet, and the three version entries.
- **Not updated:**
  - **Changelog section.** The "Breaking changes are marked in place" rule at line 543 says breaks sort first within their category. The new rule is about descriptions only, and the changelog is not affected.
  - **Line 490.** The "break is intended, keep it in the Scope slot as a question" rule contradicts the new "not in the Scope slot" for an extended failure. Line 490 says an intended-or-not break stays in Scope as a question for the maintainer. The new text sends an extended failure to the breaks. Reconcile or cross-reference (substantive).
  - **Package `apm.yml` description and `marketplace.json` description** do not mention break handling. Fine, they are summaries.
- **Counts.** No sentence counts the slots differently now. The six-slot description is unchanged.
- **Other paths.** The "R5" and "R4" reader tables list no slot position for breaks. None found.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| Case READMEs quote a rule name that does not exist ("where … promises compatibility") and cite "§2" | substantive | `cases/pgjdbc-4367-breaks/README.md:6-7`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the SKILL heading as written |
| "Takes the body's shape instead" contradicts "the lead stays" | substantive | `SKILL.md` ~310 vs 257-260 | Reword ~310 so the rule-5 body is told once |
| Rule-5 body: it is not said whether the lead's breaks carry `User-visible:` | substantive | `SKILL.md:257-260` | Say they carry it, or say how R4 and R5 find them |
| Line 490 keeps an intended break in Scope as a question; the new text moves breaks out of Scope | substantive | `SKILL.md:490` | State which wins, for a break the maintainer must decide |
| No case for a major release, an unknown release, the trailer, or a squash/commit body | substantive | cases | Add a major-release arm and an unknown-release arm, or state in the case README that they are untested |
| Commit says Opus ran at effort high; README says the session default | substantive | commit message, `4367-breaks/README.md` | Correct the commit sentence |
| Version bump in three files and the package README bullet are in no sentence | taste | `apm.yml`, `marketplace.json`, package `apm.yml` | One sentence, "bumps to 1.5.0" |
| "At most a short paragraph" has no check | taste | `4367-breaks/README.md` check 1 | Give a count in the check |

Churn items: none reported.

**Not checked.** I did not run the suite, `markdownlint`, or the repository's registration gate. I did not rerun any model case. I did not review the prose for style, and I did not read every line of the 10 result files, only the headings, the counts, and the checks I cite.
