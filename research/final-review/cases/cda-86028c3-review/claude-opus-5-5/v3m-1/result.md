# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

There is no separate task statement, so the claimed cases come from the commit message alone. This change has no code: it touches a skill, the package README, version files and a research directory. I used the analogues in §2a and say which one under each item. I did not run the drift script because it parses members of code and this change has none. Of the skills to load, I loaded `english-developer-style` from the given directory. `apm-authoring` has no copy there, so I cite none of its rules.

`SKILL.md` below means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
Analogue: what one file says about another, and what one rule says about another rule on the same input.

- **Scope rule contradicts the new rule.**
  - `SKILL.md:239-240` says a failure extended to new inputs "goes with the breaks, not in the Scope slot".
  - `SKILL.md:489-491` says that when only a maintainer can decide "whether a compatibility break is intended", it is kept "in the Scope slot as a question".
  - The `grant insert` input in pgjdbc-4367 matches both rules. `opus/result-2.md:35` follows the older one and leaves it in Scope.
- **Two checklist items disagree.**
  - The Caller item (`SKILL.md:845`) asks for the breaks first under "User-visible changes".
  - The Breaks item (`SKILL.md:849-851`) asks that slot 3 hold only the other outcomes when the release is not a major.
  - An agent following the Caller item puts the breaks in both places, which fails check 5 of the case ("Stated once").
- **Templates conflict with the new heading.**
  - `SKILL.md:300-302` says to use the template's headings when the repository has a template.
  - `SKILL.md:252` adds a `Breaking changes` heading wherever the description has headings.
  - For a repository with a template such as `Summary`/`Testing`, the text does not say which rule wins.
- **"The trailer decides" reads two ways** (`SKILL.md:247-248`).
  - Reading one: the `BREAKING CHANGE:` trailer makes the next release a major, so the breaks stay in slot 3.
  - Reading two: it decides something else.
  - Under the first reading, every break in a release-please or semantic-release repository carries the trailer, so the lead never fires there. The text does not state that outcome.
- **The case READMEs quote a rule that no longer exists.**
  - `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote "A break leads the description where the next release from the target branch promises compatibility".
  - The committed heading at `SKILL.md:234` is "…unless the next release from the target branch is a major".
- No sentence in the change narrates the change.
- Checked against the files:
  - The case READMEs' result tables match the result files: openings, where `grant insert` sits, word counts from `wc -w`, and the "Generated with" lines.
  - Every `skill-tree` id matches `git rev-parse` on the skill: HEAD gives `4798053…` and the base gives `1f020ce…`.
  - The commit message's "all four / three of four" agrees with the table.

## Item 2: claimed cases covered
Analogue: each case the commit message claims, set against the section of the skill that handles it and the case that tests it.

| Claimed case | Section | Evidence |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `:234`, `:252` | pgjdbc-4367, 4 runs plus 2 baselines |
| Result shape counts as a break | `:235-236` | 4367 check 2 |
| A failure extended to new inputs counts as a break | `:238-240` | 4367 check 3; Opus passed it in 1 of 2 runs, as stated |
| A failure that now succeeds is a fix, not a break | `:241` | 4367 check 4 |
| Next release read from the version file, milestone or branch name | `:244-246` | The 4367 prompt gives only the version file |
| The breaks lead when nothing says which release it is | `:248-250` | **none** |
| The next release is a major, so the breaks stay in slot 3 | `:254` | **none** |
| The commit body keeps the problem first, with the breaks as the first `User-visible:` lines | `:257-258` | **none**: no case writes a commit message |
| A squash that copies the description into the commit keeps the lead | `:258-260` | **none**: the 4367 prompt's merge model is `squash 3 plain 37` with bullets, so rule 5 is not in play |
| A change with no break grows no section | `:254` | pgjdbc-4392, 4 runs |

- **Commit message is broader than the skill.** It says "where squash copies the description into the commit, the lead stays". The skill limits this to §4 rule 5: a squash or merge commit under the "title and description" setting. The default squash does not copy the description.
- **Unclaimed hunks.** The version bump from 1.4.0 to 1.5.0 in `apm.yml`, `agent-packages/change-description-authoring/apm.yml` and `.claude-plugin/marketplace.json` has no sentence in the commit message. Earlier commits in this package say "Version 1.2.0 to 1.3.0." and similar.
- Commands to run: the change adds none.

## Item 3: boundaries, partitions, and the negative control
Analogue: the partitions are the modes the change claims; the negative control is pgjdbc-4392.

- **Four claimed partitions have no evidence:**
  - the next release is a major;
  - the next release is unknown;
  - a commit body;
  - the description becomes the body under rule 5.
- **The negative control has no baseline run.** pgjdbc-4392 compares its 241–256 words only with the 209-word draft. Without a run on origin/main, nothing shows whether the output grew because of the rule.

Added instructions: 4, 1 row.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:258-260` "Where §4 rule 5 makes the description the commit body, the lead stays" | Squash under "title and description" (§4 rule 5), read later by R2 via `git blame` | A permanent commit body that opens with break lines before its reason, against `:76`/`:257` | "in the pull request; the squash message the maintainer edits at merge opens with the problem" |

