# Final review of `4f69810..HEAD` (86028c3, `feat(change-description-authoring): lead the description with breaks unless the next release is a major`)

This change has no code: it changes a skill, a package README, version pins, and research regression cases. I filled the form with the §2a analogues. The drift script ran and printed nothing (exit 0), because no changed file has members it can parse. I had no task statement, so the claimed cases come from the commit message alone, plus the case READMEs. I loaded `english-developer-style` and `test-authoring` from the given directory. `apm-authoring` is not in that directory, so I did not load it. There is no previous report, so there is no carry-over table.

## Item 1: comments consistent with the code and with each other
*Analogue used: what each changed file says about other files and about itself.*

- **Old wording of the rule in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The SKILL.md heading at line 234 reads "…unless the next release from the target branch is a major". `git grep 'promises compatibility'` finds only these two READMEs. Someone searching the skill for the quoted rule finds nothing, and the two conditions differ: "promises compatibility" is not the same test as "is not a major".
- **SKILL.md now disagrees with itself about where breaks go.** The new rule says that in a release that is not a major, slot 3 "keeps the other outcomes" (line 253) and the breaks move ahead of Why. Three places were not updated:
  - Line 226 still says "Breaks come first" in slot 3, with no exception.
  - The checklist item "Caller" (lines 844-846) asks for "one line per distinct outcome under 'User-visible changes', breaks first". In a non-major release, the new "Breaks" item two lines below requires the opposite.
  - Line 128 says the `User-visible:` and `Not changed:` labels "sit after slot 3". The new paragraph (lines 259-260) says that under §4 rule 5 the body "opens with its breaks and then its problem".
- **Line 260 is ambiguous for §4 rule 5.** It does not say how a description-as-body labels its leading breaks. Line 252 allows a `Breaking changes` heading only "where the description has headings", and the Headings checklist item (line 857) bans headings under rule 5. That leaves two readings: unlabeled lines at the top, or a second `User-visible:` block ahead of slot 1. The first loses the label that line 258 says "R4 and R5 search for". The second contradicts line 128.
- **Commit message and case README disagree on run settings.** The commit message says "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says "Haiku ran at effort `high`; Opus at the session's default."
- **Checked and consistent:**
  - All six `skill-tree` files match `git rev-parse <rev>:<skill dir>`: `4798053…` is HEAD and `1f020ce…` is 4f69810.
  - The word counts in both READMEs match `wc -w` for all ten results.
  - "All three Haiku results end with a `Generated with Claude Code` line" is true.
  - Each pass/fail cell in the 4367 table matches my reading of the results.
  - §4 rule 5, §5 (`BREAKING CHANGE:` row) and §7 exist and say what the new text cites them for.
  - The marketplace.json, apm.yml and package apm.yml descriptions are unchanged and still agree with each other.
  - No new sentence narrates the change.

## Item 2: claimed cases covered
*Analogue used: each claim in the commit message, matched to the section that handles it and the case that tests it.*

| Claim | Section | Case |
| --- | --- | --- |
| Breaks lead when the next release is not a major | SKILL.md 234-255 | `pgjdbc-4367-breaks` check 1 |
| Result shape counts as a break | 235-238 | check 2 |
| A failure extended to more inputs counts as a break, not Scope | 238-240 | check 3 (passes 3 of 4) |
| A fix is not a break | 241-242 | check 4 |
| Release read from version file, milestone, or name | 245-247 | only the version file plus a tag; the milestone and branch-name readings are not exercised |
| Breaks lead where nothing says which release it is | 248-250 | **none** |
| Major release: breaks stay first in slot 3 | 254-255 | **none** |
| `BREAKING CHANGE:`/`!` tool: the trailer decides | 247-248 | **none** |
| Commit body keeps problem first, breaks first among `User-visible:` | 257-258 | **none** (both prompts ask for a PR description only) |
| Squash copies description: the lead stays | 258-260 | **none** (both prompts give "squash 3 plain 37", one commit, `* subject` bodies, so rule 5 does not apply) |
| No break means no section | 255 | `pgjdbc-4392-no-break` checks 1-2 |

- **Commands in the changed files.**
  - `git archive <rev> agent-packages/…/change-description-authoring` in `pgjdbc-4367-breaks/README.md:30`: I ran it at HEAD and it lists `SKILL.md` and `references/merge-model.md`. It writes a tar to stdout, so "copied out of the checkout" needs `| tar -x`. Nothing in the repository runs it; the sibling cases have `run-case.sh`. This is taste.
  - The `./gradlew` lines are inside model input and output, not instructions to a reader.
- **Hunks with no claim.** None. The three version bumps follow the same pattern as 4f69810. The research README hunk is claimed by "Two regression cases under research/…/cases".

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the release kinds and merge models the rule names are the partitions.*

- The rule names three release partitions: not a major, unknown, and major (plus the release-tool trailer). It names two destinations: a description, and a description that becomes the commit body. Both cases cover one cell: not a major, a PR description, and no rule 5. Five claimed partitions have no evidence, listed as **none** in the item 2 table. The "major" arm is the one most likely to regress silently: a drafter that always leads with breaks would pass both existing cases.
- **Negative control.** `pgjdbc-4392-no-break` is present and passes on all four runs. It has no run on the base, but the base has no rule that could produce a lead, so none is owed.
- **Pre-existing state.** Not applicable to a skill text. Installed copies update through the version bump.

