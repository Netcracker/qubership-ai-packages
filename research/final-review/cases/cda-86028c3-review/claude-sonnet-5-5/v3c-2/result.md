# Final review: `4f69810..86028c3` (one commit)

**Inputs.** I took the claimed cases from the commit message alone, because I had no separate task statement. The change has no code: it edits a skill, package README and versions, and a research directory. The drift script was not run, because it parses members and there are none. Each item below uses the no-code analogue. I loaded `final-review` and `english-developer-style`. I did not load `test-authoring` or any authoring skill, since none applies to this change.

## Item 1: comments consistent with the code and with each other

Analogue: statements one file makes about another, and counts and cross-references.

- **Stale quote of the rule.** `research/.../pgjdbc-4367-breaks/README.md` (line 7) and `pgjdbc-4392-no-break/README.md` (line 5) quote the rule as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 is headed "A break leads the description unless the next release from the target branch is a major." The cases cite a heading that does not exist, and "§2" also does not name the section (it sits under §2, pull request description). Substantive.
- **§4 rule 5 contradicts the new paragraph.** SKILL.md:637 says the description under rule 5 is shaped "as §2's commit body", and line 310 says it "takes the body's shape instead". Line 257 now says the lead stays and the body opens with breaks, then the problem. The lead is described as slot 3's break lines, but a commit body carries those under `User-visible:` in slot 4. Line 259 does not say whether the copied body repeats the breaks or moves them, and the label is what lines 257–258 say R4 and R5 search for. Rule 5 itself was not touched. Substantive.
- **Unchanged "breaks first" sentences.**
  - The slot 3 cell (line 198) now says "ahead of slot 1".
  - Line 226 still says "Breaks come first" in slot 3 with no qualification.
  - The checklist "Caller" line (845) still says "breaks first" under "User-visible changes".
  - Line 253 says slot 3 "keeps the other outcomes".
  - Read alone, the Caller line and line 226 describe a different layout from line 253 for a non-major release. Taste. I prefer a clause "(or in the lead, §2)" on those two.
- **Counts and versions.** `1.5.0` is consistent across `apm.yml`, the package `apm.yml` and `marketplace.json`. The tree ids in the `skill-tree` files match `HEAD:` and `HEAD~1:` for the rule and baseline runs. The word counts in both case READMEs match `wc -w`. None.
- **Narration.** No `now` or `no longer` in the new SKILL text. None.

## Item 2: claimed cases covered

Claims from the commit message, each against its detection:

| Claim | Where it is checked |
| --- | --- |
| Lead with breaks in a patch release | 4367 check 1, six runs |
| Result-shape change is a break | check 2 |
| Failure extended to later statements is a break | check 3 |
| Control grows no section | 4392 checks 1–2, four runs |
| "Without the rule both models put Why first" | the two baseline results |
| "Three of four move the extended failure out of Scope" | table matches (`opus/result-2.md` fails check 3) |
| Release read from version file, milestone, or name | **not covered** |
| Release unknown → breaks lead | **not covered** |
| Major release → breaks stay first in slot 3 | **not covered** |
| Commit body keeps problem first | **not covered** |
| Squash copies the description, lead stays | **not covered** |

- **Uncovered branches.** Both prompts give `gradle.properties` as 42.7.14, so only the "patch from version file" branch runs. The other branches of the rule are claimed but have no case. Substantive: add a major-release case, or state in the commit that the branches were not run.
- **Effort setting.** The commit says "Opus and Haiku (effort high)". The README says Haiku ran at `high` and Opus at the session's default. One of them is wrong. Substantive, since this is a claim about the evidence.
- **Command lines.** The `git archive <rev> agent-packages/...` recipe in the 4367 README (Running it) has no script or CI job that runs it. It is a recipe for reproducing the runs, and the placeholder `<rev>` and the prompt text are not checked here, so I did not run it. The `./gradlew` lines are inside the prompts, as input to the model, not instructions to the reader. Taste.
- **Hunks against claims.** Every hunk is claimed by a sentence of the commit message: the SKILL.md rule, the checklist, the package README, the version bumps, the research README, and the cases. None.

## Item 3: boundaries, partitions, negative control

Analogue: the genres, modes and situations claimed, plus the control arm of each trial.

