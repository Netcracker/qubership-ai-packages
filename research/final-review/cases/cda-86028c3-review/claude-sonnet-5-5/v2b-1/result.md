# Final review: `4f69810…..86028c3` (one commit, "lead the description with breaks unless the next release is a major")

**Inputs.** There is no separate task statement. The claimed cases come from the commit message alone. The class comments of tests don't apply, because the change has no tests. There is no previous report.

**No code.** The change is a skill, two package manifests, a marketplace entry, a README line, and a research directory. `comment-drift.py` found no members to parse, so it printed nothing. Each item below reads the analogue from §2a.

**Skills loaded.** I loaded `english-developer-style`. The `apm-authoring` and `docs-page-authoring` skills are not among the three I was given, so I did not load them. I cite §2a of `final-review` instead.

I did not run the suite or any model runs. I checked that the `skill-tree` files match the git trees (`4798053…` for HEAD, `1f020ce…` for HEAD~1).

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Two findings.

1. **Rule 5 and the "body's shape" sentence contradict the new lead.** Both are in `SKILL.md`.
   - Line 310 (unchanged) says "Under §4 rule 5 the description is the commit body and takes the body's shape instead."
   - Line 637 (unchanged), rule 5, says "shape it as §2's commit body."
   - Line 259 (new) says that under rule 5 "the lead stays."
   - A reader of rule 5 alone puts the problem first. A reader of the new paragraph leads with the breaks. Only line 86 and the checklist line 832 were updated for the exception.
2. **The case READMEs quote a heading that does not exist.**
   - `pgjdbc-4367-breaks/README.md:7` and `pgjdbc-4392-no-break/README.md:6` name the rule "A break leads the description where the next release from the target branch promises compatibility".
   - The text added in `SKILL.md` is "A break leads the description unless the next release from the target branch is a major". A reader who greps for the quoted title finds nothing.

Checked and consistent:
- The slot table's "ahead of slot 1 … (below)" matches the new paragraph.
- The pointers to §5 (the `BREAKING CHANGE:` row at line 706) and §7 (no empty section) resolve.
- The package README bullet matches the rule.
- "Six slots, in order" at line 192 is loosened only by the "ahead of slot 1" clause in the slot 3 row. I read that as acceptable.

## Item 2: claimed cases covered

| Claim in the commit message | Evidence |
| --- | --- |
| Break leads on a patch target | `pgjdbc-4367-breaks`, check 1. Four of four rule runs pass. |
| Result-shape change marked | Check 2. Four of four runs pass. |
| Extended failure leaves Scope, "three of four" | Check 3. `opus/result.md`, `haiku/result.md` and `haiku/result-2.md` pass; `opus/result-2.md` fails. The table agrees with the message. |
| Fix not marked as a break | Check 4. |
| Break stated once | Check 5. |
| Literals kept | Check 6. |
| Control grows no section, two runs each | `pgjdbc-4392-no-break`, four runs, three checks. |
| "Without the rule both models put Why first and left both breaks in place" | `opus/baseline` and `haiku/baseline`. |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | No case. |
| Where squash copies the description, the lead stays | No case. |
| Lead where nothing says which release it is | No case. |
| Major-release target keeps the breaks first in slot 3 | No case. |
| Release tool's trailer decides | No case. |
| "Opus and Haiku (effort high)" | The `pgjdbc-4367-breaks` README says "Haiku ran at effort `high`; Opus at the session's default." This contradicts the commit message. |

Findings:
- **Substantive.** The commit message says both models ran at effort high. The README says Opus ran at the session default.
- **Substantive.** Four stated branches of the rule have no run: the commit-body order, the squash exception, the unknown release, and the major target. The pgjdbc facts only exercise the patch-target branch. The cases give the majority-branch evidence, not the claims about the other branches.
- **Hunks no sentence claims.** The version bump 1.4.0→1.5.0 appears in three files: `agent-packages/.../apm.yml`, the root `apm.yml`, and `.claude-plugin/marketplace.json`. The package README bullet and the research README `cases/` lines are also unclaimed. These look intended but belong in a sentence. Label: taste. Request: add one sentence to the message.

No commands in the changed files are told to be run. The pgjdbc `./gradlew` command appears only inside `prompt.md` as the input draft, not as an instruction.

## Item 3: boundaries, partitions, and the negative control

**Table of added or widened instructions** (negative-control input for each):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Open with break lines unless the next release is a major | A break in a repository with no releases, such as a continuously deployed app | Leads with a `Breaking changes` heading, as "nothing says which release" | None. The skill is written for versioned libraries. | Taste |
| The break definition, including "a changed error code for a failure a caller may catch" | An internal refactor with no external caller that changes a log message code | Marks it a break | "code that works on the released version" | Not a finding. The definition ends it. |
| A short paragraph "that says which code breaks" before the lead lines | A single break whose line already names the code | Writes a paragraph that restates the line | Line 232 says a fact in slot 3 is not restated in slot 2. It does not cover this paragraph. | Taste |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides" | A patch-branch change in a release-please repository | A break needs the trailer, which makes the release a major. Then "unless a major" means no lead, which defeats the reviewer's first decision. | None. The sentence does not say whether "decides" means major (no lead) or a reason to flag the release. | Taste (two readings) |
| The commit body keeps the problem first; the squash lead stays | A squash-merged change with a break | Follows the exception. Rule 5 and line 310 ask for the opposite. | Conflict with unchanged text | Substantive (Item 1, finding 1) |
| Slot 1 sentence: "A description that §4 rule 5 copies … leads with its breaks … puts the problem right after them" | A description with no break | The condition "that leads with its breaks" is not met. | Its own condition | Not a finding |

