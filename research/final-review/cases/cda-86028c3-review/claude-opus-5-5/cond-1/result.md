# Final review: `4f69810..86028c3` (one commit, change-description-authoring 1.5.0)

This change has no code: it edits a skill, a package README, two manifests, and adds research cases. I filled the form using the §2a analogues and loaded `apm-authoring` and `english-developer-style` from the given skills directory. I did not run the drift script because it parses code members and this change has none. There was no task statement, so the claimed cases come from the commit message alone. The skill is `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, shortened below to `SKILL.md`.

## Item 1: comments consistent with the code and with each other

Analogue: what each changed file says about another file, and what the new rule says against other rules in the same skill.

1. **The case READMEs quote a version of the rule that was never committed.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` both say the case tests "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The case README itself says the rule was "reworded after review". Someone looking for the quoted rule will not find it. Request: quote the committed heading in both READMEs.
2. **The old Caller checklist line contradicts the new Breaks line.** `SKILL.md:845` still asks for "one line per distinct outcome under 'User-visible changes', breaks first". `SKILL.md:851` asks whether "slot 3 keep[s] only the other outcomes" once the breaks lead. On the pgjdbc-4367 input, an agent checking against `:845` would move the breaks back into slot 3. Request: give `:845` the same condition, for example "breaks first, or ahead of the Why slot (below)".
3. **Two rules give opposite placements for a break whose intent is in question.** The Scope rule at `SKILL.md:489-492` says that where "only a maintainer can answer… whether a compatibility break is intended", the agent keeps it "in the Scope slot as a question". The new rule at `SKILL.md:239-241` says an extended failure "goes with the breaks, not in the Scope slot." The `grant insert` case meets both. That is the case `opus/result-2.md` left in Scope, which the case README reports and does not explain. Request: one clause that settles the order, for example "the break line leads, and Scope keeps only the question whether it is intended".
4. **"The trailer decides" reads two ways.** At `SKILL.md:247-248`, in a repository whose release tool bumps the major on `BREAKING CHANGE:`, it can mean:
   - the trailer makes the next release a major, so the breaks stay in slot 3; or
   - the trailer decides whether something counts as a break, and the lead still applies.

   The clause "it is written whatever the description does" fits both readings. An agent in a semantic-release repository cannot tell whether to lead. Request: name the outcome, for example "the trailer makes the next release a major, so the breaks stay first in slot 3".
5. **The rule-5 body has nowhere defined for its break lines.** Under §4 rule 5 the body "opens with its breaks and then its problem" (`SKILL.md:259-261`). But `SKILL.md:128` places the `User-visible:` paragraph "after slot 3 and before the trailers", and `:258` says the label is what R4 and R5 search for. The text does not say whether the leading break lines carry the `User-visible:` label at the top, a `Breaking changes` heading, or no label. Request: one clause naming the label the leading lines carry in that body.

Everything else checked out:
- The slot-1 exception at `:86-87` and the Problem checklist line at `:831` match the new rule.
- The `§5` reference: the table at `:706` lists `BREAKING CHANGE:`. The `§7` reference: `:787` covers the no-heading case.
- The package README bullet matches the rule.
- The research README's `cases/` row and dated paragraph match the directory.
- `skill-tree` ids are correct: `4797…` is HEAD's skill tree and `1f02…` is the base commit's.

## Item 2: claimed cases covered

Analogue: claims in the commit message against the section that handles each and the case that exercises it.

