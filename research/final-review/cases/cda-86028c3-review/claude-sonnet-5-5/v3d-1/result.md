# Final review of `4f69810..HEAD` (86028c3)

**Task statement:** none was handed over. Item 2 is answered from the commit message alone.

**Skills loaded:** `final-review` and `english-developer-style`. `apm-authoring` was not loaded because it is not among the three allowed skills, so rule citations from it are missing.

**Analogue used:** the change is a skill, a README, version metadata and a research directory, with no code. §2a applies under every item. The drift script ran and printed nothing, as expected for a change with no code.

**Previous report:** none.

## Item 1: comments consistent with the code and with each other

Analogue: each statement one file makes about another, and each count or section reference.

- The section references resolve. §4 rule 5, §5 (the `BREAKING CHANGE:` row), §7 ("No section for an absent concern") and §2 (pull request description) all exist.
- The skill-tree ids hold. `skill-tree` 4798… equals `HEAD:agent-packages/change-description-authoring/.apm/skills/change-description-authoring`. The baseline id 1f02… equals the same path at the base commit. So the runs were made on the committed skill and on the base.
- The versions agree across `apm.yml`, the package `apm.yml` and `marketplace.json` (all 1.5.0).
- The package README carries the new rule. The research README line about `cases/` is accurate.

Findings:

1. **Substantive.** Both case READMEs quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility", and the 4367 README cites it as "SKILL.md §2". The committed sentence is "A break leads the description unless the next release from the target branch is a major." The case README is the record of what was tested, so its quote should match the skill.
   - `research/.../pgjdbc-4367-breaks/README.md:7-8`
   - `pgjdbc-4392-no-break/README.md:5-6`
2. **Substantive.** The commit message says "Opus and Haiku (effort high)". The 4367 README says "Haiku ran at effort `high`; Opus at the session's default". The 4392 README says only that Haiku ran at `high`. One of them is false.
   - `pgjdbc-4367-breaks/README.md` ("Running it")
3. **Substantive.** `SKILL.md` §2 has two statements that pull in different directions.
   - Line 86 says "Slot 1 opens the body", then adds the clause that a rule-5 description puts the problem after the breaks.
   - Lines 257-260 say the commit body keeps problem first, with breaks as the first `User-visible:` lines of slot 4, "the label is what R4 and R5 search for".
   - The same passage says that where rule 5 makes the description the commit body, "that body opens with its breaks and then its problem". It does not say whether those opening lines carry the `User-visible:` label or sit under a `Breaking changes` heading.
   - Under rule 5 the description "takes the body's shape" (line 310), so an agent can read the lead as either. Either reading is defensible, and the text should pick one: the label that R4 and R5 search for, or the heading.
   - `SKILL.md:86-88, 257-260`
4. **Taste.** "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides, and it is written whatever the description does" (line 247) never says what the trailer decides. The reading is probably "the release is a major, so no lead". That conclusion is circular, because the trailer exists because of the break. Stating the outcome would remove the doubt.

## Item 2: claimed cases covered

Claims come from the commit message, since no task statement was given. The covering "test" for a rule is its detection, which here is a check in a case README plus a run.

| Claim | Covered by |
| --- | --- |
| Break lines lead unless the next release is a major | 4367 check 1; runs `opus/result.md`, `opus/result-2.md`, `haiku/result.md`, `haiku/result-2.md` |
| A result-shape change is a break | 4367 check 2 |
| A failure extended to later statements is a break | 4367 check 3. Four runs claim it: `opus/result.md`, `haiku/result.md` and `haiku/result-2.md` pass, and `opus/result-2.md` fails ("in Scope"). That matches the commit's "three of four". |
| A fix that now succeeds is not a break | 4367 check 4 |
| Break lines are not repeated | 4367 check 5 |
| Literals are kept | 4367 check 6 |
| A change with no break grows no section | 4392 checks 1 and 2 |
| "Where nothing says which release it is, the breaks lead" | not covered. Every case has a version file that says it is a patch release. |
| "Where the next release is a major, the breaks stay first in slot 3" | not covered |
| A `BREAKING CHANGE:` trailer or `!` | not covered |
| A commit body keeps problem first, with the breaks as the first `User-visible:` lines | not covered |
| Rule-5 squash keeps the lead and then the problem | not covered |
| Earlier Opus runs of two drafts of the rule | not stored, and said to be so |

