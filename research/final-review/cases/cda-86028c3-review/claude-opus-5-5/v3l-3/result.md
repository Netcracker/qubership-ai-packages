# Final review: `4f69810..86028c3`, one commit (`feat(change-description-authoring): lead the description with breaks unless the next release is a major`)

There was no separate task statement, so the claimed cases come from the commit message alone, plus the case READMEs. The change has no code: a skill, its package README, version entries, a research README, and two regression cases. Every item below uses the §2a analogue. I loaded `english-developer-style` from the given skills directory. `apm-authoring` is not among the three skills I was allowed to load, so I cite its rules by the names final-review gives them and did not read them. I ran the drift script (`comment-drift.py 4f69810 HEAD`). It printed nothing and exited 0, which is expected because no changed file is in a language it parses.

## Item 1: comments consistent with the code and with each other

**Analogue used:** every statement one changed file makes about another file, plus contradictions inside SKILL.md.

Line numbers below refer to `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` at HEAD.

**Checked and consistent:**
- Slot 1 of the commit body (`:86`) and the checklist "Problem" line (`:831`) match the new commit-body paragraph (`:257`).
- The package README bullet matches the rule.
- The research README's `cases/` row and its closing paragraph match the directory.
- The case result tables match the commit message: three of four runs move `grant insert`, with `opus/result-2.md` the exception, and the control grows no section.
- The word counts in both READMEs match `wc -w` for all ten result files.
- The `skill-tree` ids match the trees. `4798053…` is the HEAD tree of the skill directory, and `1f020ce…` is the base commit's tree, used for the baselines.

**Findings:**

1. **Stale rule name in both case READMEs.**
   - `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7` and `pgjdbc-4392-no-break/README.md:6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
   - SKILL.md has no such sentence. The committed heading at `:234` is "…unless the next release from the target branch is a major".
   - A reader searching SKILL.md for the quoted rule finds nothing. The quote also states a different condition: "promises compatibility" versus "is not a major", which differ for a 0.x minor release.

2. **The Scope rule contradicts the new rule.**
   - `:488–492` still says that where only a maintainer can answer "whether a compatibility break is intended, keep it in the Scope slot as a question".
   - The new paragraph (`:240`) says an extended failure "goes with the breaks, not in the Scope slot".
   - The `grant insert` input is exactly this case: the draft frames it as a limitation that a maintainer accepts. `opus/result-2.md:35` kept it in Scope, and the case README says only "not always".
   - Nothing in the change reconciles the two rules.

3. **The checklist contradicts itself.**
   - The "Caller" line (`:844–846`) still asks for "one line per distinct outcome under 'User-visible changes', breaks first".
   - The new "Breaks" line (`:849–852`) and `:253` say that, outside a major release, slot 3 "keeps only the other outcomes".
   - An agent that follows the Caller line in a patch release writes each break twice, once in the lead and again first in slot 3. That fails the case's own check 5, "Stated once".

4. **"The reviewer's first question" no longer holds.**
   - `:203–204` says "the reviewer's first question is why that version should change".
   - The new `:243` says that in a release that is not a major, "the reviewer's first decision is whether the change may ship in it at all".
   - For a non-major release, both sentences claim to be the reviewer's first question.

5. **"Read the next release from … its version file" reads two ways.** This finding comes from the instruction table, step 2.
   - The examples the rule itself names (`Cargo.toml`, `package.json`) often hold the version last released rather than the next one.
   - The case's own fixture has this shape: `gradle.properties` says `42.7.14`, and the latest tag is `REL42.7.14`.
   - Right after a major release (file `2.0.0`, tag `v2.0.0`), an agent reads "major" and does not lead with the breaks. But the next release from that branch is 2.0.1, and the break ships unflagged. That is the failure the rule exists to prevent.

6. **"The trailer decides" reads two ways.**
   - `:247–248`: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides, and it is written whatever the description does."
   - Reading A: the break gets the trailer, the trailer makes the release a major, so the breaks never lead. Under this reading the rule never fires in any semantic-release repository.
   - Reading B: the trailer decides only the version number, and the description still leads, because the reviewer must decide whether to accept a major bump.
   - The text does not say which reading it means.

None of the changed text narrates the change ("now", "no longer").

## Item 2: claimed cases covered

**Analogue used:** for each case the commit message claims, the section that handles it and the evidence that tests it.

| Claimed case (commit message) | Section | Evidence |
| --- | --- | --- |
| Breaks lead in a patch release, read from the version file | `:234–255` | `pgjdbc-4367-breaks`, all 4 runs pass check 1 |
| Result-shape change counts as a break | `:235–237` | 4367 check 2, 4/4 |
| Extended failure counts as a break, not Scope | `:238–240` | 4367 check 3, 3/4 (`opus/result-2.md` fails) |
| Next release is a **major**, so breaks stay in slot 3 | `:254–255` | **none** |
| Release read from the **milestone** or **branch name** | `:244–246` | **none**: the fixture states "no milestone" and uses `master` |
| **Unknown** release, so breaks lead | `:248–250` | **none** |
| `BREAKING CHANGE:` trailer decides | `:247` | **none** |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | `:257–258` | **none**: every run writes a description |
| Squash with "title and description": the lead stays in the body | `:258–260`, `:86–87` | **none**: the fixture's merge model is default squash with bullets |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`, 4/4 |

