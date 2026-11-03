# Final review: `4f69810..HEAD` (86028c3, `change-description-authoring` 1.5.0)

**Scope.** There is one commit. No task statement was handed over, so item 2 takes its claimed cases from the commit message. The change has no code, so I used the §2a analogues under every item. The drift script was not run, because there are no members to parse. I loaded `english-developer-style` and `test-authoring` from the given skills directory. I did not load `apm-authoring`, which is outside the three skills named, and I did not run the suite or the package gate.

## Item 1: comments consistent with the code and with each other (statements between files)

Analogue: every statement one changed file makes about another file, a count, or a cited section.

- **Stale rule name in both case READMEs (substantive).**
  - `cases/pgjdbc-4367-breaks/README.md:7` and `cases/pgjdbc-4392-no-break/README.md:6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - The shipped heading is "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`).
  - The quoted wording was one of the earlier drafts.
- **Contradiction with §4 rule 5 (substantive).**
  - `SKILL.md:637-638` says that under a squash or merge commit with "title and description", the description is the commit body: "shape it as §2's commit body". That shape is problem first, with breaks as the first `User-visible:` lines.
  - The new text at `SKILL.md:257-260` says the lead stays: "that body opens with its breaks and then its problem".
  - `SKILL.md:310` says "Under §4 rule 5 the description is the commit body and takes the body's shape instead".
  - Rule 5 was not edited, so a reader who follows it gets the opposite order from line 259. One of the two must say which wins.
- **Slot table and prose disagree (substantive).**
  - The slot 3 table cell at `SKILL.md:198` says breaks go "ahead of slot 1".
  - The table heading at `SKILL.md:192` still says "Six slots, in order". The sentence at `SKILL.md:225` says "The Why slot has no skip condition ... the reviewer's first question is why that version should change". The new rule says the reviewer's first decision is whether the change may ship.
  - `SKILL.md:226` says "Breaks come first" in slot 3 without the exception.
  - `SKILL.md:253-254` says slot 3 keeps only "the other outcomes", while line 198 puts the break lines in slot 3.
  - A reader cannot tell whether the break lines belong to slot 3 or to a new slot 0.
- **Effort setting disagrees (substantive).** The commit message says "Opus and Haiku (effort high)". `pgjdbc-4367-breaks/README.md:33` says "Haiku ran at effort `high`; Opus at the session's default". `pgjdbc-4392-no-break/README.md:22` says only "Haiku at effort `high`". Opus's effort cannot be both.
- **Cross-references checked and true.**
  - §4 rule 5, §5 (`BREAKING CHANGE:` row at line 706), §7 (no empty section, line 787), and "§2, pull request description" all exist.
  - The skill tree id in the `skill-tree` files matches `git rev-parse HEAD:<skill dir>` (4798053…) for the rule runs. The baseline id (1f020ce…) matches the parent commit's tree.
  - The README's counts and run tags match the result files: `opus/result-2` has `grant insert` in Scope, all three Haiku 4367 results carry the "Generated with" line, and the 4392 controls have no `Breaking changes` heading.
  - The "Generated with" claim for the 4392 Haiku results is only partly confirmed: `result-2.md` and `result.md` both carry the line.
- **Narration:** none. `now` and `no longer` appear only in the commit message and the case results.

## Item 2: claimed cases covered

Analogue: a rule's test is its detection. The claims come from the commit message only.

| Claim | Covered by |
| --- | --- |
| Break leads unless the next release is a major | Checks 1-3 of `pgjdbc-4367-breaks` (patch release only) |
| Result-shape change is a break | Check 2 |
| Extended failure (`grant insert`) is a break | Check 3 (3 of 4 runs) |
| A fix that now succeeds is not a break | Check 4 |
| No break means no lead and no empty section | `pgjdbc-4392-no-break` checks 1-2 |
| Next release is a major, so breaks stay first in slot 3 | **none** |
| Release unknown, so breaks lead | **none** |
| Release read from the version file, milestone, or branch name | **none** (the prompt gives one of them) |
| A `BREAKING CHANGE:` trailer decides the release | **none** |
| Commit body keeps problem first with breaks as the first `User-visible:` lines | **none** (both cases are pull request descriptions) |

- **Untested partitions (substantive).** The major-release, unknown-release, and commit-body claims have no case. They are the exceptions the rule states and the commit message claims. The request is a case for the major and unknown branches, or a sentence in the case README that says they are not covered.
- **Commands the change tells someone to run:** none. The README's `git archive` line is a recipe for rerunning the cases, and no CI job runs it. That is acceptable for research cases.
- **Hunk to claim:**
  - Every hunk has a claiming sentence. The marketplace.json, `apm.yml`, and package `apm.yml` hunks are the 1.4.0 to 1.5.0 bump, and the commit message does not mention it.
  - The bump is expected for a skill change, and the three version fields agree.
  - Taste: one clause in the commit message would claim it.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the genres and modes the change claims. For a skill, the negative control is the table of added instructions.

- The negative control `pgjdbc-4392-no-break` exists. It has four runs, all passing.
- It has no `origin/main` baseline, so it shows the rule adds nothing to a no-break change. It does not show the baseline output was already clean. That is fine for its purpose.
- **Run counts (taste).** The positive case has one baseline run per model, and the grant-insert check passes in 3 of 4 runs. The README states this ("not always") and does not overclaim.
- The pre-existing state of the target is handled by the case design: the baseline runs use the old skill tree.

