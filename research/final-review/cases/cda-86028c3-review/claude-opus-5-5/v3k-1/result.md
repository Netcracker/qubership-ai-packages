# Final review: commit 86028c3, "lead the description with breaks unless the next release is a major"

I had no separate task statement, so the claimed cases below come from the commit message alone. The change contains no code. It changes a skill (`change-description-authoring` SKILL.md and its README), bumps the version in three manifests, and adds two research cases. I filled the form through the §2a analogues and name the analogue under each item. I did not run `comment-drift.py` because the diff has no members for it to parse. I loaded `english-developer-style` from the given directory and `apm-authoring` from the repository; neither of those is one of the three skills I was told not to load from elsewhere. There is no previous report.

## Item 1: comments consistent with the code and with each other

*Analogue: what the changed files say about each other and about the repository.*

- **Finding.** Both case READMEs quote the rule in a wording that is no longer in the skill: "A break leads the description where the next release from the target branch promises compatibility" (`cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7`). The committed heading is "unless the next release from the target branch is a major" (SKILL.md:234). Anyone using the case to find the rule searches for a sentence that doesn't exist.
- **Finding.** The commit message says "on Opus and Haiku (effort high)", which reads as both models at high effort. The case README says "Haiku ran at effort `high`; Opus at the session's default".
- **Checked and consistent:**
  - The skill-tree ids match the trees: `4798053…` is `HEAD:<skill dir>` and `1f020ce…` is the base tree.
  - The results table matches the files: word counts are 756/825/792/758/779/784, and `grant insert` sits in Scope only in the two baselines and `opus/result-2.md`.
  - The package README bullet matches the rule.
  - The slot 1 amendment (SKILL.md:86) agrees with the "§4 rule 5 … takes the body's shape" sentence (:310).
  - The Scope rule at :488 keeps the *question* of intent in Scope, and the new rule moves the *break line* out of Scope. These don't conflict; `opus/result.md` does both.

## Item 2: claimed cases covered

*Analogue: the sections that handle each claimed case, and the runs that show it.*

| Claimed case (commit message) | Section | Evidence |
| --- | --- | --- |
| Breaks lead in a non-major release | :234, :252 | pgjdbc-4367, 4 of 4 runs |
| A result-shape change counts as a break | :236 | pgjdbc-4367 check 2, 4 of 4 runs |
| A failure extended to new inputs counts as a break, not Scope | :238-240 | check 3, 3 of 4 runs (reported honestly) |
| Breaks stay in slot 3 when the next release is a major | :254 | **none** |
| Breaks lead when nothing says which release it is | :249 | **none** |
| The version is read from the version file, milestone, or branch name | :244-246 | version file only |
| The commit body keeps the problem first | :257 | **none**; both prompts ask only for a PR description |
| When squash copies the description into the commit, the lead stays | :259 | **none** |
| A change with no break grows no section | :255 | pgjdbc-4392, 4 of 4 runs |

The commit message claims a rule for each of these four arms. I list the missing runs under item 3.

The diff contains no commands for a reader to run.

Every hunk belongs to a claim, with one exception: the three version bumps to 1.5.0 (`.claude-plugin/marketplace.json:291`, `apm.yml:168`, the package `apm.yml:2`). No sentence in the commit message claims them. They follow the convention of the earlier commits and `make check` passes, so I file this as taste.

## Item 3: boundaries, partitions, and the negative control

*Analogue: the modes the change claims, and the control arm.*

- **Finding.** Only the "patch release, with a break" partition and its no-break control were run. Four partitions the change claims have no evidence:
  - next release is a major;
  - release unknown;
  - a `BREAKING CHANGE:`/`!` release tool;
  - §4 rule 5, where the description becomes the commit body.

  The commit-body order (:257) has no run either.
- The negative control (pgjdbc-4392) is present and passes. It has no baseline run, though; see item 6.
- Pre-existing state, consumers, mechanisms, and limits do not apply to this change.

Instructions the change adds or widens:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "the trailer decides, and it is written" | release-please repository on 2.3.x; a fix with an incidental break; the author writes `fix!:` | Breaks left in slot 3 after Why and What, because the author's own trailer makes the release a major; the reviewer never sees first that merging means 3.0.0 | "where this change's own trailer is what makes the release a major, the breaks lead" |

Not findings:
- `:235` "works on the released version"
- `:241` "a failure that now succeeds"
- `:249` "Where nothing says which release"
- `:254` "Where the next release is a major"
- `:255` "neither the lead nor an empty"