Findings:

5. **Substantive.** Four of the rule's branches have no run, and the commit claims the rule without naming them as unexamined: the major release, the unknown release, the commit body, and squash under rule 5. The control is only the "no break" arm. The same-input counterpart is missing: the same #4367 break aimed at a major release should not lead. Request: one run with the major-release version file, or a sentence in the case README saying those branches are untested.
6. **Taste.** The numbers in "Cost" are unsourced: token counts, and prices of $4 and $0.10 per million input tokens. They are not claimed by the rule. Either cite the price source or drop the figures.
7. **Hunk-to-claim.** Every hunk belongs to a commit-message sentence: the skill rule, the README line, the version bumps, the case directories and the research README line. None is unclaimed.

No command line is told to run, other than the Gradle line inside the case prompt, which is the input to the model and not a command the change documents.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions the change claims, and the negative control. This is a skill change, so the added-instructions table applies.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Lead the description with the break lines, under a `Breaking changes` heading, after a short paragraph naming which code breaks | a pull request with one break that the Why slot's first sentence already states in full | a heading, a paragraph and a bullet that repeat the first sentence of Why | none beyond "A change with no break has neither the lead nor an empty heading". A single-break change still gets the lead. This is taste, not substantive. |
| A failure extended to inputs that worked before goes with the breaks, not in Scope | the pre-existing failure itself, as in `grant insert` on the first statement | the whole Scope paragraph moves to the lead, including the sentence about the first statement | "for those inputs". It already ends at the extended inputs. |
| Read the next release from the version file, milestone or branch name | a repository whose version file is not one of the four named (for example `setup.py`) | falls through to "where nothing says which release it is, the breaks lead" | the same sentence. Not a finding. |
| Where the release is unknown the breaks lead | a patch-looking repo with no version file | breaks lead | this is the rule's stated default. Not a finding. |
| The commit body keeps problem first, with the breaks as the first `User-visible:` lines | a rule-5 description | see finding 3 | conflicts with the lead rule on the same input. Substantive: finding 3. |

Not findings: "A failure that now succeeds is a fix, not a break", ended by 4367 check 4. "Whether the old behavior was right does not decide it", ended by the rule's own definition.

Negative control: `pgjdbc-4392-no-break`, with 2 Opus and 2 Haiku runs, all passing. It is a true no-break input, with no mention of a break in its prompt.

Findings:

8. **Substantive.** The negative-control arm is shown only for a no-break change aimed at a patch. The rule's other negative is a break aimed at a major release, where the lead is not owed. This is finding 5 seen from the control's side.
9. **Taste.** The sample is small: one case, two runs per model, one run for the baseline. The README says so ("most of the time and not always"), so this is acknowledged. The effect it measures is the lead, not the exact line placement of `grant insert`.

## Item 3a: level, placement, and the environment

- Analogue: which file holds each rule. The rule is in the `SKILL.md` §2 (pull request description) and the review checklist at §8. The README and both manifests are updated.
- Package layout matches the siblings. `.apm/instructions/*.md` has no mention of ordering, so nothing there goes stale.
- The registration entries that the repository's own gate checks (`marketplace.json` and root `apm.yml`) agree. The gate was not run.
- Line length: added lines in the `SKILL.md` and README are within 120 columns. The one over-long added line is a table row, as are existing ones.

None.

## Item 4: names by content, not by position

Analogue: headings, cross-references and case names.

