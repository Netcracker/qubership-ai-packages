I found three substantive problems and a fourth that is a gap in the evidence rather than in the text. Each is filed under its item below, and the index at the end lists all six findings. I changed no files.

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message of `86028c3` alone. There is no earlier report of this form for this change. The change has no code: it is a skill, a package README, three version manifests, and research case files. So I used the §2a analogues, loaded `apm-authoring` and `english-developer-style`, and did not run `comment-drift.py`, because there are no members for it to parse.

### Item 1: comments consistent with the code and with each other
*Analogue used: every statement a changed file makes about another file, or about the rest of its own file.*

- **Breaks in a squash-copied commit body may lose their `User-visible:` label (`SKILL.md:257-260`, and `:86`).** The paragraph says the breaks go first among the `User-visible:` lines "because the label is what R4 and R5 search for". It then says that where §4 rule 5 makes the description the commit body, "that body opens with its breaks and then its problem". It never says whether those leading lines carry the `User-visible:` label, or whether slot 4 repeats them.
  - One reading leaves the breaks unlabeled, so a `git log --grep 'User-visible:'` search misses exactly the lines it was meant to find.
  - The other reading repeats them, which breaks "A fact stated in slot 3 is not restated" and the case's check 5 ("Stated once").
  - **Request:** one clause saying that in a commit body the leading break lines are the first `User-visible:` lines, so the body opens with slot 4's break lines.
- **The Scope rule and the new break rule disagree (`SKILL.md:488-491` against `:238-240`).** The Scope rule says a question about "whether a compatibility break is intended" stays "in the Scope slot as a question". The new rule says a failure the change extends to inputs that worked before "goes with the breaks, not in the Scope slot". The `grant insert` paragraph in the draft is exactly that kind of break plus a decision, and `opus/result-2.md:35` keeps it in Scope. The case README itself says the sentence moves the case "most of the time and not always".
  - **Request:** a clause at `:488` saying the break line goes with the breaks and only the question of whether it is intended stays in Scope.
- **Both case READMEs quote rule text the skill does not contain (`pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:5-7`).** They quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` reads "…unless the next release from the target branch is a major." A reader who searches the skill for the quoted text finds nothing.
  - **Request:** quote the committed heading.
- **Taste: `SKILL.md:192` still says "Six slots, in order".** Slot 3's breaks now come ahead of slot 1. The row's own cell says so, so the sentence can be read either way.
- **Taste: the commit message says "on Opus and Haiku (effort high)".** The case README says only Haiku ran at high effort and Opus at the session default. "(Haiku at effort high)" would avoid the reading that both did.
- **Checked and consistent:** the package README bullet, the checklist lines `:831-832` and `:849-852`, the slot-3 table cell, the `:86` carve-out, the research index line, and the commit message's run counts against the results table.

### Item 2: claimed cases covered
The claimed cases come from the commit message, since there is no task statement.

| Claimed case | Covered by |
| --- | --- |
| The description opens with the breaks when the next release is not a major (read from the version file) | `pgjdbc-4367-breaks`, check 1 (`gradle.properties` = 42.7.14); four runs pass, both baselines fail |
| Read from the milestone, or from the branch name | none (see item 3) |
| The breaks lead where nothing says which release it is | none (see item 3) |
| When the next release is a major, the breaks stay first in slot 3 | none (see item 3) |
| A break includes a new failure, a different result shape, and a failure extended to new inputs | checks 1–3 (`42703`, `0100E`, `getUpdateCount()` = `-1`, `grant insert`) |
| A break includes a removed option, a changed default, and a changed error code | definitional, not exercised; I did not file this |
| A failure that now succeeds is a fix, not a break | check 4 (`create table begin(atomic int)…`) |
| The commit body keeps the problem first, with the breaks as the first `User-visible:` lines | none (see item 3) |
| Where a squash copies the description into the commit, the lead stays | none (see item 3) |
| A change with no break grows no section | `pgjdbc-4392-no-break`, checks 1–2 |

- **Command lines the change tells someone to run:**
  - `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring` (`4367 README`, *Running it*). Nothing in the repository runs it. Its outcome is the skill tree at `<rev>`, and `git archive <tree-ish> <path>` is long-standing behavior, so the outcome is not in doubt.
  - I checked the recorded `skill-tree` ids with `git rev-parse`: `47980534…` is HEAD's skill tree, and `1f020ce5…` is the tree at `4f69810`, the baseline.
- **Hunks with no claim:** the version goes from 1.4.0 to 1.5.0 in `apm.yml`, `marketplace.json`, and the package's `apm.yml`. Every earlier commit on this package bumps it the same way, and `make test` passed with "version bump reflected after re-pack". So it counts as output of the claimed change, and nothing is unclaimed.

### Item 3: boundaries, partitions, and the negative control
*Analogue used: the partitions are the release situations and the artifacts the change claims; the negative control is the no-break case plus the table below.*

- **Only one partition has a run (Substantive).** The trial covers one partition: a non-major release read from the version file, in a description that does not become the commit body. The pgjdbc prompt reports `merge 0 squash 3 plain 37`, with bullet bodies. Four claimed partitions have no run at all:
  - the release is a major, so the breaks stay in slot 3. This is the rule's other branch and the control for its condition;
  - nothing says which release it is, so the breaks lead;
  - the commit body, which keeps the problem first;
  - a description that §4 rule 5 copies into the body, where the lead stays (this is also where the first item 1 finding lives).
  - **Request:** at least the major-release control (the same 4367 draft, with the target's version file at a new major) and one run under "title and description" squash. Alternatively, the commit message could narrow its claim to the partition that was tested.
- The no-break control is present: four runs, all passing.
- The change starts from no earlier persisted state, and it sets no limits and replaces no mechanism.

**Added instructions:**

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:245` "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides" | a release-please repository at 1.x, and a change with a break | writes the trailer, counts the next release as a major, and keeps the breaks behind Why and What, while the reviewer decides on the major | "where the target branch is already headed for a major without this change's trailer" |

