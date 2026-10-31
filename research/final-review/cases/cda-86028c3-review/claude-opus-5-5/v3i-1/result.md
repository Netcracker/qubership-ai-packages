# Final review: `4f69810..86028c3`, "lead the description with breaks unless the next release is a major"

**Inputs.** No task statement was handed over, so the claimed cases come from the commit message alone. There is no previous report. The change has no code: it edits a skill (`SKILL.md`), the package README, three version files, the research README, and adds two regression cases. I filled the form with the §2a analogues. The drift script was not run because it parses code members and this change has none. Skills loaded: `final-review` and `english-developer-style` from the skills directory, and `apm-authoring` from the repository, because none was supplied under the skills directory. `test-authoring` was not needed: there are no tests.

## Item 1: comments consistent with the code and with each other (analogue: what one file says about another)

- **Substantive.** Both case READMEs quote a rule that does not exist in the skill:
  - `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8`: "The case tests the rule in SKILL.md §2, 'A break leads the description where the next release from the target branch promises compatibility'".
  - `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md:6-7` repeats the same quote.
  - The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". `git grep 'promises compatibility'` finds only these two READMEs, so a reader who searches for the quoted rule finds nothing. The quote is left over from a draft that the README itself says was "reworded after review".
- **Taste.** The new exceptions are stated in other paragraphs while the original sentences still state the rule without them:
  - `SKILL.md:68` "the body is problem-first" and the package `README.md:36` say the same thing.
  - `SKILL.md:80`, Problem slot: "before any word about the fix".
  - `SKILL.md:226`: "Breaks come first" (in slot 3).
  - `SKILL.md:192`: "Six slots, in order".

  Each now has an exception elsewhere: the §4 rule 5 body that opens with breaks (`:83`, `:258-260`), and the lead that moves breaks ahead of slot 1 (`:198`, `:252`). The slot-3 table row and the slot-1 paragraph do carry the exception, so a reader of the whole section gets it right. A reader quoting `:226` or `:68` alone does not (`english-developer-style` §4, *Keep a truth condition in the sentence it limits*).
- Checked and consistent:
  - The new slot-1 sentence (`:86-87`) agrees with `:257-260`.
  - The table row (`:198`) agrees with `:234-255`.
  - The `§5` reference to the `BREAKING CHANGE:`/`!` row (`:706`) and the `§7` reference (`:787`) point at real text.
  - The skill-tree IDs are correct. `scripts/skill-tree.sh` on HEAD gives `4798053…`, which matches every `result*.md` run. The baseline `1f020ce…` is the skill tree at `4f69810`.
  - The README results table matches the six result files: each lead, where `grant insert` sits, and every word count (825/792/779/784/756/758).

## Item 2: claimed cases covered

The claims come from the commit message only (there is no task statement).

