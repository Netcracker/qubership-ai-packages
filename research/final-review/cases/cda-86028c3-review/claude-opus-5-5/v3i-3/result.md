I reviewed the single commit 86028c3 (`4f69810..HEAD`), "lead the description with breaks unless the next release is a major". I found six substantive findings; the main ones are a stale rule quote in both case READMEs, a checklist line that now contradicts the new rule, and no runs for the "major" and "unknown release" arms of the rule. Full report below.

# Final review: 86028c3

**Inputs.** There was no task statement, so the claimed cases come from the commit message only. There is no previous report.

**Kind of change.** It has no code: one skill (`change-description-authoring/SKILL.md`), the package README, version bumps in `apm.yml` and `.claude-plugin/marketplace.json`, and research regression cases. So the form is filled through the §2a analogues.

**Skills loaded.** `english-developer-style`, from the given path. `apm-authoring` was not loaded, because the brief allowed only the three supplied skills, so I cite its rule names only as final-review quotes them.

**Drift script.** `comment-drift.py 4f69810` was run and printed nothing: no changed file contains a member it can parse.

## Item 1: comments consistent with the code and with each other
Analogue: what each changed file says about another file, a section, or the rule.

- **Stale quote of the rule.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule under test as "A break leads the description where the next release from the target branch **promises compatibility**". `SKILL.md:234` says "…**unless the next release from the target branch is a major**". These are different conditions: an unknown release leads under the committed rule but does not "promise compatibility". A reader takes the wrong condition as the one tested.
- **Checklist line that now contradicts the rule.** `SKILL.md:844-846`, the *Caller* line, still asks for every outcome "under 'User-visible changes', breaks first". The new *Breaks* line (`:849-852`) and `:259-260` ("Slot 3 keeps the other outcomes") say that outside a major the breaks leave slot 3. A reviewer following *Caller* would flag a correct description for having no breaks in "User-visible changes".
- **"The trailer decides" has no object.** `SKILL.md:247-248`: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides". It can be read as "the trailer makes the release a major, so the breaks do not lead", or as "the trailer settles whether a break exists". The author writes that trailer, so under the first reading the author pre-empts the reviewer decision the rule exists for, and the text does not say whether that is intended.
- Cross-references checked and correct:
  - `§4 rule 5` (`:636`) is the "title and description" rule.
  - `§5` holds the `BREAKING CHANGE:` row (`:706`).
  - `§7` says there is "no section for an absent concern".
  - "§2, pull request description" exists.
  - The two new sentences in the package README match the rule.
  - The research README's new `cases/` row matches what the directory holds.
  - All four `skill-tree` ids match the skill tree at the time of the runs: `47980534…` is the tree at HEAD and `1f020ce5…` is the tree at the parent 4f69810.
