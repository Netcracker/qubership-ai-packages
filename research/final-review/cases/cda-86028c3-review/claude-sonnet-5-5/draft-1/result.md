# Final review: `4f69810..HEAD` (`86028c3`)

**Task statement:** none was given. The claimed cases come from the commit message alone.

**Claims taken from the commit message:**
1. The description opens with the break lines unless the next release is a major.
2. A break is defined as: a new failure, a different return value or result shape, a removed option, a changed default or error code, or a failure extended to inputs that worked before.
3. The commit body keeps the problem first, with the breaks as the first `User-visible:` lines.
4. Where squash copies the description into the commit, the lead stays.
5. A change with no break grows no section.
6. Case `pgjdbc-4367-breaks` ran on Opus and Haiku at effort high, two runs each with the rule and one each on `origin/main`. All four runs lead with the breaks and mark the result shape, and three of four move the extended failure out of Scope.
7. Control `pgjdbc-4392-no-break` ran twice on each model and grows no section.

**Setup:**
- This is a change with no code (§2a). The drift script ran and printed nothing, because it parses no members in Markdown or JSON.
- I loaded `apm-authoring`. I did not read `english-developer-style` in full. Wording enters this form only where a sentence reads wrongly.
- No previous report exists.
- The skill-tree ids check out. `47980534…` is the tree of the skill at `HEAD`, and `1f020ce5…` is the tree at `HEAD~1`, so the baselines ran on the base commit.

## Item 1: Comments consistent with the code and with each other

Analogue used: every statement one changed file makes about another file or section.

- **Finding 1 (substantive).** `cases/pgjdbc-4367-breaks/README.md:6-7` and `cases/pgjdbc-4392-no-break/README.md:5-6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The rule's actual lead-in is "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`). A reader searching the skill for the quoted text finds nothing, and the two wordings differ in what they cover. "Promises compatibility" suggests a patch or minor release, and the skill says "not a major". Request: quote the shipped sentence in both READMEs.
- **Finding 2 (substantive).** The commit message says `pgjdbc-4367-breaks` ran "on Opus and Haiku (effort high)". The case README says "Haiku ran at effort `high`; Opus at the session's default". One of them is false. Request: correct the commit message or the README to whichever happened.
- **Finding 3 (substantive).** `SKILL.md:247-248` says "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does". It does not say what the trailer decides, and two readings are both plausible.
  - Reading A: the trailer makes the next release a major, so the breaks do not lead.
  - Reading B: the trailer is written in every case, and the lead rule still applies.
  - Reading A is circular. Every break written with that trailer would make the release a major, so on a repository using such a tool no break would ever lead. That is the opposite of what the paragraph is for.
  - Request: state which one holds. For example: "where the tool already bumps the major for the trailer, the trailer is the signal and the lead is not owed".
- Checked and consistent:
  - The version `1.5.0` is the same in `apm.yml`, the package `apm.yml` and `marketplace.json`.
  - The §4 rule 5, §5, §7 and "(below)" references resolve.
  - The new checklist rows match the rule.
  - The slot 1 sentence at `:86-87` agrees with `:257-260`.
  - The package README bullet matches the rule.
- No narration (`now`, `no longer`) was added outside the case results.

## Item 2: Claimed cases covered

Against each claim:
- **Lead on a patch-release target with breaks.** Covered by `pgjdbc-4367-breaks` checks 1 to 3. The prompt gives `gradle.properties` as `42.7.14` and no milestone (`prompt.md:10-11`).
- **Result-shape change and extended failure are breaks.** Covered by checks 2 and 3. `opus/result-2.md` fails check 3 and the README says so.
- **No section for a change with no break.** Covered by `pgjdbc-4392-no-break`.
- **Without the rule, Why goes first.** Covered by the two baselines.
- **Unless the next release is a major.** No case. See item 3.
- **Release read from a milestone or a maintenance-branch name.** No case. See item 3.
- **Where nothing says which release it is, the breaks lead.** No case. See item 3.
- **Commit body keeps the problem first with breaks as the first `User-visible:` lines.** No case. Both prompts ask for a description. See item 3.
- **Where squash copies the description, the lead stays.** The 4367 prompt carries a merge-model line, but I did not verify that it classifies as squash, so I count this as not shown.

Counts and claims checked against the files:
- Word counts in the case READMEs match `wc -w` for the 4367 runs (756, 825, 792, 758, 779, 784) and the 4392 runs (241, 251, 256, 249).
- The "Generated with Claude Code" line appears in each of the three Haiku 4367 results.

