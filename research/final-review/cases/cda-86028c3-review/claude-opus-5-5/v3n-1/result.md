# Final review: `4f69810..86028c3` (one commit, "lead the description with breaks unless the next release is a major")

There was no separate task statement, so the claimed cases come from the commit message alone. No previous report of this form exists for this change. This change has no code: it is a skill (`change-description-authoring` SKILL.md), its package README and manifest versions, and a research directory of regression cases. I filled the form through the §2a analogues, loading `apm-authoring` and `english-developer-style`. I ran `comment-drift.py 4f69810 HEAD`, and it printed nothing because no changed file is in a language it parses.

## 1. Comments consistent with the code and with each other
Analogue: what each changed file says about other files and about the skill.

- **Both case READMEs quote a rule the skill does not contain.** `pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` cite "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". A reader of the case looks for the quoted sentence and does not find it. The phrase "promises compatibility" comes from an earlier draft, and the committed condition is a different one.
- **The checklist contradicts the new rule.** The Caller line (SKILL.md:844-846) asks for every outcome "under 'User-visible changes', breaks first". The new Breaks line (:849-852) and :252-254 say that, in a release that is not a major, the breaks move out of slot 3. A checker that applies :845 to a description that follows the rule reports the breaks as missing from User-visible changes.
- **There are two readings of "not in the Scope slot".** :238-240 puts an extended failure "with the breaks, not in the Scope slot". :488-492 keeps "whether a compatibility break is intended" in Scope as a question for the maintainer. 4367's `grant insert` is exactly that kind of question, since the draft says why `INSERT` is not narrowed. `opus/result-2.md` resolved the conflict by keeping it in Scope, which fails check 3, so the conflict shows up in the runs.
- **Breaks drop out of the `User-visible:` label under §4 rule 5.** :257-258 keeps breaks under `User-visible:` in a commit body because "the label is what R4 and R5 search for". Under rule 5, :259-260 says that body "opens with its breaks", but it names no label for them. :857 also forbids headings there. So in exactly the case where the description becomes the permanent commit, the breaks leave the label the paragraph says readers grep for.
- (taste) The commit message says "on Opus and Haiku (effort high)", but `pgjdbc-4367-breaks/README.md` says "Opus at the session's default". The message reads as if both ran at high effort.
- (taste) §4 "Default when detection fails" (:677) asks for a description that "can stand as a commit body". The exception at :86-87 covers only rule 5, so it is unclear whether a description in that default case leads with its breaks.

Statements I checked that hold:
- The baseline claim that breaks came first only inside slot 3, with no definition of a break, matches base :197.
- The word counts in the 4367 results table match `wc -w`.
- Every `skill-tree` file matches the tree it claims: 4798053 = `HEAD:<skill>` and 1f020ce = the base commit's tree.
- The Haiku "Generated with Claude Code" lines are present: three in 4367 and two in 4392.
- The commit message's grading matches the results: all four with-rule runs lead with the breaks and mark the result shape, `opus/result-2.md` leaves `grant insert` in Scope, and the control runs have no section.
- The package README, the research README index line, and the marketplace/apm.yml descriptions agree with the rule.
- I could not fetch the pgjdbc#4367 comment that the commit and README cite as the exemplar (no network).

## 2. Claimed cases covered
Analogue: the section that handles each claim, plus a trial or a detection.

| Claim (commit message) | Section | Trial |
| --- | --- | --- |
| Description opens with breaks unless the next release is a major | :234, :252-255 | 4367, four runs |
| Read from version file, milestone, or branch name | :244-246 | Version file only. In the prompt it equals the last tag (`42.7.14` / `REL42.7.14`). |
| Breaks lead where the release is unknown | :248-250 | none |
| Break definition: new failure, return or result shape, removed option, default, error code, extended failure | :234-241 | Result shape and extended failure (4367). The others: none. |
| Commit body keeps problem first, breaks first under `User-visible:` | :257-258 | none (the prompts ask only for a PR description) |
| Squash under rule 5 keeps the lead | :258-260, :86-87 | none |
| No break grows no section | :255, §7 | 4392, four runs |

- **Command lines:** `pgjdbc-4367-breaks/README.md` "Running it" gives `git archive <rev> agent-packages/…/change-description-authoring` as the way to copy the skill out. Nothing in the repository runs that form. As written it writes a tar stream to stdout and copies nothing; I checked with `git archive HEAD … | tar -t`. `agent-packages/AGENTS.md:43` documents the form that works: `… | tar -x -C <dir> --strip-components=<depth>`.
- **Unclaimed hunks:** the version bump 1.4.0 → 1.5.0 in `.claude-plugin/marketplace.json`, `apm.yml`, and the package `apm.yml`. No sentence of the commit message claims it. `d79c43d` and `51b35c9` state their bumps ("Version 1.2.0 to 1.3.0"), while `4f69810` did not, so the precedent is mixed.

## 3. Boundaries, partitions, and the negative control
Analogue: the partitions the change claims, and the control arm. For a skill, the negative control is the table of added instructions.

