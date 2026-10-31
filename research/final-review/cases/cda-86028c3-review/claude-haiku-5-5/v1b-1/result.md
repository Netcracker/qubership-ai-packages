## Final review: `4f6981065..HEAD` (one commit, `86028c3`)

**Scope and inputs.** The change is one commit, `86028c3`, "lead the description with breaks unless the next release is a major". It edits a skill, its package README, two version pins, and a research folder with four regression cases. There is no code, so the analogues in §2a apply. The claimed cases come from the commit message, since no task statement was given and there are no test class comments. No previous report exists. The drift script ran and printed nothing, because no member of a code file changed. I loaded `english-developer-style` and `test-authoring` from the provided skills directory. `apm-authoring` is not in that directory, so I did not apply its rules.

**Previous findings.** None. This is the first report on this change.

### Item 1: comments consistent with the code and with each other

Two statements in the changed files disagree with the rest of the file, and two quoted rule texts are wrong (F1 to F3). Everything else checked out:

- The `§` references resolve: §2 "Pull request description", §4 rule 5, §5 `BREAKING CHANGE:`, §7 empty headings, and the §8 checklist (line 849).
- The package README bullet (lines 23–25) and `research/.../README.md:86` agree with the rule and the 2026-10-20 run date.

### Item 2: claimed cases covered

| Claim | Covered by |
| --- | --- |
| Patch-release target leads with breaks | `pgjdbc-4367-breaks` checks 1–3 on four rule runs. Both baseline runs fail check 1 (Why first). |
| Result-shape break marked | Check 2, all four runs |
| Fix that stops failing is not a break | Check 4, all four runs |
| No lead, no empty heading, when nothing breaks | `pgjdbc-4392-no-break` checks 1–2, four runs |
| Literals kept | Check 6 and 4392 check 3 |
| Major target keeps breaks in slot 3 | **None** (F5) |
| Unknown release leads | **None** (F5) |
| Trailer decides the release | **None** (F5) |
| Squash copies the description and the lead stays | **None** (F6) |
| Each break kind (option removed, default changed, error code changed) | **Only** new failure, result shape, and extended failure have cases (F7) |

- **Command lines.** The `./gradlew … ParserTest` lines appear only in the pgjdbc draft and in the recorded outputs, and this change does not tell a reader to run them. None.
- **Hunks.** Every hunk is claimed except the version pins and the cost paragraph (F9, F10).

### Item 3: boundaries, partitions, and the negative control

- The no-break control is present (4392). The fix-is-not-a-break control is present (check 4).
- The release-kind setting has no control with a major target (F5).
- The break-kind partition is incomplete (F7).
- **Item 3a, level and placement.** The rule is observable only through model runs, so no test is possible. The offline gates pass: `make check` (`apm pack --check-versions --check-clean --dry-run`) reports "Version alignment OK" and a clean working tree, and `make check-descriptions` reports all 27 descriptions within limit. The case folders sit in the layout the research README describes.

### Item 4: names by content

`slot 3`, `slot 4`, and `slot 3's break lines` name slots by number where the slots have content names (taste T1). The `result-2.md` files repeat a run with no other content to name them by, so they are not a finding.

### Item 5: the failure report

Each case states what a failure looks like ("Fails: Why first", and so on), and the §8 checklist reaches the rule. The checklist does not reach the trailer branch (F5).

### Item 6: what the writer says it verified

- The red evidence is the origin/main baseline runs for 4367.
- The control for 4392 has no baseline run, so "the output did not grow" is not checked (F8).
- The effort level in the commit message contradicts the case README (F4).
- The README says the committed version left `grant insert` in Scope in one of two Opus runs and says so openly. That is stated, not a finding.

### Item 7: siblings

- Checked with no conflict: the package's instructions file, `references/merge-model.md` (it lists body contents, not order), and the changelog rule at SKILL.md:543, which is a different artifact.
- No installed copies of the skill are tracked in git.
- The research synthesis is the audit trail and is not updated, as the README intends.