Not findings: `:241`, `:254`.

## Item 3a: level, placement, and the environment
Analogue: where each rule lives, whether the layout matches its siblings, and the repository's gates.

- **Placement:** none.
  - The rule sits in §2 next to slot 3, has a checklist line in §8 and a summary line in the package README.
  - `cases/` matches its siblings (`research/test-authoring/cases`, `research/problem-report-authoring/cases`).
  - The super-linter filter excludes `prompt*.md` and `result*.md` and still lints the case READMEs.
- **Gates:** I ran `make check` (exit 0) and `scripts/check-skill-descriptions.py` ("all 27 skill descriptions are within 1020 characters").
- **No tutorial-level sentences:** each sentence is specific to this skill's slots.

## Item 4: names by content, not by position
None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the checks ("Lead", "Result shape is a break") are named by content. The cross-references (`§4 rule 5`, `§5`, `§7`) point to numbered sections and rules that exist.

## Item 5: the failure report
Analogue: whether the checklist reaches the rule, and whether the check tests the rule rather than something weaker.

- The new rule has a checklist line at `SKILL.md:849-852`.
- That line contradicts the Caller line at `:845`, which I filed under item 1.
- That line asks whether the description opens with the breaks, which is the rule itself. It does not ask whether an extended failure stayed out of Scope, the part of the rule that failed in one Opus run.

## Item 6: what the writer says it verified
Analogue: an example the rule passes and a bad case it fails.

- **Present:**
  - Baseline runs on origin/main fail checks 1–3; runs with the rule pass them.
  - The control passes all of its checks.
  - The tree ids prove the runs used the committed skill.
- **Missing:**
  - a baseline run for the control (item 3);
  - any run of the major-release, commit-body or rule-5 forms.

## Item 7: siblings of the change
- **The heading set lacks the new heading.** `Breaking changes` joins the description's headings, but the house-style set at `SKILL.md:300-301` still lists only `Why`, `What`, `User-visible changes`, `How to verify` and `Scope`.
- **The Scope paragraph at `:489-491`** is the sibling rule that sends the same input elsewhere (filed under item 1).
- **Other places that list or route to the package:** none.
  - The marketplace and both `apm.yml` entries agree on 1.5.0.
  - The research README lists `cases/`.
  - `english-developer-style` and `problem-report-authoring` give no order for a pull request's breaks.
  - The changelog's breaking-marker rule (`:543`) is a different artifact and is consistent.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Scope paragraph keeps "whether a break is intended" in Scope; the new rule moves extended failures out of Scope | Substantive | `SKILL.md:489-491` vs `:239-240` | Scope keeps only the question of intent; the break line goes to the lead or slot 3 |
| Caller checklist says "breaks first under User-visible changes"; Breaks checklist says slot 3 keeps only the other outcomes | Substantive | `SKILL.md:845` vs `:849-851` | Add "or in the lead (Breaks)" to the Caller item |
| Template headings conflict with the `Breaking changes` heading | Substantive | `SKILL.md:252` vs `:300-302` | Say which wins under a template |
| "The trailer decides" reads two ways | Substantive | `SKILL.md:247-248` | State it: the trailer makes the next release a major, so the breaks stay in slot 3 |
| Case READMEs quote an earlier wording of the rule | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the heading at `:234` |
| Major, unknown-release, commit-body and rule-5 partitions have no case | Substantive | `SKILL.md:248-260` | A 4367 variant with a major version file and one that writes a commit message, or narrow what the commit message claims |
| Control has no baseline run for output growth | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs on origin/main with word counts |
| Rule-5 body opens with breaks, ahead of R2's reason | Substantive | `SKILL.md:258-260` | See the row under item 3 |
| `Breaking changes` missing from the house-style heading set | Substantive | `SKILL.md:300-301` | Add it to the list |
| Commit message says "squash" where the skill means only "title and description" | Substantive | commit message, second paragraph | Name the setting |
| Version bump to 1.5.0 not claimed in the commit message | Substantive | `apm.yml`, package `apm.yml`, `marketplace.json` | One line, "Version 1.4.0 to 1.5.0." |

I did not re-run any drafting case, did not fetch the cited pgjdbc pull requests, and did not do a style-only pass over the prose.
