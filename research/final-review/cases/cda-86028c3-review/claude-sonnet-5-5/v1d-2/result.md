# Final review: `4f69810..HEAD` (one commit, 86028c3)

**Input limits.** There is no separate task statement, so the claimed cases come from the commit message alone (§1, §2 item 2). I did not run the drift script: the change is a skill, a package README, version fields, and a research directory, with no members for it to parse. I loaded the copies of `english-developer-style` and `final-review` under the given skills directory. `test-authoring` does not apply, since there are no tests. `apm-authoring` is not among the three skills I was given, so the form below uses §2a's analogues without its rule names. I did not verify the pgjdbc#4367 and #4392 links, since there is no network. No earlier report exists for this change.

The claimed cases, from the commit message:

- The description leads with breaks unless the next release is a major.
- The release is read from a version file, a milestone, or a name.
- The leads stay where nothing says which release it is.
- A break is defined by five classes.
- The commit body keeps the problem first, with breaks as the first `User-visible:` lines.
- Where squash copies the description into the commit, the lead stays.
- A change with no break grows no section.
- Result counts: `pgjdbc-4367-breaks` runs on Opus and Haiku at effort high, two with the rule and one baseline each. The negative control `pgjdbc-4392-no-break` ran twice per model.
- The earlier drafts are summarized in the case README, not stored.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another, counts, citations)

Findings:

1. **Both case READMEs misquote the rule under test.**
   - `cases/pgjdbc-4367-breaks/README.md` (intro, last sentence) cites the rule as "SKILL.md §2, 'A break leads the description where the next release from the target branch promises compatibility'".
   - `cases/pgjdbc-4392-no-break/README.md` (intro) quotes the same wording.
   - The committed rule reads "A break leads the description unless the next release from the target branch is a major" (SKILL.md line 234, in §2's pull request description part).
   - A reader who greps the skill for the quoted heading finds nothing. The README also reads as if "promises compatibility" were the condition, which is a different test from "is a major".

2. **The effort setting is stated two ways.**
   - The commit message says "on Opus and Haiku (effort high)".
   - The 4367 README says "Haiku ran at effort `high`; Opus at the session's default".
   - The 4392 README says only "Haiku at effort `high`".
   - One of these is wrong, and the reader cannot reproduce the Opus runs from the other.

3. **The unchanged paragraph on how the description maps to the commit body now contradicts the new text.**
   - It says slots 1 and 2 are the body's slots 1 to 3 and slot 3 is the body's slot 4. Where the merge model copies the description, they are the commit body, with slot 3 written as `User-visible:` lines.
   - The new text says slot 3's break lines go ahead of slot 1, and that the copied body "opens with its breaks and then its problem".
   - The old paragraph was not touched, so the mapping now holds only when no break leads.

4. **The release-tool sentence is ambiguous.** "The trailer decides, and it is written whatever the description does" does not say what the trailer decides. The contrast with "a major" is only implied. Taste, below.

5. **Other consistency checks passed.**
   - Cross-references: `§5` resolves to the `BREAKING CHANGE:` row at line 706, `§7` to the no-empty-section bullet, and `§4 rule 5` to the description-is-the-body rule.
   - Counts: "six slots" and "five slots" are unchanged and still correct.
   - Version fields: `apm.yml` (package), root `apm.yml`, and `marketplace.json` all read 1.5.0. No other 1.4.0 entry belongs to this package.
   - Result-table figures: word counts, "3 of 4 move the extended failure out", and "all three Haiku results end with a Generated line" all match the files.
   - Narration: no "now" or "no longer" outside a regression comment.

## Item 2: claimed cases covered (analogue: the case or check that detects each claimed rule)

| Claim | Evidence | Verdict |
| --- | --- | --- |
| Breaks lead in a patch release | 4367 checks 1 to 3; 6 runs | covered |
| A result-shape change is a break | 4367 check 2 | covered |
| A failure extended to inputs that worked before is a break | 4367 check 3 | covered, 3 of 4 runs |
| A change with no break grows no section | 4392 checks 1 and 2 | covered |
| **A major release keeps breaks first in slot 3** | none | **no case** |
| **Unknown release means breaks lead** | none | **no case** |
| **The release is read from a version file, milestone, or branch name** | the prompt gives no such source; checks 1 to 3 do not detect it | **no detection** |
| **A `BREAKING CHANGE:` trailer is written regardless** | none | **no case** |
| **The commit body keeps the problem first, breaks as the first `User-visible:` lines** | the cases generate PR descriptions only | **no case** |
| **A copied description keeps the lead and a body that opens with breaks** | none | **no case** |
| Fix "stays out of the lead" (the commit message does not claim it, but the README does) | 4367 check 4 | covered |

The rule has no detection for 6 of its 10 clauses. I name them as one finding in the table below.

Every hunk belongs to a claim of the commit message. The version bump, README line, marketplace entry, and research index line are each explained by it. The commit message says the same about the case READMEs. No command line is added in the changed files, so the command analysis does not apply.

## Item 3: boundaries, partitions, and the negative control (analogue: genres, modes, state left by an earlier version, values users pass)

- **Control present.** `pgjdbc-4392-no-break` is the negative control for the lead. It stays green on the base commit by construction. It was not run on `origin/main`, which is fine, because it asserts absence.
- **Missing partitions.** The target of both cases is a patch release read from the prompt. The three other situations the rule distinguishes have no run:
  - a major target;
  - a target with no version information;
  - a squash that copies the description.
- **Single prompt.** The positive case is one change, with one break of each of three kinds. The rule lists five break classes (call that now fails, return value or shape, removed or renamed option, changed default, changed error code). Only the first two are exercised. The README says the sentence moves the `grant insert` case "most of the time and not always", so the extended-failure clause is the least stable and has two runs per model.
- **State left by an earlier version.** An agent that has the earlier 1.4.0 skill installed meets the new text with the old Before/After example, and that example is unchanged. The example carries no break, so it does not conflict.
- **Mechanism and limits.** There is no replaced mechanism and no limit here.

### Table of instructions added or widened

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where nothing says which release it is, the breaks lead" | A break in a service or application that has no versioned release and no callers of a released API | A `Breaking changes` lead for a deployment-only change whose reviewer does not decide on a release | None. Suggest: "…, and the change is published as a versioned release" |
| "after at most a short paragraph that says which code breaks" | One break whose line already names the code that breaks | A sentence that repeats the break line before the line | "at most" permits none, but nothing says to omit it when the line names the code. Suggest: "only where several breaks share a condition" |
| "A failure the change extends to inputs that worked before is a break, even though other inputs failed the same way already" | A validation fix that rejects input which used to corrupt data silently | A lead item for a deliberate rejection, which the author may want in a normal slot | "Whether the old behavior was right does not decide it" ends it the other way and is quoted as the intended outcome. No finding. |
| "The commit body keeps its order… breaks as the first `User-visible:` lines" | A commit with a break and no other outcome | A single `User-visible:` line first, which is the same as the only line | Nothing is lost. No finding. |
| "A change with no break has neither the lead nor an empty heading" | A change with no break | Nothing | Already ended by its own sentence. Row is not a finding. |
| Checklist: "does the description open with the break lines… Where nothing breaks, is there no lead and no empty heading" | A change with no break | No lead | Already ended. Not a finding. |

## Item 3a: level, placement, and the environment (analogue)

- **Layout.** The cases sit under `research/change-description-authoring/cases/` with a prompt, README, and per-model results. The research README lists the directory. This matches the sibling files.
- **Registration.** The root `apm.yml`, the package `apm.yml`, and `marketplace.json` all moved together. I did not run the repository's gate, since I was told not to change files and the gate was not named.
- **No tutorial-only sentences.** Each added sentence carries a platform fact (version files, branch names, the trailer rule), except "In a release that is not a major, the reviewer's first decision is whether the change may ship in it at all". That sentence is the rationale for the rule and is the reason the order changes.
- **Case runs.** The 4367 README says the drafting agent reads the skill and `english-developer-style` as files and does not use the Skill tool. That is consistent with the `skill-tree` ids. The ids are right: the with-rule runs point at `HEAD`'s tree (`47980534…`), and the baselines at `HEAD~1`'s (`1f020ce5…`).

## Item 4: names by content, not by position

None. The cases are named `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break`, by number and by content. The two result files per model are `result.md` and `result-2.md`, an ordinal. A reader of the table must open the README to learn the second is a second run. Taste, in the table.

## Item 5: the failure report (analogue: a rule's detection says what a failure looks like)

- The checks in the 4367 README name what to look for and what a failure looks like. The runs table marks a failure with the check that failed, such as "fails: in Scope".
- Check 5 ("stated once") has no failing run in the table.
- The 4392 README groups its results as "all four pass all three checks", with no per-run table. That is adequate, because nothing failed.
- The skill's own new rule has no detection stated for clauses 1 and 3 to 6 beyond Item 2, as listed.

## Item 6: what the writer says it verified

The commit message states the runs and their outcomes. Baseline runs on `origin/main` fail checks 1 to 3, which is the red run. The rule's runs pass them, which is the green run. The commit message also says earlier drafts were run and summarized rather than stored, so a reader cannot re-check that sentence. The cases do not state a run on a prompt where the added instruction is noise beyond the one 4392 control, and that control covers only a fix with no break.

## Item 7: siblings of the change

- **Set members.** The change adds no member to a set. It adds a heading name, `Breaking changes`, a lead position, and a checklist item.
- **Other places that list the order of slots or name the breaks:**
  - Line 222 and 226 say "Breaks come first". They are now qualified by the new paragraphs but not edited, so they still read as "first in slot 3" and agree with the "Where the next release is a major" sentence.
  - Line 87 was edited.
  - Line 845 (the User-visible checklist item) says "breaks first"; it is consistent with slot 3.
  - The changelog section (line 543) already marks breaking changes in place and sorts them first. A changelog entry is a different artifact, so the rule's scope sentence ("leads the description") does not reach it. That is correct, but nothing says so. Taste.
- **Old-size prose.** No sentence counts the slots or the readers differently.
- **Remedies and symptoms.** The change writes no remedy table.
- **Package README.** Its new bullet agrees with the skill, except that it says "the commit body keeps them first in its outcome slot" without saying the problem still comes before them. A reader of the README alone could take "first" as first in the body. Taste, below.

## Findings

| # | Finding | Label | File and line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | Both case READMEs quote the rule as "where the next release … promises compatibility" and cite "SKILL.md §2", but the rule reads "unless the next release from the target branch is a major" | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md` intro, last sentence; `…/pgjdbc-4392-no-break/README.md` intro | Quote the committed wording, or link the heading it sits under |
| 2 | Effort for the Opus runs is stated as "high" in the commit message and as "the session's default" in the 4367 README; the 4392 README names only Haiku | Substantive | `…/pgjdbc-4367-breaks/README.md`, "Running it", last sentence; `…/pgjdbc-4392-no-break/README.md`, "Results" | State the effort actually used for each model in both READMEs, and correct the commit message or the README so they agree |
| 3 | Six of the rule's ten clauses have no case: major target, unknown release, source of the release (version file, milestone, name), `BREAKING CHANGE:` trailer, commit-body order, copied-description order | Substantive | SKILL.md lines 234 to 260; `cases/` | Add the partitions as cases, or state in the 4367 README that they are untested; the major-target arm is the most owed, since it is the control for the lead |
| 4 | The paragraph on how slots 1 to 3 map to the commit body says slot 3 is the body's slot 4, which no longer holds when the lead is a break | Substantive | SKILL.md, the paragraph beginning "Slots 1 and 2 are the commit body's slots 1 to 3" | Add "except for the break lines, which lead (below)" or point to the new paragraph |
| 5 | "No break" condition for the unversioned-service input: the lead fires, and the instruction has no end clause for it | Substantive | SKILL.md, "Where nothing says which release it is, the breaks lead" | Add a clause such as "…and the change is published as a versioned release" |
| 6 | The short paragraph before the break lines has no stop clause for a single self-explanatory break | Taste | SKILL.md, "after at most a short paragraph that says which code breaks" | Say "only where the lines share a condition"; expect to be declined, since "at most" already allows none |
| 7 | "the trailer decides" does not say what it decides | Taste | SKILL.md, "the trailer decides, and it is written whatever the description does" | Write "the trailer settles that the release is a major, and it is written whatever the description does" |
| 8 | The package README says the commit body keeps breaks "first in its outcome slot", which reads as first in the body | Taste | `agent-packages/change-description-authoring/README.md` new bullet | Add "after the problem" |
| 9 | `result.md` and `result-2.md` name runs by ordinal | Taste | `cases/*/*/result-2.md` | Leave as is if the README's table maps them, which it does for 4367; I would not rename |

## What this review did not check

I did not run the repository's gate, the case prompts, or any model, I did not open the pgjdbc pull requests to check the quoted facts, and I did not review the prose of the skill for style beyond sentences that read wrongly.