## Item 3a: level, placement, and the environment

*Analogue: where each rule lives, the layout of the files, and the repository's gates.*

- The rule sits in §2 next to the slot 3 text, and its checklist line is in §8. The cases follow the `cases/<name>/{prompt.md,README.md,<model>/…}` layout, and the research README indexes them. `make check` exits 0, and `scripts/check-skill-descriptions.py` reports all 27 descriptions within 1020 characters.
- **Finding (plausible).** `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters long. Super-linter's `FILTER_REGEX_EXCLUDE` does not exclude case READMEs, and the repository keeps Markdown at 120 columns (the `markdown-line-length-120` package). I could not check this offline: the org's `.markdownlint.json` is not in the checkout.
- Every new sentence is specific to this skill. None of it is generic tutorial text.

## Item 4: names by content, not by position

*Analogue: unchanged, applied to the new headings, cross-references, and case names.*

None. The cases are named by issue and content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`), and the checks are named by content ("Lead", "Result shape"). The cross-references use section numbers (§2, §4 rule 5, §5, §7), which is the convention the skill already follows.

## Item 5: the failure report

*Analogue: whether the checklist reaches every rule, and whether each check detects its own rule.*

**Finding.** The new checklist line (SKILL.md:849-852) asks whether the description opens with the break lines. It does not ask whether a different return value or result shape, or a failure extended to inputs that worked before, was counted as a break. Those are the two misses the commit cites as its reason. A reviewer applying the checklist to the baseline output would see no break lines, have nothing to lead with, and pass it. The check detects the ordering, which is the weaker property, and not the classification.

## Item 6: what the writer says it verified

*Analogue: an exemplar the rule passes, a bad case it fails, and a check that the output did not grow where the rule is noise.*

- The bad case is in place: both baselines fail checks 1–3, and the runs with the rule pass, with check 3 at 3 of 4.
- **Finding.** The control has no `origin/main` run. Its README compares the word counts (241–256) only with the 209-word draft, so it doesn't show that the rule left the no-break output the same size. §2a asks for that check on an added instruction.

## Item 7: siblings of the change

*Analogue: the places that list or route to the artifact.*

- I searched the other packages for PR-description order and breaking-change placement. `english-{us,uk}-developer-style` (line 570) defers to this skill. `russian-developer-style` has its own "Breaking changes" block in a changelog example, which is a different artifact.
- The skill's own changelog rule (§3, `**Breaking:**` in place) covers changelogs, not descriptions, and doesn't conflict.
- `references/merge-model.md` does not mention breaks.
- The marketplace description is unchanged, and its scope ("what goes where") already covers the rule.

None.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The case READMEs quote a rule wording ("promises compatibility") that no longer exists | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading (SKILL.md:234) |
| An author's own `!`/`BREAKING CHANGE:` makes the release a major, so the breaks never lead where the reviewer most needs them | Substantive | SKILL.md:247-248 | Add a clause: where this change's own trailer is what makes the release a major, the breaks lead |
| Claimed partitions have no runs: major release, unknown release, release-tool trailer, §4 rule 5 body, commit-body order | Substantive | `research/change-description-authoring/cases/` | Add a case per arm, or state in the case README that those arms are untested |
| The checklist checks the order of breaks, not the classification of a result-shape change or an extended failure as a break | Substantive | SKILL.md:849-852 | Add to the Breaks line: is every different return value or result shape, and every failure extended to inputs that worked before, among the break lines? |
| The no-break control has no baseline, so "the output did not grow" is unmeasured | Substantive | `cases/pgjdbc-4392-no-break/README.md:20-24` | Run the control on `origin/main` (tree `1f020ce…`) and report its word counts |
| The commit message reads as both models at high effort; Opus ran at the default | Substantive | commit message, paragraph 3 | "on Opus and on Haiku (effort high)" or "Haiku at effort high" |
| The README line is 121 characters, likely over the 120-column markdownlint limit (not checked offline) | Substantive (plausible) | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap to 120 columns |
| No sentence claims the version bumps to 1.5.0 | Taste | `apm.yml:168`, `.claude-plugin/marketplace.json:291`, package `apm.yml:2` | Mention the bump in the commit message, or leave it as repository convention |
| A 0.x project's "major" is a minor bump, which the rule doesn't mention | Taste | SKILL.md:243-250 | Optionally: "a major, or a minor below 1.0" |

This review did not include a style pass over the prose, did not run the drafting trials again, did not run markdownlint (no config offline), and did not run `comment-drift.py` (no code in the change).
