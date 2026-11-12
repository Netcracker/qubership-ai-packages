# Final review: `4f69810..HEAD` (86028c3, one commit)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message. Under §2a this is a change with no code: a skill, a package README, a manifest and marketplace entry, and a research directory. The drift script was not run, because it parses code members and nothing here has any. I loaded `english-developer-style` from the given skills directory. `apm-authoring` and `docs-page-authoring` were not among the three skills I was told to load, so the §2a authoring analogues are applied from the rules the review text states. There is no previous report.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files and documents)

- **Stale quoted rule name (substantive).**
  - `cases/pgjdbc-4367-breaks/README.md:7` quotes the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - `cases/pgjdbc-4392-no-break/README.md:5` quotes it the same way.
  - The committed SKILL.md:234 reads "A break leads the description unless the next release from the target branch is a major".
  - Neither heading exists any more, so a reader who searches for the quoted text finds nothing.
  - The 4367 README also cites "SKILL.md §2" with no file path.
- **§4 rule 5 contradicts the new lead (substantive).**
  - SKILL.md:637 says that under a squash or merge commit the description is "the body of the commit… shape it as §2's commit body".
  - SKILL.md:310 says the description "takes the body's shape instead".
  - The new text at SKILL.md:257-260 says "the lead stays" in that body, so the body opens with breaks and then the problem.
  - Line 257 says "the commit body keeps its order, problem first". Line 260 says the same body opens with its breaks, and line 86 says "Slot 1 opens the body".
  - Rule 5 and line 310 were not amended to carry the exception, and a reader following rule 5 gets the opposite order.
  - Line 310 also says the headings in the *After* example "stand as prose" without a template. The `Breaking changes` heading rule (line 252, "where the description has headings") is consistent with that.
- **"The trailer decides" is circular (substantive).**
  - SKILL.md:247 says that where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!`, "the trailer decides, and it is written whatever the description does".
  - It does not say what the trailer decides. If it decides that the release is a major, the lead should be dropped. Yet the same change writes the trailer for the very breaks the lead exists to flag in a patch release.
  - The reader cannot tell whether the lead stays or goes.
- **The commit message's run settings disagree with the case README (taste).**
  - The commit message says "Opus and Haiku (effort high)".
  - The 4367 README line 33 says "Haiku ran at effort `high`; Opus at the session's default".
  - The 4392 README line 22 says only Haiku ran at `high`.
- **Narration of the change.** None found, apart from the case READMEs, which are history by design.
- **Checked and consistent:** the §5 and §7 cross-references, "slot 3 / slot 4" numbering between the pull request table and the commit body, the version `1.5.0` in `apm.yml` (package and root), and the marketplace entry. The research README tree line for `cases/` is accurate.

## Item 2: claimed cases covered (analogue: sections that handle the claims, and commands to run)

| Claimed case | Evidence |
| --- | --- |
| Description leads with breaks in a non-major release | `pgjdbc-4367-breaks` check 1. All four runs with the rule lead, and I confirmed this from the `## Breaking changes` heading at line 1 or 3 of each result. |
| Result-shape change marked | Check 2. All four runs pass it. |
| Failure extended to later statements moves out of Scope | Check 3. `opus/result-2.md:35` leaves it in Scope, as the commit message and README say (3 of 4). |
| Fix is not a break | Check 4, which is stated in the README table. |
| Break read from version file, milestone, or branch name | Only the version file is exercised, and the prompt hands it over as `gradle.properties` giving 42.7.14. Milestone and branch-name arms have no case. |
| Lead stays when squash copies the description into the commit | No case. The prompt says the merge model is "plain 37" commits, so §4 rule 5 does not fire. |
| Commit body keeps problem first, with breaks as first `User-visible:` lines | No case. Only pull request descriptions were drafted. |
| Where the next release is a major, breaks stay first in slot 3 | No case. |
| Where nothing says which release it is, breaks lead | No case. |
| A change with no break grows no section | `pgjdbc-4392-no-break`, all four runs. |
| Result counts in the commit message | Counts match the README table: 3 of 4 move the failure out of Scope, and both baselines put Why first. |
| Commands the change tells someone to run | `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring` and `agent-packages/english-us-developer-style`. The path exists. The command is not in a script or CI job (`none`), but it is only the recipe for the research case. |

Hunk-to-claim reading: every hunk belongs to a sentence of the commit message. The version bumps, the marketplace entry, the package README bullet, the research README note, and the case files are all covered.

Substantive request: add cases, or say in the README that they are unrun, for the major-release arm, the unknown-release arm, and the squash-copied body. The README of 4367 calls its test the rule, but it tests one arm of it.

## Item 3: boundaries, partitions, and the negative control

- **Control arm on the base commit (taste).** `pgjdbc-4392-no-break` was run with the new skill only, with no `origin/main` baseline, so it does not show that the control also stays no-section without the rule. Since the rule adds the section rather than removing it, this is minor.
- **Missing partitions (substantive).** The target-release input is always a 42.7.x patch release. The partitions the rule names are a major target, no version information, and a maintenance branch name. These are the "nothing says which release" and "major" arms, and none has a run, which is the substantive part of Item 2.
- **Pre-existing state.** A skill reinstalled over an older version carries no state, so there is nothing to check. A user with an old `change-description-authoring` pinned at `1.4.0` just keeps the old behavior until `apm.lock.yaml` moves. The lock file has no entry for this package, so nothing is out of date there.

