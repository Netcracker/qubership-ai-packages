# Final review: `4f69810..86028c3` (`feat(change-description-authoring): lead the description with breaks unless the next release is a major`)

**Inputs.** No separate task statement was given, so item 2 takes its claimed cases from the commit message alone. The change has no code: it edits a skill, its README and manifest, the marketplace entries, and a research directory. The drift script was not run, because there are no members to parse. Each item below reads its §2a analogue, and I loaded `apm-authoring` and `english-developer-style`. There is no previous report. I did not run anything that needs a model.

## Item 1: comments consistent with the code and with each other (analogue: statements about other files and about the skill itself)

Checked: the section references, the version bump in three places, the case READMEs against the skill and against the stored results, and the new text against the old text around it.

- **Finding 1 (substantive).** Both case READMEs quote a rule title that does not exist.
  - `pgjdbc-4367-breaks/README.md:5-6` says the case tests "SKILL.md §2, 'A break leads the description where the next release from the target branch promises compatibility'".
  - `pgjdbc-4392-no-break/README.md:4-5` quotes the same title.
  - The skill's line is "A break leads the description unless the next release from the target branch is a major." (`SKILL.md:234`).
  - A reader who greps for the quoted string finds nothing, and "promises compatibility" is a different criterion from "is a major".
  - Request: quote the title as it stands. Better, name it by section and do not repeat it.
- **Finding 2 (substantive).** The README contradicts the commit message on effort.
  - The commit message says "Opus and Haiku (effort high)".
  - `pgjdbc-4367-breaks/README.md` says "Haiku ran at effort `high`; Opus at the session's default".
  - The 4392 README says only "Haiku at effort `high`".
  - Request: make the two agree, and state the Opus effort the runs actually used.
- **Finding 3 (substantive).** The rule contradicts the rule it points to when a description becomes the commit body.
  - `SKILL.md:310` says "Under §4 rule 5 the description is the commit body and takes the body's shape instead."
  - `SKILL.md:637` says to "shape it as §2's commit body".
  - The new text at `SKILL.md:257-261` says the commit body keeps problem first with breaks as `User-visible:` lines. It then says the lead stays under rule 5, so "that body opens with its breaks and then its problem".
  - The checklist at `SKILL.md:857` says headings are absent from such a description. The new text says the lead goes under a `Breaking changes` heading "where the description has headings".
  - So a squash-merged description gets two opposite instructions for its first lines. An agent that follows line 310 or 637 puts the problem first. One that follows line 259 puts the breaks first.
  - It is also unclear whether the breaks are then repeated as `User-visible:` lines or stated once.
  - Request: one sentence at line 310 that says what shape the rule 5 body takes (breaks lead, no heading, and whether `User-visible:` repeats them), and the same wording at 637.
- **Finding 4 (substantive).** A repository template conflicts with the heading clause.
  - `SKILL.md:252` says to open "under a `Breaking changes` heading where the description has headings".
  - `SKILL.md:299-300` says that where the repository has a template, use its headings.
  - A description in a `Summary`/`Testing` template has headings, so the agent adds a heading outside the template. Or it reads "use its headings" and puts the breaks under `Summary`.
  - Request: say where the break lead goes when a template exists.
- **Finding 5 (taste).** `SKILL.md:247-248`, "the trailer decides, and it is written whatever the description does", reads two ways.
  - It can mean that the tool then bumps the major, so no lead.
  - It can mean that the trailer is written whatever happens.
  - The preferred reading is: a `BREAKING CHANGE:` trailer in a repository whose tool bumps the major makes the next release a major, so the lead is dropped.
- **Narration.** None of the changed text narrates with `now`, `no longer`, or `used to` outside the Before/After examples. `SKILL.md:86-88` is the only edited sentence of the slot-1 prose. Its subject is long, but it reads correctly.
- **Cross-references.** They resolve: §4 rule 5 is at line 637, §5 holds the `BREAKING CHANGE:` row at line 706, and §7 holds "no empty heading" at line 791.

