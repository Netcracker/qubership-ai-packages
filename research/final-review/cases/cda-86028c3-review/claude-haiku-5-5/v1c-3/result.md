# Final review: 4f69810..86028c3

**Scope and inputs.** One commit, `86028c3`, on top of `4f69810`. It changes the `change-description-authoring` skill, its package README and version entries, the research README, and two case directories (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). There is no separate task statement, so the claimed cases come from the commit message and the case READMEs. No previous report exists.

**Analogues.** The change has no code, so §2a applies. The drift script was not run because the diff has no code members (Markdown, YAML, JSON only). I loaded `english-developer-style` from the skills directory. I also read the repository's `apm-authoring` (`.agents/skills/apm-authoring/SKILL.md`), which is not one of the three named copies, for the rules §2a cites. I did not load `test-authoring`, because the change has no test code.

**Gates run.** `make check` passes (version alignment OK). `make check-descriptions` passes (27 skills within the limit). The skill-tree ids check out: `HEAD` skill tree `4798053` matches the "with rule" cases, and `HEAD~1` tree `1f020ce` matches the baselines. There is no local `origin/main` ref, so the baseline's identity rests on the tree id alone.

## Item 1: comments consistent with the code and each other

Analogue: §2a, statements a changed file makes about another file or document.

The new rule (SKILL.md:234–260) agrees with the PR-description table (line 198), the slot-1 paragraph, §4 rule 5, the slot-4 paragraph (line 112), and the §8 Breaks and Problem items. The two case READMEs misquote the rule (F6). Wording taste is in T2. Otherwise: none.

## Item 2: claimed cases covered

| Claim | Covered by | Result |
| --- | --- | --- |
| Breaks lead unless the next release is a major | 4367 check 1 | 4/4 pass; the major branch has no case (F2) |
| Result shape is a break | 4367 check 2 | 4/4 pass |
| `grant insert` leaves Scope | 4367 check 3 | 3/4 pass, as the commit says |
| A fix is not a break | 4367 check 4 | 4/4 pass |
| No break, no section | 4392 check 2 | 4/4 pass; the wording is wrong (F8) |
| Commit body keeps problem first; squash keeps the lead | none | no case (F3) |

- **Commands.** No command in the changed files tells a reader to run anything. The gradle line appears only inside pgjdbc draft text in the case files. Outcome: none.
- **Hunks.** The version bump in three files is claimed by no sentence (F5). Every other hunk maps to a claim.

## Item 3: boundaries, partitions, negative control

Analogue: §2a, the partitions the change claims.

- **Covered partitions.** Break and no-break, and the extended-failure case.
- **Uncovered partitions.** Major next release, unknown next release, and the `BREAKING CHANGE:`/`!` trailer. Both cases target `master` at 42.7.14 with no milestone (F2).
- **Negative control on base.** 4392 has no baseline run (F4).
- **Pre-existing state.** The author's draft is the state the rule meets, and 4367 covers it.
- **Version-file reading.** The rule reads the next release from the version file (F1).

Added instructions (the §2a table):

| Instruction | Input it does not serve | What an agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "Read the next release … its version file" (244–246) | Branch file already names a shipped major (`43.0.0` after its tag); a patch fix that breaks code | "Major": no lead, so a patch release loses its lead | None in the text (**F1**) |
| "Where nothing says which release it is, the breaks lead" (248–249) | No file, milestone, or branch name | Lead | The sentence itself: none |
| "under a `Breaking changes` heading where the description has headings" (252–253) | A description that §4 rule 5 makes a commit body | Break lines, no heading | "where the description has headings": none |
| "A failure … extended to inputs that worked before is a break" (237–238) | A failure on inputs that already failed | Break line for those inputs | "for those inputs" and "that worked before": none |

## Item 3a: level, placement, environment

The rule sits in §2 beside the PR-description table, and its checklist item is in §8. Both match the file's layout. The registration gates pass (`make check`, `make check-descriptions`). Otherwise: none.

## Item 4: names by content

Ordinals appear where content names would work (T1). Otherwise: none.

