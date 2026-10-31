# Final review: `4f69810..86028c3`, "lead the description with breaks unless the next release is a major"

The change has no code: one skill (`change-description-authoring` SKILL.md), its README, three version fields, and two research regression cases. I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring` alongside it. I did not run the drift script, because there are no members for it to parse. There was no task statement, so the claimed cases come from the commit message alone. There is no previous report.

## Item 1: comments consistent with the code and with each other

*Analogue used: statements one file makes about another, and statements inside SKILL.md about the same fact.*

- **The case READMEs quote a rule that isn't in the skill.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` both cite the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` says "…unless the next release from the target branch is a major". A search for the quoted text finds nothing. The two versions also disagree on the unknown-release case: the quoted one doesn't lead there, the committed one does.
- **The review checklist now contradicts itself.** The unchanged *Caller* line at `SKILL.md:844-848` asks for every outcome under "User-visible changes", "breaks first". The new *Breaks* line at `:849-852`, and `:252-254`, say that when breaks lead, slot 3 keeps only the other outcomes. A reviewer following *Caller* would put the breaks back into slot 3.
- **When squash copies the description into the commit, the lead has no stated form.**
  - `:257-260` says the copied body "opens with its breaks and then its problem".
  - `:206-208` says slot 3 is written there as `User-visible:` lines.
  - `:310` and the *Headings* checklist line (`:856-858`) say a rule-5 body has no headings, so the `Breaking changes` heading from `:252` doesn't apply.
  - Nothing says whether the leading break lines carry the `User-visible:` label. `:258` gives that label as the reason R4 and R5 find the breaks.
- **The skill's own paste-in line for this merge setting says problem first.** `references/merge-model.md:61-63` gives the house-rule line for "title and description" as: "write … the description as a commit body: problem, symptom, approach". That is now false when the change has a break, because `:259` says the lead stays.
- **The heading list is missing the new heading.** `SKILL.md:300-301` lists the headings that match the slots (`Why`, `What`, `User-visible changes`, `How to verify`, `Scope`). It doesn't include `Breaking changes`, which `:252` introduces.
- **The "now" wording is fine.** The skill only uses it to describe outcomes in examples, not to narrate this change.

## Item 2: claimed cases covered

*Analogue used: a section and a case per claim. Claims are taken from the commit message only.*

| Claim (commit message) | Where the skill handles it | Evidence |
| --- | --- | --- |
| Breaks lead when the next release isn't a major | `:234`, `:252` | `pgjdbc-4367-breaks` check 1; 4 of 4 runs pass |
| Read the release from the version file, milestone, or branch name | `:245-247` | Version-file form only (the prompt gives `gradle.properties`). Milestone and branch name: none |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| Next release is a major → breaks stay first in slot 3 | `:254` | **none** |
| A changed return value or result shape is a break | `:236-237` | check 2; 4 of 4 runs |
| A failure extended to inputs that worked before is a break | `:238-240` | check 3; 3 of 4 runs (one Opus run fails), which the README reports honestly |
| New failure | `:235` | The draft already marked these as breaks, so this is weak evidence |
| Removed option, changed default, changed error code | `:237-238` | **none** |
| A fix is not a break | `:241` | check 4 |
| Commit body keeps problem first, breaks as the first `User-visible:` lines | `:257-258` | **none**: both prompts ask only for a pull request description |
| Where squash copies the description, the lead stays | `:259-260` | **none**: both prompts use the default squash setting |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`; 4 of 4 runs |

- **Detection:** the new *Breaks* checklist line reaches the lead rule. No checklist line detects the commit-body ordering at `:257`.
- **Commands:** the case README tells readers to run `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring`. I ran it at HEAD and it produces the skill directory. The `english-us-developer-style` path it names exists. Nothing in CI runs the command, but its outcome is just the file listing, which I checked.
- **Unclaimed hunk:** the version bump from 1.4.0 to 1.5.0 in `apm.yml`, the package `apm.yml`, and `marketplace.json` has no sentence in the commit message. The previous commits in this package state theirs ("Version 1.2.0 to 1.3.0.").

## Item 3: boundaries, partitions, and the negative control

*Analogue used: the partitions are the release kinds and merge settings the change claims. The negative control is `pgjdbc-4392-no-break` plus the table below.*