## Item 3a: level, placement, and the environment
*Analogue used: file placement, sibling layout, and the repository gate.*

- **Run directories are named `opus/` and `haiku/`.** The sibling cases (`research/problem-report-authoring/cases/*/`, `research/test-authoring/cases/*/`) name them by model id (`claude-opus-5-5`, `claude-haiku-4-5`, `claude-sonnet-5`). The new names do not record the model version. It appears only in the cost paragraph, which says "Opus 5.5" and "Haiku 5.5".
- **The style skill is not pinned.** `english-developer-style` is read from the working tree with no revision or tree id recorded, so a later change to it cannot be told apart in a rerun. This is taste.
- **Lint exclusions.** I checked the super-linter `FILTER_REGEX_EXCLUDE`: every `result*.md` and `prompt.md` is excluded, and the two case READMEs are linted, as for the siblings.
- **Gates not run.** `make check` and `make test` go through `uvx`/`uv` and need the network, so I did not run them.

## Item 4: names by content, not by position
None. Case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and check names ("Lead", "Result shape is a break", …) are by content. The numbers on the checks are labels that the table repeats next to their names.

## Item 5: the failure report
*Analogue used: does the checklist reach the rule, and does the detection detect the rule?*

The new "Breaks" checklist item (lines 849-852) reaches the non-major and unknown arms and the no-break arm. It does not reach the major arm or the commit-body order. The case checks detect the rule itself (position before Why, and membership in the lead), not a weaker property.

## Item 6: what the writer says it verified
Both kinds of evidence are present:
- The rule fails the bad case: both baseline runs on 4f69810 fail checks 1-3.
- The rule passes the good case: four rule runs, with one Opus run failing check 3, stated as such.
- The two earlier drafts are summarized and not stored, which the commit message says.

The cited exemplars (pgjdbc#4367 and the maintainer's rewrite comment, and #4392) could not be fetched: there is no network. The claim that the maintainer put breaks first "because `master` ships 42.7.x patch releases" is unverified by this review.

## Item 7: siblings of the change
- The places that list the package (marketplace.json, root apm.yml, package apm.yml) all moved to 1.5.0. The cross-references in other packages name the skill's scope, which is unchanged.
- The package README gained a bullet for the rule.
- The research README added `cases/` to its file list.
- `references/merge-model.md:62-63` is a suggested CONTRIBUTING line for squash with "title and description". It still lists the body as "problem, symptom, approach…". Under the new line 260, that body opens with breaks in a non-major release. This is taste, because the line lists what goes in the body rather than the order.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote an old wording of the rule ("promises compatibility") that is not in SKILL.md | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the heading as committed: "…unless the next release from the target branch is a major". |
| The "Caller" checklist item and the slot 3 prose still put breaks first in "User-visible changes" with no exception, which contradicts the lead rule | Substantive | SKILL.md:226, 844-846 | Add "or ahead of Why, unless the next release is a major" to both, or point them at the Breaks item. |
| Under §4 rule 5, the label and placement of the leading break lines are unspecified, and they conflict with line 128 ("sit after slot 3") | Substantive | SKILL.md:128, 252-260 | Say which label the body's leading breaks carry and amend line 128 to allow it. |
| Commit message says Opus ran at effort high; the case README says the session default | Substantive | commit message ¶3; `pgjdbc-4367-breaks/README.md:33` | Make one of them match what was run. |
| Five claimed partitions have no case: unknown release, major release, release-tool trailer, commit-body order, description-as-body (rule 5) | Substantive | SKILL.md:247-260; `research/…/cases/` | At least a major-release case (breaks stay in slot 3) and a rule-5 squash case, or say in the case README that these arms are untested. |
| Run directories `opus/`, `haiku/` drop the model version that sibling cases record as the directory name | Substantive | `research/change-description-authoring/cases/*/` | Rename to `claude-opus-5-5/` and `claude-haiku-5-5/`, as in `problem-report-authoring/cases`. |
| The `git archive` recipe writes a tar to stdout and nothing scripts the run | Taste | `pgjdbc-4367-breaks/README.md:30` | Add `\| tar -x -C <dir>`, or a `run-case.sh` like the siblings. |
| The style skill read by the drafter is not pinned by revision or tree id | Taste | `pgjdbc-4367-breaks/README.md:30-32` | Record its tree id next to `skill-tree`. |
| The merge-model CONTRIBUTING line lists the squash body without the break lead | Taste | `references/merge-model.md:62-63` | Optional: "breaks, where the release is not a major; problem, symptom, approach…". |

This review did not run `make check` or `make test`, which need the network. It did not fetch the cited pgjdbc pull requests or comment, did not rerun any model case, did not verify the prompt's repository facts (the `gradle.properties` version, the release tag, the merge-model count), and did not do a style-only pass over the prose.
