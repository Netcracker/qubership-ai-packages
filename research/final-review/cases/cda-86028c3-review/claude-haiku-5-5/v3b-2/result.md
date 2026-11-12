# Final review: `4f69810..HEAD` (one commit, `86028c3`)

**Change:** `feat(change-description-authoring): lead the description with breaks unless the next release is a major`. No previous report exists, so §4's table does not apply. No task statement was handed over, so the claimed cases come from the commit message and from the case READMEs under `research/change-description-authoring/cases/`, which stand in for test-class comments.

**Setup**
- Skills: `final-review` read in full. `english-developer-style` and `test-authoring` loaded from the given directory. `apm-authoring`, the authoring skill for an instruction or skill package, is not in that directory, so it was not loaded. The rules were applied from the skill text itself.
- Drift script: ran and printed nothing, because no changed file has Java, Kotlin, Groovy, or Scala members.
- Offline gates, both exit 0: `make check-descriptions`, and `apm pack --check-versions --check-clean --dry-run` (dry run, no writes; `git status` stayed clean).
- Tree ids: `git rev-parse` of the skill directory gives `47980534` at HEAD and `1f020ce5` at base. The `skill-tree` files in the cases match these, so the rule runs were on the committed text and the baselines on the base text.

## Item answers

**1. Comments consistent with the code and with each other.** Analogue: statements the change makes about other files, cases, and counts. Findings F3, F4, F5, F9. The §8 checklist items at `SKILL.md:831` and `:849` agree with §2 at lines 86–88 and 252–260. The package README bullet agrees with the skill. Narration: `SKILL.md:241` "now succeeds" describes an outcome, not the change. None further.

**2. Claimed cases covered.**
- Lead before Why unless major: 4367 check 1, both models, with the rule. Passes; all four rule runs open with `## Breaking changes`.
- Result shape is a break: 4367 check 2. Passes per the README table.
- Extended failure goes with the breaks, not Scope: 4367 check 3. Three of four runs pass; `opus/result-2.md` has it in Scope. Confirmed by grep.
- A fix is not a break: 4367 check 4. Passes per the README table.
- No break, so no lead and no heading: 4392 checks 1–2. Confirmed by grep: no `## Breaking changes` in the four results.
- Next release is a major: no case. **F1.**
- Nothing says which release it is: no case. **F1.**
- Commit body keeps breaks first in slot 4 and problem first; rule-5 squash copies the lead: no case. Every prompt asks for a PR description. **F2.**
- Command line: `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring` (4367 README, "Running it"). No script runs it. Its output is the skill tree, and the recorded ids match that tree at HEAD and base. None.
- Hunks: the three version bumps are claimed by no sentence. **F6.** Every other hunk has a claim.

**3. Boundaries, partitions, negative control.** Covered: break and no-break, one extended-failure case, result shape. Not covered: major and unknown releases (F1). The control 4392 has no base run (F7). Pre-existing state: none; the skill is read fresh each run.

**3a. Level, placement, environment.** Placement matches the slot structure, and both offline gates pass. "Breaking" is defined at `SKILL.md:234–241` and marked for changelogs at `:543`, with no conflict. None.

**4. Names by content.** `SKILL.md:198` says "ahead of slot 1" where `:254` says "the Why slot". **T2.** Run files `result-2.md` are ordinals. **T3.**

**5. Failure report.** The §8 Breaks item (`:849–852`) detects the lead and the heading, not whether a failure extended to previously working inputs is in the break lines. **F8.** Each case's Checks table names the failing check per run. None further.

**6. What the writer says it verified.** Red evidence exists: the origin/main baselines fail checks 1–2 for both models. The tree ids tie each run to its text. Gap: the negative control has no base run and no word comparison. **F7.**

**7. Siblings.** Grep for "breaks first", "break leads", "Breaking changes", and the package name finds no other package restating the description rule. The three version pins agree at 1.5.0, and the gate passes. `qubership-repo-essentials/apm.yml:10` includes the package unpinned. None.

## §2a instruction table

Instructions the change adds or widens, one row each. Rows the artifact's own condition ends are listed below the table.

