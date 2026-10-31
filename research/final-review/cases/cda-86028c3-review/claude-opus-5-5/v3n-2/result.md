# Final review of 86028c3: lead the description with breaks unless the next release is a major

There was no task statement, so I took the claimed cases from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), the package README, the version manifests and the research README, and adds two regression-case directories. I used the §2a analogues throughout and loaded `apm-authoring` and `english-developer-style` from the skills directory. There is no previous report.

The drift script ran and printed nothing, because the change has no members it can parse. Every `SKILL.md` line number below is in `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

I used the analogue: every statement one changed file makes about another file, about the skill's own sections, or about the runs.

- **The checklist contradicts the new rule (`:845`).** The *Caller* checklist line still asks whether the description carries every outcome under "User-visible changes", breaks first. The new *Breaks* line (`:849`) and the rule at `:252-254` say that slot 3 keeps only the other outcomes when the breaks lead. An agent checking its draft against the *Caller* line would move the breaks back into slot 3, or list them twice.
- **The Scope rule pulls the opposite way (`:488-491`, against `:238-240`).** The existing Scope rule says that a question only a maintainer can answer, "as with whether a compatibility break is intended", stays in the Scope slot. The new rule says that a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot".
  - The `grant insert` input fits both rules: the draft frames it as a known limitation, and whether to accept it is the maintainer's call.
  - Neither text says that the break line goes in the lead while the question about intent stays in Scope.
  - This is a plausible reason why `opus/result-2.md` left the case in Scope.
- **Both case READMEs quote a rule that no longer exists.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote it as "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `:234` reads "…unless the next release from the target branch is a major". The README itself says the rule was reworded after review, so these quotes are left over from a draft.
- **The commit message misstates the effort setting.** It says "on Opus and Haiku (effort high)", which reads as both models at high effort. `pgjdbc-4367-breaks/README.md:33` says Haiku ran at `high` and Opus at the session's default.
- **"The trailer decides" does not say what it decides (`:247`).** It could mean that the release counts as a major and the breaks stay in slot 3, or that the version file is ignored. Both readings give the same output, so this is taste.
- **Checked and found correct:**
  - The `§4 rule 5` cross-references at `:86` and `:258` point to the right rule: squash or merge commit with "title and description".
  - The `§5` reference at `:247` points to the `BREAKING CHANGE:` row at `:706`, and `§7` at `:255` points to the absent-concern rule at `:787`.
  - The skill-tree ids match the code: `47980534…` is `HEAD:<skill dir>` and `1f020ce5…` is `HEAD~1:<skill dir>`.
  - Every word count in both case READMEs matches `wc -w`, including the 209-word draft.
  - Each "Generated with Claude Code" statement matches the files.
  - The results table matches each result file I read: all four 4367 runs, the Opus baseline, and two of the four control runs.
  - The package README bullet agrees with the skill.

## Item 2: claimed cases covered

Claims from the commit message, the section that handles each, and the evidence:

| Claimed case | Section | Run that exercises it |
| --- | --- | --- |
| Breaks lead when the next release is not a major, read from the version file | `:234-255` | `pgjdbc-4367-breaks`, 4 runs with the rule, 2 baselines |
| …read from the milestone or the branch name | `:245-246` | none |
| Breaks lead when nothing says which release it is | `:248-250` | none |
| Breaks stay in slot 3 when the next release is a major | `:254` | none |
| A changed result shape is a break | `:236-237` | 4367, check 2 |
| A failure extended to more inputs is a break, not Scope | `:238-240` | 4367, check 3 (3 of 4 runs) |
| A new failure is a break | `:235-236` | 4367 (`42703`, `0100E` lines) |
| The commit body keeps the problem first, breaks as the first `User-visible:` lines | `:257-258` | none: the prompt asks only for a description |
| Under squash "title and description" the lead stays in the body | `:258-260`, `:86-87` | none: the case's merge model is plain or default squash |
| No break: no lead and no empty heading | `:255`, `:787` | `pgjdbc-4392-no-break`, 4 runs |

**Commands.** `pgjdbc-4367-breaks/README.md:31-32` gives `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring`. I ran it on `HEAD` and it lists the skill tree, as promised. No script or CI job runs it, which is fine for a manual procedure. The `./gradlew` lines are prompt data, not instructions to the reader.

**Hunks.** Every hunk belongs to a claim. The research README hunks belong to "Two regression cases under …". The package README hunk restates the rule. The three 1.4.0 → 1.5.0 bumps are this package's own version, which the earlier commits on this branch bump the same way. The commit message does not mention the bump; I don't count that as a finding.

## Item 3: boundaries, partitions, and the negative control

- **Partitions with no evidence (substantive).** The 4367 case exercises one branch of the condition: a version file that shows a patch release. The commit message also claims these partitions, and none of them was run:
  - the next release is a major, so the breaks stay in slot 3 (the other branch of "unless");
  - nothing says which release it is;
  - the commit body order;
  - the description copied into the commit body, where the lead stays.

  The major-release branch is the one most likely to regress silently, because no run shows that the rule stops firing there.
- **Negative control: present.** `pgjdbc-4392-no-break` gives the same target and no break. All four runs pass its checks.

Added instructions: 2, no rows.

Not findings: `:235`, `:241`, `:247`, `:249`, `:255`.

## Item 3a: level, placement, and the environment

- **The rule is in the right place.** It sits in §2 next to the slot-3 rules, and the checklist line is in §8.
- **The gates pass.**
  - `python3 scripts/check-skill-descriptions.py` passed: all 27 descriptions are within 1020 characters.
  - The versions agree across `apm.yml`, `.claude-plugin/marketplace.json` and the package `apm.yml`.
  - I did not run `make check` (`apm pack`), because it needs `uvx`/network.
- **The lint filter covers the new files.** `.github/super-linter.env` excludes `prompt.md` and `result*.md` through `results?[^/]*`, so only the case READMEs are linted.
- **One line is likely over the limit.** `pgjdbc-4367-breaks/README.md:17` is 121 characters. If the shared markdownlint config pins MD013 at 120 (the Qubership default, according to `agent-packages/markdown-line-length-120`), super-linter will flag it. I could not check this, because the config comes from `netcracker/.github`.
- **The case layout differs from its sibling.** `research/blackbox-test-design/cases/` uses `results/<with|without>-skill-<model>/` with `grading.json` and `run.txt`. This change uses `<model>/result*.md` and `<model>/baseline/`. Taste.

## Item 4: names by content, not by position

None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) name their content. The checks are numbered and named together ("Lead (1)"). `result-2.md` is an ordinal, but the repeated samples have no content that tells them apart. The new text uses the skill's existing slot numbering.

## Item 5: the failure report

- **The checklist line checks less than the rule (substantive).** The *Breaks* line at `:849-852` asks only whether the description opens with break lines. It does not ask whether every break is among them. The 3 of 4 rate on `grant insert`, and the earlier failure of a draft without the extended-failure sentence, show these are the failures the rule meets.
  - A draft that leads with two breaks and leaves the extended failure in Scope passes this line. That is `opus/result-2.md`.
  - A draft that leaves the result-shape line in slot 3 passes it too.
- **The case README checks name what to look at and what a failure is.** None to report there.

## Item 6: what the writer says it verified

- **Present.** The bad case is the two baseline runs on the parent tree: both fail checks 1 to 3. The exemplar is the four runs with the rule: they pass, apart from one named Opus failure on check 3. The committed wording was run again, and the `skill-tree` ids equal `HEAD`'s tree.
- **Missing: a baseline for the control (substantive).** `pgjdbc-4392-no-break` has no baseline run. It compares the output (241 to 256 words) with the 209-word draft, not with the skill before the rule. The section checks hold, but nothing establishes that the output did not grow because of the added rule, which §2a asks for when an instruction is added after a bad output.

## Item 7: siblings of the change

- **The surfaces that list the package agree.** I checked `apm.yml`, `.claude-plugin/marketplace.json`, the package `apm.yml` and README, and the umbrella `qubership-repo-essentials`, which uses a relative path and has no version pin.
- **`english-developer-style` defers to this skill** at `:570`, so it does not conflict.
- **Pre-existing conflict, now wider (substantive).** `russian-developer-style/modules/code-comments.md:118-131` has its own pull-request structure: Что, Зачем, Как проверять, then **Breaking changes** as an optional extra block. It does not refer to `change-description-authoring`. A Russian-language description for a patch release would still put the breaks last. The request is to fix it in this change or name it as follow-up.
- **The changelog's "marked in place and sorted first" rule (`:543`)** is a different artifact, and the change leaves it alone, as it should.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The *Caller* checklist line still asks for breaks first in "User-visible changes" | Substantive | `SKILL.md:845` | Say "breaks first, or in the lead (*Breaks*)" |
| The Scope question rule and "not in the Scope slot" conflict on an extended failure | Substantive | `SKILL.md:488-491`, `:238-240` | State that the break line leads and only the question about intent stays in Scope |
| The case READMEs quote a rule wording that was replaced | Substantive | `pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading at `SKILL.md:234` |
| The *Breaks* checklist line passes a draft that leaves a break in Scope or slot 3 | Substantive | `SKILL.md:849-852` | Ask whether every break, extended failures and result shapes included, is in the lead |
| No run for: a major release, an unknown release, the commit body, or the description copied into the body | Substantive | `cases/pgjdbc-4367-breaks/` | A run with the version file at a major (one per model), or the README naming these as untested |
| The control has no baseline, so output growth from the rule is not measured | Substantive | `cases/pgjdbc-4392-no-break/README.md:22-25` | One baseline run per model on the parent tree, with word counts |
| The commit message says "(effort high)" for both models; Opus ran at the default | Substantive | commit message | Put "effort high" on Haiku only |
| The Russian style skill's PR structure puts breaks last | Substantive | `russian-developer-style/modules/code-comments.md:129-131` | Fix in this change, or name it as follow-up |
| Line of 121 characters, over MD013's 120 if enforced | Substantive, unverified | `pgjdbc-4367-breaks/README.md:17` | Rewrap |
| "The trailer decides" does not name what it decides | Taste | `SKILL.md:247` | "the release counts as a major, and the breaks stay in slot 3" |
| The case layout differs from `blackbox-test-design/cases` | Taste | `research/change-description-authoring/cases/` | Align with `results/<with/without>-skill-<model>/`, or leave it |

Not checked: `make check` and super-linter, which need network or `uvx`; whether the baseline tree (`HEAD~1`) is on `origin/main`, because the checkout has no remote refs; the two control result files I did not open; and the prose for style alone, which this review does not cover.