- **Only the patch-release partition has evidence.** Both cases target the same pgjdbc `master` (42.7.x), with the same default squash setting and a pull request description as output. Four claimed partitions have no run:
  - next release is a major (the condition's other arm, which keeps the breaks in slot 3);
  - unknown release (breaks lead);
  - commit-body output;
  - "title and description" squash.
- **The no-break control is good.** Both models, two runs each, produced no section and no compatibility sentence.
- **The skill-tree ids match the commits.** `47980534…` is the skill tree at HEAD and `1f020ce5…` is the tree at the base, matching the "with the rule" and "baseline" labels.
- **Pre-existing state and limits:** none apply. This is a skill change; existing installs pick up the new text on version bump.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:243` "In a release that is not a major…" | a 0.x library, or calver, where any release may break by policy | leads with breaks the reviewer has already accepted | "unless the project's versioning admits breaks in the next release" |
| `:248` "Where nothing says which release it is, the breaks lead" | a continuously deployed service repository with no releases | a `Breaking changes` lead ahead of the Why, for a reviewer with no ship-or-not decision | "only where the project publishes versioned releases" |

Not findings: `:237` "a changed error code", `:241` "a failure that now succeeds", `:247` "the trailer decides", `:255` "neither the lead nor an empty heading".

## Item 3a: level, placement, and the environment

*Analogue used: where each file lives, its layout against siblings, and the repository gate.*

None. The rule sits in the pull request description section beside the slot rules. The cases sit under `research/change-description-authoring/cases/`, and the research README now lists them. `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` covers `prompt*.md` and `result*.md`, while the case READMEs stay linted, matching the other research directories.

I ran `make check` (exit 0: versions aligned and the index in sync) and `make check-descriptions` (all 27 descriptions within 1020 characters). The new paragraphs are specific to this skill, not tutorial text.

## Item 4: names by content, not by position

None. The cross-references name sections by number in the skill's own house style (`§2`, `§4 rule 5`, `§7`). The cases are named by issue and content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). The checks are numbered but each has a title ("Lead", "Result shape is a break").

## Item 5: the failure report

*Analogue used: whether the checklist reaches the rule, and whether each detection checks the rule rather than a weaker property.*

- The *Breaks* checklist line detects the lead and the empty-section control. It reaches the rule.
- The checks in the case README name the literal each one looks for, and the results table shows which check failed and where ("fails: in Scope").
- The contradiction with the *Caller* line is filed under item 1, so it isn't repeated here.

## Item 6: what the writer says it verified

The change states its evidence:

- **Bad case:** two baseline runs (Opus and Haiku) on the pre-rule tree, which fail checks 1 to 3.
- **Passing runs:** four runs on the committed tree, with check 3's one failure reported.
- **Control:** four runs on the no-break input, where the added rule is noise. Word counts are given, and the control output didn't gain a section. Its growth over the draft's 209 words (241 to 256) isn't attributed to the rule or to a baseline, because the control has no baseline run.
- **Earlier drafts:** described in prose and not stored, which the commit message says.

The commit message's "on Opus and Haiku (effort high)" reads as if both ran at high. The README says Opus ran at the session default.

## Item 7: siblings of the change

- **`references/merge-model.md:61-63`** still prescribes problem-first for the "title and description" setting. This is filed under item 1.
- **The package README bullet** says the commit body keeps the breaks first in its outcome slot, and leaves out the squash exception at `:259`. It is a summary, so this is taste.
- **`russian-developer-style` `modules/code-comments.md:128-130`** has its own pull request template that puts "Breaking changes" among optional blocks after Что/Зачем. It conflicts with the new rule in another package. Name it as a follow-up.
- **The `english-developer-style` copies** route pull request description content to this skill, so nothing changes there.
- **Marketplace, `apm.yml`, and package `apm.yml`** all carry 1.5.0, and `make check` agrees.
- **Old set size:** the "Six slots" count (`:192`) still holds, because no slot was added.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule wording ("promises compatibility") the skill doesn't contain, and that wording means something else for an unknown release | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading from `SKILL.md:234` |
| The *Caller* checklist line asks for breaks first under "User-visible changes"; the *Breaks* line and `:253` say slot 3 keeps only the other outcomes | Substantive | `SKILL.md:844-848` | Make *Caller* say breaks first in slot 3 only where the next release is a major |
| When squash copies the description into the commit, nothing says whether the leading break lines keep the `User-visible:` label that `:258` gives as the reason for the label | Substantive | `SKILL.md:257-260`, `:206-208`, `:310` | One clause: in a body the lead is the `User-visible:` break lines, with no heading |
| merge-model.md's paste-in line for "title and description" still prescribes problem first | Substantive | `references/merge-model.md:61-63` | Add "breaks first, where the change has any" |
| The heading list at `:300` leaves out `Breaking changes` | Substantive | `SKILL.md:300-301` | Add it to the list |
| Major, unknown-release, commit-body, and "title and description" partitions have no case run | Substantive | `cases/` | A case per partition, or a sentence in the commit message that limits the evidence to patch-release pull request descriptions |
| The lead rule fires in a 0.x or calver project where any release may break | Substantive | `SKILL.md:243` | The clause in the instruction table |
| The unknown-release default fires in a repository with no versioned releases | Substantive | `SKILL.md:248-250` | The clause in the instruction table |
| Version bump to 1.5.0 has no claiming sentence in the commit message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | "Version 1.4.0 to 1.5.0.", as the earlier commits write it |
| Removed option, changed default, and changed error code have no case | Taste | `SKILL.md:237-238` | A case, or accept that they rest on the definition alone |
| The commit message's "(effort high)" reads as applying to Opus too | Taste | commit message | "Haiku at effort high" |
| The package README bullet leaves out the squash exception | Taste | `agent-packages/change-description-authoring/README.md:23-25` | Add "except where squash copies the description" |
| `russian-developer-style` template puts Breaking changes after Что/Зачем | Taste | `russian-developer-style/.../modules/code-comments.md:128-130` | Name it as a follow-up |

Not checked: I didn't re-run the model trials, I didn't open the cited pgjdbc pull requests or the maintainer's comment (no network), and I didn't do a style-only pass over the prose.
