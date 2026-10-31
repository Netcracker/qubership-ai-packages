## Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (commit `86028c3`)

**Inputs.** One commit, 26 files. There was no separate task statement, so the claimed cases come from the commit message and from the claims in the case READMEs and prompts. The change is a skill package, so the §2a analogues apply. I loaded `apm-authoring` and `english-developer-style` from the skills directory. `test-authoring` was not needed because the change has no tests. This is the first review of the change, so there is no previous report to re-check against.

**Drift script.** It ran and printed nothing, because the diff has no code members.

### Item 1: comments consistent with the code and with each other
- F1: the two case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". That wording is not in SKILL.md, which now says "unless the next release from the target branch is a major".
- F2: the commit message says the case ran "on Opus and Haiku (effort high)". The case README says "Haiku ran at effort `high`; Opus at the session's default."
- F9 (taste): the break definition lists "a changed error code", but not a changed message text that a caller matches. Two readings are possible; I prefer treating a text a caller matches as a break, and the sentence should say so.

### Item 2: claimed cases covered
- F3: the commit claims the rule applies "unless the next release … is a major" and that breaks lead "where nothing says which release it is". No case covers a major target, an unknown release, or the `BREAKING CHANGE:` trailer. Both cases use `master` at 42.7.14.
- F4: the "Running it" recipe `git archive <rev> <path>` writes a tar stream to stdout. It does not copy files out as the README says. Confirmed with `git archive HEAD … | od -c`, which shows a `pax_global_header`. The recipe needs `| tar -x -C <dir>`.
- F5: the version bumps in `.claude-plugin/marketplace.json:291`, `apm.yml:168` and `agent-packages/change-description-authoring/apm.yml:2` are not claimed by any sentence of the commit message. The bump is needed for `apm pack --check-versions --check-clean`, so the request is a sentence that claims it.
- Every other hunk is claimed by a sentence of the commit message.

### Item 3: boundaries, partitions, and the negative control
- Partitions: F3 covers the untested major, unknown and trailer partitions.
- F10 (taste): the no-break control `pgjdbc-4392-no-break` has no run on the pre-rule tree, so it is not shown to stay green on base.

### Item 3a: level, placement, and the environment
- The rule sits in the right section (§2 pull request description), with a matching checklist line in §8 and a README bullet.
- `apm pack --check-versions --check-clean --dry-run` run directly: exit 0, "Version alignment OK".
- `check-skill.sh` run on the parent tree and on HEAD: the diff adds three ordinal references, reported under F6. The `§15` report is pre-existing.
- Markdown lint: `super-linter.env` excludes `prompt.md`, `result.md` and `result-2.md` from the case directories, which matches the case results. The case READMEs are still linted.

### Item 4: names by content, not by position
- F6: new `§4 rule 5` references at SKILL.md:86, :259 and :832, which `check-skill.sh` flags. New "(below)" at SKILL.md:198.
- F11 (taste): the case README refers to "Checks 1 to 3" and "4 to 6" by number. The checks are named in its table.

### Item 5: the failure report
- none. The new checklist line at SKILL.md:849-852 is reached from the §8 checklist.

### Item 6: what the writer says it verified
- The evidence is present. The baselines (`*/baseline/`) fail check 1 (lead) on the pre-rule tree, and the rule runs pass it.
- The `skill-tree` ids match the trees: HEAD `4798053…`, parent `1f020ce…`.
- Caveat: the clone has no `main` or `origin/main`. The baseline tree equals the parent commit's tree, but I could not confirm it equals `origin/main`.

### Item 7: siblings of the change
- F7: `references/merge-model.md:89`, in the paste-ready "title and description" block, still says the body is "problem, symptom, approach". Under SKILL.md:257-260 the body opens with breaks in that setup, so this site applies.
- F8 (taste): `agent-packages/change-description-authoring/README.md` says the body is "problem-first" without the rule-5 exception.
- The instructions file and the research synthesis need no change.

### Item 2a: the instruction table
Added instructions: 13, no rows.
Not findings: `SKILL.md:241`, `:254-255`, `:255`.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Case READMEs quote a rule title that is not in SKILL.md | substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | Quote the current wording "A break leads the description unless the next release from the target branch is a major." |
| F2 | Commit says both models ran at effort high; README says Opus at session default | substantive | commit `86028c3` body; `cases/pgjdbc-4367-breaks/README.md:33` | State effort per model, in the commit message or the README |
| F3 | Major, unknown-release and trailer partitions have no run | substantive | SKILL.md:243-255; cases | Run a target with a major version file, and one with no version file, milestone or branch name |
| F4 | `git archive` recipe writes a tar to stdout, not files | substantive | `cases/pgjdbc-4367-breaks/README.md:29-30` | `git archive <rev> <path> \| tar -x -C <dir>` |
| F5 | Version bump 1.4.0→1.5.0 in three files is unclaimed | substantive | `.claude-plugin/marketplace.json:291`, `apm.yml:168`, package `apm.yml:2` | A commit sentence claiming the bump, or a separate commit |
| F6 | New ordinal and position references | substantive | SKILL.md:86, :259, :832 (`§4 rule 5`); :198 (`(below)`) | Name the rule by content, e.g. "where the squash setting copies the description into the commit (§4)" |
| F7 | Paste-ready title-and-description block omits breaks-first | substantive | `references/merge-model.md:89` | Add the lead clause, or a pointer to SKILL §2 |
| F8 | README says the body is problem-first with no exception | taste | `agent-packages/change-description-authoring/README.md` | Note the rule-5 exception |
| F9 | Break definition does not settle a changed message text | taste | SKILL.md:236-238 | State whether a text a caller matches counts as a break |
| F10 | Control has no run on the pre-rule tree | taste | `cases/pgjdbc-4392-no-break/` | Run it on the parent tree, to show it stays green on base |
| F11 | Case checks referred to by number | taste | `cases/pgjdbc-4367-breaks/README.md:25` | Name the checks |

### Not checked
- Markdownlint could not run: the config is fetched from netcracker/.github, which is not local. `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters.
- The GitHub threads (pgjdbc#4367 and #4392, and the maintainer's rewrite) were not checked, because there is no network.
- The cases were not re-run. Prices and token counts in the case README were not checked.
- `origin/main` is not in this clone, so the baseline was checked only against the parent tree.
- The `make check` wrapper was not used. I ran the `apm` binary directly with `--dry-run`.
