## Final review: `4f6981065..HEAD` (one commit, `86028c3`)

**Scope and inputs.** The change is one commit, `86028c3`, which edits the `change-description-authoring` skill, its package README and version fields, and adds research cases. There is no code, so `comment-drift.py` was not run. Its output lists code members, and there are none. I used the §2a analogues. The task statement was not handed over, so the claimed cases come from the commit message alone; there are no test class comments. There was no previous report. `apm-authoring` and `english-developer-style` were not listed by the Skill tool, so I read their copies under the skills directory directly. `test-authoring` was not loaded because the change has no tests.

**Checked directly:** the skill-tree IDs in all four `skill-tree` files equal `HEAD:` of the skill path, so the runs tested the committed text. Word counts, the 4392 draft count (209), and the literals in the case results match the READMEs. The `Generated with` lines appear in exactly the Haiku runs the READMEs name. The version fields in the three registration places all read 1.5.0.

### Item 1: comments consistent with the code and with each other

Findings 1, 2 and 5. Finding 1 is a stale quote: both case READMEs cite the rule as "promises compatibility", which is not the rule's text. Finding 2 is a commit-message fact that the 4367 README contradicts. Finding 5 is the trailer sentence, which can be read two ways. Also a taste finding: "Six slots, in order" now sits beside a slot 3 row that moves ahead of slot 1.

### Item 2: claimed cases covered

Claims from the commit message, each against a run:
- Lead unless the next release is a major: covered for a non-major target only (finding 4).
- Break kinds: result shape and the extended failure are run. Removed option, changed default and changed error code are not (finding 8).
- Commit body breaks-first and squash copy: no run. The 4367 prompt asks for the PR description only (finding 3).
- No break means no section: covered by 4392, two runs per model.

Command lines: one documented form does not do what it says. `git archive <rev> <path>` writes a tar stream to stdout; the copy happens only with `-o` or a pipe to `tar -x` (finding 6). I confirmed the stdout behavior with `git archive HEAD … | od`. Reverse check: the version bumps (marketplace.json:291, root apm.yml:168, package apm.yml:2) are claimed by no sentence (finding 7).

### Item 3: boundaries, partitions, negative control

The major and no-version-file partitions have no evidence (finding 4). The 4392 control has no run on `origin/main`, so "grows no section" has no baseline (finding 9). State: the 4367 partition for a non-major target does have evidence (`origin/main` baseline and two rule runs per model).

### Item 3a: level, placement, environment

The rule sits in SKILL §2 with the §4 rule 5 exception and the §8 checklist, which is the right level. The registration versions agree. `apm` is not available offline, so its gate was not run. Item 7 has no further finding.

### Item 4: names by content

Taste: the new text refers to "slot 3", "slot 1" and "slot 4" by number where the slots have names, "User-visible changes" and "Why". The existing text does the same, so this is a taste finding.

### Item 5: failure report

The §8 checklist reaches the description lead (lines 849–852), but no line reaches the commit-body break-first rule (lines 257–260). That gap is finding 3.

### Item 6: what the writer says it verified

The bad case is in place: the `origin/main` baseline fails the checks. The rule passes them. The evidence for the first two drafts is summarised, not stored, and the commit says so. Taste: the READMEs do not say who judged each check.

### Item 7: siblings

Three version fields, all 1.5.0, and the package has no CHANGELOG. `merge-model.md`, the instructions file and the package README state no slot order, so nothing conflicts. The changelog's "breaking changes sorted first" (§3) is a different artifact and consistent.

### §2a instruction table

Added instructions: 11, no rows.

Not findings: `:234`, `:241`, `:255`.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Both case READMEs quote the rule as "promises compatibility", which is not in the skill. The skill says "unless … is a major", and the two conditions differ. | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8`; `…/pgjdbc-4392-no-break/README.md:6-7` | Quote the current text at SKILL.md:234 and re-check the case wording against the actual condition. |
| 2 | Commit message says "pgjdbc-4367-breaks, on Opus and Haiku (effort high)". The 4367 README says Opus ran at the session default. | Substantive | Commit message; `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:33` | Say Haiku ran at effort high and Opus at the session default, in the commit message or in a follow-up. |
| 3 | The commit-body and squash-copy rules (lines 257–260) have no run; the 4367 prompt asks for the PR description only. The §8 checklist does not reach the commit-body rule. | Substantive | `SKILL.md:257-260`; `research/…/pgjdbc-4367-breaks/prompt.md` | Run one commit-body case with the break-first check, and add a §8 line for the commit body. |
| 4 | Only the non-major, known-release partition is run. The major ("unless … is a major") and unknown-release ("where nothing says") partitions have no run. | Substantive | `SKILL.md:234`, `248-250`, `254-255`; 4367 case | Add a 4367 variant whose version file reads a major, and one with no version file, milestone or branch name. |
| 5 | "The trailer decides, and it is written whatever the description does" does not say what the trailer decides, or whether a `BREAKING CHANGE:` on a maintenance-branch change makes the next release major. | Substantive | `SKILL.md:248` | Say which decision the trailer makes and whether it applies on a maintenance branch. |
| 6 | `git archive <rev> <path>` writes a tar stream to stdout, so the case does not copy the skill out as the sentence says. | Substantive | `research/…/pgjdbc-4367-breaks/README.md:29` | Replace with `git archive <rev> <path> \| tar -x -C <dir>`, or add `-o`. |
| 7 | The version bumps in `marketplace.json:291`, root `apm.yml:168` and package `apm.yml:2` have no sentence in the commit message that claims them. | Substantive | Commit message; the three files above | Add a sentence to the commit message claiming the bump under apm-authoring's "bump when the contract changes" rule, or move it to its own commit. |
| 8 | The break definition lists five kinds. Only result shape and the extended failure are run; removed option, changed default and changed error code are not. | Substantive | `SKILL.md:235-238` | Run one case for each kind not yet run, or cut the list to the kinds the runs cover. |
| 9 | The 4392 control has no run on `origin/main`, so "grows no section" has no baseline to compare against. | Substantive | `research/…/pgjdbc-4392-no-break/README.md` | Run 4392 on `origin/main` for both models and state the comparison. |
| 10 | "Slot 3", "slot 1" and "slot 4" name slots by number, where the slots have names. | Taste | `SKILL.md:234-260` | Say "the User-visible changes slot" in the new sentences. The existing text does the same, so this may be declined. |
| 11 | "Six slots, in order" now sits beside a slot 3 row that moves ahead of slot 1. | Taste | `SKILL.md:190`, `198` | Qualify "in order" with the slot 3 exception. |
| 12 | The Results table does not say who judged each check. | Taste | `research/…/pgjdbc-4367-breaks/README.md` Results | State how each check was judged. |

**Not checked:** the case runs were not re-run, and the pricing and token figures were not verified (no network). `markdownlint` and the `apm` gate were not run because the lint config is not in the repo and the tools are not available offline. The one 121-character line at `research/…/pgjdbc-4367-breaks/README.md:17` may fail MD013 if the gate pins 120.