Table of added instructions (skill):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release is a major" | A one-sentence description of a breaking change in a repository with a `-SNAPSHOT` major | A leading `Breaking changes` heading, which §7 would drop for a short description | Ended: "A change with no break has neither the lead nor an empty heading" and "Where the next release is a major, the breaks stay first in slot 3". The heading rule applies only "where the description has headings". |
| "A failure the change extends to inputs that worked before is a break… not in the Scope slot" | A change that makes a failure fire on inputs that previously failed with the same error | Nothing extra | Ended by "to inputs that worked before". |
| "Where nothing says which release it is, the breaks lead" | A non-code change (docs-only) with a break-like statement | A lead for something the rule defines as code that "works on the released version" | Ended by the definition of break. |
| Commit body "keeps its order… the lead stays when §4 rule 5 applies" | A squash where the description is a 1-line fix | A body that opens with breaks | Ended by "A change with no break has neither". Conflicts with §4 rule 5 as filed under Item 1. |
| Checklist line "Breaks:" | A change that breaks nothing | A pass with no output | Ended: "Where nothing breaks, is there no lead and no empty heading". |

## Item 3a: level, placement, and the environment

- The rule lives in `SKILL.md` §2 beside the slot table, which is its natural place. The package README and the checklist (§8) both carry it.
- Registration entries are the ones named: `apm.yml` (package and root) and `marketplace.json`, all at `1.5.0`. I did not run the repository's own gate, so I did not check that the three versions agree beyond reading them.
- The `cases/` directory is new, and the research README lists it. The cases follow the stated convention of one README per case with `<model>/result*.md` and `skill-tree`.
- Skill trees: the four with-rule 4367 files and the 4392 files share a tree id, and both baselines share a different one. That fits the README, though the baseline tree is not checkable here without the commit.
- A sentence in the skill that fits any tutorial: none found.

## Item 4: names by content, not by position

- Result files are `result.md` and `result-2.md`, an ordinal name. They differ by run, not by content (taste; the README table does name each by path).
- "The first, … the second" at 4367 README lines 49-52 names rule drafts by ordinal. Those drafts are not stored, so the reader cannot find them. The text already says they are summarized and not stored, so this is churn.
- `case 3` and `check 1 to 3` in the README refer to a numbered list of checks. The checks are named in bold, so no finding.

## Item 5: the failure report

Every rule has a detectable check in the README (Lead, Result shape, `grant insert`, Fix out, Once, Literals). Check 5, "stated once", is evaluated by reading, not by a script. A rule such as "the lead is under 'at most a short paragraph'" has no stated length, so a run cannot fail it (taste).

## Item 6: what the writer says it verified

The commit message names the runs, and the README records one run on `origin/main` per model as the red case. The negative control is named. This is enough for a skill change. Gaps:

- The rule was reworded after review ("reworded after review"), and the 4367 README says the committed wording moved `grant insert` in one of two Opus runs. The runs match the committed wording, so no re-run is owed.
- `skill-tree` ids are present, so the run skill is identifiable.
- The Haiku `Generated with Claude Code` footers are noted as not asked for.

## Item 7: siblings of the change

- **Package README:** the new bullet is present. It says "the commit body keeps them first in its outcome slot", consistent with line 257.
- **Instruction file** (`.apm/instructions/change-description-authoring.instructions.md`): a trigger only, and no rule needs mirroring.
- **Other skills that cite or route to the artifact** (`docs-page-authoring`, `english-developer-style` copies under `.claude`, `.agents`, `.cursor`): none restates the order "Why first" or "problem first" (`git grep` found none outside the skill), so no sibling carries the old order.
- **Set size:** "Six slots" and "Five slots" are unchanged because no slot was added. A Breaking changes lead is described as a lead, not a slot, which is consistent.
- **Remedy check:** the symptom "break leads in a non-major release" has paths for the pull request description and the commit body. The changelog entry is the third artifact, and it already marks breaks first (§3, line 543), so it needs nothing here.
- **Other consumers of the same decision:** the checklist line at §8 has it. Line 86 has it. §4 rule 5 does not (see Item 1).

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule heading that no longer exists | substantive | `research/.../pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:5` | Quote the committed heading, "A break leads the description unless the next release from the target branch is a major", and name the file. |
| §4 rule 5 and line 310 say the squashed description takes the commit body's shape, while lines 257-260 say the lead stays | substantive | `SKILL.md:310`, `:637`, `:257-260`, `:86` | State the exception in rule 5 and line 310, or reword lines 257-260 to say what order the body has. |
| "The trailer decides, and it is written whatever the description does" does not say what it decides | substantive | `SKILL.md:247` | Say whether a release tool's major bump on a trailer makes the lead unnecessary or still required. |
| No case for the major arm, the unknown-release arm, a milestone or branch-name source, the squash-copied body, or the commit body | substantive | `cases/pgjdbc-4367-breaks/README.md` | Add a run for the major and unknown arms, or state in the README that they are untested. |
| Commit message says Opus ran at effort high, but the README says the session's default | taste | commit message; `cases/pgjdbc-4367-breaks/README.md:33` | Correct whichever is wrong. |
| Control has no `origin/main` baseline run | taste | `cases/pgjdbc-4392-no-break/README.md` | Optional: add one run. |
| "At most a short paragraph" has no measurable bound | taste | `SKILL.md:253` | Optional: name a length. |

The review did not run the suite or the repository's lint and gate, did not re-run any model on the cases, and did not do a style pass over the prose beyond the sentences that read wrongly.