### Item 2a: instructions table

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release … is a major." (SKILL.md:234) | A change with no break | No lead, no heading. The 4392 runs match this. | "A change with no break has neither the lead nor an empty heading (§7)." (SKILL.md:256). Quoted, not a finding. |
| "A failure the change extends to inputs that worked before is a break for those inputs … not in the Scope slot." (SKILL.md:237–239) | A failure that now succeeds | Not a break, stays out of the lead | "a failure that now succeeds is a fix, not a break" (SKILL.md:240). Quoted, not a finding. |
| "Where the next release is a major, the breaks stay first in slot 3." (SKILL.md:254–255) | A breaking change aimed at a major release | Why, What, then the break lines in slot 3, as the text reads | None needed. Untested (F5). |
| "Where nothing says which release it is, the breaks lead." (SKILL.md:249–250) | A target whose version file, milestone, and branch name say nothing | Break lines first | None needed. Untested (F5). |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides" (SKILL.md:247–248) | A change carrying the trailer | The text does not say whether the trailer on the change makes the next release a major, or only the tool's configuration | No clause. Ambiguous, see F5. |
| "The commit body keeps its order … with the breaks as the first `User-visible:` lines of slot 4." (SKILL.md:257–258) | A change with no break | Problem, Impact, Change, then Outcome with no break lines | None needed. The squash lead is untested (F6). |

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | Both case READMEs quote a rule that is not in SKILL.md: "A break leads the description where the next release from the target branch promises compatibility". The skill says "unless the next release from the target branch is a major". A reader following the citation finds a different trigger. | Substantive | `cases/pgjdbc-4367-breaks/README.md:7–8`; `cases/pgjdbc-4392-no-break/README.md:7` | Quote SKILL.md:234 verbatim, and cite §2. |
| F2 | "the label is what R4 and R5 search for" names R5 as a reader of the Outcome slot. The commit-body table gives slot 4 the readers R3 and R4. R5 reads slots 2 and 5. | Substantive | SKILL.md:258; table row at SKILL.md:83 | Replace with "R3 and R4". |
| F3 | Two statements contradict on a description that becomes the body. Line 310 says it "takes the body's shape", which leads with the problem. Lines 258–260 say that body "opens with its breaks and then its problem". | Substantive | SKILL.md:310 against SKILL.md:258–260 | Say the body's shape, with the breaks ahead where the description leads with them. |
| F4 | The commit message says the Opus and Haiku runs were at "effort high". The case README says Haiku was at `high` and Opus "at the session's default". | Substantive | Commit `86028c3` message, line 23; `cases/pgjdbc-4367-breaks/README.md:33` | Correct one of them. Amend the commit message if you want the commit to match the case. |
| F5 | Three rule branches have no run: a major target, an unknown release, and the trailer route. The one target in the cases is a patch release with a version file. There is no control for the release-kind setting. The trailer sentence does not say what a trailer on the change means for the next release. | Substantive | SKILL.md:247–250, 254–255 | Add a run with a major-target draft (expect Why first, breaks in slot 3) and one with no version information (expect the lead). State what a trailer on the change means for the next release. |
| F6 | The commit-body path is claimed ("where squash copies the description into the commit, the lead stays") but no output shows a commit body. | Substantive | SKILL.md:257–260; commit message | Run the squash path on one draft and record the commit body, or drop the claim. |
| F7 | The break definition lists removed or renamed option, changed default, and changed error code (SKILL.md:236–238). No case covers any of them. | Substantive | SKILL.md:236–238 | Add a draft with a removed option or a changed default, or narrow the definition to the kinds the cases exercise. |
| F8 | The 4392 control has no run on the baseline skill. The README reports 241–256 words against a 209-word draft, with nothing to compare. The check that the output did not grow is therefore missing. | Substantive | `cases/pgjdbc-4392-no-break/README.md:20–25` | Run 4392 on the origin/main skill tree and record word counts and sections beside the rule runs. |
| F9 | Version pins are changed without a claim in the commit message: 1.4.0 to 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The pins follow the repository's convention, since `4f69810` bumped the same way, and `make check` passes. | Substantive (low severity) | Lines above | Add a commit-body sentence that claims the bump. |
| F10 | The cost paragraph is not claimed by the commit message. The token counts have no transcript in the repository. The list prices could not be checked offline. | Substantive (low severity) | `cases/pgjdbc-4367-breaks/README.md:59–61` | Remove the paragraph, or claim it with its source. |
| T1 | Slot numbers stand in for content names: "slot 3", "slot 4", "slot 3's break lines". The table gives the slots names. | Taste | SKILL.md:198, 254, 258 | Name the slot as well, for example "the User-visible changes slot". |
| T2 | The *Before/After* block now follows the break rule, so a reader may take it as that rule's example. It illustrates headings, which are discussed at line 300. | Taste | SKILL.md:262 | Move the break block below the headings paragraph. |
| T3 | "the trailer decides, and it is written whatever the description does" is ambiguous: "it" could mean the description or the break. | Taste | SKILL.md:248 | "the trailer is written whatever the description does". |

**Not checked.** I did not run any of the model runs again, and I did not check the pgjdbc facts (PostgreSQL 17 outcomes, the release tag, the 40-commit classifier count, the maintainer's link) because there is no network or database here. I did not run `make test` or markdownlint. I did not load `apm-authoring`, which is not in the provided skills directory. I wrote two log files outside the repository (`/tmp/unused` and the scratchpad log). No repository file was changed and nothing was committed.