Added instructions: 4.
Not findings: `:255`, `:787`.

### Item 3a: level, placement, and the environment
None.
- The rule sits in the pull-request-description section next to slot 3. The checklist entry is in §8 and the README bullet is with the others.
- The cases sit under `research/change-description-authoring/cases/`, and the directory index lists them.
- The prompt and result files match the research markdownlint exclusion in `.github/super-linter.env`.
- Offline gates: `make check-descriptions` printed "ok: all 27 skill descriptions are within 1020 characters", and `make test` printed PASS.
- The rule is specific to this skill's slots and merge model, not generic tutorial material.

### Item 4: names by content, not by position
None. The new text says "slot 1", "slot 3", and "slot 4", but that numbering is the skill's own established convention from its slot tables. The case checks have numbers but are named in bold and in the table headers ("Lead (1)").

### Item 5: the failure report
None. The new checklist line ("Breaks: … does the description open with the break lines …") reaches the rule, and it detects the rule's actual property, the order. The empty-heading arm is checked as well.

### Item 6: what the writer says it verified
None.
- The case README states a red run: both baselines fail checks 1–3.
- It states green runs: all four runs with the rule pass checks 1, 2, 4, 5, and 6, and three of the four pass check 3.
- The control passes four of four.
- The committed rule wording is the one that was run, since the tree id matches HEAD. The earlier drafts are summarized.
- The partitions with no evidence are filed under item 3.

### Item 7: siblings of the change
None.
- I checked that the version goes from 1.4.0 to 1.5.0 in all three manifests that list it.
- The package README, the §8 checklist, and the research index each gained their line.
- The trigger instruction and the skill's `description:` do not need widening, because the scope did not change.
- §3's changelog rule ("marked in place and sorted first within their category") governs a different artifact and does not conflict.
- `references/merge-model.md` says nothing about body order.
- The umbrella `qubership-repo-essentials` pins `../change-description-authoring` by path, with no version.

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| A squash-copied body's leading breaks may lose the `User-visible:` label or be repeated | Substantive | `SKILL.md:257-260` | 1 |
| The Scope rule keeps a compatibility question in Scope; the new rule moves the extended failure out | Substantive | `SKILL.md:488-491`, `:238-240` | 1 |
| Both case READMEs quote rule text that is not in the skill | Substantive | `pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:5-7` | 1 |
| No run covers a major release, an unknown release, the commit body, or a squash-copied body | Substantive | `research/change-description-authoring/cases/` | 3 |
| "Six slots, in order" while the breaks now come ahead of slot 1 | Taste | `SKILL.md:192` | 1 |
| "(effort high)" reads as covering Opus too | Taste | commit message of `86028c3` | 1 |

I could not run the repository's `apm pack --check-versions` gate here. It runs through `uvx` with `apm-cli`, which I did not attempt without network access.
