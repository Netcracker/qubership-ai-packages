# Final review: `4f69810..HEAD` (86028c3, one commit)

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message alone. I also read the two case READMEs, which claim cases too. There is no previous report.

**Skills.** I loaded `apm-authoring` and `english-developer-style` from the given directory. I did not read the `english-developer-style` file.

**Drift script.** I did not run `comment-drift.py` meaningfully. The change has no code, only a skill, READMEs, manifests and research cases, so I used the §2a analogues. The suite and markdownlint were not run.

## Item 1: Comments consistent with the code and with each other

Analogue: statements one file makes about another, and section references.

- **Section references.** I checked the `§4 rule 5`, `§5`, `§7` and `§2` references against the headings. They all resolve: `BREAKING CHANGE:` is at line 706, rule 5 at 637, and §7 holds "no section for an absent concern".
- **Rule 5 contradicts the new lead (substantive).**
  - Line 640 says the description under rule 5 is shaped "as §2's commit body". That body is problem-first, with breaks as `User-visible:` lines.
  - Lines 257-260 say that under rule 5 "the lead stays" and the body "opens with its breaks and then its problem". Line 86 says the same.
  - Rule 5 and line 310 ("takes the body's shape instead") are unchanged, so a reader of §4 gets the opposite answer.
  - Another reading is open too. The lead is "slot 3's break lines", yet slot 3 under rule 5 is written as `User-visible:` lines. It is unclear whether the lead lines carry that label and whether they are also kept in slot 4.
  - The slot 3 row also puts a slot "ahead of slot 1" in a table that says "Six slots, in order".
- **Case READMEs quote a rule the skill no longer states (substantive).**
  - `pgjdbc-4367-breaks/README.md:6-7` and `pgjdbc-4392-no-break/README.md:5-6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - SKILL.md line 234 reads "…unless the next release from the target branch is a major". The quote is stale; the README also cites "SKILL.md §2" for it.
- **Effort setting contradicts the commit message (substantive).** The commit says "Opus and Haiku (effort high)". The 4367 README line 33 says "Haiku ran at effort `high`; Opus at the session's default". The 4392 README line 22 says only Haiku ran at `high`.
- **Narration of the change.** The rule text has none. Line 86's "puts the problem right after them" is a rule, not narration.
- **Count and list claims.**
  - Tree ids: the rule runs all carry `4798053…`, which equals `HEAD:` the skill dir. The baselines carry `1f020ce…`, which equals `HEAD~1:` the skill dir, so they are runs on the skill before the rule.
  - Table claims in the 4367 README: I checked the `grant insert` column (opus result-2 leaves it in Scope; the other three put it in the lead) and the 5-of-6 literals. All hold.
  - The six word counts for 4367 and the four for 4392 were not checked.

## Item 2: Claimed cases covered

Claimed: the break leads in a non-major release; the result-shape change is a break; a later-statement failure is a break; a fix is not a break; a change with no break grows no section; the commit body keeps problem-first; unknown release means breaks lead; a major means breaks stay first in slot 3.

- **Break leads, result shape, later-statement failure.** Covered by the `pgjdbc-4367-breaks` checks 1-3, with runs on Opus and Haiku and baselines.
- **Fix is not a break.** Check 4 is stated and the results are in the table. I did not verify it in each result.
- **No break, no section.** Covered by `pgjdbc-4392-no-break`.
- **Unknown release means breaks lead, and a major means breaks stay first in slot 3.** No case. The prompt fixes `pgjdbc.version=42.7.14`, so the patch-release arm is the only one run. See item 3.
- **Commit-body rule.** The commit body order and the rule-5 behaviour are claimed in the commit message but have no prompt and no run.
- **Commands in the changed files.** The only command is the case's gradle line, which sits inside the author's draft in `prompt.md`, not an instruction to a reader. Nothing runs it; none, as expected for a draft.
- **Hunks no sentence claims.**
  - The version bump 1.4.0 → 1.5.0 appears in four places: `apm.yml` (package), `apm.yml` (root), `marketplace.json`, and the package README text. The commit message never mentions it.
  - It is consistent, and the contract change plausibly justifies it, so this is taste. The request is one sentence in the message.

## Item 3: Boundaries, partitions, and the negative control

- **Partitions the change claims but has not tested.** The rule has three arms: patch (tested), major (untested) and unknown (untested). The commit does not claim a run for the other two, but the skill states both. Request: a case with a major target, where breaks stay first in slot 3, and one with no version evidence.
- **Control.** `pgjdbc-4392-no-break` is the negative control for "no break". It has no baseline (origin/main) arm, so "grows no section" is compared against the draft's 209 words rather than against a run without the rule. That is taste.
- **Effort.** Opus ran at a different effort level than Haiku, so the Opus and Haiku rows are not comparable. See item 1.
- **Prior state.** The change replaces nothing persisted. The version bump means installs of 1.4.0 get an update; nothing else is read back.
- **Added instructions: 4.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:244` "after at most a short paragraph that says which code breaks" | a description with a single break line that already names the code | a paragraph restating the one break line | "only where there is more than one break line" |

