# Final review: `4f69810..86028c3`, one commit, "lead the description with breaks unless the next release is a major"

**Inputs.** No separate task statement was handed over, so item 2 takes its claimed cases from the commit message alone. The change is all Markdown, JSON and YAML: a skill, a package README, two version files, a marketplace entry and a research directory. There is no code, so I did not run `comment-drift.py` (it parses members), and I filled the form through the no-code analogues of §2a. I loaded `english-developer-style` from the given directory. `apm-authoring` and `docs-page-authoring` are not among the three skills I was allowed to load, so I did not apply them. The previous report: none exists.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Findings:

- `SKILL.md:310` says "Under §4 rule 5 the description is the commit body and takes the body's shape instead." That line is unchanged.
- `SKILL.md:637` (rule 5) says to "shape it as §2's commit body". The commit-body section keeps problem first (`:257`).
- The new text at `:259–260` and `:86` says that under rule 5 "the lead stays" and the body "opens with its breaks and then its problem".
- So three places answer the same question differently: where rule 5 copies the description into the commit, does the problem or the break come first?
- Rule 5 was not edited.

Other statements checked:

- The version `1.5.0` is the same in the package `apm.yml`, root `apm.yml` and `marketplace.json`.
- The README bullet matches the rule.
- The §8 checklist items point to existing sections (§2, §4 rule 5, §7).
- The slot-3 table cell, `:196–198` and `:255` agree that breaks stay first in slot 3 when the next release is a major.
- Both case READMEs quote the rule under wording the skill no longer has:
  - `pgjdbc-4367-breaks/README.md:6` cites "SKILL.md §2, 'A break leads the description where the next release from the target branch promises compatibility'".
  - `pgjdbc-4392-no-break/README.md:5` quotes the same.
  - The skill's sentence is "A break leads the description unless the next release from the target branch is a major."
  - The case README quotes the rule the runs tested before the rewording.
- Narration words (`now`, `no longer`): none in the added skill text.

## Item 2: claimed cases covered

I took the claims from the commit message and checked the results in the case directories.

| Claim | Evidence | Verdict |
| --- | --- | --- |
| Without the rule, both models put Why first and left both breaks in place. | `opus/baseline` and `haiku/baseline` are listed as failing checks 1–3. | Holds. |
| With the rule, all four runs lead with the breaks and mark the result shape. | I grepped the headings and `getUpdateCount()` lines in all four result files. | Holds. |
| Three of four move the extended failure out of Scope; one Opus run left it there. | `opus/result-2.md:35` keeps `grant insert` in Scope. The others list it under Breaking changes. | Holds. |
| The control grows no section in any run. | The `pgjdbc-4392-no-break` README says all four pass. I did not open those results beyond a grep for "breaking" and "compatib", which found nothing. | Holds on that grep. |
| `skill-tree` ids name the skill that was run. | HEAD's skill tree is `4798053…`, which matches every with-rule `skill-tree`. The parent's `1f020ce…` matches both baselines. | Holds. |
| Haiku and Opus ran at effort high. | The commit message says "Opus and Haiku (effort high)". The README (`:41`) says "Haiku at effort `high`; Opus at the session's default". | **Finding, substantive.** The two disagree. |

Hunks no sentence claims: none. The version bumps, the README bullet and the research index each belong to the commit message. Commands the change tells someone to run: the `git archive …` line in the 4367 README. No script or CI job runs it, and the line is a recipe for reproducing a research case, not a promise of an outcome. I did not run it.

## Item 3: boundaries, partitions, and the negative control

The rule has three arms, and only one is tested.

| Arm | Evidence |
| --- | --- |
| A break, patch release | Tested: `pgjdbc-4367-breaks`. |
| No break, patch release | Tested: `pgjdbc-4392-no-break`. |
| A break, next release is a major | Not tested. The sentence "the breaks stay first in slot 3" has no run. |
| A break, nothing says which release | Not tested. The prompts name the target, so the "breaks lead where nothing says" arm is unexercised. |
| Release read from a version file, milestone or maintenance-branch name | Not tested. Only pgjdbc `master` is used. |

The negative control `pgjdbc-4392-no-break` has no run on the base commit. A control should stay green there. As written, it shows the rule adds nothing to a no-break change. It does not show the baseline would have behaved the same. Both gaps are in the commit message's scope, since it names only two cases. Label: substantive for the major-release arm, taste for the rest.

Pre-existing state and limits: not applicable to a skill. Models are n=1 or n=2 per cell, and the README says so ("most of the time and not always").

**Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| A break leads the description unless the next release is a major. | The change targets a major release. | Breaks first in slot 3, Why before them. | Ended by the skill's own text: "Where the next release is a major, the breaks stay first in slot 3." Listed below the table as not a finding. |
| Open with a `Breaking changes` heading and "at most a short paragraph that says which code breaks". | A description with no template and four paragraphs, which `:300–302` says is prose without headings. | A heading in a short description. | `:252` says "where the description has headings", so the skill ends it. Not a finding. |
| A failure extended to inputs that worked before is a break. | A failure that already hit the same inputs in the same way. | Nothing. | `:238` says "for those inputs". Not a finding. |
| Read the next release from a version file, milestone or branch name. | A repository with none of these, such as a docs-only repository. | The breaks lead. | `:249` handles it: "Where nothing says which release it is, the breaks lead". Not a finding. |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." | A repository with release-please on a patch branch. | The agent cannot tell whether the trailer makes the lead unnecessary (the release becomes a major) or only adds a trailer to a leading description. | None. **Finding, substantive**, with the clause below. |
| The commit body keeps problem first, with the breaks as the first `User-visible:` lines. | A description that rule 5 copies into the commit. | Two orders. | None. This is the contradiction filed under item 1. |

## Item 3a: level, placement, and the environment

- Files sit beside the siblings: the package README, the research README and `research/…/cases/` under the existing research directory.
- Two lines in `research/change-description-authoring/README.md` register the new directory.
- The index and marketplace entries are in the place the repository gates check.
- I did not run the repository's gate.
- The new `SKILL.md` lines I checked are under 120 columns. The 120-column limit applies to the case READMEs, and no line in them or in the package README exceeds it.
- The long table rows at `SKILL.md:45–49` and `:81–84` predate this change.
- Level: the new rule is the platform-specific knowledge this skill is for (release-version signals, merge-model effects), not tutorial text.

## Item 4: names by content, not by position

None found. The cases are named by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). The results are `result` and `result-2`, an ordinal, but they are run files, not names the text refers to. One reference is positional: "(below)" at `:198`, which points at the paragraph under the table. Taste.

## Item 5: the failure report

The detection for each rule is the case README's check list. Checks 1–3 detect the rule under test, and 4–6 guard against collateral loss. Check 1 ("opens before the Why slot, after at most a short paragraph") is observable from the result. The skill's §8 gives the same check to the writer ("does the description open with the break lines"). None.

## Item 6: what the writer says it verified

The commit message states the with-rule and baseline runs, and the case READMEs tabulate each result. It also says that two earlier drafts of the rule were run on Opus and are summarized but not stored. That is stated honestly; the stored runs are only for the committed version. I did not rerun any model and did not run the suite.

## Item 7: siblings of the change

- The set is the package's rule list and the places that list it: README, `apm.yml` ×2, `marketplace.json` and the checklist in §8. All were updated.
- No sentence counting the old size of the set remains. A grep for "breaks first" and "opens with" found the lines at `:112`, `:198`, `:226`, `:543` and `:845`; they agree with the new rule.
- `:543` ("Breaking changes are marked in place and sorted first within their category") is for the changelog entry and is not in conflict.
- The changelog-entry and title sections carry no lead, which is intentional (the commit message does not claim them).
- The `.claude/` and `.agents/` copies of skills listed in the repository are other skills; none embeds this one.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Three places disagree on what a description copied into the commit body opens with: `:310` ("takes the body's shape instead") and `:637` ("shape it as §2's commit body") say problem first, while `:259–260` and `:86` say the lead stays and the body opens with its breaks. | substantive | `SKILL.md:86, 259, 310, 637` | Pick one order for the copied-in description and state it once. Edit `:310` and rule 5 (`:637`) to match, or drop the "lead stays" sentence. |
| Both case READMEs quote the rule in wording the skill no longer has ("promises compatibility", "SKILL.md §2"). | substantive | `pgjdbc-4367-breaks/README.md:6`, `pgjdbc-4392-no-break/README.md:5` | Quote the committed heading and name the section it sits in, or say the runs tested an earlier wording. |
| The `BREAKING CHANGE:` / `!` sentence does not say whether the trailer replaces the lead, adds to it, or marks the release as a major. | substantive | `SKILL.md:247–248` | Add the clause: the trailer is written in every case; a lead is still owed unless the target's next release is a major. |
| The commit message says effort high for both models; the README says Opus ran at the session default. | substantive | commit message; `pgjdbc-4367-breaks/README.md:41` | Correct the commit message, or the README if Opus did run at high. |
| The arms "next release is a major" and "nothing says which release" have no run, and the negative control has no baseline run. | substantive | `cases/*/README.md` | Add a run for the major arm, or add a sentence to the README that those arms are untested. Run `pgjdbc-4392-no-break` on the base skill tree. |
| "Six slots, in order" now has slot 3 ahead of slot 1; "(below)" is positional. | taste | `SKILL.md:192, 198` | I would add "in order, except that slot 3's breaks lead" and name the paragraph. Expect this to be declined without discussion. |

I did not do a style-only pass over the prose, did not run the suite, the repository's gates or any model, and did not open the 4392 result files beyond the grep for "breaking" and "compatib".
