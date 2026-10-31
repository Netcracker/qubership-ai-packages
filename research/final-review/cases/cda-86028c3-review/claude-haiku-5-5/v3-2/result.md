# Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit 86028c3)

Nothing in the repository was changed and nothing was committed. Three scratch files were written outside the repository; one was an accidental `/tmp` redirect, now removed.

**Inputs.** No task statement was handed over, and as a subagent I could not ask for one. The claimed cases come from the commit message, the two case READMEs, and `prompt.md`. The change is a skill, a README, version metadata, and research cases, with no code members. `comment-drift.py 4f69810 HEAD` ran and printed nothing, because no members moved. Per §2a, each item below uses its analogue. The skills loaded were `final-review`, `test-authoring`, and `english-developer-style`. `apm-authoring` was not among the provided skills, so the instruction-file rules it would carry were not checked. Repository gates: `make check` (version alignment OK, marketplace clean) and `make check-descriptions` (27 descriptions within 1020 characters) both exit 0.

**Previous report.** None. This is the first review of this change.

## Item 1: comments consistent with the code and with each other

Analogue: statements the changed files make about other files and documents.

- **Substantive.** `SKILL.md:192` says "Six slots, in order", but the new rule at `:198` and `:234–255` puts the breaks ahead of slot 1.
- **Substantive.** Both case READMEs quote a rule that does not exist. `cases/pgjdbc-4367-breaks/README.md:8` and `cases/pgjdbc-4392-no-break/README.md:7` cite "…where the next release from the target branch promises compatibility". The rule at `SKILL.md:234` says "unless the next release from the target branch is a major".
- Consistent: the commit-body paragraph (`:257–260`) against §4 rule 5 and the slot 4 row; the §8 Problem, Caller, and Breaks lines; and the package README bullet.

## Item 2: claimed cases covered

Claims taken from the commit message:

- **Break leads unless the next release is a major.** Covered for the non-major branch by `pgjdbc-4367-breaks` (four runs pass check 1). The major branch has no run.
- **Lead where nothing says which release it is.** No run. The 4367 target has a version file, so the case never reaches this branch.
- **Breaks in the commit body as the first `User-visible:` lines.** No run. The cases test only the description.
- **Break definition** (result shape, extended failure, fix not a break). Covered by checks 2–4 of `pgjdbc-4367-breaks`.
- **No lead and no empty heading without a break.** Covered by `pgjdbc-4392-no-break`.

Command lines the change tells someone to run:

- `pgjdbc-4367-breaks/README.md` ("Running it") says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". `git archive` writes a tar stream to stdout and copies no files. The form that runs is `git archive <rev> <path> | tar -x -C <dir>`. Beside the documented form the answer is `none`.

Hunks against claims:

