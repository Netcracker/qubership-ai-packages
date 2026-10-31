I found ten substantive findings and two taste findings in commit 86028c3. The commit changes only a skill, a package README, versions, and research cases, so the form below is filled through the analogues for a change with no code (§2a). There was no task statement, so item 2 takes its claimed cases from the commit message alone. I did not run the drift script, because the change has no code members for it to parse. I loaded `english-developer-style` from the skills directory you gave. The skill also asks for `apm-authoring`, which is not in that directory, so I did not load it. No earlier report of this form exists.

## Item 1: comments consistent with the code and with each other

Analogue used: statements one changed file makes about another file.

- **The case READMEs quote a rule that no longer exists.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` quotes the rule as "A break leads the description where the next release from the target branch promises compatibility". `pgjdbc-4392-no-break/README.md:6-7` quotes the same wording. The committed rule, at `SKILL.md:234`, reads "…unless the next release from the target branch is a major." A reader who searches the skill for the quoted sentence finds nothing. The two wordings also differ at an edge: a 0.x minor release does not promise compatibility, yet it is not a major.
- **Two checklist items in SKILL.md contradict each other.** The "Caller" item (`SKILL.md:844-846`) asks for "one line per distinct outcome under 'User-visible changes', breaks first". The new "Breaks" item (`:849-852`) asks that "slot 3 keep only the other outcomes" when the breaks lead. Before a major release both are satisfiable; in any other release they are not. The prose has the same problem in a milder form: `:222-224` ("Breaks come first…") is unqualified, and only the next paragraph qualifies it.
- **The Scope rule and the new rule can be read as conflicting.** `SKILL.md:488-491` says that where it is unclear "whether a compatibility break is intended", the question goes in the Scope slot. The new text at `:238-240` says a break "goes with the breaks, not in the Scope slot". A writer with a break of uncertain intent cannot tell whether the break line moves to the lead or stays in Scope. The 4367 draft is exactly that case, and one Opus run (`opus/result-2.md`) kept it in Scope. The request is one clause in `:488-491` saying the break line leads and only the question stays in Scope.
- **The commit-body table does not carry the new ordering.** `SKILL.md:257-258` says the commit body puts "the breaks as the first `User-visible:` lines of slot 4". The commit-body table row for slot 4 (`:83`) does not say so, and the rule exists only inside the pull-request section. Filed as taste.
- **The merge-model template omits the lead.** `references/merge-model.md:62-63` gives a CONTRIBUTING line for "title and description": "the description as a commit body: problem, symptom, approach". Under the new rule that body opens with its breaks. The template contradicts `SKILL.md:258-260` and was not updated.
- **"The trailer decides" can be read two ways.** `SKILL.md:247-248` says: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." It could mean that this change's own trailer makes the next release a major, so the breaks never lead in such repositories. It could also mean that a trailer already on the branch decides. Under the first reading, the rule's own rationale (`:243-244`, "the reviewer's first decision is whether the change may ship in it") argues the other way: a break that forces an unplanned major is the decision a reviewer most needs first. The request is to state the outcome explicitly.
- No sentence narrates the change with words such as "now" or "no longer".
- The cross-references §4 rule 5, §5 (the `BREAKING CHANGE:` row at `:706`), and §7 (`:787`) are correct.
- The `skill-tree` ids match the trees: `47980534…` is HEAD's skill tree and `1f020ce5…` is the base's.
- The run counts and word counts in both case READMEs match the files.

## Item 2: claimed cases covered

Analogue used: the claims come from the commit message, since there was no task statement. Each claim is matched to the section that handles it and the case that detects it.

| Claim (commit message) | Section | Detection or case |
| --- | --- | --- |
| Breaks lead unless the next release is a major | `SKILL.md:234-255` | `pgjdbc-4367-breaks`, check 1 |
| The release is read from the version file, milestone, or branch name | `:245-247` | 4367 covers the version file only; no case for a milestone or a maintenance-branch name |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| Next release is a major: breaks stay in slot 3 | `:254-255` | **none** |
| Definition of a break: result shape, extended failure | `:234-241` | 4367 checks 2 and 3 |
| A fix is not a break | `:240-241` | 4367 check 4 |
| The commit body keeps the problem first, breaks first among the `User-visible:` lines | `:257-258` | **none**: both prompts ask for a pull request description only |
| Where squash copies the description, the lead stays | `:258-260` | **none**: both prompts state a default squash of one commit, so rule 5 never applies |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`, checks 1 and 2 |

