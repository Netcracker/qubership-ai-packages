# Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit `86028c3`)

No file was changed and nothing was committed.

**Scope and inputs**
- The change has no code, so this is the §2a form. The analogues are the skill's own rules, `apm-authoring` rules 1 to 4 and `english-developer-style` §3, §4a and the commit-message section, read in place of the doc-comment skill.
- `comment-drift.py` was not run because the change touches no source file with members. It changes only `.md`, `.yml` and `.json` files.
- No task statement was handed over, and there is no previous report. The claimed cases come from the commit message, the `Checks` sections of the two case READMEs, and the rule's own sentences. The pgjdbc PR text is not available offline.
- Checks I ran, all read-only: the `skill-tree` ids against the git trees, `git archive` output, `make check` (passed, "Version alignment OK"), `make check-descriptions` (passed), per-run word counts, literal presence, and grep for sibling rule text. `make test` was not run.

**Items 1 to 7 and the §2a analogues**

**1. Comments consistent with code and each other.** Two findings, F1 and F2 below. The §4 rule 5, §5 `BREAKING CHANGE` row and §7 cross-references all exist and say what the new text relies on. Checklist lines 831 and 849 agree with the new rules. None otherwise.

**2. Claimed cases covered.** Analogue: claimed situations and the commands the artifact tells a reader to run.
- Covered: the lead on a patch-release break, and the `grant insert` case in Scope (one Opus run left it there, as stated). `## Breaking changes` opens all four rule runs. `getUpdateCount` appears in all six 4367 runs. The literals are present. The no-break control has no "Breaking" or "compatib" text. The `skill-tree` ids match: the rule runs are on `47980534`, which is HEAD's skill tree, and the baselines are on `1f020ce`, the parent's tree. The word counts match the README.
- Not covered: the major-release branch, the unknown-release branch, and the commit body and squash-copied output (F7, F8).
- Commit message vs. README on effort (F4).
- Command in a README with no matching run, and the outcome it does not produce (F5).
- Reverse read: the three version-bump hunks are not claimed by any sentence (F6).

**3. Boundaries, partitions, negative control.** Analogue: partitions are the release kinds the rule claims, and the control is the no-break case. The no-break control is present. The patch-release partition is covered, but the major and unknown partitions are not (F7). The control has no origin/main arm and no growth check (F9). No pre-existing state, limit, or replaced mechanism applies.

**3a. Level, placement, environment.** Analogue: the cases are LLM runs under `research/`, which has siblings of the same kind. The version fields agree across the three manifests, as `make check` confirmed. Nothing else to report.

**4. Names by content.** One taste finding, F10.

**5. Failure report.** The new rules' detections are reached by the checklist (line 849), and checks 1 to 3 detect the lead rule rather than something weaker. None.

**6. What the writer says it verified.** The baseline arm on origin/main fails checks 1 to 3 for both models, which is the red evidence. The rewritten rule was re-run on the committed tree. The control's growth check is missing (F9).

**7. Siblings.** A repo-wide search for the new sentences found no stale copy. The package README and the root manifests were updated. The changelog rule at SKILL.md:543 is a separate slot and does not conflict. None.

**Added instructions: 10.** The form asks for a row per substantive input, so I give rows for the three inputs that are not covered.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:234` "A break leads the description unless the next release … is a major" | a break in a major release | Why and What first, then the breaks in slot 3 | "unless … is a major" ends the lead (`:254–255`). No run covers it. |
| `:248–249` "Where nothing says which release it is, the breaks lead" | a break on a branch whose version file, milestone and name say nothing | breaks first; no run covers it | none. The branch is an untested partition. |
| `:257–260` "The commit body keeps its order … breaks as the first User-visible lines" | a break in a commit body, or a squash copy of the description | problem first, then breaks; no run covers it | none. The output is claimed but untested. |

Not findings: `:240` (a failure that now succeeds is a fix), `:255` (no break, no lead, no heading).

**Findings**

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | §4 rule 5 "takes the body's shape", but `:257–260` says that body "opens with its breaks and then its problem"; the commit body is problem-first (`:86`). | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:310` vs `:257–260` | Say which part of the shape carries over, e.g. "takes the body's headings", or state the break-first order there. |
| F2 | "the trailer decides" does not say what it decides. It may mean the trailer makes the next release a major, or that the trailer always gets written. | Substantive | `SKILL.md:247–248` | Name the decision: "the trailer makes the next release a major, so the breaks stay in slot 3". |
| F3 | Both case READMEs quote a rule that the committed skill does not contain: "promises compatibility". The current rule is "unless the next release … is a major" (`SKILL.md:234`). | Substantive | `cases/pgjdbc-4367-breaks/README.md:6–8`; `cases/pgjdbc-4392-no-break/README.md:6–7` | Quote the rule as committed. |
| F4 | The commit message says both cases ran "on Opus and Haiku (effort high)". The 4367 README says Haiku ran at high and Opus at the session default. | Substantive | commit `86028c3` body; `cases/pgjdbc-4367-breaks/README.md:33` | Fix whichever is wrong. The commit is HEAD, so the fix is an amend or a new commit, your call. |
| F5 | The README's documented command, `git archive <rev> <path>`, writes a tar stream to stdout and copies no files. I confirmed this locally. The sentence says the skill is "copied out". The 4392 README inherits the same recipe. | Substantive | `cases/pgjdbc-4367-breaks/README.md:29–30` | Pipe into an extraction, for example `git archive <rev> <path> \| tar -x -C <dir>`, or say the archive is written out. Its outcome is the copy. |
| F6 | The version bumps (1.4.0 to 1.5.0) are in three manifests, and no sentence in the commit message claims them. The repo's previous feature commit `4f69810` also bumped its manifests, so this looks like convention. | Substantive, under the form | `agent-packages/change-description-authoring/apm.yml:2`; `.claude-plugin/marketplace.json:291`; `apm.yml:168` | Add a sentence to the commit body that claims the bump, or move it to its own commit. |
| F7 | The major-release branch and the unknown-release branch are claimed, but no case runs them. Both 4367 runs use a 42.7.x patch release. | Substantive | `SKILL.md:234`, `:248–249`, `:254–255`; the 4367 case and its `prompt.md` | Add a case whose target's next release is a major, and one with no version file, milestone or branch name. Run each with checks 1 to 3 on the committed tree. Table row A and row B. |
| F8 | The commit-body output and the squash-copied description are claimed, but no case covers them. Every run is a PR description. | Substantive | `SKILL.md:257–260`; the cases | Add a run that drafts the commit body for a break change, and one with a squash. Table row C. |
| F9 | The 4392 control has no origin/main arm, so its growth is unmeasured. Its runs are 241 to 256 words against a 209-word draft. The checks have no "output did not grow" test. | Substantive | `cases/pgjdbc-4392-no-break/README.md:20–24` | Run the control on origin/main (tree `1f020ce`) and compare word counts, or state the growth and what caused it. |
| F10 | "Checks 1 to 3" and "4 to 6" name checks by position. The check names are available. | Taste (expect it declined) | `cases/pgjdbc-4367-breaks/README.md:25` | Name the checks by content, e.g. "lead, result shape and later-statement failure". |

**Not checked:** the pgjdbc PR text, the maintainer rewrite, and the pricing sentence (`cases/pgjdbc-4367-breaks/README.md:59–62`) need network access or are not verifiable offline. The 209-word draft count and the Opus and Haiku model claims were not re-run. `make test` was not run.