Commands the change tells someone to run: the `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring` line in the case READMEs. No script or CI job runs it, so it is `none`. Its outcome depends on the path existing at `<rev>`, which holds for any revision from `HEAD~1` on. The `gradlew` line is inside the case prompt as input to the drafter, not an instruction to a reader. No finding.

Hunks beyond the claim: none. The `research/…/README.md` additions are the cases entry and the dated note, both claimed by the commit.

## Item 3: Boundaries, partitions, and the negative control

- **Finding 4 (substantive).** The only break trial runs one partition: a patch release (`42.7.14`) where the release is read from a version file. The rule has four more partitions: the next release is a major; the release comes from a milestone; the release comes from a maintenance-branch name; nothing says. It also has a commit-body arm.
  - The negative control is a no-break change on the same target. It tests "no break, no section", not "break in a major".
  - The exception arm ("Where the next release is a major, the breaks stay first in slot 3") could regress without notice. An agent that always leads would pass every stored run.
  - Request: one case with the same breaking draft aimed at a target whose version file says a major, with the check "breaks are the first lines of slot 3 and no lead precedes Why". Or add a sentence to the case README that these partitions are untested.
- Pre-existing state: an installed `1.4.0` package replaced by `1.5.0`. Nothing is read or replaced by the change at runtime. None.
- Replaced mechanism, limits, pass-through values: not applicable.

**Added instructions:** 4, no rows.
The four are the break definition, the lead-unless-major rule with how to read the release, the lead's format, and the commit-body arm.
**Not findings:** `:234-241`, `:242-250`, `:252-255`, `:257-260`.
Finding 3 is filed under item 1 as an ambiguity, as §2a requires.

## Item 3a: Level, placement, and the environment

- The cases sit under `research/change-description-authoring/cases/`, with the prompt, README and per-model results layout used by both cases. The research README lists the directory (`:49`).
- The rule lives in the skill's §2 pull request description, and the checklist rows are in §8.
- I did not run `make check`. It needs `uvx` and the network. Versions are aligned across the three manifests by reading.
- No finding.

## Item 4: Names by content, not by position

- `result-2.md` names the second run by ordinal. The README table cites it by path and gives each run its verdict, so the report is readable (taste, not filed).
- "The first … the second" in the README paragraph on rule drafts: each is identified by what it contains ("without the sentence on a failure extended…"). None.

## Item 5: The failure report

The change has no assertions or parameterized ids. Each case README lists numbered checks that name what to look at and what failure looks like. Check 6 names its literals. None.

## Item 6: What the writer says it verified

- Red runs: the baselines on `HEAD~1` (`opus/baseline`, `haiku/baseline`) fail checks 1 to 3 and pass 4 to 6.
- Green runs: the four rule runs, one of which fails check 3 (`opus/result-2.md`). That is stated plainly.
- The commit message also states that earlier drafts were run and not stored.
- Gap: the controls were not run on the baseline. The README table gives no base-commit result for `pgjdbc-4392-no-break`, so the "stays green on the base commit" half of the control is not shown. Taste. It is plausibly green, and the 4367 baselines also omit the section.

## Item 7: Siblings of the change

- Places that enumerate the package: `apm.yml` (root), `marketplace.json`, the package `apm.yml` and the package README. All were updated.
- Other skills that mention breaks, such as the changelog entry in §3 ("Breaking changes are marked in place and sorted first within their category"), are about a different artifact and do not conflict.
- A search for the old count found no sentence that counts the slots or rules differently.
- No finding.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Case READMEs quote the rule with wording the skill does not contain | Substantive | `cases/pgjdbc-4367-breaks/README.md:6`, `cases/pgjdbc-4392-no-break/README.md:5` | 1 |
| Commit message says Opus ran at effort high; README says session default | Substantive | commit `86028c3`; `cases/pgjdbc-4367-breaks/README.md` (Running it) | 1 |
| "The trailer decides" does not say what it decides, and one reading defeats the rule | Substantive | `SKILL.md:247` | 1 |
| Major, milestone, branch-name, unknown-release and commit-body arms have no case | Substantive | `cases/pgjdbc-4367-breaks/README.md` | 3 |

Not done: the marketplace gate (`make check`) and markdownlint were not run, since both need tools or network not available here.
