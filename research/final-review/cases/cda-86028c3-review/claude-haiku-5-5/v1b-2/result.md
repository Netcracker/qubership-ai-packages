# Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit 86028c3)

**Scope and inputs.** The change is one commit with no code. It edits the `change-description-authoring` skill, its README, the package version in three files, and adds research cases under `research/change-description-authoring/cases/`. There is no separate task statement, so the claimed cases come from the commit message and the case READMEs, as the skill allows. No previous report exists, so §4's table is omitted. I loaded `final-review` and `english-developer-style` from the provided skills directory. `test-authoring` does not apply, since nothing is tested in code. The `apm-authoring` skill that §2a names is not in the provided set, so I did not load it, and its rule citations are unchecked. The drift script ran and printed no members, since it does not parse Markdown. Nothing was changed or committed.

## Item 1: comments consistent with the code and with each other
Analogue used: statements one changed file makes about another (the skill, README, case READMEs, commit message).
- **Scope rule contradicts the new break rule.** Substantive. `SKILL.md:490-491` still says that a compatibility break whose intent a maintainer must decide "stays in the Scope slot as a question". The new rule at `SKILL.md:234-241` says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". A reader cannot tell where a break line goes when whether it is intended is still open. Request: state in the new rule where the break line sits and where the intent question sits, and make line 490 match.
- **Stale rule quote in both case READMEs.** Substantive. `pgjdbc-4367-breaks/README.md:8` and `pgjdbc-4392-no-break/README.md:7` quote "A break leads the description where the next release from the target branch promises compatibility". The skill now says "unless the next release from the target branch is a major". Request: quote the current text.
- **Commit message overstates the old state.** Substantive. The message says the skill "had no rule for what counts as a break". The base skill defined one (`SKILL.md:197` at 4f69810: "what worked before and now fails or differs"). Request: say that the base definition was one clause and omitted the extended-failure, result-shape, and changed-default cases.
- **Effort level is ambiguous.** Substantive. The message says "on Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says Haiku ran at effort high and Opus at the session default. Request: state the effort for each model.
- **Lead wording conflicts with its checklist.** Substantive. `SKILL.md:252-253` says the description "opens with slot 3's break lines … after at most a short paragraph". The checklist at `SKILL.md:849-851` asks whether it "opens with the break lines" and whether slot 3 "keeps only the other outcomes". Request: make the checklist allow the paragraph, and say whether break lines leave slot 3 or stay in it.
- **"The trailer decides" has no subject.** Substantive. `SKILL.md:247-248`. The sentence does not say what the trailer decides, which is the next release's major status. Request: "the trailer makes the next release a major, so the breaks stay in slot 3".

## Item 2: claimed cases covered
Analogue used: the case checks in each research README, read against the commit message and the rule text.

Claimed cases with their checks, where the run results confirm them:
- Result shape is a break: check 2 of `pgjdbc-4367-breaks`. Passes in 4 of 4 with-rule runs; fails in 2 of 2 baseline runs.
- Later-statement failure (`grant insert`): check 3. Passes in 3 of 4 runs. `opus/result-2.md:35` keeps it in Scope.
- A fix is not a break: check 4. Passes.
- Stated once and literals kept: checks 5 and 6. Pass.
- No break, no section: `pgjdbc-4392-no-break` check 2. Passes in 4 of 4 runs.
- Lead when the release is not a major: check 1. Passes in 4 of 4 runs.

Claimed cases with no test:
- **Substantive.** Removed option, changed default, changed error code, and a `BREAKING CHANGE:` trailer. These are listed at `SKILL.md:234-241` and the commit message, and no case exercises them.
- **Substantive.** The commit-body form, "where squash copies the description into the commit, the lead stays" (`SKILL.md:257-260`). No case covers it.
- **Substantive.** A major or unknown next release. This is in Item 3.

Commands in changed files:
- **Substantive.** `pgjdbc-4367-breaks/README.md:29-30` says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". Without `-o` or `| tar -x -C <dir>`, `git archive` writes a tar stream to stdout. I confirmed this locally: the output starts with `pax_global_header`. No script or CI job runs the documented form. Request: add the pipe to `tar -x` or `-o`, and state the outcome. (The `gradlew` line in `prompt.md` is the draft's text, not an instruction of this change, so it is not listed.)