Each **none** is a claimed case without evidence. The skill does name a detection for the claimed rule: the checklist "Breaks" line.

**Commands:** `pgjdbc-4367-breaks/README.md:26` shows `git archive <rev> agent-packages/…/change-description-authoring` and says it "copies the skill out of the checkout".
- No script or CI job runs it: **none**.
- `git archive` writes a tar archive to stdout. As written it copies nothing to disk unless it is piped to `tar -x -C <dir>`.

**Hunks the message does not claim:** the three `1.4.0` → `1.5.0` version entries (`.claude-plugin/marketplace.json:291`, `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`).
- The earlier commits on this package state their bump in the body: `51b35c9` has "Version 1.1.0 to 1.2.0.", and `d79c43d` has "Version 1.2.0 to 1.3.0.". This commit does not.
- `make check` passes, so the entries agree with each other.

## Item 3: boundaries, partitions, and the negative control

**Analogue used:** the modes the change claims; the negative control; the table of added instructions.

**Partitions:**
- The rule's condition has three branches: non-major (known), major, and unknown. The evidence covers only "non-major, known from the version file".
- `pgjdbc-4392-no-break` is the control for the "has a break" condition. It is not a control for the "unless major" branch.
- No case runs the same 4367 draft with a fixture whose next release is a major (for example, `gradle.properties` at `43.0.0-SNAPSHOT`). That run would show the lead does *not* appear.
- No case covers the commit-body mode or the "title and description" mode.

**Existing state:** a pull request description that already exists and is rewritten (§7a) is a partition the change does not mention. It is not owed, because §7a's growth budget applies unchanged.

Added instructions: 4, no rows.
- `:234` break leads, with its definition of a break
- `:243` how to read the next release
- `:252` the opening shape and heading
- `:257` commit-body order

For `:243` and `:247`, the inputs where the instruction does not help (a version file that holds the released version, and a semantic-release repository) are filed as ambiguities under item 1, findings 5 and 6.

Not findings:
- `:234`: a change to behavior added since the last release. The definition "code that works on the released version" ends the rule there.
- `:252`: a pull request whose whole purpose is the break. "A fact stated in slot 3 is not restated in slot 2" (`:230`) ends the duplication.
- `:257`: one commit under rebase and merge. "Breaks first" in slot 4 is unchanged from the base.

## Item 3a: level, placement, and the environment

**Analogue used:** which file each rule lives in, the layout against sibling packages, and the repository's offline gate.

- The rule lives in §2 next to the slot-3 rules it amends. The checklist line is in §8. The cases sit under `research/change-description-authoring/cases/`, next to the phase files.
- `make check` (versions aligned and in sync) passed with exit 0.
- `make check-descriptions` passed: "all 27 skill descriptions are within 1020 characters".
- The super-linter `FILTER_REGEX_EXCLUDE` (`.github/super-linter.env`) excludes `research/…/prompt*.md` and `result*.md`, so the pasted model outputs are not linted, while the case READMEs are.
- No added sentence is general tutorial material: each one names this skill's slots or sections.

## Item 4: names by content, not by position

**Analogue used:** headings, cross-references, and case names.

