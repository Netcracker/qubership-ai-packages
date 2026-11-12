## Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit `86028c3`)

**Inputs.** The change has no code, so the §2a analogues apply and each item says which one it used. The drift script (`skills/final-review/scripts/comment-drift.py`) ran with exit 0 and printed nothing. The changed files are Markdown, YAML and JSON, so there are no members to parse. No task statement was handed over, so the claimed cases come from the commit message (its body, its "Two regression cases" paragraph, and its results sentences), plus the package README bullet and the research README note that the change adds. The authoring skill `change-description-authoring` is not in the skills directory, so I read the in-repo `SKILL.md` as the artifact. I loaded `test-authoring` and `english-developer-style` from the given directory. No files were changed and nothing was committed.

**Claimed cases.**
1. A break leads the PR description unless the next release from the target branch is a major (SKILL.md:234–260).
2. The definition of a break: result shape, a removed option, and a failure extended to inputs that worked before. A fix is not a break.
3. The commit body keeps problem first, with breaks as the first `User-visible:` lines. A squash keeps the lead.
4. `pgjdbc-4367-breaks`: the baseline fails checks 1–3 on both models, and all four treatment runs pass check 1 and check 2. Three of four move `grant insert` out of Scope.
5. `pgjdbc-4392-no-break`, the negative control: two runs per model, no lead and no heading.

### Item 1: comments consistent with the code and with each other (analogue: prose claims about other files and documents)
- Finding F1: both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". That sentence is not in `SKILL.md` at HEAD, which says "unless the next release from the target branch is a major".
- Finding F2: the sentence "the trailer decides, and it is written whatever the description does" does not say what the trailer decides or in which direction.
- Taste T1: `SKILL.md:310` says a description under §4 rule 5 "takes the body's shape". The new carve-out at `SKILL.md:258–260` makes the body open with breaks, not with the problem, so "the body's shape" no longer means one thing.
- Cross-references checked: §4 rule 5 (`SKILL.md:637`), §5 trailers (`:706`), §7 "no empty heading" (`:783–794`), and the checklist line at `:850`. All resolve.

### Item 2: claimed cases covered (analogue: the test that covers a rule is its detection)
- The 4367 case covers the result-shape break (check 2), the later-statement break (check 3), and "a failure that now succeeds is a fix" (check 4).
- Finding F3: nothing runs the commit-body arm. Both cases run PR descriptions only, so "the breaks as the first `User-visible:` lines" and "where squash copies the description, the lead stays" are claimed without a run.
- Finding F4: the version bump `1.4.0 → 1.5.0` in three files (`.claude-plugin/marketplace.json:291`, `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`) is claimed by no sentence of the commit message. The bump is needed: `.github/workflows/marketplace.yml` runs `--check-clean`, and `release.yml` checks the tag against `apm.yml`.
- Every other hunk maps to a claim: the SKILL rule, the slot-3 table row, the checklist, the package README bullet, and the research README note.

### Item 3: boundaries, partitions, and the negative control (analogue: partitions the change claims)
- Finding F5: the rule names three release-identifying sources (version file, milestone, branch name) and a trailer path, and it has a default ("nothing says which release, the breaks lead"). No case covers the major branch, the unknown branch, the milestone reading, the branch-name reading, or the trailer path. Both cases target `master` at 42.7.14, so they cover one partition. The rule text at `SKILL.md:247–256` states the defaults.
- Finding F6: the control has only treatment runs. Its README (4392, Results) and the commit message say it "grows no section". That is a comparison against a base, and no base run exists to compare with.
- Table of added instructions (§2a):

| Instruction | Input it does not serve | What the agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release from the target branch is a major" (SKILL.md:234) | A change that breaks nothing (4392) | Problem first, no heading, in all four runs | Present: "A change with no break … has neither the lead nor an empty heading" |
| Same instruction | A change that breaks code in a release the target names as major (no run) | Not measured | Present, untested: "Where the next release is a major, the breaks stay first in slot 3" (`:254–255`) |

### Item 3a: level, placement, environment (analogue: placement and the repository gate)
- The rule sits in the skill's own section and is mirrored in the package README, which matches the sibling layout. The case directories sit under `research/change-description-authoring/cases/`, where the super-linter filter exempts `prompt*.md` and `result*.md`. The gate was not run, so this is `none` as far as I checked.

### Item 4: names by content (analogue: unchanged)
- `none`. Case names are by content. `result-2.md` names a run by ordinal, which I did not count as a finding.

### Item 5: the failure report (analogue: the rule's detection)
- `none`. The new checklist line at `SKILL.md:849–852` asks whether the description opens with the break lines, which is a readable detection of the rule.

### Item 6: what the writer says it verified (analogue: evidence the rule can fail)
- Red evidence is present: four baseline runs fail checks 1–3 on the pre-rule tree `1f020ce`. The treatment runs use the HEAD skill tree `4798053`, which I checked.
- Finding F7: the commit says the 4367 runs were "on Opus and Haiku (effort high)". The 4367 README (line 33) says "Haiku ran at effort `high`; Opus at the session's default".
- Finding F8: the commit and README say the baseline ran "on `origin/main`". No `origin/main` ref exists locally, and the baseline tree equals the tree of the parent commit `4f69810`. I could not verify the origin/main claim.

### Item 7: siblings (analogue: other places that enumerate or route to the artifact)
- The rule appears in the slot-3 row (`:198`), the slot-1 sentence (`:86`), the commit-body checklist (`:832`), the PR checklist (`:850`), and the package README. The "breaks first" line in the checklist at `:845` is consistent, since it orders within slot 3.
- §7a and §7b state no ordering claim. No other copy of the rule exists in the repository (`git grep` found only the case READMEs and the research note).

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| F1: case READMEs quote a rule text that is not in SKILL.md | substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:8`; `…/pgjdbc-4392-no-break/README.md:7` | Quote the committed wording, "unless the next release from the target branch is a major". |
| F2: "the trailer decides" does not say what the trailer decides | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:247–248` | State the outcome: a `BREAKING CHANGE:` trailer or `!` makes that release a major, so the breaks stay in slot 3. |
| F3: the commit-body arm has no run | substantive | `SKILL.md:86`, `:258–260` | Run one breaking change in commit-body form, or narrow the claim to PR descriptions. |
| F4: version bump hunks are not claimed by the commit message | substantive | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Add a sentence saying the bump is required by `marketplace.yml --check-clean` and the `release.yml` tag check, or move it to its own commit. |
| F5: major, unknown, milestone, branch-name, and trailer partitions have no run | substantive | `SKILL.md:243–256` | Run one input whose target is a major, and one with no release information, or narrow the claim. |
| F6: "grows no section" compares against no base run | substantive | `research/.../pgjdbc-4392-no-break/README.md` (Results); the commit message | Run the control on the base commit, or change "grows" to "has". |
| F7: "(effort high)" is wrong for Opus | substantive | commit message; `research/.../pgjdbc-4367-breaks/README.md:33` | Correct the commit message: Haiku at effort high, Opus at the session default. |
| F8: "on origin/main" cannot be verified here | substantive | commit message; `research/.../pgjdbc-4367-breaks/README.md:33` | Name the baseline tree `1f020ce` or the ref you checked. |
| T1: "takes the body's shape" conflicts with the carve-out | taste | `SKILL.md:310` vs `:258–260` | Prefer: "takes the body's shape, with the breaks ahead of the problem". |

### Not checked
I did not run the repository's markdownlint or super-linter, did not re-run any case, did not confirm `origin/main`, and did not do a full wording pass beyond the sentences above.
