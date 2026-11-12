## Final review: 86028c3 (`4f69810..HEAD`)

**Scope and inputs.** The change is one commit, `86028c3`, which edits the change-description-authoring skill (`agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`), its package README and version files, and adds two regression cases under `research/change-description-authoring/cases/`. No code or test changed. The claims come from the commit message, since no separate task statement was given. No previous report of this form exists for this change.

**Skills and analogues.** I loaded `final-review` and `english-developer-style`. I did not load `test-authoring`, because no test changed. The artifact's authoring skill (`apm-authoring`) is not in the skills directory I was given, so I did not load a copy and its rules are not checked. The §2a analogues are used throughout: comments are statements about other files and cases, and the checklist table is in Item 3.

**Drift script.** `comment-drift.py 4f698106 HEAD` was run and printed nothing, exit 0. No code member changed, so the script has nothing to parse.

**Gates run offline.** `check-skill-descriptions.py`: ok, 27 descriptions. `misspell` over the changed Markdown: clean.

---

### Item 1: comments consistent with the code and with each other

Checked the new SKILL §2 text against the slot table (line 198), the slot 1 paragraph (86–89), the §4 rule 5 cross-reference, and the §8 checklist (831, 849–852). They agree, except for the two conditional sentences below (S3, S4). The research README statements about the rule and about the branch are checked against the repository (S1, S2).

### Item 2: claimed cases covered

Claimed cases, and where each is covered:
- Break lead on a patch release: `pgjdbc-4367-breaks` checks 1–3.
- Result shape as a break: check 2.
- Later-statement failure as a break: check 3.
- Fix not a break: check 4.
- No break means no lead and no heading: `pgjdbc-4392-no-break` checks 1–2.
- Major release, unknown release, trailer-decided release, commit body and squash lead under §4 rule 5: **no case** (S5).

Command recipe: the `git archive` line in `pgjdbc-4367-breaks/README.md:29` does not produce files (S7).

Hunks: the version bumps in three files are not named in the commit message (S8). The case README's cost paragraph is not claimed by the commit; its figures were not checked (no network).

### Item 3: boundaries, partitions, negative control

The negative control exists only for the no-break case, and it was run only on the new tree (S6). The major-release partition has no control (S5).

§2a table of added instructions:

| Instruction (SKILL.md) | Input it does not serve | What an agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release … is a major" (234) | A change that breaks nothing | Break lines, or an empty "Breaking changes" heading | Already in the text: "A change with no break has neither the lead nor an empty heading (§7)" (255). Not a finding |
| Same instruction | A break in a major release | Breaks first in slot 3, after Why | Already in the text: "Where the next release is a major, the breaks stay first in slot 3" (254). Not a finding |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!`, the trailer decides" (247–248) | A commit with the trailer in a repository whose tool bumps the major | Undetermined: the sentence does not say what the trailer decides | None in the text (S3) |

### Item 3a: level, placement, environment

The rule is in the right section (§2, pull request description), and §8 reaches it. The package README bullet was added. The skill-description gate passes. The version gate (`apm pack --check-versions`) needs `uvx` and was not run. No test is added, so the level question does not apply. Answer: none.

### Item 4: names by content, not by position

Taste only (T1). Answer otherwise: none.

### Item 5: the failure report

The check table in the 4367 README names the failing check for each run. Answer: none.

### Item 6: what the writer says it verified

Evidence is present: baseline runs and with-rule runs for two models, with tree ids that match (`1f020ce` for baseline, `47980534` for rule runs). Two problems in how it is stated: the baseline is labelled `origin/main` (S1), and the control has no base arm (S6). Word counts in the README table match the files.

### Item 7: siblings of the change

Checked the package README, the §8 checklist, the `merge-model.md` reference (its body lists do not name outcomes, so nothing it says is contradicted), and the `cases/` entry in the research README. The `english-us-developer-style` path named in the README exists. Answer: none beyond S1, S7 and S8.

---

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| S1 | The commit and the case README say the baseline ran "on `origin/main`". It is the parent `4f69810` (skill tree `1f020ce`). No `main` ref exists in this clone. `8c8eb00`, the parent of the branch's first commit, has tree `2670ea8`, which differs. The baseline therefore includes four unmerged commits. The commit's "(effort high)" also reads as applying to Opus, but the README says Opus ran at the session default. | Substantive | Commit `86028c3` message; `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:33` | Say the baseline is the parent commit `4f69810`. Name effort for Haiku only. Or rerun the baseline on `8c8eb00`. |
| S2 | Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". That sentence does not exist. The rule says "unless the next release … is a major" (SKILL.md:234). | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`; `cases/pgjdbc-4392-no-break/README.md:7` | Quote SKILL.md:234 verbatim, or link to it. |
| S7 | `git archive <rev> <path>` writes a tar stream to stdout. It does not copy files. I checked: the output is a POSIX tar archive. The recipe's outcome is not produced. | Substantive | `cases/pgjdbc-4367-breaks/README.md:29` | Use `git archive <rev> <path> \| tar -x -C <dir>`. |
| S5 | Untested partitions of the release condition: a major target, an unknown release, a `BREAKING CHANGE:` trailer, and the §4 rule 5 commit body. Both cases are patch releases. The rule claims all of these. | Substantive | `cases/` (both cases); SKILL.md:234–260 | Add a major-target case (expect Why first, breaks in slot 3) and an unknown-release case (expect the lead). Or name the untested partitions in the README. |
| S6 | `pgjdbc-4392-no-break` has runs only on the new tree (`47980534`). It has no baseline arm, so "the control grows no section" is not compared with the base. | Substantive | `cases/pgjdbc-4392-no-break/README.md` (Results) | Run the 4392 prompt on the parent tree `1f020ce` and state the difference. |
| S3 | "the trailer decides, and it is written whatever the description does" does not say what the trailer decides. A reader cannot tell whether the trailer turns the lead off or on. | Substantive | SKILL.md:247–248 | State the outcome. If a `BREAKING CHANGE:` trailer makes the next release a major, say so and say the breaks stay in slot 3. |
| S4 | "read the next release … its version file (`gradle.properties`…)". The case facts say the file holds `42.7.14`, which is the latest release tag (`prompt.md:10`). The rule does not say how to turn a version file that names the last release into the next one. | Substantive | SKILL.md:245–246 | Say how to derive the next release from the file: the `-SNAPSHOT` version, or the release after the last tag. |
| S8 | The version bumps (`1.4.0` → `1.5.0`) in `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, and `apm.yml:168` are not named by any sentence in the commit message. Every prior feature commit in this series also bumps them. | Substantive (small) | Commit `86028c3` | Add one sentence naming the bump, or move it to its own commit. |
| T1 | The case README says "Checks 1 to 3" and "4 to 6", naming them by ordinal. The new SKILL §2 text says "slot 3" and "slot 1" where the table names them "User-visible changes" and "Why". | Taste | `cases/pgjdbc-4367-breaks/README.md:25`; SKILL.md:252 | Name the checks and slots by content at first mention. The file's slot-number convention is already established, so this is a preference. |

I expect T1 to be declined without discussion.

---

### Not checked

I did not re-run the model runs (no network and no model access), and I did not verify PostgreSQL or pgjdbc behavior. I did not run the Gradle suite or `apm pack --check-versions`, and I did not run super-linter, markdownlint or Vale. The prices and token counts in the 4367 case README are unverified. I wrote the `git archive` output to `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-fG11i2xjrh-repo/4bbc94db-6384-4cf3-b51c-4f21aa5a0545/scratchpad/ga/out.tar` to confirm S7; the repository is unchanged.