Not findings: `:233-240` (a failure that now succeeds is a fix, a major ends the lead, a change with no break grows no section), `:236-238` (the "unknown release" rule: the rule states its own cost).

## Item 3a: Level, placement, and the environment

- Each rule lives in the file it belongs to: the skill, the package README, and `research/…/cases/`, beside the siblings.
- `cases/` is new but the research README now lists it.
- The repository's registration gate (marketplace and `apm.yml` versions) is consistent across all three places; I did not run any gate.

## Item 4: Names by content, not by position

- `result.md` and `result-2.md` name runs by ordinal. The README table points at both. This is taste: it needs a content name, such as the model plus the effort or the draft of the rule.
- `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break` name cases by content. Fine.

## Item 5: The failure report

Analogue: each rule's detection. Checks 1-6 of the 4367 README detect the lead, the result shape, the later-statement failure, and the guards. They reach what they name. One check is weaker than the rule: check 1 passes any description that opens with the breaks, while the rule also requires "a short paragraph at most". Taste, since the Opus runs open with a short paragraph and pass.

## Item 6: What the writer says it verified

- The commit states a red run on the baseline: all four baseline results fail the checks the rule is for, and the runs with the rule pass them. That is the bad case and the exemplar.
- The control grows no section in four runs.
- Rewrite applied again: the skill's own worked example (the *After* at lines 261-300) is problem-first prose and carries no breaks, so it is not contradicted. Line 310 still says that under rule 5 the description "takes the body's shape", which is the item 1 contradiction.

## Item 7: Siblings of the change

- **Places that list the package.** `marketplace.json`, root `apm.yml`, the package `apm.yml` and the package README: all updated. The umbrella and `english-developer-style` mention the package by name and need no change.
- **The old count and old wording.** Line 86 and the checklist line for "Problem" were both updated. The line 190 intro "Six slots, in order" was not, which is the slot-3-ahead-of-slot-1 point in item 1.
- **The checklist.** The new "Breaks" line is present. The "Headings" line (857) says headings are absent from a rule-5 body, while the lead says "under a `Breaking changes` heading where the description has headings". For a rule-5 description the heading is allowed in one text and forbidden in the other; this goes with the rule-5 finding.

## Findings

| # | Finding | Label | Where | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Rule 5 and line 310 say a squash-copied description is shaped as the problem-first commit body; the new text says the lead stays and the body opens with its breaks. The lead's label (`User-visible:` or not), its repeat in slot 4, and its heading under the "no headings in a rule-5 body" checklist line are undefined. | Substantive | SKILL.md:86, 233-260, 310, 640, 857; slot 3 row | Edit rule 5 and line 310 to match, and say whether the lead lines are `User-visible:` lines |
| 2 | Both case READMEs quote the rule as "promises compatibility", not the skill's "unless … is a major" | Substantive | `pgjdbc-4367-breaks/README.md:6-7`; `pgjdbc-4392-no-break/README.md:5-6` | Quote the current wording |
| 3 | The commit says Opus ran at effort high; the READMEs say session default | Substantive | commit message; `pgjdbc-4367-breaks/README.md:33` | Correct one to match what ran |
| 4 | The major and unknown-release arms have no case | Substantive | commit; SKILL.md:234-242 | Add one case each, or say they were not run |
| 5 | A single break line gets a paragraph restating the code that breaks | Substantive (table row 1) | SKILL.md:244 | "only where there is more than one break line" |
| 6 | The version bump is not claimed in the message | Taste | four manifests | Add a sentence |
| 7 | `result-2.md` is an ordinal name; the 4392 control has no baseline arm | Taste | cases | Name by content; add a baseline run |

Not checked: the suite, markdownlint and the cross-file link check were not run, and checks 4 and 5 of the 4367 README were not verified per result. The prose was not reviewed for style.
