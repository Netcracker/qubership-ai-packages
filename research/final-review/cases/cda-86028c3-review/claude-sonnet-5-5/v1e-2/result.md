I've read the diff, the skill and the case files. I'm writing up the report now.

# Final review: `4f69810..86028c3` (one commit)

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message alone. The change is a skill, a README, version bumps and research files, with no code. I used the §2a analogues and did not run `comment-drift.py`, because it has nothing to parse here. Of the skills I was told to load, I loaded `final-review` and `english-developer-style`. `test-authoring` does not apply. `apm-authoring` is not among the three provided skills, so I did not apply it. There was no previous report.

## Item 1: Comments consistent with the code and with each other (statements across files)

Findings:
- **Stale rule quote in both case READMEs.**
  - `cases/pgjdbc-4367-breaks/README.md` (intro) and `cases/pgjdbc-4392-no-break/README.md` (intro) quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The SKILL heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major."
  - The quoted title does not exist, so a grep for it finds nothing.
  - The 4367 README also cites "SKILL.md §2" without naming the package.
- **Effort level contradicts the commit message.**
  - The commit message says Opus and Haiku both ran at effort high.
  - The 4367 README says "Haiku ran at effort `high`; Opus at the session's default".
  - The 4392 README says only "Haiku at effort `high`".
  - One of the two is wrong.
- **The skill contradicts itself on a description that becomes the commit body.**
  - The new text at `SKILL.md:257-260` and `:86-88` says the lead stays and the body opens with its breaks, then its problem.
  - Unchanged `SKILL.md:310` says "Under §4 rule 5 the description is the commit body and takes the body's shape instead".
  - Unchanged `SKILL.md:637` says to "shape it as §2's commit body". That shape puts the Problem first, with breaks as late `User-visible:` lines.
  - `SKILL.md:257-258` says the commit body keeps its order, while `:259-260` says the body under rule 5 opens with breaks. A reader gets two orders for the same text.
- **Ambiguous trailer sentence (`SKILL.md:247-248`).**
  - It reads "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does."
  - "The trailer decides" can be read as "the change's own trailer makes it a major, so no lead is needed". That would drop the lead for exactly the patch-branch break the rule exists for.
  - The sentence does not say what the trailer decides.
- **Table header versus order.** The pull request table header still says "Six slots, in order", while slot 3 now precedes slot 1. The cell's "(below)" covers most of this. I rate it taste.

Checked and consistent:
- `§5` points to the `BREAKING CHANGE:` row at line 706.
- `§7` points to "No section for an absent concern".
- The checklist line "Breaks:" matches the rule.
- The `version` field is 1.5.0 in `marketplace.json`, the package `apm.yml` and the root `apm.yml`.
- No narrating `now` or `used to` appears in the new skill text.

## Item 2: Claimed cases covered

The commit message claims these cases:

| Claim | Evidence |
| --- | --- |
| Rule leads with breaks | The 4367 table checks 1 to 3, one passing run per model. |
| Result shape counts as a break | Check 2. |
| Extended failure leaves Scope | Check 3. `opus/result-2` fails it. The commit message and README both say so, which matches "three of four". |
| No section when nothing breaks | 4392 checks 1 and 2, four passing runs. |
| Literals kept | Check 6 in the 4367 case and check 3 in the 4392 case. |
| Rule applies "unless the next release is a major" | **No case.** |

Findings:
- **No major-release case.** No case has a target whose next release is a major, so the carve-out has no evidence.
  - The same goes for the "unknown release, the breaks lead" arm, since both cases state a patch version in the prompt.
  - The stored cases show the rule fires; they cannot show it stops.
  - The request is a case whose `gradle.properties` says a major, or a stated non-claim in the README.
- **Squash-copy claim has no case.** "Where squash copies the description into the commit, the lead stays" is a claimed case and has no case. Both prompts use a merge-model classifier that prints `squash 3`, which is not the "title and description" setting.
- **Commit-body arm has no case.** "The commit body keeps the problem first, with the breaks as the first `User-visible:` lines" has no case either.
- **Runs not stored.** The README says "Earlier Opus runs of two drafts of the rule are summarized in the case README, not stored", so that evidence cannot be checked.
- **Hunk with no claim.** The research `README.md` tree-line addition is claimed only implicitly. I rate it taste.

Commands the change tells someone to run: none in the changed files. The README's `git archive <rev> …` recipe is a command, and it has no script or CI job that runs it. It only reproduces the cases, and I rate it taste.

## Item 3: Boundaries, partitions, negative control

For a skill or an instruction file, this item carries the table of added instructions below.

Partitions the change claims:
- Release kinds: patch, major, unknown.
- Breaks: result shape, extended failure, plain fix.
- Merge model: description only, copied as commit body.

Covered partitions:
- Patch release with breaks.
- Patch release with no break. This is the negative control (`pgjdbc-4392`), two runs per model.
- A fix inside a break-containing change staying out of the lead (check 4).