- **The partition the subject line names has no trial.** Both cases target `42.7.14`, so no run checks the "unless the next release is a major" branch: a change with breaks whose target says a major is next. 4392 is a control for "no break", not for "major". No run covers an unknown release, a milestone or a branch name as the source, a release-tool trailer, the commit-body ordering, or the rule-5 squash body. That is six claimed partitions with no evidence.
- The changed version and the cases do not depend on state an earlier version left behind. No limits or replaced mechanisms are involved.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "the trailer decides" | release-please repo, a 1.x patch line; this change's own `!` forces the major | Why first, breaks in slot 3, although merging means shipping a major | "where a breaking commit already landed since the last release" |

Not findings: `:235`, `:255`, `:787`.

## 3a. Level, placement, and the environment
Analogue: which file each rule lives in, whether the layout matches its siblings, and the repository's own gate.

- The rule sits in §2, beside slot 3 of the pull request description. The cases sit under `research/<package>/cases/`, as `agent-packages/AGENTS.md` asks. This is the package's first set of cases.
- `scripts/check-skill-descriptions.py` passed: "all 27 skill descriptions are within 1020 characters". I did not run `make check` (`apm pack --check-versions`) because it needs uvx and the network. The three versions agree by inspection.
- (taste) The result directories are named `opus/` and `haiku/`. Every sibling case uses full model IDs (`claude-opus-5-5`, `claude-haiku-4-5`), and the short names do not say which Haiku produced a result.
- The new rule contains nothing a generic tutorial on the topic would say.

## 4. Names by content, not by position
- (taste) SKILL.md:198, the slot-3 row: "ahead of slot 1 unless the next release is a major (below)". "(below)" is a positional pointer. The paragraph has a bold lead it could be named by ("A break leads the description…").
- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the check names are by content. "Slot n" and "§4 rule 5" are the skill's existing numbering.

## 5. The failure report
Analogue: what the checklist tells the reader to look at, and whether that detects the rule.

- The checklist reaches the rule (:849). **But the detection is weaker than the rule.** It asks only whether the description opens with "the break lines". It never asks whether every outcome that fits the definition at :234-241 is among them. The 4367 baseline failure was exactly that kind: the result-shape change unmarked and the extended failure left in Scope. A description that leads with the two lines the author had already marked as breaks passes :849 and still fails checks 2 and 3 of the case.

## 6. What the writer says it verified
- The evidence is present: a bad case (the 4367 baselines fail checks 1-3), a passing case (four with-rule runs), and a control where the rule is noise (4392). The control is checked for no added section and no compatibility sentence.
- **The baseline cells ran once each.** `agent-packages/AGENTS.md:60` says to run each cell the conclusion rests on at least twice before calling a change a fix. The claim "without the rule both models put Why first" rests on one run per model.
- 4392 has no baseline run, so its 241-256 words are compared only with the 209-word draft. Checks 1 and 2 still catch the growth this rule could cause.

## 7. Siblings of the change
Analogue: the places that list or route to the skill.

- These agree with the change: the marketplace entry, the root `apm.yml`, the package `apm.yml`, the package README bullet, and the `research/change-description-authoring/README.md` index line and paragraph. Changelog §3 already sorts breaks first within a category, which is consistent.
- `references/merge-model.md:63` lists the body as "problem, symptom, approach". That is a content list in a house-rule template, not an order, so it is not a finding.
- The checklist sibling at :845 is filed under item 1.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule sentence the skill does not contain | substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote :234 as committed |
| Caller checklist line still puts breaks first under User-visible changes | substantive | SKILL.md:845 | Condition it on a major, or point to the Breaks line |
| "not in the Scope slot" conflicts with the Scope rule for an intended-break question | substantive | SKILL.md:238-240 vs :488-492 | Say the break line leads and only the open question stays in Scope |
| Under rule 5 the leading breaks leave the `User-visible:` label that :258 says readers grep | substantive | SKILL.md:257-260 | Name the label (or the lack of one) for the leading breaks in a rule-5 body |
| Claimed partitions with no trial: major target, unknown release, milestone or branch source, commit body, rule-5 body | substantive | `research/…/cases/` | At least one run of 4367 with a target that says a major is next |
| Trailer rule removes the lead where the change's own `!` makes the major | substantive | SKILL.md:247 (§3 table) | The clause in the table row |
| Checklist detection does not check the break definition | substantive | SKILL.md:849-852 | Ask whether every result-shape change or extended failure is among the leading lines |
| Version bump hunks claimed by no sentence | substantive | `apm.yml`, `.claude-plugin/marketplace.json`, package `apm.yml` | One sentence in the commit message |
| Run recipe `git archive <rev> <path>` extracts nothing | substantive | `cases/pgjdbc-4367-breaks/README.md` "Running it" | Use the `\| tar -x -C … --strip-components` form from AGENTS.md:43 |
| Baselines ran once per model | substantive | `cases/pgjdbc-4367-breaks/*/baseline/` | A second baseline run per model, or say it is single-run |
| "(effort high)" reads as applying to Opus too | taste | commit message | "Haiku at effort high" |
| Default-when-detection-fails description: lead or problem first | taste | SKILL.md:86, :677 | Name it beside rule 5 |
| Model directories `opus/`, `haiku/` vs full IDs in sibling cases | taste | `cases/*/` | Full model IDs |
| "(below)" in the slot-3 row | taste | SKILL.md:198 | Name the paragraph |

Not checked:
- I ran no models.
- I did not run `make check` (it needs the network).
- I could not open the pgjdbc pull requests and comment the change cites as its exemplar.
- I did not do a style-only pass over the prose.
