**Final review of `4f69810..HEAD` (one commit, `86028c3`)**

**Inputs.** There is no task statement. Item 2 takes its claimed cases from the commit message alone. The previous report is none. The change adds no code, so it is a skill plus research cases and fills the §2a analogues. The drift script was not run because there are no members to parse. I loaded `english-developer-style` and `test-authoring` from the given skills directory. `apm-authoring` and `docs-page-authoring` are not in that directory and were not loaded.

## Item 1: Comments consistent with the code and with each other (analogue: statements one file makes about another)

Two findings.

- **Stale quoted heading.** `cases/pgjdbc-4367-breaks/README.md:8` and `cases/pgjdbc-4392-no-break/README.md:6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 now reads "A break leads the description unless the next release from the target branch is a major." The quoted wording is the first draft of the rule. A reader who greps SKILL.md for the quote finds nothing. The READMEs also cite "SKILL.md §2" and never say that the rule sits in the pull-request-description subsection.
- **Effort level contradicts the commit message.** The commit message says "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says "Haiku ran at effort `high`; Opus at the session's default". The 4392 README says "Haiku at effort `high`" only. At least one source is wrong about the Opus effort.

Checked and consistent:
- The §4 rule 5, §2, §5, and §7 references all resolve.
- `BREAKING CHANGE:` and `!` are in the §5 trailer table.
- The checklist line and the slot 1 sentence match the new rule.
- The package README, `apm.yml`, `agent-packages/.../apm.yml`, and `marketplace.json` all say 1.5.0.
- All `skill-tree` ids equal `git rev-parse` of the skill directory. `47980534…` is HEAD and `1f020ce5…` is `HEAD~1`.

One more finding, on a sentence that now contradicts its neighbor:
- SKILL.md:222-226 says the slot is "breaks first" and that "Breaks come first". The PR table at line 198 now says "ahead of slot 1". Line 254 says "Slot 3 keeps the other outcomes" in the lead case. Read together, a break is both in slot 3 and no longer in slot 3. The new paragraph resolves this, but the intermediate lines (198 and 226) still read as "first within slot 3". Taste: add "within the slot" at 226, or point it to the new paragraph.

## Item 2: Claimed cases covered

The claimed cases come from the commit message only, and I say so.

| Claim | Evidence |
| --- | --- |
| Description leads with breaks, unless next release is a major | `pgjdbc-4367-breaks` check 1. Runs: `opus/result.md`, `opus/result-2.md`, `haiku/result.md`, `haiku/result-2.md`. |
| Result shape is a break | Check 2. |
| Extended failure (`grant insert`) is a break, not Scope | Check 3. |
| Negative control: no break means no section | `pgjdbc-4392-no-break`, four runs. |
| "Where nothing says which release it is, breaks lead" | **No case.** |
| "Next release is a major": breaks stay first in slot 3 | **No case.** |
| "A `BREAKING CHANGE:` trailer decides" | **No case.** |
| Commit-body behavior (breaks as first `User-visible:` lines) | **No case.** |
| Squash copying the description: "the lead stays" | **No case.** |

Substantive. The change adds five branches, and the cases exercise one: a patch release whose version is read from `gradle.properties`. The unknown-release, major-release, commit-body, and squash branches are claimed in the skill and have no run (item 3 repeats the partitions).

Commit-message numbers checked against the README table:
- "all four runs lead with breaks and mark the result shape": the table agrees.
- "three of four move the extended failure out of Scope (one Opus run left it)": `opus/result-2.md` is the exception, as stated.
- "two runs each with the rule, one each on origin/main": agrees.
- "Control grows no section in any run": agrees with the 4392 README.

Every hunk belongs to a sentence of the commit message. The version bumps and the cases README line are claimed by the 1.5.0 skill change. The research README `cases/` row and the 2026-10-20 sentence are claimed by "Two regression cases under research/…".

No command lines were added.

## Item 3: Boundaries, partitions, and the negative control

Substantive.
- **Release-kind partitions.** There is a control for "no break". The partitions "release is a major" and "release unknown" have no run. The "major" partition is exactly the one where the rule says to do the opposite (breaks stay in slot 3), so a regression there would not show.
- **Break-kind partitions.** Only 2 of the 4 break kinds in the definition are exercised: result shape and failure extended to inputs that worked before. The other two (removed or renamed option, changed default or error code) are not.
- **Fix-not-break control.** Check 4 ("the fix is not a break") passes on all six runs. There is no baseline arm that proves the check can fail.
- **Run counts.** n=1 to 2 per arm. The README states this and attributes the one miss to variance, which is honest. "Moves the case most of the time and not always" is fair.
- **State left behind.** A package upgrade over 1.4.0 leaves nothing on disk but the skill text. Not applicable.

Rules of the skill, one row per instruction added or widened:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Open with slot 3's break lines under a `Breaking changes` heading" | A one-paragraph change whose only break is one line | A heading plus one bullet above a one-sentence Why | "where the description has headings" ends the heading. A short paragraph before it is optional. — |
| "A break leads unless the next release is a major" | Repository with no version file, milestone, or branch name (a fresh repo) | Breaks lead | "Where nothing says which release it is, the breaks lead." This is the intended behavior, so no finding. Taste: say so for a repository with no release process at all, where "which release" has no meaning. |
| "A failure the change extends to inputs that worked before is a break" | A change that extends a failure to inputs that failed before only | — | "inputs that worked before" ends it. |
| "Whether the old behavior was right does not decide it" | A bug fix where the old output was plainly wrong (a wrong count) | Marks the corrected count as a break | Another rule asks the opposite: "a failure that now succeeds is a fix, not a break". That sentence covers only failure-to-success. A changed wrong return value is untouched. **Substantive:** a clause is needed, for example "a wrong value corrected to the documented one is a break only where callers may rely on it". |
| "Where a release tool bumps on `BREAKING CHANGE:`, the trailer decides, and it is written whatever the description does" | A project whose release tool is not present | Writes a trailer anyway | §5 table: "The tool is present". — |
| "Commit body keeps problem first; breaks as the first `User-visible:` lines" | A change with one commit and no breaks | — | "A change with no break has neither the lead nor an empty heading." — |
| "Where §4 rule 5 makes the description the commit body, the lead stays" | A squash with "title and commit details" setting, where the description does not become the body | Lead in the PR, problem-first body | The "Where §4 rule 5 makes…" condition. — |

Substantive on the squash row: the checklist line (SKILL.md:831-832) and slot 1 apply "a description that §4 rule 5 copies into the body and that leads with its breaks" and the commit-body paragraph (line 257-260) says the commit body "opens with its breaks and then its problem". SKILL.md:257 first says "the commit body keeps its order, problem first". Both statements hold in the same paragraph for two different commits, and a reader must discover that the second is the rule 5 exception. This is a conflict the skill resolves in the next sentence, so I rate it taste: a leading "except" would read better.

## Item 3a: Level, placement, and the environment

None. The cases sit under `research/change-description-authoring/cases/`, which the research README now lists, beside the phase files. Both cases share the prompt shape. The package README, the marketplace entry, and both `apm.yml` files are bumped together. I did not run the repository gate (Makefile/tests); see the last line.

## Item 4: Names by content, not by position

None. Case names are `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break`. The result files are `result.md` and `result-2.md`, which are ordinal. Taste: the READMEs' rows refer to them by path, so a future `result-3.md` insertion is harmless, but a content name would not need the table. The checks are "Check 1"/"Checks 1 to 3" by number, with a bold content label on each, so the numbers are fine.

## Item 5: The failure report

Analogue: every rule has a detection, and the detection detects the rule it is attached to.

- Checks 1 to 3 detect the lead and the breaks. Check 5 ("stated once") and 6 ("literals kept") guard other properties.
- Check 4 passes in the baseline as well, so it is a guard rather than a test of the rule. The README says so ("4 to 6 are the guard against the rule costing other facts").
- Substantive: the checklist line at SKILL.md:849-852 tests lead and slot 3, but not "the fix is not a break" or "stated once", which are where the rule's text is most likely to regress. Taste, since the case README covers them.

## Item 6: What the writer says it verified

Stated: the red arm is `origin/main` baselines (both models fail checks 1 to 3) and the green arm is the rule. For the control, the evidence is "pass in all four runs", with no baseline arm. A control that has no failing arm shows the rule did no harm, not that the check could fail. The README does not say so. Nothing else is stated. Substantive: for the 4392 control, one `origin/main` baseline run shows that the check "no empty section" can fail, or the sentence should say that it cannot.

Also, the README states that earlier Opus runs of two drafts are "summarized in the case README, not stored", which makes the 4367 table's version claim unauditable. That is stated openly. Taste.

## Item 7: Siblings of the change

- **Set members and sizes.** The change adds a rule, not a member of a set, so the search is for places that name the other slot rules. SKILL.md:221 ("the slot is not a list of breaks only") is fine. Line 543-544 (changelog entry: "Breaking changes are marked in place and sorted first within their category") is a sibling statement about the changelog, which the new rule does not touch. I read it as consistent, since the changelog has no Why slot.
- **Other surfaces.** The `references/` directory of the package was not read for the old "breaks first within slot 3" wording. `git grep -n 'Breaks first'` hits only SKILL.md:198 and 845. Line 845-846 (checklist: "carry one line per distinct outcome under 'User-visible changes', breaks first") is now ambiguous in the same way as 198 and 226. Taste.
- **Frontmatter.** The `description:` of SKILL.md (line 3) does not mention the lead-with-breaks rule, and the plugin README gained a bullet. The load decision is driven by the frontmatter. This skill is loaded for any change description, so the rule is reached anyway. None.
- **Set of passes.** The `change-description-authoring` entry appears in `apm.yml`, `marketplace.json`, and the package `apm.yml`, all at 1.5.0. `apm.lock.yaml` was not changed; I did not check whether it pins this package's version. Not checked.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the rule's first-draft heading, "promises compatibility", which is not in SKILL.md | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the current heading, "A break leads the description unless the next release from the target branch is a major", and name the subsection. |
| Commit message says Opus ran at effort high; the README says the session default | Substantive | commit message; `pgjdbc-4367-breaks/README.md:33` | Make the two agree; state the Opus effort in the 4392 README too. |
| Branches claimed with no run: unknown release, major release, commit body, squash copy, trailer | Substantive | SKILL.md:243-260 | Add a case per branch, or have the README say these five are unrun. The major-release case is the one that can regress the others. |
| The 4392 control has no baseline arm, so "no empty section" is shown to hold but not to be able to fail | Substantive | `pgjdbc-4392-no-break/README.md:22-25` | Add one `origin/main` run, or say the check has no failing arm. |
| "Whether the old behavior was right does not decide it" meets "a failure that now succeeds is a fix" with no rule for a wrong return value corrected | Substantive | SKILL.md:240-242 | Add a clause on a value corrected to the documented one. |
| Only 2 of the 4 break kinds in the definition appear in a case | Taste | SKILL.md:235-238 | Add a case for a removed option or changed default, or leave it. |
| "Breaks first" at lines 198, 226, 845 reads as first within slot 3, beside the new "ahead of slot 1" | Taste | SKILL.md:198, 226, 845 | Add "within the slot" or point to the new paragraph. |
| Commit body "keeps its order, problem first" is followed by the rule 5 exception | Taste | SKILL.md:257-260 | Lead with the exception. |
| Checklist does not test "fix is not a break" or "stated once" | Taste | SKILL.md:849-852 | Add the two checks. |

I did not run the repository gate or the suite, did not run any draft case, did not read the `references/` files or `apm.lock.yaml`, and did not do a style-only pass over the prose.