Findings:
- **Missing partitions.** "Major" and "unknown release" have no run (see item 2). "Copied into a commit body" is the same.
- **Sample size.** Rule support is 1 to 2 runs per arm. One Opus run left `grant insert` in Scope. The README says so ("most of the time and not always"), but the skill text claims the rule without that qualifier. The README's own sample size is not one a commit message "three of four" hides.
- **Pre-existing state.** None applies; this is not a package that replaces earlier installed state.
- **Added instructions, and an input each does not serve:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "The description then opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings, after at most a short paragraph that says which code breaks" | A one-line change with one break, in a repository with a template whose headings are `Summary`/`Testing` | A `Breaking changes` heading above a single line, plus a paragraph restating the line | None. `SKILL.md:300-306` says headings are the exception and a template's headings are used, which covers the heading. The "short paragraph" has no ending clause, so I suggest "and the paragraph is absent where the line alone says which code breaks". |
| "Where nothing says which release it is, the breaks lead" | A new project with no release yet (any change is on the first version) | A break lead for code that has no released version to break | None. "Code that works on the released version" (`SKILL.md:235`) covers it, since nothing has been released, and the checklist line `SKILL.md:849-851` omits that. I rate it taste, since a reader rarely meets it. |
| "A failure the change extends to inputs that worked before is a break for those inputs" | A strictness fix where the old acceptance was a bug (an input that worked by accident) | A break line for an input nobody should have relied on | The next sentence, "Whether the old behavior was right does not decide it", ends the instruction by making it a break anyway. This is intended, not a finding. |
| "The commit body keeps its order, problem first, with the breaks as the first `User-visible:` lines" | A commit with a break and no problem statement worth a slot | Nothing wrong; the skill's Problem slot is "Never" skipped | Not a finding. |

## Item 3a: Level, placement, and the environment

- **Level and placement.**
  - The rule sits in the pull request description section beside the slot table, and the checklist line sits with its siblings.
  - The research cases sit under `research/change-description-authoring/cases/`, listed in the tree.
  - Layout of the two case directories matches each other.
- **Gate.** I ran no repository gate. A markdownlint gate may apply to `cases/*/*/result*.md`, which are pasted outputs. The research README says its result files are excluded from markdownlint, and I did not check whether the `cases/` paths are covered by that exclusion.

## Item 4: Names by content, not by position

- **Run names.** "`result-2.md`" and "result-2" name runs by ordinal. They are filenames under a directory and the README's table lists them one per row, so I rate it taste.
- **Prose.** "Three versions of the rule", "the first/second" in the 4367 README narrate versions by ordinal with no file to follow. I rate it taste. The commit's "two drafts of the rule" has the same property.
- **Headings.** The new `SKILL.md` headings add none.

## Item 5: The failure report

- The 4367 table is the report. It names which check fails per run, which satisfies "print the operands" better than a bare pass/fail.
- The checks themselves have no executable detection. Check 5, "Stated once", and check 1, "short paragraph", are judged by reading. A rule with no mechanical test is an Item 2 gap rather than a failure-report gap, and I did not file it separately.

## Item 6: What the writer says it verified

- Stated: baseline runs on the previous skill tree (`1f020ce…`) fail checks 1 to 3, and runs on the new tree (`4798053…`) pass. I confirmed that the stored `skill-tree` files hold those two ids and that the new id equals the HEAD tree of the skill directory.
- **Word counts** in the README (756, 825, 792, 758, 779, 784, and 241, 251, 256, 249) match `wc -w` of the stored results.
- **Not checked:** I did not re-run the models. The cost paragraph, with its prices and token counts, cannot be checked offline. I rate it taste, since it is not used by a rule.

## Item 7: Siblings of the change

- **Package version.** The three version sites are consistent. `grep` for `1.4.0` next to the package name finds nothing left over. The pinning umbrella `qubership-repo-essentials/apm.yml` lists the package without a version, so there is no pin to bump.
- **Set-size sentences.** The skill's `description`, which decides whether it loads, does not mention breaks. I rate that taste: the skill loads on "pull request description" already.
- **README bullet.** The package `README.md` bullet was added.
- **Other repeaters of the slot order.** The `Before`/`After` example under "Pull request description" (`SKILL.md:262-300`) is unchanged and carries no breaks, so it does not contradict the rule. The changelog section's own "Breaking changes are marked in place" rule at line 543 addresses a different artifact and does not conflict.
- **Sibling skills:** `docs-page-authoring`, `problem-report-authoring` and `test-authoring` name the package only as an owner, so none needs an edit.
- **Paths showing the same symptom:** the commit-body path under rule 5 is the sibling the finding in item 1 covers.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Skill gives two orders for a description copied into a commit body (breaks first versus the body's shape) | Substantive | `SKILL.md:86-88`, `:257-260` against `:310` and `:637` | Make `:310` and `:637` say the lead stays, or drop the "lead stays" sentence |
| Case READMEs quote a rule title that does not exist | Substantive | `cases/pgjdbc-4367-breaks/README.md` intro; `cases/pgjdbc-4392-no-break/README.md` intro | Quote the current heading, "A break leads the description unless the next release from the target branch is a major" |
| Effort level for Opus: commit message says high, README says session default | Substantive | commit message against `4367 README` "Running it" | State the effort each model actually ran at, in one place |
| No case where the next release is a major, or where it is unknown; no case for the description copied into a commit body | Substantive | `cases/` | Add a major-release run, or state in the README that the carve-out and the squash arm are untested |
| "The trailer decides" does not say what it decides | Substantive | `SKILL.md:247-248` | Say that a repository whose tool reads the trailer as a major bump treats the release as a major, so the lead is not required, or that the trailer is written and the lead stays |
| Skill claims the rule without the README's "not always" qualifier | Taste | `SKILL.md:234-260` | None needed; the README carries it |
| "Short paragraph" has no ending clause | Taste | `SKILL.md:252-254` | Add "absent where the break lines alone say which code breaks" |
| Pull request table header says "in order" while slot 3 now leads | Taste | `SKILL.md:192` | Say "in order, except that slot 3 can lead" |
| Ordinal names for versions and runs (`result-2`, "the first, the second") | Taste | 4367 README | Name by content |

**Not checked:** I did not run the models, the repository gates (markdownlint, lychee, the `apm` validators) or the drift script, and I did not review the prose for style beyond where a sentence read wrongly.
