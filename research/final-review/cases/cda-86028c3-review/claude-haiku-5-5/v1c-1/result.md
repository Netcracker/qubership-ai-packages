# Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD`

**Scope.** One commit, `86028c3`: "lead the description with breaks unless the next release is a major". It changes the `change-description-authoring` skill (SKILL.md, package README, version files) and adds research cases under `research/change-description-authoring/cases/`. No code and no tests changed.

**Claimed cases.** No separate task statement was handed over, so the claims come from the commit message, as the skill allows. No test class comments apply.

**Previous report.** None exists, so there is no reconciliation table.

**Drift script.** Run: `comment-drift.py 4f69810… HEAD` printed nothing. The change has no source members, so the script has nothing to parse. Item 1 uses the analogue for a change with no code.

**Skills.** `final-review` was read in full. `english-developer-style` was loaded from the given directory for wording. `test-authoring` was not loaded because the change has no test code. The form also calls for the `apm-authoring` skill, which is not in the given directory, so its rules (one canonical example per concern, encode platform knowledge only, fix a bad output where the rule stops) were not checked against this change.

**Analogues used.** The skill's §2a: skill text and research cases instead of doc comments and tests.

---

### Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about other files, documents, and results.

- **Stale rule quote (substantive).** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The shipped rule is "A break leads the description unless the next release from the target branch is a major" (SKILL.md:234). The runs did test the shipped text (their skill-tree is `4798…`, which is HEAD's). Only the quote is stale. The 4392 README calls itself the control "for the rule" with the misquoted text.
- **"The trailer decides" (substantive).** SKILL.md:247–248 reads "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." A reader could take this as "the trailer makes the release major, so breaks stay in slot 3" or as "the trailer is always written, so the description need not lead". The two readings lead to different descriptions.
- **Other statements checked, all consistent:** table row 3 (SKILL.md:198), the §2 paragraph (234–260), the §8 checklist "Breaks" bullet (849–852), the §7 "no empty heading" rule, and the commit-body exception for rule 5 (257–260). Nothing else in the file says the description opens with the problem. The §3 changelog rule about breaking changes is a different artifact.

### Item 2: claimed cases covered

Claims from the commit message, each against the file that handles it and the run that tests it:

| Claim | Handled at | Covered by |
| --- | --- | --- |
| Lead unless the next release is a major | SKILL.md:234–238 | 4367 check 1, patch target only |
| Result shape and extended failure are breaks | SKILL.md:234–241 | 4367 checks 2 and 3 |
| A fix is not a break | SKILL.md:241 | 4367 check 4 |
| Unknown release → breaks lead | SKILL.md:249–250 | **none** (item 3) |
| Commit body: problem first, breaks as first `User-visible:` lines; squash keeps the lead | SKILL.md:257–260 | **none** (below) |
| No break → no lead and no section | SKILL.md:255, §7 | 4392 check 2, 4 of 4 runs |

- **Commit-body claim has no test (substantive).** Every case prompt asks for a pull request description. No result contains a commit body. The claim at SKILL.md:257–260 is therefore untested.
- **Run counts and outcomes checked against the files.** The 4367 case has 2 with-rule runs per model and 1 baseline run per model. The 4392 case has 2 runs per model. Baseline fails checks 1 and 2 for both models. With the rule, all four runs pass check 1 (lead) and check 2 (result shape). Check 3 (`grant insert`) passes in three of four, with `opus/result-2.md` leaving it in Scope. All of this matches the commit message.

**Commands the change tells a reader to run:**
- `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:29`, "Running it": the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". Alone, `git archive` writes a tar stream to stdout and copies nothing out. The documented form therefore does not produce the files the sentence promises. **Substantive.** The request is `git archive <rev> <path> | tar -x -C <dir>`, or a sentence saying the output is a tar stream.
- The `./gradlew` lines in the result files are the drafting models' output, not instructions from the change, so they are not listed.

**Hunks no sentence claims (substantive).**
- The version bump 1.4.0 → 1.5.0 in `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and `agent-packages/change-description-authoring/apm.yml:2`. The commit message does not mention it. The series bumps the version in every commit (for example 4f69810 went 1.3.0 → 1.4.0), so this is a convention. The form still counts an unclaimed hunk as a finding. The request is a sentence in the commit message that names the bump, or the bump moved to its own commit.

### Item 3: boundaries, partitions, and the negative control

- **Partitions not run (substantive).** The rule has three partitions: a patch target (lead), a major target (breaks stay in slot 3, after Why), and an unknown release (lead). Only the patch partition ran. The 4392 control has a known patch version and no break, so it is not a control for the major branch. The request is one run on a target whose version file or milestone reads as a major, checking that the breaks stay in slot 3 after Why. A second run with no version information would check the unknown-release default.
- **Pre-existing state.** Not applicable: this is a skill, with no installed state to meet.
- **Values users already pass.** Not applicable.

### Item 3a: level, placement, and the environment

- Level: a skill rule belongs in the skill, and the change keeps it there. The package README, the root `apm.yml`, and the marketplace entry match at 1.5.0. Read as a check, `make check` (`apm pack --check-versions`) should pass. It was not run, because `apm` is not available offline.
- Lint: `research/.../pgjdbc-4367-breaks/README.md:17` is 121 characters long, and the repo ships a `markdown-line-length-120` package. The super-linter filter does not exclude the case READMEs, so the markdown gate would flag this line if it runs. **Substantive, low impact.** The request is to wrap the line. The gate itself could not run here: `.markdownlint.json` is not in the checkout, and markdownlint is not installed.

### Item 4: names by content, not by position

- `research/.../pgjdbc-4367-breaks/README.md:25`: "Checks 1 to 3 are the rule under test; 4 to 6 are the guard…". The checks have names (lead, result shape, `grant insert`, fix out, once, literals). **Taste.** The preferred form names them.
- Slot numbers in SKILL.md are the skill's house convention, so they are not flagged.

### Item 5: the failure report

None. The change adds no assertions. The new §8 "Breaks" bullet detects the lead, and the case checks name what a failure looks like.

### Item 6: what the writer says it verified

None. The red evidence exists: the baseline runs on `origin/main` fail the lead and result-shape checks for both models. The 4392 control has no base run, but its purpose is to detect over-application, which only the with-rule run measures. The commit states honestly that `grant insert` moved in three of four runs. The earlier Opus drafts are summarized in the README, not stored, so their evidence cannot be re-checked.

### Item 7: siblings of the change

- Sites checked, all updated or correct: the §2 table row, the §2 paragraph, the §8 checklist, the package README, the research README, and the three version files.
- `git grep` for "User-visible" outside the cases found only the SKILL.md itself.
- `research/change-description-authoring/phase3_result.md:331` and `phase2_prompt.md:123` carry the older "problem first" framing. Both are dated research, and the research README says the canonical copy is the package. **None.**

### §2a: table of added instructions

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release from the target branch is a major." | A fix with no break (4392) | Why first, no lead; 4 of 4 runs | Ended by its own condition: "A break…" |
| "Where nothing says which release it is, the breaks lead." | A major target (SKILL.md:247–249) | Not tested (item 3) | Ended by "unless… is a major" |
| "The commit body … with the breaks as the first `User-visible:` lines." | A change with no break | Problem first, no breaks lines | Ended by "with the breaks as…" (conditional on there being breaks) |

No row is a substantive finding. The major row is an untested partition (item 3).

---

## Report

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule sentence the skill does not contain | substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7–8`; `…/pgjdbc-4392-no-break/README.md:7` | Quote the shipped sentence from SKILL.md:234: "…unless the next release from the target branch is a major". |
| "The trailer decides, and it is written whatever the description does" has two readings | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:247–248` | State which: the trailer makes the next release major, so breaks stay in slot 3; and the trailer is written regardless. |
| Version bumps 1.4.0 → 1.5.0 not claimed by any commit sentence | substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Add a commit-message sentence naming the bump, or move it to its own commit. |
| Commit-body rule (problem first, breaks as first lines; squash keeps lead) has no test | substantive | `SKILL.md:257–260` | Add a run that produces a commit body on a break change and checks its first lines, or drop the claim. |
| Major-release and unknown-release partitions have no run | substantive | `SKILL.md:234–255`; `research/.../cases/` | Run a major-version target (breaks stay in slot 3 after Why) and a target with no version information (breaks lead). |
| Git archive recipe does not copy files out | substantive | `research/.../pgjdbc-4367-breaks/README.md:29` | Write `git archive <rev> <path> \| tar -x -C <dir>`, or say the output is a tar stream. |
| Case README line over 120 characters, against the repo's line-length convention | substantive (lint, if the gate applies) | `research/.../pgjdbc-4367-breaks/README.md:17` | Wrap the line. |
| "Checks 1 to 3… 4 to 6" refers by ordinal where the checks have names | taste | `research/.../pgjdbc-4367-breaks/README.md:25` | Name the checks, for example "the lead, result-shape, and `grant insert` checks are the rule under test". |

**Not checked:** I did not re-run the drafting agents or the markdown gate. `make check` (apm), `make test`, and the super-linter were not run, because they need `apm`, markdownlint, or network, and none of them are available here. The result files were read and grepped, not re-generated. The `apm-authoring` rules were not available in the given skills directory. No files were changed and nothing was committed.
