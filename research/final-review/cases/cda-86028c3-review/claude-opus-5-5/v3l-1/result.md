# Final review: `4f69810..86028c3` (one commit, change-description-authoring 1.4.0 → 1.5.0)

I found five substantive findings, and two of them are cheap text fixes. The main ones: both case READMEs quote an older wording of the rule that disagrees with the committed rule on one case, and most of the situations the commit message claims were never run.

This change has no code: it is a skill, a package README, version bumps, and research cases. So I filled the form through the §2a analogues and name the analogue under each item. The drift script ran and reported nothing, because the change has no source members. There was no task statement, so the claimed cases come from the commit message alone. There was no previous report.

## Item 1: comments consistent with the code and with each other
Analogue: statements one changed file makes about another file.

- **Both case READMEs quote a rule that is not in SKILL.md.** `pgjdbc-4367-breaks/README.md:6-7` and `pgjdbc-4392-no-break/README.md:5-6` quote "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The two disagree when the release is unknown: the quote would not lead, and the committed rule leads (`:248-250`).
- **The "Caller" checklist line contradicts the new rule.** `SKILL.md:844-846` still asks for "one line per distinct outcome under 'User-visible changes', breaks first". `:252-254` moves the breaks out of slot 3 when they lead. An agent that runs the Caller line faults a correct lead. The slot-3 prose at `:226` ("Breaks come first") has the same gap, but the new paragraph right after it settles it.
- I checked these and found them consistent: `:86-87` against `:257-260` and `:310`; the `:198` table row; the `§5` reference (`:706` has `BREAKING CHANGE:` and `!`); the `§7` reference (`:787`); `§4 rule 5` (`:637`); the package README bullet; and the research README line. The `skill-tree` ids match: `47980534…` is the skill tree at HEAD, and `1f020ce5…` is the tree at the base commit.

## Item 2: claimed cases covered
Analogue: each claim in the commit message → the section that handles it and the run that shows it. The claims come from the commit message only, since there was no task statement.