## Item 2: claimed cases covered

Claims from the commit message, each with its case and run:

| Claim | Case that covers it |
| --- | --- |
| Break leads when a patch release is next | `pgjdbc-4367-breaks`, check 1: `opus/result.md`, `opus/result-2.md`, `haiku/result.md`, `haiku/result-2.md` pass; the two `baseline/result.md` fail |
| Result-shape change is a break | check 2, same runs |
| Extended failure (`grant insert`) goes with the breaks, not in Scope | check 3: 3 of 4 pass, and `opus/result-2.md` leaves it in Scope. The commit message states this. |
| A change with no break grows no section | `pgjdbc-4392-no-break`, 4 runs |
| **Unless the next release is a major** | **no case** |
| **Release read from the version file, milestone, or branch name** | **only the version file is exercised** (the prompt gives `gradle.properties`); milestone and branch name have no case |
| **Where nothing says which release it is, the breaks lead** | **no case** |
| **Where squash copies the description, the lead stays; the commit body keeps problem first** | **no case**. The prompt has no commit body and no merge model other than the classifier line. |
| **`BREAKING CHANGE:` trailer decides** | **no case** |

- **Finding 6 (substantive).** Four claimed branches of the rule have no case: the major-release exception, the unknown-release default, the commit-body and squash shape, and the trailer. The commit message presents the rule as covering them. The only evidence is one patch-release input with a break and one without.
  - A major-release run of the 4367 prompt is the arm that would fail if the exception were deleted, and the rule has never been run on that input.
  - Request: either add a case with a major target (the prompt's `pgjdbc.version=43.0.0` is enough) and a commit-body case, or have the commit message and README say that only the patch-release arm was tested.
- **Commands.** Two commands appear in the change. The checks in the case READMEs are described, not run by a script.
  - `git archive <rev> <path>` in `pgjdbc-4367-breaks/README.md` (Running it) has no CI job or script behind it, and it needs `| tar -x` to produce files. This is taste. It is a reproduction note, and the outcome it promises is only "copied out".
  - Item 2 lists no other command line.
- **Reverse reading.** The hunks that change a rule (`SKILL.md`), a version (`apm.yml`, `marketplace.json`, the package `apm.yml`) and the READMEs are all claimed by the commit message. The version bump to 1.5.0 is the same in the three places that carry it, and `apm.yml:36` and `:48` are other packages. No unclaimed hunks.

## Item 3: boundaries, partitions, and the negative control

Added instructions: 5 (the break lead and its release condition; the definition of a break including the extended failure; reading the release from the version file, milestone, or branch name; the unknown-release default; the commit body keeping its order). I counted the heading-and-paragraph clause and the checklist line as part of the first. One row follows.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:253-256` "Where nothing says which release it is, the breaks lead" | a stacked pull request that targets a feature branch | a `Breaking changes` lead for a branch that ships in no release | "only where the target branch ships a release" |

Not findings: `:235-241` (the break definition; a fix is excluded by its own sentence), `:257-261` (ended by "where §4 rule 5 makes…").

- **Finding 7 (substantive).** The negative control is weaker than the one the rule claims.
  - `pgjdbc-4392-no-break` has no `origin/main` arm.
  - Its words (241, 251, 256, 249) are compared with the draft's 209, not with the baseline output.
  - So the README shows that the rule added no section. It cannot show that the output "did not grow", and the 16 to 22 percent over the draft is unexplained.
  - Request: one baseline run of the control per model (`apm-authoring` rule *Fix a bad output where the rule stops*).
- **Partitions.** The other arms are in Finding 6. Only the patch-release arm with a break has a baseline.
- **Pre-existing state.** The skill is read fresh by the drafting agent through `git archive`; there is no installed-copy path, so none was tested. Nothing in the change migrates anything.
- **Replaced mechanism and limits.** Neither applies.

## Item 3a: level, placement, and the environment

- The cases sit under `research/change-description-authoring/cases/`, beside the phase files. The research README lists `cases/` in its tree and the date line. There is no gate that runs the cases.
- The registration entries are the ones the repository's own list requires: `apm.yml`, the package `apm.yml`, and `marketplace.json`. I did not run an offline gate; I know of none for them here.
- The case READMEs say the first line of the runs is the model's output "pasted unedited", but the results have no wrapper. They are stored as the model wrote them.
- The drafting agent reads `english-developer-style` from `agent-packages/english-us-developer-style`. Both case READMEs say so, and the path exists. The `skill-tree` files hold `4798053…`, which equals `git rev-parse HEAD:agent-packages/change-description-authoring/.apm/skills/change-description-authoring`.

## Item 4: names by content, not by position

none. The cases are named by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`, `result-2.md`). The checks are numbered in the READMEs, and the results table cites them by name as well as number. `result-2.md` is an ordinal file name, which is taste: `opus/result-2.md` in the commit message and README means "the second run".

