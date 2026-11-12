I've finished reading the change and am writing the report now. The task statement was not handed over, so the claimed cases come from the commit message alone. The drift script was not run, because there is no code to parse. Items below use the no-code analogues of §2a. I loaded `english-developer-style` and did not load `apm-authoring`, since the brief restricts me to the three skills.

## Item 1: Comments consistent with the code and with each other (analogue: statements about other files and about the document itself)

Substantive findings:

- **Stale rule title in both case READMEs.** The two quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - Cited at `pgjdbc-4367-breaks/README.md:6-7` (as SKILL.md §2) and `pgjdbc-4392-no-break/README.md:5`.
  - The rule as committed is "A break leads the description unless the next release from the target branch is a major" (SKILL.md:234).
  - The two wordings differ in the default. "Where … promises compatibility" leads only on a positive signal. "Unless major" leads when nothing says which release it is (SKILL.md:248-250).
  - A reader checking the cases against the skill searches for a heading that does not exist.
- **"Six slots, in order" is no longer true.** SKILL.md:193 still says "Six slots, in order" for the pull request description. The new slot-3 row and the new paragraphs put slot 3's break lines ahead of slot 1.
  - The slot-3 row carries the exception ("ahead of slot 1").
  - The sentence that says the order is fixed does not, so the two read differently.
  - Likewise, SKILL.md:221 says slots 1 and 2 are the commit body's slots 1 to 3 "written for a reader who has the diff open". It then adds "where the merge model copies the description into the commit, they are the commit body" with no mention of the new lead.
  - The order that sentence implies is Why, What, then outcomes. The new text (lines 258-261) says the body opens with its breaks.
- **Slot 1 line (SKILL.md:86-87)** now says a description "that §4 rule 5 copies into the body and that leads with its breaks puts the problem right after them". This is true, but it contradicts line 258, which says the commit body "keeps its order, problem first". The two sentences cover different cases (a commit written by hand versus a description copied by squash), but the second case is only stated at the end of a long paragraph. A reader of the slot-1 text alone gets the exception without the rule.

Taste:

- The new text at SKILL.md:490 still says a question about an intended break stays in the Scope slot as a question. The new rule says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". These are two different things (a question versus a break line), but a draft can read either as covering the other. A one-clause pointer such as "the break itself leads; only the question stays here" would settle it.

Checked and consistent:

- The `§5` reference for the `BREAKING CHANGE:`/`!` trailer resolves (table row at line 706).
- The `§7` reference for "no empty heading" resolves (line 787).
- The `§4 rule 5` references resolve (line 637).
- Versions: `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `marketplace.json` all read 1.5.0.
- The checklist "Problem" and new "Breaks" items match the new rule.
- The README bullet matches the rule.
- `skill-tree` ids in all case directories equal `git rev-parse HEAD:<skill dir>` (4798053…). The baselines equal the base commit's tree (1f020ce…). The runs were therefore made on the committed text and the previous text.

No narration of the change (`now`, `no longer`) was found in the skill text. The case READMEs and results are research records, where it is expected.

## Item 2: Claimed cases covered (analogue: sections that handle each claim; the case checks are the detection)

Claims from the commit message, and what covers each:

| Claim | Covered by |
| --- | --- |
| Description opens with the breaks | Check 1; passes in 4 of 4 rule runs. |
| Result-shape change (`getUpdateCount()` `-1`) is marked | Check 2; passes in 4 of 4. |
| Extended failure moves out of Scope | Check 3; 3 of 4 (`opus/result-2.md:33-37` keeps it in Scope). The commit message and README both say so. |
| Fix (`begin(atomic int)`) is not a break | Check 4. |
| No section for a change with no break | Control check 2; 4 of 4. |
| Break defined as new failure, different return value or shape, removed option, changed default, changed error code, failure extended | Only three of these appear in the 4367 draft. No case exercises a removed option, a changed default, or a changed error code. These are untested partitions of the definition. |
| Release read from version file, milestone, or branch name | No case varies the release. Both cases target `master` of a 42.7.x line. The "major" branch of the rule, where breaks stay in slot 3, has no run. |
| Commit body keeps problem first with breaks as first `User-visible:` lines | No case drafts a commit body, only a pull request description. |
| Squash copies description, lead stays | No case. |

Commands the change tells someone to run: none. `git archive …` in the 4367 README names `agent-packages/english-us-developer-style`, which exists. The script that runs it is not in the repository, so it cannot be repeated (the prompt and skill tree are, so the runs are traceable, but there is no runner).

Hunks with no claiming sentence: none. Every hunk is covered by the commit message. The marketplace and `apm.yml` version bumps are the release mechanics for the package.

Substantive: the major-release branch, the commit-body branch, and the non-lead definitions have no evidence. The commit message does not claim runs for them, but the skill text asserts them as rules. See the instruction table below.

## Item 3: Boundaries, partitions, and the negative control

- The control `pgjdbc-4392-no-break` exists and has two runs per model. It has no baseline run on `origin/main`. That is acceptable: a control that stays green on the base commit would only show the base also writes no lead, which the 4367 baseline already shows for the other outcome. Taste, no request.
- Partitions the rule names but no case covers:
  1. Next release is a major (breaks stay first in slot 3, no lead).
  2. Release unknown (breaks lead).
  3. The `BREAKING CHANGE:` trailer case.
  4. A change that has a break and also a `!` or release tool.
  5. Commit body and squash-copied description.

  Taste for 2, 3 and 4 (the text says "the breaks lead"). Substantive for 1: it is the one partition where the rule reverses the default, and a reader or agent over-applying the lead to a major release has no evidence either way. Request: one case with a `main` branch for a 2.0 line, or a sentence saying the major branch is untested.
- Pre-existing state: no migration or leftover state applies.
- Runs per case: two per model is a thin sample for a rule the README itself says "moves the case most of the time and not always". The README says this plainly, so it is not hidden.
- The Opus effort differs from the commit message. The commit message says "on Opus and Haiku (effort high)". The README says "Haiku ran at effort `high`; Opus at the session's default" (`pgjdbc-4367-breaks/README.md:33`, `pgjdbc-4392-no-break/README.md:22`). **Substantive**: one of the two is false, and the commit message is the one a reader sees. Request: make the commit message match the README, or state the effort Opus ran at.

### Instruction table (§2a), one row per instruction added or widened

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| "A break leads the description" (SKILL.md:234) | A pull request to a pre-release branch (`0.x`, `alpha`) where every change may break | A `Breaking changes` lead on every description, since the rule leads wherever "nothing says which release it is" and `0.x` is not a major | "or the version is below 1.0" | Taste: the skill is written for tagged release lines, the input is a kind of repository it does not address. |
| "A failure the change extends to inputs that worked before is a break" (SKILL.md:239) | A change that makes an already-rejected input fail earlier with the same error | A break line for inputs that failed before and still fail | Already stated: "to inputs that worked before" | Not a finding: the text quoted ends it. |
| "Where nothing says which release it is, the breaks lead" (SKILL.md:248) | A description for a repository with no version file, milestone, or branch naming, and a one-line break | A `Breaking changes` heading plus a short paragraph above a one-sentence Why | "a short paragraph" is already allowed to be absent? No: the text says "after at most a short paragraph", and §7 bans an empty heading, not a one-line section | Taste: the lead for a single break is a heading and one line, which costs little. |
| Break lines "under a `Breaking changes` heading where the description has headings" (SKILL.md:252) | A description without headings (the 4-paragraph prose shape at SKILL.md:301) | Prose that opens with the break, with no heading, as the text allows | Already stated: "where the description has headings" | Not a finding. |
| "The commit body keeps its order" with breaks as first `User-visible:` lines (SKILL.md:257) | A one-commit change whose break is the only outcome | A one-line `User-visible:` section holding the break, as before | Already stated by the slot-4 condition | Not a finding. |

## Item 3a: Level, placement, and the environment

- Placement matches siblings: the case directories follow the layout of the earlier research directories (README, prompt, per-model results), and the research README lists `cases/`.
- Registration entries: `apm.yml`, the package `apm.yml`, and `marketplace.json` agree. I did not run the repository's marketplace gate (`.github/workflows/marketplace.yml`) and did not check whether `apm.lock.yaml` needs a change. It does not name the package, so likely not.
- Taste: the research README says the cases "were added on 2026-10-20", a date that dates the sentence; the git log carries it.

## Item 4: Names by content, not by position

- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) name an issue and a content. Fine.
- `result-2.md` names a run by ordinal. The README's table calls the rows `opus/result-2.md`, and its text calls them "one of two Opus runs". Taste: a content name is not available for a repeat run of one input, so no request.
- Checks are numbered 1 to 6, and the README refers to "Checks 1 to 3 are the rule under test; 4 to 6 are the guard". Same reasoning: the ordinal is the record of a fixed list within one file. None.

## Item 5: The failure report (analogue: what each rule tells the reader to look at; each detection detects its rule)

- Checks 1 and 3 are phrased as observable positions in the output ("opens, before the Why slot"; "not left in Scope"). They detect the rule.
- Check 5 ("Stated once") is a property of the draft, not of the rule. It guards cost, as the README says.
- Check 4 detects an over-wide definition of "break". It is the only check for that, and it has one input. Taste.
- The control's check 2 says no `Breaking changes` heading and no sentence that nothing breaks. It detects the lead and the empty section, not the more likely failure of a short compatibility sentence in other words ("this change is backward compatible"). The README counts "no sentence about compatibility" as a pass, so the check text and the result text agree; the check is stricter than its title.

## Item 6: What the writer says it verified

- The cases carry the red run: baseline on `origin/main` fails checks 1, 2, 3 on both models, and the rule runs pass 1 and 2 in all four runs. That is the evidence the rule can fail and then pass. It is stated in the commit message and the README.
- The rule was rewritten after review (README: "reworded after review"), and the committed wording has two runs per model. Applying the rewritten rule to the cases again is what the runs are.
- The bad case where the added item is noise is the control, with two runs per model and the output sizes reported (241 to 256 words against a 209-word draft). That covers "output did not grow".
- Not stated: whether the checks were scored by a person or a script. The table is hand-filled. Minor.

## Item 7: Siblings of the change

- Places that enumerate the package: `apm.yml` (root marketplace block), `.claude-plugin/marketplace.json`, the package `apm.yml`, and the package README. All four are updated. `git grep` of the package name finds no other listing (the other hits are research prose and `.lycheeignore`).
- The research README's listing of `cases/` is added. Its prose says the synthesis "runs to about 4,700 words". That count was untouched, and the skill text, not the synthesis, changed.
- Counts in prose of the old size: the checklist and §2 still say "Six slots" (see Item 1). No sentence still says "five" for the pull request description.
- Sibling skills: `english-uk-developer-style`, `english-us-developer-style` and `english-developer-style` exist as packages. The new text uses no new style rules, so no sibling needs the change.
- Sibling paths of the same symptom: the changelog entry already marks breaking changes first (line 543, `**Breaking:**` in place), and the new pull request rule does not conflict with it. The commit-body rule is covered in the new last paragraph.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote the rule as "promises compatibility"; the skill says "unless … is a major". The defaults differ. | Substantive | `cases/pgjdbc-4367-breaks/README.md:6-7`; `cases/pgjdbc-4392-no-break/README.md:5` | Quote the committed rule title. |
| Commit message says Opus ran at "effort high"; READMEs say Opus ran at the session default. | Substantive | commit message; `pgjdbc-4367-breaks/README.md:33`; `pgjdbc-4392-no-break/README.md:22` | Make them agree. |
| "Six slots, in order" and "slots 1 and 2 are the commit body's slots 1 to 3" ignore the new lead. | Substantive | `SKILL.md:193`, `:221` | Say "in order, except that break lines may lead (below)" or equivalent. |
| Slot-1 sentence states the exception (problem after breaks) while line 258 states the rule (problem first) with no link between them. | Substantive | `SKILL.md:86-88`, `:257-261` | Make the two sentences point at each other, or state the squash case once. |
| The "next release is a major" branch has no case, and it is the one partition where the rule reverses its default. | Substantive | `cases/` | Add one case on a major-release branch, or state in the README that it is untested. |
| Definition of a break lists removed option, changed default, and changed error code, with no case for any. | Taste | `SKILL.md:235-237` | Optional: name them as untested in the case README. |
| Scope-slot sentence on "a question about an intended break" (line 490) overlaps the new "not in Scope" rule. | Taste | `SKILL.md:490` | Add "the break itself leads; only the question stays here". |
| `0.x` and pre-release lines are not addressed. | Taste | `SKILL.md:234-250` | Optional clause. |
| Control check 2 detects a heading, not a rephrased compatibility sentence. | Taste | `pgjdbc-4392-no-break/README.md:14-15` | None required. |
| Research README sentence dated "2026-10-20". | Taste | `research/change-description-authoring/README.md` | Drop the date. |

The review did not run the suite or any case, did not run the marketplace gate, did not check `apm.lock.yaml`, did not read the full 4367 and 4392 prompt files or every result line by line (it checked headings, break lines, and the generated-by line), and made no pass over the prose for style alone.