| Instruction (line) | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Break leads unless next release is major (234) | A major-release break (version file says 43.x) | Why, What, then breaks first in slot 3 | Ends at `:254`. No case runs it: F1 |
| Extended failure goes with breaks, not Scope (237–240) | A fix that makes a previously failing input succeed | Fix line, no break line | Ends at `:241`, "is a fix, not a break" |
| Read next release; trailer decides; breaks lead if unknown (243–250) | Release-please repo, `BREAKING CHANGE:` trailer | Breaks in slot 3 after Why | Ends at `:248`, "the trailer decides" |
| Lead under a `Breaking changes` heading (252–253) | Break in a prose description with no headings | Short paragraph, then breaks, no heading | Ends at `:252`, "where the description has headings" |
| No break, no lead, no empty heading (255) | 4392, a patch-release fix | Problem first, no heading | Its own condition; 4392 passes |
| Commit body: breaks as first `User-visible:` lines (257–258) | A commit with a new error text and no break | One `User-visible:` line, no break line | Presupposes a break; no case: F2 |
| Rule 5: lead stays, body opens with breaks (258–260) | Squash with "title and description", break in a major release | Body opens with breaks, Why not first, though the description keeps Why first | **No clause ends it. F3** |
| Slot 1 paragraph widened (86–88) | Rule-5 squash, non-major break | Problem right after the breaks | Conditioned on the lead; fine |
| Slot 3 row widened (198) | Non-major break | Breaks ahead of slot 1 | Conditioned on major; fine |
| §8 Breaks item (849–852) | Failure extended to working inputs left in Scope, with other breaks listed first | Passes the checklist | Does not ask the question: **F8** |

Ended by the artifact's own condition, not findings: the lead at `:234`, the major clause at `:254`, the trailer clause at `:248`, the heading condition at `:252`, and the no-break sentence at `:255`.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The major-release and unknown-release branches have no case, though the commit claims both. | Substantive | `SKILL.md:234–254`; `cases/` READMEs | Add one case with a major target (breaks stay in slot 3) and one with no version, milestone, or branch signal (breaks lead). Or narrow the commit message. |
| F2 | The commit-body rule and the rule-5 squash lead are claimed but untested. Every case asks for a PR description. | Substantive | `SKILL.md:257–260`; package README `:23–25`; commit message | Add a commit-message run on 4367 with the same checks, and a rule-5 squash run. Or narrow the claim. |
| F3 | Rule 5 says the copied body "opens with its breaks and then its problem" with no major clause. In a major release the description keeps Why first, so the body would differ from it. | Substantive | `SKILL.md:258–260` vs `:254` | Make the sentence conditional: "where the lead applies, that body opens with its breaks". |
| F4 | Both case READMEs quote a rule that the skill no longer contains ("…promises compatibility"). The committed text is at `:234`. | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`; `cases/pgjdbc-4392-no-break/README.md:7` | Quote the committed sentence. |
| F5 | The commit says the 4367 runs were "on Opus and Haiku (effort high)". The case README says Opus ran at the session default. Both cannot be right. | Substantive | Commit `86028c3`; `cases/pgjdbc-4367-breaks/README.md:33` | Make the commit message and README agree. I could not check effort from the result files. |
| F6 | The version bumps (1.4.0 to 1.5.0) are claimed by no sentence. The gate `--check-clean` ties the three copies together, so the bump is a consequence of a repo rule. | Substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Add a commit-message sentence stating the bump and why it moves with the rule change. |
| F7 | The negative control has no base run and no word comparison. Its outputs are 241–256 words against a 211-word draft. Item 6 requires a check that the output did not grow. | Substantive | `cases/pgjdbc-4392-no-break/README.md:22–24` | Run the 4392 input on origin/main and report word counts beside the rule runs. |
| F8 | The §8 Breaks item checks the lead and heading, not whether an extended failure sits in the break lines. A description that leaves it in Scope passes. | Substantive | `SKILL.md:849–852` vs `:237–241` | Add: "does every failure the change extends to inputs that worked before sit in the break lines (§2)?" |
| F9 | `the body is problem-first` is unqualified, but under rule 5 with a break the body opens with breaks. | Substantive (low) | `SKILL.md:68` vs `:86–88`, `:257–260` | Add: "except where §2's description lead applies". |
| T1 | The `Breaking changes` heading is outside the house heading set. | Taste | `SKILL.md:252` vs `:300–302` | Use `User-visible changes`, or add the heading to the set. Expect this to be declined. |
| T2 | "ahead of slot 1" where the same section says "the Why slot". | Taste | `SKILL.md:198` | Write "ahead of Why". |
| T3 | Run files are named `result-2.md`, an ordinal. | Taste | `cases/*/result-2.md` | Optional. Expect this to be declined. |

Churn: none reported.

**Not checked:** The pgjdbc#4367 and #4392 inputs, and the maintainer's rewrite, are external and could not be checked offline. The motive is stated two ways: "master ships 42.7.x patch releases" in the case README, and "the pull request targets a 42.7.x patch release" in the commit. Token and price figures in the 4367 README could not be verified offline. I checked the rule-run results only for headings and the `grant insert` placement, not every check. No model runs were made. `apm-authoring` was not loaded, and markdownlint and super-linter were not run.