## Item 5: the failure report

The results table of each README lists which check fails per run, by name. Each check has a pass/fail condition a reader can apply to the text. A rule's detection is the check list. Checks 4 to 6 guard other facts, and the README says so. none.

## Item 6: what the writer says it verified

The commit message states the runs and the baseline: "Without the rule both models put Why first and left both breaks in place". The `baseline/` directories carry the skill tree before the rule (`1f020ce…`) and the failing results. The exemplar that passes is `opus/result.md`, and the bad case that fails is `baseline/result.md`. The rewritten rule was not applied again to the *After* example in the skill. That example has no break, so it is unaffected. For the added instruction, the noise input is the 4392 control, and Finding 7 covers its missing baseline.

## Item 7: siblings of the change

- The skill is the only place that states the slot order. `SKILL.md:86`, the table row at line 198, the checklist at lines 831-833 and 849-852, and the package README all carry the new rule.
- The instructions file (`.apm/instructions/…instructions.md`) is a trigger and needs no change.
- Other packages name `change-description-authoring` only to delegate to it (`docs-page-authoring`, the two `english-*-developer-style` packages). No sentence there describes the order of a pull request description.
- No sentence counts the slots with a number that changed.
- `marketplace.json` repeats the description string of `apm.yml`, and both are unchanged and equal.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Both case READMEs quote a rule title the skill does not have | Substantive | `pgjdbc-4367-breaks/README.md:5`, `pgjdbc-4392-no-break/README.md:4` | 1 |
| README says Opus ran at the session default; the commit says effort high for both | Substantive | `pgjdbc-4367-breaks/README.md` (Running it), commit message | 1 |
| Rule 5 body shape: lines 310 and 637 say the body's shape, line 259 says the lead stays | Substantive | `SKILL.md:310`, `:637`, `:259` | 1 |
| Heading clause conflicts with "use the template's headings" | Substantive | `SKILL.md:252`, `:299` | 1 |
| "The trailer decides" reads two ways | Taste | `SKILL.md:247` | 1 |
| Major, unknown-release, commit-body, and trailer arms have no case | Substantive | commit message; `cases/` | 2 |
| `grant insert` stays in Scope in 1 of 4 runs | not a finding (stated in the commit message and README) | `opus/result-2.md` | 2 |
| `git archive` line is not a runnable form | Taste | `pgjdbc-4367-breaks/README.md` (Running it) | 2 |
| Stacked pull request to a feature branch gets a break lead | Substantive | `SKILL.md:253` | 3 |
| Control has no `origin/main` arm, so growth is measured against the draft only | Substantive | `pgjdbc-4392-no-break/README.md` (Results) | 3 |
| `result-2.md` names a run by ordinal | Taste | `cases/*/*/result-2.md` | 4 |

I did not check the drift script (not applicable), the rendering of the new skill text through `apm compile`, or whether the cited pgjdbc pull requests say what the cases attribute to them. The network was not available.