| Claim | Section | Run |
| --- | --- | --- |
| Breaks lead when the next release is not a major (version file) | `:243-250` | `pgjdbc-4367-breaks`, check 1: 4/4 lead, 0/2 on baseline ✓ |
| Release read from a milestone or a branch name | `:245-246` | none |
| Breaks lead when nothing says which release it is | `:248-250` | none |
| A major release keeps breaks first in slot 3 | `:254-255` | none |
| `BREAKING CHANGE:` / `!` decides | `:247-248` | none |
| Result-shape change counts as a break | `:236` | check 2: 4/4 ✓ |
| Extended failure counts as a break, not Scope | `:238-240` | check 3: 3/4 (`opus/result-2.md` left it in Scope; the commit message says so) ✓ |
| New failure counts as a break | `:235` | `42703` and `0100E` lines ✓ |
| Removed option, changed default, changed error code | `:237-238` | none |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | `:257-258` | none (both prompts ask only for a PR description) |
| Under squash, the copied description keeps the lead | `:258-260` | none (the prompts' merge model is squash with commit bullets, so rule 5 does not apply) |
| A change with no break grows no section | `:255`, §7 | `pgjdbc-4392-no-break`: 4/4 ✓ |
| Run counts, "three of four", "control grows no section", "two drafts summarized" | case READMEs | Confirmed by reading every result. The word counts in both READMEs match `wc -w`. |

- **The commit message's "on Opus and Haiku (effort high)" misstates the Opus effort.** It reads as both models at high. The case README (`:30-31`) says Opus ran at the session default.
- **One hunk has no sentence claiming it: the version bump** (`apm.yml`, `agent-packages/change-description-authoring/apm.yml`, `marketplace.json`). Earlier commits on this package claim it ("Version 1.2.0 to 1.3.0."); this one does not.
- **Command lines:** `git archive <rev> agent-packages/…/change-description-authoring` (case README, "Running it"). Nothing in the repository runs it; there is no `run-case.sh`, unlike the sibling research directories. Its outcome depends only on archiving a path at a revision, which git handles the same in every version. The `english-us-developer-style` path it names exists. This is not a finding.

## Item 3: boundaries, partitions, and the negative control
Analogue: the claimed situations are the partitions; the negative control is `pgjdbc-4392-no-break` plus the table below.

- **The trial covers one of the rule's claimed situations.** Only "version file says a non-major" was run. These claimed partitions have no evidence:
  - unknown release (breaks lead by default);
  - major release (no lead);
  - trailer-decided release;
  - commit-body order;
  - the description copied under rule 5.

  Both prompts state the version (`pgjdbc.version=42.7.14`) and a squash model with commit bullets. So no run reached the "nothing says" branch, which is the one most likely to fire on repositories with no version file, or the rule-5 branch, which changes the shape of a commit body.
- The negative control is present and passes 4/4.

Added instructions: 4, no rows. They are the break definition (`:234-241`), the lead condition (`:243-250`), the lead shape (`:252-255`), and the commit-body order (`:257-260`). The `:86-87`, `:198`, `:831`, and `:849` lines restate them.

Not findings:
- `:240`: "Whether the old behavior was right does not decide it" ends the definition for a fix that also breaks.
- `:232` and §7 `:787`: "no empty section" ends the lead shape for a change whose only outcomes are breaks.
- `:254-255`: "Where the next release is a major, the breaks stay first in slot 3".

## Item 3a: level, placement, and the environment
Analogue: where the rule lives, the layout against sibling directories, and the repository's gate.

- The rule sits in §2 "Pull request description", next to slot 3, and the checklist entries are in §8. That is the right place.
- `make check` passes (exit 0, tree clean). `scripts/check-skill-descriptions.py` passes. `marketplace.json` parses.
- Super-Linter's `FILTER_REGEX_EXCLUDE` covers the new `prompt.md` and `result*.md` files. The case READMEs are linted.
- Taste: `pgjdbc-4367-breaks/README.md:17` is 121 characters. markdownlint's default non-strict MD013 allows it, because the overflow has no whitespace past column 120. I could not read the remote `.markdownlint.json` to confirm.
- Taste: the model directories are named `opus/` and `haiku/`. The sibling cases (`research/problem-report-authoring/cases/*`, `research/test-authoring/cases/*`) use `claude-opus-5-5/`.

## Item 4: names by content, not by position
None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`), the check names (Lead, Result shape, …), and the cross-references (§2, §4 rule 5, §5, §7) all name things by content. The checks are numbered, but the results table pairs each number with its name.

## Item 5: the failure report
Analogue: what each rule tells the reader to look at.

None. The §8 checklist reaches the new rule through the "Breaks" line (`:849-852`) and the amended "Problem" line (`:831-832`). Each case README states what a failure looks like for each check, and the results table names the failing check and how it failed ("fails: in Scope"). The detections test the rule itself: lead position, where the result-shape line sits, where the `grant insert` line sits.

## Item 6: what the writer says it verified
- Present: red runs on the base skill (both baselines fail checks 1-3), green runs on the committed tree (tree ids verified), and a guard against lost facts (checks 4-6).
- **Missing: a growth check on the noise input.** The control `pgjdbc-4392-no-break` has no baseline run. Its README compares the 241-256 words of the results with the 209-word draft, not with output from the old skill. So it is not shown that the rule left the output on that input unchanged. Item 2 already covers the untested partitions.

## Item 7: siblings of the change
Analogue: places that list or route to the artifact.

- Checked: `marketplace.json`, root `apm.yml`, the package `apm.yml`, the package README, and the research README's file table. The umbrella `qubership-repo-essentials` points to a relative path with no version pin, and earlier bumps of this package did not touch it either.
- `english-*-developer-style:570` defers placement of breaks to this skill and has nothing to update. The changelog rule (§3 `:543`, breaks sorted first within the category) agrees with the new rule.
- No sentence counts the slots differently; the "Six slots" line still holds, since the lead is not a new slot.
- None found.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote a superseded rule ("where … promises compatibility") that disagrees with the committed rule on an unknown release | Substantive | `cases/pgjdbc-4367-breaks/README.md:6-7`, `cases/pgjdbc-4392-no-break/README.md:5-6` | Quote `:234` as committed: "…unless the next release from the target branch is a major" |
| The "Caller" checklist line still puts breaks first under "User-visible changes" | Substantive | `SKILL.md:844-846` | Add "or ahead of the Why slot where they lead (Breaks below)" |
| Claimed partitions have no run: unknown release, major release, trailer-decided, milestone or branch name, commit-body order, rule-5 copied body; three of the six break kinds | Substantive | commit message ¶2; `SKILL.md:243-260` | Add cases for the unknown-release branch and the rule-5 body at least, or narrow the commit message to what the runs show |
| The control has no baseline, so "no growth on a no-break input" is not established | Substantive | `cases/pgjdbc-4392-no-break/README.md` Results | Add a baseline run of the control on the base skill tree and compare word counts with it |
| The commit message says "(effort high)" for both models, but Opus ran at the default | Substantive | commit message ¶3 | "on Opus (default effort) and Haiku (effort high)" |
| The version bump is not claimed in the commit message, unlike earlier commits | Substantive | `apm.yml`, package `apm.yml`, `marketplace.json` | Add "Version 1.4.0 to 1.5.0." |
| Model directory names differ from sibling cases (`opus/` vs `claude-opus-5-5/`) | Taste | `research/change-description-authoring/cases/*/` | Use the full model id as the siblings do |
| `pgjdbc-4367-breaks/README.md:17` is 121 characters | Taste | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap if the remote markdownlint config sets MD013 strict |

What I did not check: I did not rerun any model case or the full `make test` suite, I did not read the remote markdownlint config, I did not load `apm-authoring` beyond the rule names the form cites, and I did not do a style pass over the prose.