Command lines:
- `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring` (4367 README, "Running it"). I ran it on HEAD and it produces the skill tree. No script runs the cases, so each run is manual.
- The `./gradlew` lines inside `prompt.md` are input data for the drafts, not instructions to the reader.

Hunks no sentence claims:
- **The version bump is unclaimed.** `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json` go from 1.4.0 to 1.5.0, and the commit message has no sentence for it. Earlier commits state it: `51b35c9` says "Version 1.2.0 to 1.3.0." and `d79c43d` says "Version 1.1.0 to 1.2.0."
- The package README line and the research README's `cases/` entry are claimed by the rule and the cases.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the partitions are the modes the change claims; the negative control is the no-break case.

- **The no-break control is present.** `pgjdbc-4392-no-break` ran twice on each model, and the baselines are red on the base commit.
- **The other half of the rule has no evidence.** No case covers "next release is a major", "release unknown", or a release-tool trailer.
  - The major case is the control for the rule's own condition: a break aimed at a major must not lead. As committed, a rule that always leads breaks would pass every case.
  - Both prompts state `pgjdbc.version=42.7.14` on `master`, so they exercise one partition.
- **The commit-body and description-as-body forms have no case.** Both prompts use a default squash of one commit, which is outside §4 rule 5. The two forms the commit message claims (problem first in the commit body, and "the lead stays" when squash copies the description) have no evidence.
- **The 0.x boundary is not defined.** For a version file with `0.9.3`, the rule does not say whether a minor bump counts as "a major". Under semver 0.x a minor bump is the breaking bump.
- No earlier installed state applies, and no setting starts reaching a new consumer.

## Item 3a: level, placement, and the environment

Analogue used: where each rule lives, the layout against sibling packages, and the repository's offline gate.

- The rule sits in the PR-description section of SKILL.md, with a checklist entry and a package README bullet. That is right.
- `make check` (`apm pack --check-versions --check-clean --dry-run`) passed offline with "Version alignment OK", and change-description-authoring is at 1.5.0.
- The `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` covers `prompt.md` and `result*.md`. The case READMEs are linted. `pgjdbc-4367-breaks/README.md:17` is 121 characters, but its only whitespace past column 120 is none, so non-strict MD013 should not flag it.
- **The case layout differs from its siblings.** Taste:
  - Siblings name their directories by model id: `problem-report-authoring/cases/*/claude-opus-5-5`.
  - Siblings record the second skill's tree: `blackbox-test-design/…/skill-tree-test-authoring`.
  - These cases use `opus/` and `haiku/` with no model version.
  - These cases record no tree for `english-us-developer-style`, although the drafting agent read that skill too (README "Running it"). Without that tree a rerun cannot pin the style skill.

## Item 4: names by content, not by position

Analogue used: the change's own headings, cross-references, and case names.

None introduced beyond the skill's existing convention ("slot 3", "§4 rule 5"). The new text names the Why slot by name. The case checks carry both a number and a name ("Lead (1)").

## Item 5: the failure report

Analogue used: whether each rule is reached by the skill's checklist, and whether the detection catches the rule.

- The new rule is reached by the "Breaks" checklist item.
- **The checklist item detects a weaker property than the rule.** It asks "where the change breaks code…", but not whether a changed return value or result shape, or a failure extended to inputs that worked before, was classified as a break. Those two misclassifications are what the commit message names as the defect, and what the baselines failed (checks 2 and 3). A writer who leaves `getUpdateCount()` returning `-1` in slot 3 passes the item. The request is one clause that names both kinds.

## Item 6: what the writer says it verified

Analogue used: an exemplar the rule passes and a bad case it fails, both named in the change.

