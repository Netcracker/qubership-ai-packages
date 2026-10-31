## Final review: commit 86028c3 (`4f69810..HEAD`)

**Scope of the form.** This change has no code, so the form ran through its analogues (§2a). The drift script ran and printed nothing, because the changed files hold no members. The claimed cases come from the commit message alone, since no task statement was handed over. `english-developer-style` was loaded. `apm-authoring`, the authoring skill §2a names for a skill package, is not in the skills directory and I did not load another copy, so the §2a rules that cite it were applied from the form's own wording. `test-authoring` does not apply: there are no tests.

**Previous report.** None; this is the first review of this change.

### Item 1: comments consistent with the text and with each other

Analogue: the statements the changed files make about each other and about cited material.

- `SKILL.md` slot 1 (lines 86–88), the slot 3 row (line 198), the new rule (lines 234–260), the §8 checklist (the *Breaks* line), and §7 agree with one another. The cross-references §2, §4 rule 5, §5, and §7 resolve to the right sections.
- Two README statements do not match the current text; see S2.
- The sentence "The commit body keeps its order, problem first" is contradicted by the next sentence for the squash case; see S8.

### Item 2: claimed cases covered, and every hunk claimed

Claims come from the commit message only.

- Break lead for a patch release: covered by `pgjdbc-4367-breaks`. Break lead for a major release, and for an unknown release: no case; see S3.
- The break definition names a removed option, a changed default, and a changed error code. No case exercises any of them; see S5.
- "The commit body keeps its order … the lead stays" under squash: no run; see S4.
- "A change with no break grows no section": covered by `pgjdbc-4392-no-break`.
- Hunks: the three version bumps (`marketplace.json:291`, `apm.yml:2`, root `apm.yml:168`) are claimed by no sentence; see S1. The rest of the diff is claimed, directly or as the rule's own detection or summary.
- Command lines: `git archive <rev> <path>` in `pgjdbc-4367-breaks/README.md:29`; see S7. The `./gradlew` lines are in the author's draft inside `prompt.md`, which is input to an agent rather than an instruction from this change, and their outcome is not checked by it: none.

### Item 3: boundaries, partitions, and the negative control

- The lead condition has three partitions: patch release with a break, major release, and no release information. Only the first has a case; see S3.
- The 4392 control has no origin/main run, so it is not shown to stay green on the base; see S8.
- Pre-existing state (descriptions drafted under the old rule): none. No instruction in the change asks for a rewrite of an existing description.

### Item 3a: level, placement, environment

- Placement: the rule sits in `SKILL.md` §2 under the pull request description, next to the slot table it changes. Fine.
- `make check-descriptions`: exit 0, all 27 descriptions within the limit.
- `make check` (`apm pack --check-versions --check-clean --dry-run`): exit 0, "Version alignment OK". This is why the version bumps matter; see S1.
- markdownlint is not installed and no config was found at the repository root, so Markdown lint was not run.

### Item 4: names by content, not position

None. The run files `result-2.md` differ only in the run number, so there is no content to name them by.

### Item 5: the failure report

The *Breaks* checklist line tests the lead and slot 3. It does not test that an extended failure left Scope; see S6.

### Item 6: what the writer says it verified

- The red evidence for `pgjdbc-4367-breaks` is the origin/main baseline run, which fails the lead and the result-shape checks as stated.
- The committed wording was run on Opus twice. `opus/result-2.md:35` leaves `grant insert` in Scope. The commit body and README disclose this ("one Opus run left it there"), so it is reported, but the rule's own check fails in one of two committed-wording runs; see S6.
- Word counts in the README (756, 825, 792, 758, 779, 784; 241, 251, 256, 249) match the files. The literal and heading checks I spot-checked match.

### Item 7: siblings

- Other statements of description order in the repository (repo-wide search): none normative. The `research/change-description-authoring/phase*_result.md` files are dated research and were left as they are.
- The package README and the research README were updated consistently.
- The stale quote in the two case READMEs is the sibling miss; see S2.

### §2a instruction table