Hunks against claims:
- **Substantive.** The version bumps are unclaimed hunks: `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and `agent-packages/change-description-authoring/apm.yml:2`, all 1.4.0 to 1.5.0. Each feature commit has bumped the version so far, and `apm pack --check-versions` passes. Item 2 still requires a sentence that claims the hunk. Request: one sentence in the commit body naming the bump.

## Item 3: boundaries, partitions, and the negative control
- **Substantive.** The release-major setting has no control arm. Both cases target `master` at 42.7.14 (`prompt.md`, "Repository facts"), a patch release. The "major: breaks stay in slot 3" branch and the "unknown release: lead" branch are untested. The negative control `4392` varies whether there is a break, not the release, so it is not the other value of this setting. Request: a case with a major target, such as a version file at 43.0.0, that shows breaks staying in slot 3, and a case with no version file that shows the lead.
- **Substantive.** The negative control has no baseline run. The commit says the control "grows no section in any run", but nothing was run on the parent skill tree (`1f020ce…`). The form requires the control to stay green on the base commit. Request: two runs of `pgjdbc-4392-no-break` on that tree, or a statement that the base was not run.

## Item 3a: level, placement, and the environment
None. The rule belongs in the authoring skill. `apm pack --check-versions --check-clean --dry-run` (the Makefile `check` target) exits 0 with "Version alignment OK". `scripts/check-skill-descriptions.py` reports all 27 descriptions within the limit. The research cases are run by hand and no gate runs them.

## Item 4: names by content, not by position
- **Taste.** `pgjdbc-4367-breaks/README.md:25` says "Checks 1 to 3 are the rule under test; 4 to 6 are the guard", and the results table uses "(1)" to "(6)" as headers. Each check has a content name, such as "Result shape" or "Fix out". The skill's `§4 rule 5` cross-references (`SKILL.md:86`, `:259`, `:310`) also cite by number a rule that has a content name. Not requested; expected to be declined.

## Item 5: the failure report
- **Substantive.** The new checklist item (`SKILL.md:849-851`) detects only whether the lead is present. It does not detect whether a break was classified correctly. A run that leads with breaks but leaves `grant insert` in Scope passes it. Request: add a clause such as "does every failure the change extends to inputs that worked before appear under the break lines?"

## Item 6: what the writer says it verified
Evidence is present: two baseline runs that fail checks 1 to 3, four with-rule runs, and four control runs. The `skill-tree` ids match `git rev-parse` for both the new and the parent skill trees. The word counts in the results match `wc -w`. The gaps are the missing major-release arm and the missing control baseline, both under Item 3.

## Item 7: siblings of the change
- The Scope conflict is under Item 1.
- The version strings agree across the three files.
- The sentence "five slots" and "six slots" still counts correctly.
- No mirrored copy of this skill exists elsewhere in the repository.
- `§7b` and the changelog section need no update.

## Item 2a table: instructions added or widened
| Instruction | Input it does not serve | What the agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "A break leads the description unless the next release … is a major" (`SKILL.md:234`) | a change with no break (`pgjdbc-4392`) | no lead; all four runs open with the problem | the subject "A break" is the rule's own condition: ends it, so no finding |
| "A failure the change extends to inputs that worked before is a break" (`SKILL.md:238`) | a new method that no released version had | not run | "code that works on the released version" in the same paragraph: ends it, so no finding |
| "opens with slot 3's break lines … after at most a short paragraph" (`SKILL.md:252`) | a break in a major release | not run (Item 3) | "unless the next release … is a major": ends it, but the branch is untested |

## Findings
| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Scope rule contradicts break rule | Substantive | `SKILL.md:490-491`, `:234-241` | Say where the break line and the intent question each sit; match line 490 |
| Stale rule quoted in case READMEs | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | Quote the current heading |
| "No rule for what counts as a break" overstated | Substantive | commit message, paragraph 1 | Describe the base definition accurately |
| Effort level ambiguous | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md:33` | State effort per model |
| Lead vs checklist wording | Substantive | `SKILL.md:252-253`, `:849-851` | Align the checklist with the paragraph; say where break lines sit |
| "The trailer decides" | Substantive | `SKILL.md:247-248` | Name what the trailer decides |
| `git archive` form writes to stdout | Substantive | `cases/pgjdbc-4367-breaks/README.md:29-30` | Pipe to `tar -x` or use `-o` |
| Removed option, changed default, error code, trailer, commit-body lead: no test | Substantive | `SKILL.md:234-260` | Add a case per kind, or narrow the claim |
| Version bump hunks unclaimed | Substantive | `marketplace.json:291`, `apm.yml:168`, `agent-packages/…/apm.yml:2` | One sentence in the commit body naming the bump |
| No major or unknown-release case | Substantive | `cases/*/prompt.md` | Add a major-target case and a no-version-file case |
| Control has no base run | Substantive | `cases/pgjdbc-4392-no-break/` | Two runs on `1f020ce…`, or state the gap |
| Checklist detects lead only | Substantive | `SKILL.md:849-851` | Add the extended-failure clause |
| Ordinal references | Taste | `cases/pgjdbc-4367-breaks/README.md:25`; `SKILL.md:86`, `:259`, `:310` | Name checks and rules by content |

**Not checked.** I did not re-run any model case, since there is no model access here. I could not check `origin/main` because there is no remote, so the claim that the baseline ran on it is unverified. I did not run markdownlint, Vale, lychee, or super-linter, and I did not check the external pgjdbc facts against GitHub. I did not verify the `apm-authoring` rule citations.