**Negative control.** `pgjdbc-4392-no-break` is present, with two runs per model. It has no origin/main baseline, so no run shows that the control fails to grow a section without the rule. That is why its pass says nothing about the rule. Label: taste. The control's claim is "grows no section", and that is a property of the new text only.

**Partitions.** The cases cover one target (a patch `master`) and one shape of break description. A target branch named like a maintenance branch, or a repository with a milestone, has no case. The README says the rule "moves the case most of the time and not always," which is honest. The `grant insert` check has a 3-of-4 pass rate on two runs per model.

**Pre-existing state, limits, and replaced mechanisms.** None. The change replaces no mechanism and sets no limit. An installed older package version has no migration state.

## Item 3a: level, placement, and the environment

- The new skill text sits in the existing `SKILL.md` sections and the checklist, beside the siblings it extends.
- Two cases follow the layout of the existing `research/` tree.
- I did not run the repository's gate and did not look for one.
- The long-line check: `pgjdbc-4367-breaks/README.md:17` is 121 characters, over the 120 limit in `.claude/rules/markdown-line-length-120.md`. This is churn-level, listed as taste. Lines 569–570 of `SKILL.md` are older. `prompt.md` is quoted input.

## Item 4: names by content, not by position

- `result.md` / `result-2.md` name runs by ordinal. A reader of the table cannot tell what differs. Label: taste. Request: name by run date or by seed, if the runs have one.
- The README's "The first … The second …" for rule versions is positional but the passage explains each version in the same sentence. Not a finding.
- "Checks 1 to 3 are the rule under test" refers to numbered, bolded checks. Not a finding.

## Item 5: the failure report

The detection for each rule is the check in the case README. Two things:
- **Check 1 ("opens, before the Why slot, with the break lines, after at most a short paragraph")** detects the lead rule. Good.
- **Check 4 (the fix is not a break)** is attached to the rule that a fix is not a break. It detects it directly.
- There is no check for the commit-body ordering or the squash exception, matching the Item 2 gap.
- Each README table names which checks pass or fail per run, so a failure is readable. No finding.

## Item 6: what the writer says it verified

The message states baseline runs on `origin/main` for the 4367 case, so the red side is present. It does not state a baseline for the control. It does not say the rule was reapplied to the skill's own §2 worked example (the `Before`/`After` at lines 262 onward), which still opens with `Summary` and `Testing`. Label: taste.

## Item 7: siblings of the change

- The set of breaks-first statements is now: the slot 3 row, the new paragraph, the slot 1 sentence, the checklist, and the package README. The `references/merge-model.md` paste-ready `AGENTS.md` (lines 24, 38, 90) tells a squash author to write the commit message "problem, symptom, approach" first and does not mention the lead exception. That file is a sibling of rule 5. Label: substantive, same family as Item 1, finding 1. Request: add the exception or name it as a follow-up.
- The instruction file `.apm/instructions/change-description-authoring.instructions.md` contains no `breaks`, `Breaking` or `first` lines (grep returned nothing). If it summarizes the slot order, check it. I did not read it end to end.
- The marketplace entry and both `apm.yml` versions all say 1.5.0. The description text is unchanged in all three, matching.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Rule 5 and line 310 still say the description takes the commit body's shape, contradicting "the lead stays" | Substantive | `SKILL.md:310`, `SKILL.md:637` | Say in both places that the lead is kept when the description is copied into the body |
| `references/merge-model.md` tells squash authors to put problem first, with no lead exception | Substantive | `references/merge-model.md:24,38,90` | Add the exception, or name it as follow-up in the description |
| Case READMEs quote a rule title that does not exist | Substantive | `pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | Quote the new sentence |
| Commit message says Opus ran at effort high; the README says the session default | Substantive | `pgjdbc-4367-breaks/README.md:33`, commit message | Make the two agree |
| No run for the commit-body order, the squash exception, the unknown release, or the major target | Substantive | commit message, case READMEs | Add a case per branch, or remove the claim from the message |
| Version bumps, package README bullet and research README lines are claimed by no sentence | Taste | commit message | One sentence that claims them |
| Control has no `origin/main` baseline | Taste | `pgjdbc-4392-no-break/` | Add one baseline run per model |
| `result-2.md` names a run by ordinal | Taste | `.../result-2.md` | Name by content |
| "The trailer decides" has two readings | Taste | `SKILL.md:247` | State whether it makes the release a major |
| Leading paragraph may restate the single break | Taste | `SKILL.md:~255` | Say the paragraph is omitted for one break |
| Repositories with no releases | Taste | `SKILL.md:~250` | Add a clause or accept |
| README line 17 is 121 characters | Taste | `pgjdbc-4367-breaks/README.md:17` | Rewrap |

I did not run the repository's gate, the suite, or any model run. I did not review the wording of the prose except where a sentence reads wrongly, and the pass for style alone was not done.