| Instruction added or widened | Input it fires on | What the agent writes | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Open with the break lines unless the next release is a major (`SKILL.md` §2, rule paragraph) | `pgjdbc-4367`, target 42.7.14 | `## Breaking changes` first (`opus/result.md:1`) | "unless the next release is a major" | Holds for patch; major branch untested, S3 |
| Breaks lead where nothing says which release it is | Target with no version file, milestone, or branch name | not run | "where nothing says which release it is" | S3 |
| A failure extended to earlier-working inputs goes with the breaks, not in Scope | `grant insert` statement | Scope paragraph in `opus/result-2.md:35` | none in the text | S6 |
| No break: no lead and no empty heading | `pgjdbc-4392` | no section, all four runs | "A change with no break…" | Clean |
| Commit body keeps problem first; breaks are the first `User-visible:` lines | `pgjdbc-4367` commit body | not run | "Where §4 rule 5 …" | S4, S8 |
| A `BREAKING CHANGE:` trailer or `!` decides the major | Commit with the trailer | not run | "the trailer decides" | S3 |

### Findings

Every finding is substantive. There are no taste findings and no churn.

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| S1 | Version bumps 1.4.0 → 1.5.0 in three files are claimed by no sentence of the commit message. The skill names this case explicitly. | Substantive | `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168` | Add a sentence to the commit body that claims the bump (the alignment gate checks the three files together), or move the bump to its own commit. |
| S2 | Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". No such sentence exists; the rule now says "unless the next release … is a major". | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7–8`, `…/pgjdbc-4392-no-break/README.md:6–7` | Quote the current sentence (`SKILL.md` line 234) in both. |
| S3 | The lead's conditions are claimed, but the cases cover only a patch release with a break. A major release (breaks stay in slot 3) and a target with no release information (breaks lead) have no run. The trailer rule has none either. | Substantive | `SKILL.md` lines 234–255; `cases/` | Run the 4367 prompt with a major target, and with no version file, and record the lead or its absence. Add a trailer input if the trailer rule stays claimed. |
| S4 | The commit-body rule (problem first, breaks as the first `User-visible:` lines, and the squash case) is claimed but has no run. Both cases test only the description. | Substantive | `SKILL.md` lines 257–260; commit message | Run the 4367 input for the commit body and record the order, with the squash case. |
| S5 | The break definition names a removed option, a changed default, and a changed error code. No case exercises any of them. | Substantive | `SKILL.md` lines 234–238 (definition) | Add an input for one of them, or cut the three from the claim. |
| S6 | With the committed wording, one Opus run (`opus/result-2.md:35`) still writes the `grant insert` failure in Scope, although the rule says it goes with the breaks. The checklist has no line for it, so the detection does not catch it. The commit discloses the run; the rule itself does not yet hold. | Substantive | `SKILL.md` lines 238–240 and the §8 checklist; `cases/pgjdbc-4367-breaks/opus/result-2.md:35` | Add a clause that ends the Scope placement (for example: Scope names only what is left out, and an extended failure is not left out), plus a checklist line for it. Then rerun the Opus case. |
| S7 | The README's command `git archive <rev> agent-packages/…` writes a tar archive to standard output, so it does not copy the skill out of the checkout as the sentence says. I confirmed the output is a POSIX tar by writing it to a file. | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:29` | Pipe it: `git archive <rev> <path> \| tar -x -C <dir>`. |
| S8 | "The commit body keeps its order, problem first" is an unconditional sentence. The squash exception is stated in the next sentence, so a reader quoting the first sentence gets the wrong order for squash. The 4392 control also has no origin/main run, so it is not shown to stay green on the base. | Substantive | `SKILL.md` lines 257–260; `cases/pgjdbc-4392-no-break/` | Put the condition in the first sentence, for example "Unless §4 rule 5 makes the description the commit body, the commit body keeps its order…". Run the 4392 prompt once on origin/main. |

**Not checked.** No model run was repeated, so the results files are taken as recorded. The list prices in the cost note were not verified. `markdownlint` was not run because it is not installed. `make test` was not run because this change does not touch its suites. `apm-authoring` was not available, so §2a rules that cite it were applied from the form's own text. The author's task statement was not handed over, so the claimed cases come from the commit message alone.