| Claim | Where the skill handles it | Evidence (case/run) |
| --- | --- | --- |
| Breaks lead unless the next release is a major | `SKILL.md:234-255` | `pgjdbc-4367-breaks`: patch release, version file |
| Next release read from the version file, the milestone, or the branch name | `:244-246` | version file only; milestone and branch name: **none** |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| What counts as a break: new failure, return value or result shape, removed option, changed default, changed error code, extended failure | `:234-241` | 4367 covers new failure, result shape, and extended failure; removed option, changed default, and changed error code: none |
| Commit body keeps the problem first, breaks first under `User-visible:` | `:257-258` | **none** |
| Squash copies the description into the body, so the lead stays | `:258-260` | **none** (the 4367 prompt is `merge 0 squash 3 plain 37`, so rule 5 does not apply) |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break` |
| Run counts and outcomes in the commit message | case READMEs | consistent with the result files |

- The cases with no evidence are listed under item 3 as missing partitions.
- **Command lines:** the 4367 README (`Running it`) gives `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring`. No script runs it. It is plain `git archive` with a pathspec, which behaves the same in every git version (it writes a tar to stdout), and `agent-packages/english-us-developer-style` exists. Nothing in this configuration changes the outcome, so this is not a finding.
- **Hunks:** every hunk is claimed except the version bump `1.4.0 → 1.5.0` in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and `agent-packages/change-description-authoring/apm.yml:2`. No sentence of the commit message mentions it. **Taste:** the bump is consistent across all three files and matches `apm-authoring` *Versions*.

## Item 3: boundaries, partitions, and the negative control

- **Substantive: the other value of the triggering setting is untested.** The rule is conditional on "the next release is a major". The only control, 4392, varies something else: whether a break exists. No run gives a target whose next release is a major and checks that the breaks stay first in slot 3, after Why and What. Without that run, the evidence cannot tell "the lead follows the release type" apart from "breaks always lead".
- **Substantive: further claimed partitions with no evidence:**
  - the release is unknown (no version file, no milestone, no branch name);
  - the release is read from the milestone or from a maintenance-branch name;
  - the commit-body order (`:257`);
  - the §4 rule 5 squash, where the body opens with breaks (`:258-260`);
  - the release-tool trailer branch (`:247-248`).

  The trial exercised one of these situations.
- **Pre-existing state:** the package is installed over 1.4.0. The change is prose only, with no persisted format, so there is nothing to check.

Table of added instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:234` "A break leads the description unless…", with the definition "what code that works on the released version gets" | A patch-branch refactor that renames a method in an internal, undocumented package only the project calls | A `Breaking changes` lead naming the internal rename, ahead of Why | "…code that uses what the project documents as supported (public API, a documented option)" |
| `:247` "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer…, the trailer decides" | A release-please repository, a change that breaks a public call | Either the trailer, which makes the release a major, so breaks stay last-ish in slot 3 and the reviewer meets the forced major bump after Why and What; or a lead. The sentence does not say what "decides" settles | State the result: "…the trailer makes the next release a major, so the breaks stay in slot 3" or "…and the breaks lead, since the reviewer decides whether to accept the major" |

Not findings:
- `:252`, ended by "after at most a short paragraph" (a one-line break needs no paragraph);
- `:255`, ended by "A change with no break has neither the lead nor an empty heading";
- `:239`, an extended failure to inputs that were documented as unsupported, ended by "Whether the old behavior was right does not decide it";
- `:257`, no input found where the problem-first commit body with the breaks first under `User-visible:` serves no reader.
- `:849` (checklist) is filed under item 5.

## Item 3a: level, placement, and the environment