- **Bad case:** both baselines fail checks 1 to 3.
- **Pass with the rule:** all four runs pass checks 1 and 2. Three of four pass check 3; `opus/result-2.md` leaves `grant insert` in Scope, and the README says so.
- **Control:** four of four runs pass.
- The runs were made on the committed tree, since the `skill-tree` ids match HEAD.
- I could not fetch the cited exemplar, the maintainer's rewrite in pgjdbc/pgjdbc#4367 issuecomment-6079358908, because there is no network.
- **The commit message misstates the Opus effort.** It says "on Opus and Haiku (effort high)", but the case README says only Haiku ran at high and Opus ran at the session's default.

## Item 7: siblings of the change

Analogue used: the places that list or route to the artifact, and the other skills that describe the same structure.

- The package README is updated, and the research README lists `cases/`.
- The marketplace and `apm.yml` description is unchanged. That is right, because the skill's scope did not widen.
- `english-us-developer-style` §7 hands description structure off to this skill, so it does not conflict.
- `references/merge-model.md:62-63` is not updated (see item 1).
- **The Russian developer-style skill keeps the old order.** `agent-packages/russian-developer-style/.apm/skills/russian-developer-style/modules/code-comments.md:120-130` lists the pull request description as Что, Зачем, Как проверять, with "Breaking changes" as an optional extra block, and it does not defer to change-description-authoring. It now gives the opposite order for a patch-release break. The request is to fix it here or name it as a follow-up in the description.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote the rule as "…promises compatibility"; the skill says "…unless … is a major" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading |
| The "Caller" checklist item still asks for breaks first under "User-visible changes"; the "Breaks" item asks for them outside it | Substantive | `SKILL.md:844-846` vs `:849-852` | Qualify "breaks first" in Caller, and at `:222-224`, with "unless they lead the description" |
| The Scope rule keeps a break of uncertain intent in Scope; the new rule moves it to the lead | Substantive | `SKILL.md:488-491` vs `:238-240` | Say the break line leads and only the question stays in Scope |
| "The trailer decides" has two readings, and the likely one works against the rule's own rationale | Substantive | `SKILL.md:247-248` | State the outcome for release-please and semantic-release repositories explicitly, and reconcile it with `:243-244` |
| The merge-model "title and description" template still says the body is "problem, symptom, approach" | Substantive | `references/merge-model.md:62-63` | Add that breaks lead where the release is not a major |
| No case for a major release, which is the control for the rule's condition, or for an unknown release | Substantive | `research/change-description-authoring/cases/` | Add a case with the same draft aimed at a major, plus one with no version information; or state the gap in the README and the commit |
| No case for the commit-body ordering or for "the lead stays" under §4 rule 5 | Substantive | `SKILL.md:257-260`; both prompts | Add a run with a "title and description" squash and a run that asks for the commit message, or state the gap |
| 0.x boundary of "a major" is undefined | Substantive | `SKILL.md:234, 243-250` | Say how a 0.y version file is read |
| The checklist item does not detect a misclassified result-shape change or extended failure | Substantive | `SKILL.md:849-852` | Ask whether a changed return value or result shape and an extended failure are among the break lines |
| Version bump 1.4.0 → 1.5.0 has no sentence in the commit message | Substantive | `apm.yml`, `agent-packages/change-description-authoring/apm.yml:2`, `.claude-plugin/marketplace.json:291` | Add "Version 1.4.0 to 1.5.0.", as `51b35c9` and `d79c43d` do |
| Russian developer-style module gives a description order with breaks as an optional trailing block | Substantive | `russian-developer-style/.../modules/code-comments.md:120-130` | Align it, or name it as a follow-up |
| The commit message says "(effort high)" for both models; the case README says Opus ran at the session default | Substantive | commit message, paragraph 3 | Attach "effort high" to Haiku only |
| Commit-body table row 4 does not carry "breaks first" | Taste | `SKILL.md:83` | Add it to the row's "Answers" cell |
| Case directories not named by model id; no tree recorded for the English style skill | Taste | `cases/*/opus`, `cases/*/haiku` | Follow the sibling layout: `claude-opus-5-5/`, and a `skill-tree-english-developer-style` file |

I did not check the prose for style alone, the list prices quoted in the 4367 README (no network), or the cited pull request and comment on GitHub (no network); `make check` was the only gate run, and `make test` was not run because it covers no changed file.