- Case names are content names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`).
- Results are named `result.md` and `result-2.md`. Both runs have the same shape, and the README table identifies them by path. `result-2` is an ordinal, but it is a file name for a rerun, not a reference.
- The text in SKILL.md refers to "slot 3", "slot 4", "slot 1" by number, the same as the existing sections do.
- The 4367 README refers to "SKILL.md §2" and to "checks 1 to 3" by number, which is local and fine.

None.

## Item 5: the failure report

Analogue: what each rule's detection tells the reader to look at.

- Each check in the case READMEs names an observable: what leads, which literal appears, which heading is absent. The failure reads as "fails: Why first" or "fails: in Scope". That is specific.
- Detection quality: check 3 detects the `grant insert` line anywhere outside the lead, which is what the rule asks. Check 1 detects "opens, before the Why slot, with the break lines" but allows "at most a short paragraph". It does not measure how short; the two Opus results open with a 1- to 2-sentence paragraph, so that is untested at the margin.
- The checks are not reached by a checklist in the skill. The skill's §8 gains a "Breaks" line that says the same thing.

None substantive.

## Item 6: what the writer says it verified

The change states its evidence: a baseline run on the base tree (1f02…), one run each on Opus and Haiku, which lead with Why first, and runs on the new tree. So the rule can fail, and the baseline shows it.

- Gap: the "bad case" for the negative control is not shown on the base tree. 4392 has no baseline run, so nothing shows that the control would stay unchanged without the rule. Only the with-rule arm of the control ran. Request: a baseline run of 4392, to show the rule does not grow the output. The word counts (241 to 256 against the draft's 209) cannot be compared with the baseline's growth.
- The claim "Earlier Opus runs of two drafts are summarized in the case README, not stored" can't be checked.

10. **Substantive.** There is no baseline of 4392, so the no-growth claim has no comparison (§2a "What the writer says it verified": a check that the output there did not grow).

## Item 7: siblings of the change

- Places that restate the PR slot order or "Why first": `SKILL.md` line 86 (updated), line 831 checklist (updated), the Before/After example (unaffected, no break), the README (updated). The package `.apm/instructions` file does not mention order. The sibling packages (`docs-page-authoring`, `problem-report-authoring`, `qubership-repo-essentials`) only cross-reference the package.
- Set additions: no member added to a set. The version is bumped in all three places.
- Old-size sentences: "Six slots, in order" still holds. The break lead is not a new slot, and the text avoids that.
- Another path with the same symptom: the changelog entry. The rule covers PR descriptions and commit bodies. The changelog entry has its own "Breaking changes sorted first within their category" (line 543), which is consistent.
- The "ahead of slot 1" in the table cell sits next to "Slot 1 opens the body" in the commit section, which is finding 3.

None beyond finding 3.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The case READMEs quote a rule title that is not in the skill, and cite it as §2 | Substantive | `pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:5-6` | Quote the committed sentence |
| 2 | Commit says Opus ran at effort high; the README says Opus ran at the session default | Substantive | `pgjdbc-4367-breaks/README.md` ("Running it"), commit message | Make one agree with the other |
| 3 | The commit-body lead is ambiguous: "slot 1 opens the body" and "problem first" against "that body opens with its breaks"; the label (`User-visible:`) or the heading is not chosen | Substantive | `SKILL.md:86-88, 257-260, 310` | State which form the lead takes under rule 5 |
| 4 | "The trailer decides" does not say what it decides | Taste | `SKILL.md:247` | Say "the release is then a major, and the breaks need not lead" |
| 5 | The major, unknown, commit-body and squash branches have no run, and the commit does not say so | Substantive | case READMEs | One run on a major-release version file, or a sentence listing the untested branches |
| 6 | Token counts and prices are unsourced | Taste | `pgjdbc-4367-breaks/README.md` ("Cost") | Cite a source or drop the figures |
| 8 | The control arm lacks the break-at-a-major input | Substantive | case READMEs | Same as 5 |
| 10 | No baseline run of 4392, so "the output did not grow" has no comparison | Substantive | `pgjdbc-4392-no-break/` | Add a baseline run on the base tree |

Findings 5 and 8 are the same request from two sides, and finding 7 is a hunk check and not a finding.

Not checked: the suite and the repository's registration gate were not run, the case results were read but not reproduced (no model calls), the prices and token counts were not verified, and no pass was made over the prose for style alone.