- Case names are by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`), and the checks are named ("Lead.", "Result shape is a break.").
- Cross-references use section numbers ("§4 rule 5", "§2, pull request description"), which is the skill's existing convention.
- The result table refers to checks by number, but each column header carries the name as well ("Lead (1)").

**none**

## Item 5: the failure report

**Analogue used:** what each rule tells the reader to look at, and whether the checklist reaches every rule.

The checklist's "Breaks" line reaches `:234–255`. It does not check:
- the definition of a break: result shape, and extended failures out of Scope;
- the commit-body order.

So a description that leaves the `grant insert` failure in Scope passes the checklist, because it opens with *some* break lines. That is the exact failure seen in `opus/result-2.md`, so the detection checks a weaker property than the rule. The checklist line itself is fine; it needs the added clause listed in the table below.

## Item 6: what the writer says it verified

**Analogue used:** the exemplar and the bad case named, and a growth check on an input where the rule adds nothing.

**What was shown:**
- On the exemplar, the base fails checks 1–3 and HEAD passes them (3/4 on check 3).
- The README says the rule was re-run after its rewording ("The version committed here, reworded after review"). The `skill-tree` ids confirm the runs used the committed tree.

**Gap:** the control has no growth check against a baseline.
- `pgjdbc-4392-no-break` has no `baseline/` run.
- Its four results run 241–256 words against a 209-word draft, which is 15–22% growth.
- Without runs on `1f020ce` there is no way to tell whether the rule or the existing skill causes that growth.

## Item 7: siblings of the change

**Analogue used:** places that list or route to the artifact, and sets the change adds a member to.

- The package README is updated. The marketplace description and the skill's frontmatter `description` are unchanged. This is correct, because the change does not widen when the skill loads.
- The umbrella `qubership-repo-essentials/apm.yml:10` references the package by path, with no version pin.
- `apm.lock.yaml` does not list the package.
- **Heading set:** `:300–301` lists "`Why`, `What`, `User-visible changes`, `How to verify`, and `Scope`" as "one set that matches the slots". The new `Breaking changes` heading (`:252`) is not in that set.
- **Changelog:** §3 (`:543`) already sorts breaks first within their category, which is consistent. No count of slots changed: the description still has "Six slots".

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Both case READMEs quote a rule heading that SKILL.md does not contain, with a different condition | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed heading, "…unless the next release from the target branch is a major" |
| 2 | The Scope rule still sends "whether a compatibility break is intended" to Scope, against `:240` | Substantive | SKILL.md `:488–492` | Add a clause: the break itself is a line in the lead (or in slot 3), and Scope carries only the question to the maintainer |
| 3 | Checklist "Caller" still asks for breaks first under "User-visible changes" | Substantive | SKILL.md `:844–846` | Add "…breaks first, unless they lead the description (Breaks below)" |
| 4 | "Reviewer's first question is why" conflicts with "first decision is whether it may ship" | Substantive | SKILL.md `:203–204` | Add "…after any breaks that lead (below)" |
| 5 | A version file that equals the latest release tag names the released version; read as the next one right after a major, the breaks do not lead | Substantive | SKILL.md `:244–246` | Add: a version equal to the latest release tag is the released one, so nothing says which release is next, and the breaks lead |
| 6 | "The trailer decides" reads as "a break with the trailer never leads" | Substantive | SKILL.md `:247–248` | State which reading is meant, for example "the trailer decides the version; the breaks still lead, because the reviewer decides whether to accept a major" |
| 7 | Major, unknown, milestone or branch name, trailer, and commit-body / rule-5 modes are claimed with no case | Substantive | commit message; `cases/` | Add at least the 4367 draft with a major next release (negative control for "unless major") and one rule-5 squash fixture, or narrow the commit message's claims |
| 8 | The negative control has no baseline, so 15–22% growth over the draft cannot be attributed | Substantive | `cases/pgjdbc-4392-no-break/` | Add `opus/baseline/` and `haiku/baseline/` runs on `1f020ce` and compare word counts |
| 9 | The checklist "Breaks" line passes a description that leaves an extended failure in Scope | Substantive | SKILL.md `:849–852` | Add "and is every result-shape change and extended failure among them, none left in Scope?" |
| 10 | The version bump is not stated, while earlier commits on this package state theirs | Substantive | `apm.yml:168`, `.claude-plugin/marketplace.json:291`, package `apm.yml:2` | Add "Version 1.4.0 to 1.5.0." to the body |
| 11 | "(effort high)" in the commit message reads as covering Opus, but the README says Opus ran at the session default | Substantive | commit message, third paragraph | "on Opus (session default) and Haiku (effort high)" |
| 12 | The `git archive <rev> <path>` command writes a tar to stdout and copies nothing | Taste | `cases/pgjdbc-4367-breaks/README.md:26` | `git archive <rev> <path> \| tar -x -C <dir>` |
| 13 | The heading set at `:300` does not list `Breaking changes` | Taste | SKILL.md `:300–301` | Name it in the set, or say it adds to any set |

I did not run the regression cases or any model, I did not review the prose for style alone, and I did not read `apm-authoring` (not among the allowed skill copies).