## Item 5: failure report

The §8 Breaks item detects the lead and the absent empty heading, and it is reached from the checklist. Otherwise: none.

## Item 6: what the writer says it verified

- **Red.** The 4367 baselines for both models fail checks 1–3 (`opus/baseline/result.md`, `haiku/baseline/result.md`).
- **Green.** The 4392 control passes with the rule.
- **Gap.** The control has no base run (F4).

## Item 7: siblings

Checked against §4 rule 5, §8 (line 845, "breaks first", still compatible), the slot-4 paragraph (line 112), the package README (line 23), the research README (line 86), and the trigger instructions file. A grep across the other packages found no description-ordering claims. The three version entries are aligned. Apart from F5, none.

## Findings

| # | Label | File and line | Finding | Change requested |
| --- | --- | --- | --- | --- |
| F1 | substantive | `.apm/skills/change-description-authoring/SKILL.md:244–246` | "Next release" is read from a version file, but the file names the release already shipped (the case's own `gradle.properties` says 42.7.14 with tag `REL42.7.14`). A branch whose file says `43.0.0` after that release reads a patch break as "major", and the break does not lead. | Say the file gives the next release only while its version is unreleased; otherwise the next bump of that line, unless a milestone names a major. Add a case where the file names a shipped major and a patch break must lead. |
| F2 | substantive | `SKILL.md:234–248`; `cases/pgjdbc-4367-breaks/prompt.md` | The major, unknown-release, and trailer branches have no case. | A case with a major next release (no lead, breaks stay in slot 3) and one with nothing naming the release (lead). A trailer case, or drop the trailer clause from the claim. |
| F3 | substantive | Commit `86028c3` body; `SKILL.md:257–260` | "The commit body keeps the problem first … where squash copies … the lead stays" has no case. | Run the commit-body form on 4367 and check order and the first `User-visible:` lines, or mark the claim untested. |
| F4 | substantive | `cases/pgjdbc-4392-no-break/` | No base run, so the control is not shown green on base. | One run per model on the pre-change skill tree (`1f020ce…`). |
| F5 | substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Version bump 1.4.0 → 1.5.0 is claimed by no sentence. `apm-authoring` §Versions ("bump when the contract changes (new required step…)") would support it. | A body sentence claiming the bump with that reason, or move the bump to its own commit. |
| F6 | substantive | `cases/pgjdbc-4367-breaks/README.md:8`; `cases/pgjdbc-4392-no-break/README.md:7` | Both quote the rule as "promises compatibility", which the skill does not contain. | Quote `SKILL.md:234` as written. |
| F7 | substantive | Commit `86028c3`; `cases/pgjdbc-4367-breaks/README.md:33` | Commit says "on Opus and Haiku (effort high)"; the README says Opus ran at the session default. | State the effort per model. |
| F8 | substantive | Commit `86028c3` ("grows no section in any run"); `cases/pgjdbc-4392-no-break/opus/result.md:16`, `opus/result-2.md:16`, `haiku/result-2.md:16` | Three of four control runs add a `## User-visible changes` heading that the draft lacks. | Say "no Breaking changes section", which is what check 2 tests. |
| T1 | taste | `SKILL.md:198`, `:252`; `cases/pgjdbc-4367-breaks/README.md` ("Checks 1 to 3") | Ordinals ("slot 3", "slot 1", "Checks 1 to 3") where content names exist. I prefer "the User-visible changes slot". Expect this to be declined, since the file numbers its slots throughout. | — |
| T2 | taste | `SKILL.md:247–248` | "the trailer decides, and it is written whatever the description does": "it" can read as the lead. I prefer "the trailer makes the next release a major, and is written whatever the description does". | — |

Churn: none.

**Not checked.** The cases were not re-run (no network, no model calls). The pgjdbc and PostgreSQL behaviour in the drafts was not verified. The English-style pass covered only sentences that a reader could misread. `markdownlint` is not installed, so it was not run. No test suite was run. The drift script was not run (§2a). The baseline's identity as `origin/main` rests on the tree id, since no local ref exists.