- The rule sits in §2 next to the slot 3 text it modifies, and its checklist line is in §8. The placement is right.
- No sentence of the rule could appear unchanged in a generic tutorial: the pgjdbc example and the classification of extended failures are specific knowledge.
- **Taste:** the per-model directories are named `opus/` and `haiku/`. The sibling case directories (`research/problem-report-authoring/cases/*/`, `research/test-authoring/cases/*/`) use `claude-opus-5-5`, `claude-haiku-4-5`, and so on, which record the model version. Here the version appears only in the cost paragraph.
- Lint: `prompt.md`, `result.md`, `result-2.md`, and `baseline/result.md` all match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`. The 4367 README's line 17 is 122 characters long. The markdownlint config comes from `netcracker/.github` and is not in the repository, so I could not check the limit.
- `make check` (apm through `uvx`) needs the network and was not run.

## Item 4: names by content, not by position

- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the check titles name content.
- **Taste:** the 4367 README refers to checks by number: "Checks 1 to 3 are the rule under test; 4 to 6 are the guard", and the table headers "Lead (1)", "Once (5)". Each check has a bold name that could be used instead.

## Item 5: the failure report (analogue: detections)

- **Substantive:** the new checklist line at `SKILL.md:849-852` checks a weaker property than the rule. It asks whether the description opens with the break lines, not whether every outcome the break definition covers is among them. The one observed failure, `opus/result-2.md` leaving `grant insert` in Scope, passes this checklist line, because its description does open with break lines. The request is a clause along these lines: "and does no line in slot 3 or Scope meet the break definition (a failure extended to inputs that worked before, a different result shape)?"
- The checklist reaches the new rule through the Breaks line and the edited Problem line.

## Item 6: what the writer says it verified

- **The bad case and the exemplar are present.** The baseline runs on the parent tree fail lead, result shape, and `grant insert`. The runs with the rule pass, and the one partial failure is reported honestly.
- **Substantive: the noise check has no baseline.** For the control, the README compares output length with the author's draft (209 words, against 241–256 words). There are no runs of the control on the parent skill tree, so nothing shows whether the rule made the no-break output grow. The request is baseline runs of `pgjdbc-4392-no-break` on tree `1f020ce…` for both models.
- **Taste:** the commit message says "on Opus and Haiku (effort high)", which reads as both models at high effort. The README says Opus ran at the session default.

## Item 7: siblings of the change

- **Substantive:** `SKILL.md:300-301` lists the heading set that "matches the slots": `Why`, `What`, `User-visible changes`, `How to verify`, `Scope`. It does not include the new `Breaking changes` heading that `:252` introduces.
- All the other places that list or route to the package are consistent:
  - the version is 1.5.0 in all three manifests;
  - the umbrella `qubership-repo-essentials` depends on it by path, with no version pin;
  - the package README gained a bullet that matches the rule;
  - `english-developer-style:570` defers the marking of breaks to this skill.
- No prose counts the slots or the headings differently than before.
- **Taste:** a 0.x project, where the next minor may break under semver, is not addressed. Whether a minor such as 0.10 counts as "a major" is left to the agent.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule wording ("promises compatibility") that the skill does not contain | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote `SKILL.md:234` as committed |
| No run where the next release is a major (the control for the condition itself) | Substantive | `cases/` | Add a case or run with a major target, checking that breaks stay in slot 3 |
| Claimed partitions with no evidence: unknown release, milestone or branch name, commit-body order, §4 rule 5 squash lead | Substantive | `SKILL.md:244-260` | Add runs, or narrow the commit message's claims to what was run |
| "the trailer decides" does not say what it decides; under release-please the lead may never fire | Substantive | `SKILL.md:247-248` | State the outcome for both the description and slot 3 |
| The break definition covers internal, unsupported APIs | Substantive | `SKILL.md:234-236` | Limit it to what the project supports (public API, documented options) |
| The checklist line checks the lead, not that every break is in it | Substantive | `SKILL.md:849-852` | Add the clause asking whether slot 3 or Scope still holds a break |
| No baseline runs for the no-break control, so growth is measured only against the draft | Substantive | `cases/pgjdbc-4392-no-break/README.md` (Results) | Run the control on tree `1f020ce…` for both models |
| The heading set omits `Breaking changes` | Substantive | `SKILL.md:300-301` | Add it to the set |
| "problem-first", "before any word about the fix", "Breaks come first", "Six slots, in order" stated without the new exceptions | Taste | `SKILL.md:68,80,192,226`; package `README.md:36` | Put the condition in those sentences |
| Version bump not claimed by the commit message | Taste | `apm.yml:168` and two others | One sentence in the commit message |
| "(effort high)" reads as applying to both models | Taste | commit message | "Haiku at effort high, Opus at the default" |
| Model directories named `opus/` and `haiku/`, unlike the siblings' versioned names | Taste | `cases/*/opus`, `cases/*/haiku` | Use the versioned model ID |
| Checks referred to by number | Taste | `cases/pgjdbc-4367-breaks/README.md` | Refer to them by their bold names |
| 0.x projects not addressed | Taste | `SKILL.md:244` | Say whether a 0.x minor counts as a major |

Not checked: I did not re-run any model, did not run `make check` or the linters (network or external config), could not resolve `origin/main` locally (the baseline was checked only against the parent commit's tree), did not verify the cost figures, and did not review the prose for style alone.