- The version bumps are unclaimed. `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, and `apm.yml:168` change `1.4.0` to `1.5.0`, and no sentence of the commit message mentions a version. The gate passes, so the bump is consistent but unexplained.

## Item 3: boundaries, partitions, and the negative control

Partitions are listed in the instruction table in the Boundaries section below. The major, unknown, and trailer branches are unexercised. The extended-failure partition has one case. The control `pgjdbc-4392-no-break` is present.

## Item 3a: level, placement, and the environment

The rule sits in the right skill, and the case directory sits beside the existing research files. Both gates pass. No test was added, so the test-authoring rules do not apply.

## Item 4: names by content, not by position

- **Taste.** The new text refers to "slot 3", "slot 1", and "§4 rule 5" (`SKILL.md:252–259`) where the slots have content names ("User-visible changes", "Scope"). The file numbers its slots throughout, so the reader is not misled.

## Item 5: the failure report

The rule's detection is the Breaks line in the §8 checklist (`SKILL.md:846–851`), which reaches the rule. Case names are by content. None.

## Item 6: what the writer says it verified

The baseline (lead fails, result shape fails, `grant insert` fails in Scope) and the rule runs are in the case directories. I spot-checked the word counts, the Haiku "Generated with Claude Code" lines, and the `grant insert` placements against the result files, and they match the READMEs. Not re-run.

- **Substantive.** The commit message says the pgjdbc-4367 runs were "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says "Haiku ran at effort `high`; Opus at the session's default".

## Item 7: siblings of the change

The package README and the research README were updated, and the §8 checklist covers the rule. The version metadata is aligned across the three files, as the gate confirms. The changelog sentence in `.claude/skills/english-developer-style/SKILL.md:181–188` is a separate rule and does not conflict.

## Boundaries, partitions, and the negative control: table of added instructions

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`) | A break in a PR to a major release | Why first; breaks stay in slot 3 | "unless the next release from the target branch is a major". No run covers it (Item 2) |
| "Where nothing says which release it is, the breaks lead" (`:249`) | A change with no break and an unknown release | Why first; no `Breaking changes` heading | "A change with no break has neither the lead nor an empty heading (§7)" |
| Commit body: breaks are the first `User-visible:` lines of slot 4 (`:257–258`) | A commit with a new outcome and no break | Outcome lines in order, nothing to reorder | The definition of "break" at `:236–240`. No run covers it (Item 2) |
| `Breaking changes` heading "where the description has headings" (`:253`) | A break in a description with no other headings | No heading; breaks follow the lead | "where the description has headings" |
| "The trailer decides" for a `BREAKING CHANGE:` release (`:247–248`) | A commit with the trailer on a release-please repo | No lead, since the release is major | The trailer. Taste: the sentence does not say what the trailer decides (see below) |

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | "Six slots, in order" contradicts the rule that breaks lead ahead of slot 1. | Substantive | `SKILL.md:192`, `:198`, `:234–255` | Qualify "in order" with the break lead, or name the exception. |
| 2 | The case READMEs quote a rule phrase that does not exist in the skill. | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | Quote `SKILL.md:234` as written. |
| 3 | The effort recorded for the Opus runs conflicts between the commit message and the case README. | Substantive | Commit 86028c3; `cases/pgjdbc-4367-breaks/README.md:33` | Correct one record, and state the effort of each Opus run. |
| 4 | The major, unknown, and trailer branches are claimed or implied, and have no run. The commit-body lead and the squash-copy lead have no run either. | Substantive | `SKILL.md:234–260`; commit message | Add a run with a major target and one with no release signal, or drop the claim. Add a run of the commit body. |
| 5 | The version bumps are unclaimed hunks. | Substantive | `.claude-plugin/marketplace.json:291`, `apm.yml:2`, `apm.yml:168` | Claim the bump in the description, or move it to its own commit. |
| 6 | The rule says to read the next release from the version file, but that file names the last release (`gradle.properties` says `42.7.14`, tag `REL42.7.14`). The rule gives no step from one to the other. | Substantive | `SKILL.md:246–247`; `cases/pgjdbc-4367-breaks/prompt.md:10` | State the derivation, such as the version after the newest release tag. |
| 7 | The documented `git archive` form writes a tar stream to stdout and copies no files. | Substantive | `cases/pgjdbc-4367-breaks/README.md`, "Running it" | Replace it with `git archive <rev> <path> \| tar -x -C <dir>`, and run it. |
| 8 | "slot 3", "slot 1", and "§4 rule 5" refer by ordinal where the slots have content names. | Taste | `SKILL.md:252–259` | Name them by content. The file numbers its slots throughout, so this is likely to be declined. |
| 9 | "The trailer decides" does not say whether it decides the release is major or whether the lead applies. | Taste | `SKILL.md:247–248` | Say "the trailer makes the next release a major". |

Churn: none reported.

**Not checked.** I did not re-run any model case, and I spot-checked the case results rather than reading each in full. The instruction-level rules of `apm-authoring` were not checked because that skill was not provided. The English style rules were checked for em-dashes only; no em-dash appears in the added lines.
