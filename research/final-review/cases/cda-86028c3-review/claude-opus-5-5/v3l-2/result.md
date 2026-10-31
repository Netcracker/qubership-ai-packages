I found five substantive findings, and the commit should not be treated as final until they're addressed. Two are contradictions inside SKILL.md, one is a stale quote of the rule in both case READMEs, and two are gaps in the evidence. I changed no files. `make check` and `make check-descriptions` pass offline.

**Inputs.** There was no task statement, so the claimed cases come from the commit message `86028c3` alone. The change has no code: it is a skill, a package README, version bumps, and research cases. I filled the form through the §2a analogues. The drift script (`comment-drift.py 4f69810 HEAD`) printed nothing, because the change has no code members to parse. I loaded `english-developer-style` from the given folder and `apm-authoring` from the repository. There is no previous report.

### 1. Comments consistent with the code and with each other
*Analogue: every statement one file makes about another.*

- **The case READMEs quote a rule SKILL.md no longer states.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". Searching SKILL.md for the quoted phrase finds nothing. The two versions also disagree on a 0.x minor bump: SKILL.md's wording leads with the breaks there, the README's wording would not.
- **Two checklist items contradict each other.** SKILL.md:844-845 ("Caller") asks for one line per outcome under "User-visible changes", breaks first. The new item at :849-851 ("Breaks") asks that slot 3 keep only the other outcomes when the release is not a major. A reviewer following the "Caller" item would flag a description that obeys the new rule.
- **Two rules send the extended failure to different places.**
  - SKILL.md:237-239 says a failure the change extends to inputs that worked before goes with the breaks, not in Scope.
  - SKILL.md:488-491 says that where only a maintainer can answer whether a compatibility break is intended, it stays in the Scope slot.
  - The `grant insert` draft frames the extension as a decision a maintainer weighs ("This change does not narrow which `INSERT` counts…"), so both rules fire on it.
  - `opus/result-2.md:33` kept it in Scope. The case README admits the new sentence moves the case "most of the time and not always".
- **The commit message and the case README disagree on effort.** The commit message says "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:29-30` says Opus ran at the session's default.
- Checked and consistent:
  - SKILL.md:86-87 (commit body slot 1) matches :257-260 and §4 rule 5.
  - The `BREAKING CHANGE:` / `!` reference matches the §5 table row at :706.
  - The §7 reference at :255 matches §7 "No section for an absent concern".
  - The package README bullet and the research README's `cases/` entry match.
  - The `skill-tree` ids match: `4798053…` is the skill tree at HEAD, and `1f020ce…` is the tree at the base commit, used for the baselines.
  - No sentence narrates the change.

### 2. Claimed cases covered
*Analogue: the section that handles each claim, and the trial run that shows it.*

| Claim (commit message) | Section | Evidence |
| --- | --- | --- |
| Lead with breaks when the next release is not a major, read from the version file | :234, :243-246, :252-254 | `pgjdbc-4367-breaks` check 1: 4 of 4 runs pass, both baselines fail |
| Next release read from a milestone or a branch name | :245-246 | none |
| Lead where nothing says which release it is | :248-250 | none |
| Major release: breaks stay first in slot 3 | :254 | none |
| A result-shape change is a break | :235-237 | check 2: 4 of 4 runs pass, both baselines fail |
| An extended failure is a break | :237-239 | check 3: 3 of 4 runs pass |
| Removed option, changed default, changed error code | :237-238 | none (illustrative, not claimed as tested) |
| Commit body keeps the problem first, breaks first among `User-visible:` lines | :257-258 | none |
| Under a squash that copies the description, the lead stays | :258-260 | none |
| A change with no break grows no section | :255 | `pgjdbc-4392-no-break`: 4 of 4 runs pass |

- The rows marked `none` are partitions the change claims but has no evidence for; they are filed under item 3.
- **The rule is not mechanically checkable.** The SKILL.md rule (:248) says "Read the next release from the target branch", but the case prompt says `gradle.properties` holds `42.7.14` and the latest tag is `REL42.7.14`. So the version file names the release already out, not the next one. All results then say "In 42.7.13 it…", taking the version from the draft. *Taste:* a case input whose version file names the next release would test the reading the rule asks for.
- Commands added: none. The cases re-quote the draft's `./gradlew` line as data.
- Unclaimed hunks: the 1.4.0 → 1.5.0 bump in `apm.yml`, the package `apm.yml`, and `marketplace.json`. The repository bumps on every `feat` and `make check` enforces alignment, so this is *taste*: one earlier commit's body names its bump ("Version 1.2.0 to 1.3.0").

### 3. Boundaries, partitions, and the negative control
*Analogue: the modes and situations the change claims, and the control arm.*

- **The trial covers one partition of six.** The runs cover a pull request description, a non-major release read from the version file, and a merge model where §4 rule 5 does not apply. These partitions have no evidence:
  - a major release, where the breaks stay in slot 3;
  - an unknown release;
  - a release read from a milestone or a branch name;
  - a release tool reading `BREAKING CHANGE:`;
  - the commit body order;
  - the description copied into the commit by §4 rule 5.

  The major-release arm is the negative control of the condition itself and is the one most owed.