- **Control arm.** The control (4392) was run only with the rule and was not run on `origin/main`. It does not show the pre-rule output, so "the control grows no section" compares only against the draft's 209 words. Taste.
- **Partitions with no evidence.** Major release, unknown release, a maintenance-branch name, a milestone, and a `BREAKING CHANGE:` trailer (SKILL.md:247) each have no run. For the unknown-release branch the text says "the breaks lead". That means a no-break change on an unknown release still gets no lead, which is covered only for the patch case. See Item 2.
- **Pre-existing state.** The change adds text to a skill, and the existing installed copies are not a concern for this check. None.
- **Table of added instructions** (one row per instruction):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Breaks lead the description unless the next release is a major | a description of a change in a major release | `Breaking changes` stays in slot 3, first | Ended: "Where the next release is a major, the breaks stay first in slot 3." Not a finding |
| Open with a short paragraph saying which code breaks | one break that the heading line already names | a paragraph repeating the line below it | "at most a short paragraph" bounds it but does not drop it. Taste: add "only where a break line does not name the code" |
| Read the release from the version file, milestone, or branch name | a repository whose description is copied into a squash commit | reads the version file and tags it, then writes the lead | Not addressed, and rule 5 conflicts (Item 1). Substantive, filed there |
| A failure extended to inputs that worked before is a break | an input the old release failed in the same way | nothing, since it did not work before | Ended by "inputs that worked before" |
| Breaks as the first `User-visible:` lines of the commit body | a change with no break | no `User-visible:` break lines | Ended: "A change with no break has neither the lead nor an empty heading" |

## Item 3a: level, placement, environment

Analogue: which file each rule lives in, and the registration entries.

- The rule sits in SKILL.md §2 beside slot 3, and the checklist is updated. The package README and the three version entries are updated. The cases follow the existing `cases/` layout, which the research README now lists. I did not run the repository's lint gate, and the markdown linters (`super-linter`) were not run. Not checked.

## Item 4: names by content, not position

None. The new headings, case names and cross-references (`§4 rule 5`, `slot 3`) are by content. One reference points at a position: "(below)" in the slot 3 cell (SKILL.md:198) for the major-release rule. Taste: name the paragraph ("the rule below" is fine; "(§2, the break rule)" is better).

## Item 5: failure report

Analogue: a rule's detection, and whether the checklist reaches it. The 4367 checks 1–3 detect the rule. The checklist "Breaks" line (SKILL.md:849) covers the lead, but it asks "slot 3 keep only the other outcomes" and so conflicts with the "Caller" line (Item 1). Check 5 ("stated once") detects a duplicate. None beyond Item 1.

## Item 6: what the writer says it verified

The red and green runs are stated: baselines fail checks 1–3, runs pass checks 1–2 in all four, and check 3 in three of four. The commit states that Opus run 2 left `grant insert` in Scope. The control has no baseline run (Item 3). The bad case where the added item is noise is 4392, and growth is reported as words. Verified as stated.

## Item 7: siblings

- The package README, `apm.yml`, `marketplace.json` and the checklist are all updated. No sentence counts the slots or rules as before. `docs-page-authoring` and the instruction file mention the skill only by name. None.
- Rule 5 (§4) is the sibling that was missed. See Item 1.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| Case READMEs quote a rule heading that does not exist | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`; `cases/pgjdbc-4392-no-break/README.md:5` | Quote SKILL.md:234 exactly |
| §4 rule 5 and line 310 say the copied description is shaped as the commit body, while §2 says the lead stays; it is unclear if the lead repeats or moves the `User-visible:` breaks | Substantive | SKILL.md:257–260, 310, 637 | Reconcile in rule 5, and say whether the break lines appear once |
| Major, unknown-release, milestone, branch-name and trailer branches, and the commit-body order, have no case | Substantive | commit message; `cases/` | Add a major-release case, or state in the commit that these were not run |
| Effort level: commit says Opus ran at "high", README says session default | Substantive | commit message; 4367 README (Running it) | Make them agree |
| "Breaks first" sentences in slot 3 text and checklist unchanged | Taste | SKILL.md:226, 845 | Add "(or in the lead, §2)" |
| Control not run on `origin/main` | Taste | 4392 README | Add one baseline run, or say none was made |
| "(below)" refers by position | Taste | SKILL.md:198 | Name the rule |

**Not checked.** I did not run the repository's lint gate or the case recipes, and I did not run `test-authoring`'s rules because there are no tests. The wording review (`english-developer-style`) was not done beyond where a sentence reads wrongly.