**Table of added instructions**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Open the description with the break lines (`SKILL.md:252`) | A project's first release with no released version, where "code that works on the released version" is empty | A `Breaking changes` lead for changes that break nothing released | none (taste) |
| "Where nothing says which release it is, the breaks lead" (`SKILL.md:248`) | A repository whose branch is a development branch of a pre-1.0 project | A lead where every release is breaking | "a break read first in a major release costs a paragraph" accepts the cost, so this is a taste row |
| "after at most a short paragraph that says which code breaks" (`SKILL.md:253`) | A single break whose line already says which code breaks | A restating paragraph above one self-explanatory line | none (taste) |
| A failure extended to inputs that worked before is a break (`SKILL.md:238`) | A failure on inputs that were already failing in all positions | n/a; ended by "for those inputs" | |
| Commit body keeps its order with breaks as the first `User-visible:` lines (`SKILL.md:257`) | A pull request description copied under rule 5 | Problem first | **Conflict with rule 5**, filed in item 1 |

Not findings:
- "a failure that now succeeds is a fix, not a break" is ended by the instruction's own sentence at `SKILL.md:240-241`.
- A change with no break is ended by "A change with no break has neither the lead nor an empty heading".

## Item 3a: level, placement, and the environment

- **Placement:** the cases sit under `research/change-description-authoring/cases/`, beside the phase files, and the research README lists the new directory. The rule is in the skill, and the package README has a new bullet.
- **Registration:** the three version fields agree. I did not run the repository's gate.
- **Tutorial-level sentences:** none found.
- **Duplicated skill text (taste, not a request):** the Breaks checklist line at `SKILL.md:849-851` restates the rule. That is the same instruction, so it gets no row.

## Item 4: names by content, not by position

- Case ids are named by pull request and content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`).
- `result-2.md` is an ordinal name for a rerun file. The README's table distinguishes the runs by file name, so the ordinal is the only identity. Taste: name them `run-1` and `run-2` consistently, or by seed. Not a request.
- The README's `1 to 3` and `4 to 6` check numbers are local to the README, and its list is a numbered one. No finding.

## Item 5: the failure report

Analogue: each rule's detection must detect that rule and be reachable.

- The checks name the literals to look for, so a failure names what was missing.
- **Check 4 (substantive):** it says `create table begin(atomic int); insert into t(a) values(?)` stays out of the lead. It does not say how a reader would tell, for a result that mentions the statement in a non-lead place, whether the check passed. This is partly mitigated by the results table, which marks pass and fail.
- **Check 5 ("Stated once"):** it checks "the Why slot or a later outcome list". It detects duplication, not the rule it is attached to, so it is a weaker property than the skill's rule. Taste.

## Item 6: what the writer says it verified

- The commit message states baseline runs on `origin/main` (one per model) and rule runs (two per model), with the pass and fail pattern. That is the red-and-green evidence for check 1: both baselines fail it and all four rule runs pass.
- There is no stated evidence for the major-release branch, the unknown-release branch, or the commit-body clause. See item 2.
- The checks are applied by reading, and the README does not say who or what scored them. Taste: say whether the scoring was by the author or by script.

## Item 7: siblings of the change

- **Sets that list members:** the change adds one rule to one skill. The package README, the marketplace entry, the root `apm.yml`, and the package `apm.yml` are updated.
- **Description sentence in the manifests:** it does not mention the new rule. Fine, since it is a general summary.
- **Other skills that name `change-description-authoring`** (`english-developer-style` in three copies, `docs-page-authoring`, `problem-report-authoring`) route to it without restating the slot order. No sibling needs the change.
- **Prose that counts the old set:** `SKILL.md:192` says "Six slots, in order". The break lead is a seventh position. This is the same finding as in item 1.
- **Other readers of the Why-first rule:** `SKILL.md:86` is edited. `SKILL.md:225` ("The Why slot has no skip condition ... reviewer's first question") and the checklist line at `SKILL.md:831` are partly adjusted, and line 225 is not. Same finding as in item 1.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Rule 5 says "shape it as §2's commit body", and the new text says the body opens with breaks, then problem. They conflict. | substantive | `SKILL.md:637-638` against `257-260`, `310` | Edit rule 5 and line 310 to say the lead stays, or drop the lead for copied descriptions. |
| 2 | Slot table says "Six slots, in order" with a slot-3 cell that goes ahead of slot 1. Line 225 says the Why slot comes first because the reviewer's first question is why. Lines 198 and 253 disagree on whether breaks are in slot 3. | substantive | `SKILL.md:192`, `198`, `225-226`, `253` | State once where the break lines sit, and qualify lines 225-226 with the exception. |
| 3 | Both case READMEs quote the rule as "promises compatibility", which is an earlier draft. | substantive | `pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | Quote the shipped heading. |
| 4 | Commit message says Opus ran at effort high. The 4367 README says Opus ran at the session's default. | substantive | commit message, `pgjdbc-4367-breaks/README.md:33`, `pgjdbc-4392-no-break/README.md:22` | Make the three agree with what was run. |
| 5 | The major-release, unknown-release, and commit-body claims have no case and no stated exclusion. | substantive | commit message, case READMEs | Add a case for the major and unknown branches, or state in the README that they are uncovered. |
| 6 | The version bump is not claimed in the commit message. | taste | the three version fields | Add one clause to the message. |
| 7 | Rule fires on a first release with no released version, and for a short paragraph above a single self-explanatory break. | taste | `SKILL.md:248`, `253` | Add "only where a released version exists" and drop the paragraph for one break, if you want them. |

This review covered consistency and coverage only. It did not check the pass and fail verdicts in the results table against the rule line by line, and it did not run the suite, the gate, or the mutation check. It also did not pass over the prose for style alone.