- The no-break control exists (`pgjdbc-4392-no-break`) but has no baseline arm; see item 6.
- Pre-existing state: not applicable, since a skill package has no persisted state.

Added instructions: 3, no rows.
- The break definition (:234-241).
- The lead-unless-major rule with its release reading (:234, :243-255; the checklist line at :849-852 restates it).
- The commit-body order (:257-260, with :86-87 and :831).

Not findings:
- `:240-241` "a failure that now succeeds is a fix, not a break" ends the definition for the `BEGIN ATOMIC` fix and for the escape fix in 4392.
- `:254` "Where the next release is a major, the breaks stay first in slot 3" ends the lead for a major target.
- `:255` "A change with no break has neither the lead nor an empty heading" ends it for 4392.
- `:259-260` "the lead stays, because the reviewer reads the description before it becomes a body" ends the commit-body order under §4 rule 5.

The extended-failure input goes to item 1 as a conflict, not to this table.

### 3a. Level, placement, and the environment
None found.
- The rule sits in §2 "Pull request description", beside slot 3, where the slot table already said "Breaks first".
- The checklist line is in §8, and the cases are under `research/change-description-authoring/cases/` with the existing research.
- The registration entries are aligned: `make check` and `make check-descriptions` pass offline (27 descriptions within 1020 characters).
- The rule is specific to how a reviewer decides a non-major release, not a generic tutorial sentence.

### 4. Names by content, not by position
None found. The headings ("Breaking changes", "Lead", "Result shape is a break") and the case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) name content. The "first/second/third version" of the rule in the 4367 README's history paragraph is a time sequence, not a position in a file.

### 5. The failure report
None found.
- The new rule is reached by the §8 checklist ("Breaks", :849-852).
- The checklist detects the rule itself: it asks whether the description opens with the break lines and whether slot 3 keeps only the other outcomes, not a weaker property.
- The case checks name what a failure looks like ("fails: Why first", "fails: in Scope").

### 6. What the writer says it verified
- Bad case without the rule: both baselines fail checks 1 to 3 (4367 README results table). With the rule, 4 of 4 runs pass checks 1 and 2, and 3 of 4 pass check 3. The table and the stored word counts match: I re-counted with `wc -w` and got 756, 825, 792, 758, 779, 784.
- The reworded rule was re-run: the `skill-tree` ids equal HEAD's tree.
- **The no-break control was not run without the rule.** §2a asks, for an instruction added after a bad output, for a check that the output did not grow where the instruction is noise. `pgjdbc-4392-no-break` compares 241 to 256 words only with the 209-word draft. Without a baseline run there, growth from this rule cannot be told apart from growth caused by earlier rules, such as the added User-visible slot.

### 7. Siblings of the change
None found.
- `change-description-authoring` has no installed copy under `.claude/skills` or `.agents/skills`.
- The changelog's own breaks rule at SKILL.md:543 ("marked in place and sorted first within their category") is a separate artifact and stays consistent.
- `english-developer-style` (both dialects, line 570) defers the placement of breaks to this skill.
- The package README and the research README list the new behavior and `cases/`.
- The `description` fields in `apm.yml` and `marketplace.json` are unchanged, and the loading surface did not need to widen.
- No sentence counts the slots differently: "Six slots" still holds, because the lead is not a new slot.
- A `git grep` for "breaks first", "breaking change", and "promises compatibility" found only the stale quote filed under item 1.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a superseded wording of the rule ("promises compatibility") | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8`; `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading, "A break leads the description unless the next release from the target branch is a major" |
| Checklist "Caller" still asks for breaks first under "User-visible changes", against "Breaks" | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:844-845` | Add "or ahead of the Why slot where the Breaks item applies" to the "Caller" item |
| Scope rule (a maintainer question on a break stays in Scope) conflicts with the extended-failure rule; one Opus run followed Scope | Substantive | SKILL.md:488-491 against :237-239 | At :491, add that the break itself is a line among the breaks, and Scope keeps only the question |
| No evidence for the major, unknown, milestone or branch-name, release-tool, commit-body, and §4 rule 5 partitions | Substantive | SKILL.md:243-260; `research/change-description-authoring/cases/` | At least a major-release control arm (breaks stay in slot 3), or narrow the commit message to the partition tested |
| No-break control has no baseline arm, so "grows no section" is not shown against the old skill | Substantive | `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md:20-23` | Run `pgjdbc-4392-no-break` on the base skill and record the word counts beside the current ones |
| Commit message says effort high for Opus; the README says the session default | Substantive | commit `86028c3` body; `cases/pgjdbc-4367-breaks/README.md:29-30` | Say "Haiku at effort high" in the commit message |
| Case prompt's version file names the released version, not the next | Taste | `cases/pgjdbc-4367-breaks/prompt.md:11-12` | Give `gradle.properties` the next version (for example `42.7.15-SNAPSHOT`) so the case tests the reading the rule asks for |
| Version bump to 1.5.0 not named in the commit message | Taste | `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168`, `.claude-plugin/marketplace.json:291` | One sentence naming the bump, as an earlier commit did |

I did not re-run the model trials, run `make test`, or do a style pass over the prose. I did not open the cited pgjdbc#4367 rewrite, because there was no network access.