- Not checked: the cited exemplar (the pgjdbc#4367 maintainer rewrite at `issuecomment-6079358908`) could not be fetched, because there is no network.

## Item 2: claimed cases covered
Analogue: each claim in the commit message, set against the section and the run that cover it.

| Claim (commit message) | Section | Run |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `SKILL.md:234-262` | `pgjdbc-4367-breaks`, 4 runs, all lead |
| Read from the version file | `:244-246` | 4367 (`gradle.properties` 42.7.14) |
| Read from the milestone, or from the branch name | `:245-246` | **none** |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| Next release is a major: breaks stay first in slot 3 | `:260-261` | **none** |
| Result-shape change counts as a break | `:235-237` | 4367 check 2, 4/4 pass |
| A failure extended to new inputs counts as a break | `:238-240` | 4367 check 3, 3/4 pass (README says so) |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | `:264-266` | **none** (every prompt asks for a PR description) |
| Squash copies the description into the commit: the lead stays | `:266-268`, `:86-87` | **none** (both prompts give `squash 3 plain 37` with bullets, so rule 5 does not apply) |
| A change with no break grows no section | `:262`, §7 | `pgjdbc-4392-no-break`, 4/4 |

Commands: the case READMEs name a `git archive <rev> …` form for extracting the skill, which no script runs. It is a recipe for reproduction, and nothing in this change depends on its outcome beyond the recorded tree ids, which match.

Hunks no sentence claims:
- **Version bump.** The `1.4.0 → 1.5.0` bump in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and `agent-packages/change-description-authoring/apm.yml:2` has no sentence in the commit message. Earlier commits d79c43d and 51b35c9 state it ("Version 1.2.0 to 1.3.0.").
- **Effort level.** The commit message's "on Opus and Haiku (effort high)" reads as both models at high effort. The case README says "Haiku ran at effort `high`; Opus at the session's default".

## Item 3: boundaries, partitions, and the negative control
Analogue: the release situations and merge paths the rule claims, plus the table of added instructions.

- **Partitions with no evidence.**
  - Next release is a major. This is the rule's own control arm: "unless … is a major".
  - Unknown release.
  - Milestone or branch name as the source.
  - The commit-body path.
  - The §4 rule 5 path.

  Every run is a patch-release PR description under the same merge model, so all evidence comes from one of the claimed situations. The "major" arm matters most: without it, nothing shows the rule ever stops firing on a real break.
- **Control.** `pgjdbc-4392-no-break` is a sound control for "no break", but it is the only control.
- **Earlier state.** No earlier state applies: the skill is reread in full on install.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:258` "under a `Breaking changes` heading where the description has headings" | a repository template with its own breaking-change section or checkbox | a second `Breaking changes` heading above the template's own section | "where the template has a section for breaks, fill that one" |
| `:266-268` "that body opens with its breaks and then its problem" | a squash with "title and description" (§4 rule 5) | break lines at the top of the body with no `User-visible:` label, so the search for that label misses them | "as `User-visible:` lines" |

Not findings:
- `:234`, ended by "code that works on the released version" (input: a break in a feature added since the last release).
- `:264`, ended by "Where §4 rule 5 makes the description the commit body".
- `:84-85`, ended by "and that leads with its breaks".
- `:262`, ended by "A change with no break has neither the lead nor an empty heading".

## Item 3a: level, placement, and the environment
Analogue: where the rule lives, whether the layout matches the repository, and the repository's own gates.

none. Checked:
- **Placement.** The rule sits in §2, under the pull request description and next to slot 3, which it amends, and the checklist gained a matching line.
- **Layout.** The cases sit under `research/change-description-authoring/cases/` with prompt, README, and results, matching the research-directory convention. All result and prompt files fall under `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`; the two case READMEs are linted.
- **Gates run.**
  - `scripts/check-skill-descriptions.py`: "ok: all 27 skill descriptions are within 1020 characters".
  - `make test`: PASS.
  - `apm pack --check-versions --check-clean` was not run; it needs `uvx` and likely the network.
- **Generic sentences.** No added sentence could appear unchanged in a tutorial: the rule is specific to release lines and merge models.

## Item 4: names by content, not by position
none. The case ids (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and check names ("Lead", "Result shape", "`grant insert`") name content. The skill's cross-references use section numbers and rule numbers, which is the file's existing style.

## Item 5: the failure report
Analogue: what each rule tells the reader to look at, and whether its detection detects that rule.

- Every new rule is reached by the checklist (`:849-852`).
- Each case check detects its own rule: check 1 tests position, and check 3 tests where the `grant insert` line lands.
- One gap: no check catches a lead that adds facts the prompt forbade. `opus/result.md` adds a "what to do" sentence per break that is not in the draft ("Call `execute()` and read each result with `getMoreResults()` instead", "Request key column names only where…"). The prompt says "add none that it does not carry". The README mentions this growth but scores it nowhere. The skill's slot 3 asks for "what the reader does about it", so the rule invites this. It is a weakness of the case, not of the rule, so I label it taste.

## Item 6: what the writer says it verified
- **Exemplar and bad case are named.** The baseline runs (`*/baseline/result.md`, on the parent tree) fail checks 1 to 3, and the runs with the rule pass them. The README records that the reworded rule moves `grant insert` in 3 of 4 runs, and the commit message says so.
- **Growth on the control has no baseline.** §2a asks, for an instruction added after a bad output, for "a check that the output there did not grow". The control reports 241 to 256 words against the draft's 209, but it has no baseline run. So nothing shows whether the rule or the existing skill caused the growth. The commit message says "two runs each" for the control, which is accurate, and claims nothing about growth.

## Item 7: siblings of the change
- **Places that list the package version.** Root `apm.yml`, `marketplace.json`, and the package `apm.yml` are all bumped together. `make test` passes, including its "version bump reflected after re-pack" check.
- **Wording of the rule.** `git grep 'promises compatib'` finds the two stale quotes filed under item 1. The sibling "breaks first" statements are `:198` (updated), `:221-222` (followed by the new qualifier), and `:845` (stale, filed under item 1).
- **Other skills.** The `english-developer-style` copies, `docs-page-authoring`, and `problem-report-authoring` route to this skill by name only and state no ordering of breaks.
- **Description surface.** The marketplace and front-matter descriptions are unchanged. The scope did not widen, so that is correct.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote the rule as "where the next release … promises compatibility"; the committed rule is "unless … is a major" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed sentence |
| The *Caller* checklist line still asks for breaks first under "User-visible changes", contradicting the new *Breaks* line | Substantive | `SKILL.md:844-846` | Qualify it: "breaks first where the next release is a major; otherwise in the lead (§2)" |
| "the trailer decides" has no object and reads two ways | Substantive | `SKILL.md:247-248` | Say what it decides, e.g. "the trailer makes the next release a major, and the breaks stay in slot 3" |
| Under §4 rule 5, the leading break lines get no `User-visible:` label, though the same paragraph says that label is what R4 and R5 search for | Substantive | `SKILL.md:266-268` | Add "as `User-visible:` lines" |
| A template's own breaking-change section is not addressed; the rule adds its own `Breaking changes` heading | Substantive | `SKILL.md:258` | "where the template has a section for breaks, that section, first" |
| No run of the "major", "unknown release", commit-body, or rule-5 partitions; every run is a patch-release PR description | Substantive | `cases/` | A case whose target's next release is a major, with a break (the control arm), and one with no version information; or narrow the commit message to the partition that was run |
| No baseline for the negative control, so its growth over the draft is not attributed | Substantive | `cases/pgjdbc-4392-no-break/README.md:23-25` | Two baseline runs of the control on the parent tree, with word counts |
| The `1.4.0 → 1.5.0` bump has no sentence in the commit message | Substantive | `apm.yml:168`, `marketplace.json:291`, package `apm.yml:2` | Add "Version 1.4.0 to 1.5.0.", as earlier commits do |
| "on Opus and Haiku (effort high)" reads as both at high effort; Opus ran at the session default | Substantive | commit message, paragraph 3 | "on Opus (default effort) and Haiku (effort high)" |
| No check catches what-to-do sentences the prompt forbade, which `opus/result.md` adds | Taste | `cases/pgjdbc-4367-breaks/README.md` checks | A check that no break line carries a fact the draft lacks |

What this review did not check: the full test suite beyond `make test` and the description gate, `apm pack --check-versions --check-clean` (needs uvx and likely the network), the pgjdbc#4367 exemplar and the maintainer comment (no network), whether `origin/main` matched the parent when the baselines ran (no local `origin/main`), and a style-only pass over the prose.
