I found 9 substantive problems and 2 matters of taste in this one-commit change. None of them blocks the rule itself: the regression runs back up what the commit message says. Most of the fixes are a clause or a sentence each. There is no separate task statement, so I took the claimed cases from the commit message alone. The change is a skill plus research cases with no code, so I filled each item through the no-code substitutes the skill gives (§2a), and I name the one used under each item. I did not run the drift script, because there is nothing for it to parse. I loaded `english-developer-style` and `apm-authoring` (the copy at `agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`). There is no previous report, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other
Checked here: every statement one changed file makes about another file.

- **Stale rule quote.** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility" (`research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7`). The committed heading is "…unless the next release from the target branch is a major" (`SKILL.md:234`). A reader who searches the skill for the quoted text finds nothing.
- **Old checklist line contradicts the new rule.** The checklist "Caller" line (`SKILL.md:844-845`) still asks for every outcome under "User-visible changes", breaks first. The new rule takes the breaks out of slot 3 and into a lead whenever the next release is not a major, so the old line contradicts the new one at line 849.
- **Unclear sentence about release tools.** "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides" (`SKILL.md:247-248`) does not say what the trailer decides. The agent writes that trailer for every break, so a literal reading is: under release-please or semantic-release the next release is always a major, and the breaks never lead. If that is the intent, it should say so; if not, the clause is wrong.
- **Checked and consistent:**
  - The slot 1 paragraph (`SKILL.md:86-87`) and the line "takes the body's shape" (`:310`) agree with the new commit-body paragraph (`:257-260`).
  - The case tables match their result files: the word counts match `wc -w`, the `grant insert` placement matches, and the `skill-tree` ids match HEAD (`4798053…`) and the parent commit (`1f020ce…`) for the baselines.

## Item 2: claimed cases covered
Checked here: each claim in the commit message against the case or section that handles it.

| Claim in the commit message | Covered by |
| --- | --- |
| Breaks lead when the target is a patch release | `pgjdbc-4367-breaks`, check 1 (4 runs with the rule, 2 baselines) |
| A result-shape change is a break | `pgjdbc-4367-breaks`, check 2 |
| A failure extended to inputs that worked before is a break | `pgjdbc-4367-breaks`, check 3 (3 of 4 runs pass, as the commit says) |
| A change with no break grows no section | `pgjdbc-4392-no-break`, checks 1 and 2 |
| Breaks lead when nothing says which release it is | **none** |
| The release is read from the milestone or the branch name | **none**; both prompts give only `gradle.properties` |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | **none**; no case drafts a commit message |
| Where squash copies the description into the commit (§4 rule 5), the lead stays | **none**; both prompts give the merge model as mostly plain commits, so rule 5 does not apply |
| The breaks stay in slot 3 when the next release is a major | **none** (see Item 3) |

- **Hunk no sentence claims.** The version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2` and `.claude-plugin/marketplace.json:291` is not mentioned anywhere in the commit message. The previous commits in this series say "Version 1.2.0 to 1.3.0." for the same kind of bump.
- **Unclear sentence in the commit message.** "on Opus and Haiku (effort high)" reads as if both models ran at high effort. The case README (`pgjdbc-4367-breaks/README.md:27-28`) says Opus ran at the session's default.
- There are no commands to run in the changed skill text.

## Item 3: boundaries, partitions, and the negative control
Checked here: the situations the rule claims, its control case, and the table of added instructions.

- **The rule's own condition has no control.** No case has a change with breaks whose target's next release is a major. That is the run that should come out "breaks stay first in slot 3". `pgjdbc-4392-no-break` only checks that a change with no break grows no section, not the release condition.
- **The control has no baseline to measure growth against.** The control case was not run on the old skill. Its outputs (241–256 words against a 209-word draft) cannot show that the rule added nothing where it does not apply.

Instructions the change adds or widens (4):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Read the next release from the version file, milestone, or branch name | `version=3.0.0` in the version file, latest tag `v3.0.0`, next release 3.0.1 | Reads "major", so the breaks are not led | "a version that equals the latest release tag names the released one" |
| Where a release tool reads `BREAKING CHANGE:`, the trailer decides | A release-please repository on 1.x, a change with a break | Either reading; most likely writes the trailer and does not lead | "the trailer makes the next release a major, so the breaks stay in slot 3" (or the opposite) |
| Under §4 rule 5 the lead stays, and the body opens with its breaks | One-commit pull request, squash with "title and description", no headings | Break lines with no label, or `User-visible:` written twice | Name the label the leading lines carry in a commit body |
| Checklist line "Breaks" | A draft that leads with the breaks but leaves an extended failure in Scope | Passes the checklist | Add "is a result-shape change or an extended failure listed with the breaks?" (see Item 5) |

Not findings:
- "A failure the change extends to inputs that worked before is a break": ended for a fix by "a failure that now succeeds is a fix, not a break".
- "A change with no break has neither the lead nor an empty heading": ended by its own condition.

## Item 3a: level, placement, and the environment
Checked here: where the files live and whether the repository's own checks pass.

- **One line is too long.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:17` is 121 characters. The repository's Markdown rules (the `markdown-line-length-120` skill) limit body lines to 120. That file is not excluded from linting (`.github/super-linter.env` excludes `prompt*` and `result*` only), so super-linter will flag it.
- **Gates run.** `make check` and `make check-descriptions` both pass offline ("all 27 skill descriptions are within 1020 characters").
- **Layout matches the siblings.** The cases use the same `prompt.md` / `README.md` / `<model>/result*.md` / `skill-tree` layout as `research/problem-report-authoring/cases`. The rule sits in the pull-request-description section of §2, which is the right place.