| Claimed case | Section | Evidence |
| --- | --- | --- |
| Breaks lead when the next release is not a major (from the version file) | `:234-250` | `pgjdbc-4367-breaks`: 4 runs pass check 1 |
| What counts as a break: result shape | `:235-237` | check 2: 4/4 runs pass |
| What counts as a break: failure extended to inputs that worked before | `:239-241` | check 3: 3/4 runs pass (stated) |
| A fix is not a break | `:242` | check 4: all runs pass |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`: 4/4 runs pass |
| Next release is a major: breaks stay in slot 3 | `:254-255` | **none** |
| Release unknown: breaks lead | `:248-250` | **none** (both prompts state the version file) |
| Release read from milestone or branch name | `:245-246` | **none** |
| Commit body keeps problem first, breaks first under `User-visible:` | `:257-258` | **none** |
| Under squash "title and description" the lead stays in the body | `:259-261` | **none**: both prompts give the default squash, where rule 5 does not apply |

The claim "Without the rule both models put Why first and left both breaks in place" matches both baseline results. Those four `none` rows are claimed in the commit message and have no case behind them. Of them, the major-release row is the one that keeps the rule from firing everywhere, which makes it the important gap; I filed it under item 3 rather than here. The commit body and rule-5 rows rest on instructions with no run; I filed them as one finding here: a case on a prompt whose merge model is "title and description", and one that asks for the commit message.

No commands are added or edited. Every hunk is claimed: the version bump to 1.5.0 is the package's own release for this rule, in all three places that pin it.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the release kinds and output shapes the change claims. The negative control is the no-break case and the table below.

- **The negative control covers the "no break" side, not the "major release" side.** `pgjdbc-4392-no-break` checks that a change with no break grows no section. But the rule's own condition, "unless the next release is a major", has no case. The rule would pass every existing run even if that condition were deleted. Request: a variant of `pgjdbc-4367-breaks` whose prompt gives a major as the next release (for example `pgjdbc.version=43.0.0`), with the check that the description opens with Why and the breaks lead slot 3.
- **The "nothing says which release" partition has no case.** Request: one run with the version line removed from the prompt.
- There is no pre-existing state this change meets. Consumers pick up the new version through the manifests.

Added instructions: 3, no rows.

Not findings: `:254`, `:255`, `:252`.

## Item 3a: level, placement, and the environment

none: the rule sits in §2 beside the slot it modifies, the cases follow the layout of the existing `research/` directories, and the version is bumped in all three places that pin it. `scripts/check-skill-descriptions.py` passed ("all 27 skill descriptions are within 1020 characters"). The model outputs and prompts match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, and the two case READMEs stay linted, like the existing research READMEs. I could not run `make check` (`apm pack --check-versions`) because it fetches through `uvx` and there is no network. I checked by hand that `marketplace.json`, `apm.yml`, and the package `apm.yml` all read 1.5.0.

## Item 4: names by content, not by position

none: headings and cross-references name sections by number and title (`§4 rule 5`, `§2, pull request description`), case directories are named by issue and content, and the result tables name checks by content with their number in parentheses.

## Item 5: the failure report

none: each case README lists its checks, each check says what failure looks like ("fails: Why first", "fails: in Scope"), and the skill's checklist reaches the new rule through the Breaks line at `:849-852`. That line checks the rule as written, not a weaker property, apart from the conflict filed under item 1.2.

## Item 6: what the writer says it verified

The baseline runs on the base commit's skill tree fail checks 1 to 3; the runs with the rule pass checks 1 and 2 in all four runs and check 3 in three of four. That is the evidence that the rule can fail. The bad-case input where the rule is noise is `pgjdbc-4392-no-break`, and its README gives word counts (241–256 against a 209-word draft) with no section added. That README gives no baseline word counts for the same input. With an addition of zero sections, I take the growth check as met. The break case grew by 22 to 69 words over its baseline, and the README names where the growth comes from.

## Item 7: siblings of the change

none: I read every file that names `change-description-authoring` outside the package, and none counts the package's rules or restates the slot order. The frontmatter `description` and the marketplace descriptions name "the slots of a commit body and a description" without listing an order, so the scope did not widen there. The changelog rule at `:543-544` ("Breaking changes are marked in place and sorted first within their category") is a separate artifact and does not conflict.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "promises compatibility", wording that was never committed | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | 1 |
| Caller checklist still puts the breaks first under "User-visible changes" | Substantive | `SKILL.md:845` | 1 |
| Scope rule keeps an in-question break in Scope; the new rule moves it out | Substantive | `SKILL.md:490`, `:239` | 1 |
| "The trailer decides" reads two ways | Substantive | `SKILL.md:248` | 1 |
| The rule-5 body opens with breaks but names no label for them | Substantive | `SKILL.md:259`, `:128` | 1 |
| No case for the commit body order or the rule-5 description-as-body path | Substantive | `research/change-description-authoring/cases/` | 2 |
| No case for a major next release (the rule's own condition) or an unknown one | Substantive | `research/change-description-authoring/cases/` | 3 |

I could not run `make check` because it needs network access through `uvx`.