## Item 4: names by content, not by position
Checked here: headings, cross-references, and case names.

- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the headings name things by content.
- **Taste:** "Checks 1 to 3 are the rule under test; 4 to 6 are the guard" (`pgjdbc-4367-breaks/README.md:24`) could name the checks (Lead, Result shape, `grant insert`), as the results table already does.

## Item 5: the failure report
Checked here: whether each rule is reached by the skill's own checklist, and whether the check tests the rule itself.

- **Checklist misses the break definition.** The new "Breaks" line (`SKILL.md:849-852`) checks the lead and the empty heading. It does not check the definition of a break: a result shape, or a failure extended to inputs that worked before, listed with the breaks rather than in Scope. The commit message names that missing definition as the cause of the original miss, and case checks 2 and 3 test exactly that.

## Item 6: what the writer says it verified
Checked here: whether there is a bad case the rule fails and an exemplar it passes.

- **The evidence is there.** The baselines on the pre-rule skill fail checks 1–3. The runs on the committed skill (tree id equal to HEAD) pass them, except `opus/result-2.md` on check 3, which is reported honestly.
- The earlier drafts of the rule are summarized, not stored, as the commit message says.
- The only gap is the missing baseline for the control case, filed under Item 3.

## Item 7: siblings of the change
Checked here: every place that lists or routes to this skill.

- The package README, the research index (new `cases/` entry), `apm.yml` and the marketplace manifest are all updated. `make check` confirms the versions are in sync.
- The changelog's "Breaking changes are marked in place" rule (§3) belongs to a different artifact and does not conflict.
- **Taste:** the package README (`agent-packages/change-description-authoring/README.md:23-25`) says "the commit body keeps them first in its outcome slot" without the §4 rule 5 exception, where the body opens with the breaks.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Case READMEs quote a rule heading that no longer exists | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote "…unless the next release from the target branch is a major" |
| Checklist "Caller" line still puts all breaks first under User-visible changes | Substantive | `SKILL.md:844-845` | Add "or in the lead (§2, breaks)" |
| "The trailer decides" does not say which way | Substantive | `SKILL.md:247-248` | State whether a written `BREAKING CHANGE:` trailer means a major, so no lead |
| A version file that holds the released version is misread | Substantive | `SKILL.md:244-246` | Clause: a version equal to the latest release tag names the released version |
| Under §4 rule 5 the leading break lines have no label | Substantive | `SKILL.md:257-260` | Name the label (`User-visible:`) the leading lines carry in a body |
| "Breaks" checklist line does not check the break definition | Substantive | `SKILL.md:849-852` | Ask whether result-shape changes and extended failures are among the break lines |
| No case for the major-release arm, the unknown-release arm, the commit body, or rule 5; the control has no baseline | Substantive | `research/change-description-authoring/cases/` | Add a case with breaks aimed at a major and a baseline run of `pgjdbc-4392-no-break`, or narrow the commit message to what was run |
| Version bump not mentioned in the commit message; "effort high" reads as both models | Substantive | commit message | Add "Version 1.4.0 to 1.5.0."; say "Haiku at effort high" |
| Line 17 is 121 characters | Substantive | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap to 120 |
| Checks referred to by number | Taste | `cases/pgjdbc-4367-breaks/README.md:24` | Name the checks |
| Package README omits the §4 rule 5 exception | Taste | `agent-packages/change-description-authoring/README.md:23-25` | Add the exception |

The review did not rerun the model cases, did not run super-linter or markdownlint themselves (the 121-character line was measured directly), did not check the external pgjdbc links or the token prices, and was not a pass over the prose for style.
