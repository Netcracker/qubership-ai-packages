I found eight substantive findings and four taste findings, though most are small. The new rule itself is sound, and the claimed runs are real: the committed skill tree matches the case results' `skill-tree` ids, the baselines match the parent commit, and the case tables match the result files. The weak spots are statements elsewhere in SKILL.md that the new rule makes false, and conditions in the commit message that have no case.

# Final review: `4f69810..86028c3` (one commit, `feat(change-description-authoring): lead the description with breaks unless the next release is a major`)

There was no task statement, so the claimed cases come from the commit message alone. There is no previous report of this form, so there is no table of held findings.

This change has no code: it touches a skill (SKILL.md), a package README, version manifests, and a research directory of case prompts and results. I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring` (the repository's copy under `agent-packages/apm-authoring`). I did not run `comment-drift.py`: no changed file is source code it can parse (they are `.md`, `.json`, `.yml`, and plain `skill-tree` ids).

## Item 1: comments consistent with the code and with each other
**Analogue:** the statements SKILL.md makes about its own slots and sections, and the statements the case READMEs make about SKILL.md.

- **Unchanged statements the new rule makes false:**
  - **Slot 3 order:** `SKILL.md:226` ("Breaks come first…", in slot 3) and checklist `SKILL.md:845` ("one line per distinct outcome under 'User-visible changes', breaks first") still put the breaks inside slot 3. The new paragraph at :252–255 says the opposite unless the next release is a major ("Slot 3 keeps the other outcomes"). A reader who runs only the §8 checklist gets two conflicting answers from the Caller line and the new Breaks line (:849).
  - **Body shape under §4 rule 5:** `SKILL.md:310` says "Under §4 rule 5 the description is the commit body and takes the body's shape instead". The body's shape is problem first, but :259–260 now say that this body "opens with its breaks and then its problem". The sentence at :310 was not qualified, although the parallel one at :86–88 was.
- **Stale quotes in the case READMEs:** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` both quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". `git grep` finds the quoted text nowhere in the skill. This looks like a draft wording left behind.
- **Commit message vs case README on effort:** the commit message says "on Opus and Haiku (effort high)", but the case README says "Haiku ran at effort `high`; Opus at the session's default".
- **Things I checked that hold:**
  - The research README's new `cases/` row.
  - The package README bullet against the rule.
  - The `skill-tree` ids: `4798053…` equals the HEAD tree of the skill, and `1f020ce…` equals the 4f69810 tree, which is the baseline.
  - The case-result tables against the results themselves (grep of headings and of where `grant insert` sits).
  - Word counts via `wc -w`.
  - No sentence narrates the change ("now" appears only inside quoted draft facts).

## Item 2: claimed cases covered
| Claim (commit message) | Section | Evidence |
| --- | --- | --- |
| The description opens with the breaks when the next release is not a major | SKILL.md:234–255 | pgjdbc-4367-breaks: 4 rule runs pass check 1 and 2 baselines fail it |
| A result-shape change is a break | :236–237 | 4367 check 2: 4/4 pass, baselines fail |
| A failure extended to inputs that worked before is a break, not Scope | :238–240 | 4367 check 3: 3/4 pass (opus/result-2 fails), as the message says |
| Removed option, changed default, changed error code | :237–238 | no case (partitions with no evidence; see item 3) |
| Release read from the version file, milestone, or branch name | :244–247 | the prompt gives only `gradle.properties`; milestone and branch name not exercised |
| Breaks lead where nothing says which release it is | :248–250 | **no case** |
| Next release is a major → breaks stay first in slot 3 | :254–255 | **no case** |
| Commit body keeps problem first, breaks first under `User-visible:` | :257–259 | **no case**: every prompt asks only for a PR description |
| Squash copies the description → the lead stays in the body | :259–260, :86–88 | **no case**: both prompts give `merge 0 squash 3 plain 37`, so §4 rule 5 does not apply |
| A change with no break grows no section | :255 | pgjdbc-4392-no-break: 4/4 pass |

**Commands the change tells a reader to run:** `cases/pgjdbc-4367-breaks/README.md:23-24` says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`".
- Runs it: none, because no script in the repository runs this form.
- Outcome: `git archive` writes a tar stream to stdout and copies nothing out. A reader who reproduces the case from this line gets a tarball on the terminal.
- Also unrecorded: the companion `english-developer-style` copy is named only by path, with no revision or tree id.

**Hunks no sentence claims:** the version bumps 1.4.0 → 1.5.0 in `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json`. They follow the convention of the three previous commits, and `make check` passes.

## Item 3: boundaries, partitions, and the negative control
**Analogue:** the partitions are the release kinds and merge models the change claims. The negative control is the no-break case plus the table of added instructions below.

- **The control does not control the "unless" condition.** pgjdbc-4392 varies whether there is a break, not whether the next release is a major. The rule's condition has three branches: not major, major, and unknown. Only "not major" has a case. A run of 4367 with `gradle.properties` at `43.0.0` (or a milestone `43.0`) is the input where the lead must not fire. None exists, so a rule that always leads would pass every committed check.
- **The commit-body and §4 rule 5 partitions have no evidence** (see the table in item 2).
- **The control has no baseline run.** The control results are 241–256 words against a 209-word draft, but there is no `baseline/` run on 4f69810. So nothing shows that the rule did not cause the growth.
- Pre-existing state, values users pass, replaced mechanisms, and limits: not applicable; the change replaces no mechanism and sets no limit.

**Table of added instructions.** I counted 7: the break definition, reading the release, the trailer, the lead's shape, the commit-body order, the lead under rule 5, and the "Breaks" checklist line (which restates the lead's shape, so it shares that row). The amendments at :86–88 and in the Problem checklist line restate the rule-5 instruction.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "A failure the change extends… goes with the breaks, not in the Scope slot" (:238–240) | An extended failure whose intent only a maintainer can settle (Scope rule, :487–492) | Moves the break up and drops the open question Scope requires | "the question whether the break is intended stays in Scope (§2, Scope)" |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer…, the trailer decides" (:247–248) | A release-please repository on a 1.x line, with a break | Either no lead (the trailer makes the next release a major) or a lead; the text does not say which | Say what the trailer decides: "the trailer makes the next release a major, so the breaks stay in slot 3" (or the opposite) |
| "Where §4 rule 5 makes the description the commit body…, that body opens with its breaks" (:259–260) | A squash-merged repository whose readers grep `User-visible:` (the reason given at :258) | Leading break lines with no label, so the grep misses them | "…opens with its breaks, under `User-visible:`, and then its problem" |
| "Read the next release from the target branch… a break read first in a major costs a paragraph" (:244–250) | A 0.x project, where a minor release is the breaking bump by semver | Leads with breaks for a release whose users expect breaks | None in the text; the artifact does not address 0.x (taste) |

Not findings:
- "Where the next release is a major, the breaks stay first in slot 3" ends the lead for a major.
- "A change with no break has neither the lead nor an empty heading" ends it for the control.
- "a failure that now succeeds is a fix, not a break" ends it for check 4.

## Item 3a: level, placement, and the environment
**Analogue:** the file each rule lives in, whether the layout matches its siblings, and the repository's own gates.

- **Placement:** the rule sits in §2 under the pull request description, next to slot 3, which it modifies. The commit-body consequence is placed at :86–88 and :257–260. The case layout (`prompt.md`, `README.md`, `<model>/result*.md`, `<model>/skill-tree`, `baseline/`) matches `research/blackbox-test-design/cases` and `research/problem-report-authoring`. Results and prompts match the markdownlint exclusion in `.github/super-linter.env:14`.
- **Gates run offline:** `make check-descriptions` printed "ok: all 27 skill descriptions are within 1020 characters". `make check` exited 0 (versions aligned). `tests/marketplace_roundtrip.sh` printed PASS.
- **Tutorial-generic text:** none. The rationale sentence at :243–244 is specific to this rule's release-branch decision.

## Item 4: names by content, not by position
- **`SKILL.md:198`:** "ahead of slot 1 unless the next release is a major (below)" points by position to a paragraph 36 lines down that has a bold lead it could be named by ("the break-lead rule"). Taste: the slot numbers themselves are the skill's established naming scheme.
- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the check names (Lead, Result shape, …) name by content.

## Item 5: the failure report
**Analogue:** whether the §8 checklist reaches the rule, and whether its detection detects the rule.

- **Reaches it:** yes, the new "Breaks" line at :849–852.
- **Detects a weaker property:** the line checks only the *placement* of the breaks: "does the description open with the break lines, and does slot 3 keep only the other outcomes". It does not check the *classification*, which is the defect the commit reports. That classification is that a result-shape change and a failure extended to inputs that worked before are breaks, and that neither sits in Scope.
  - opus/result-2.md passes every question of the checklist line while leaving `grant insert` in Scope.
  - Case checks 2 and 3 detect it, but a drafting agent never sees them.

## Item 6: what the writer says it verified
- **Exemplar and bad case:** both are named. The baselines on the parent tree fail checks 1–3, and the rule runs pass, except one check-3 failure that the commit states.
- **Rewritten rule re-run:** yes. The README says the committed wording was "reworded after review", and the `skill-tree` ids confirm the rule runs used exactly the committed tree.
- **Output growth on the "noise" input:** not established, because the control has no baseline run (item 3).

## Item 7: siblings of the change
- **The Scope paragraph** `SKILL.md:487–492` ("whether a compatibility break is intended, keep it in the Scope slot as a question") is the sibling the new "not in the Scope slot" clause meets. It is filed in the table above.
- **The changelog entry** (part 5, "breaking or not", and the `**Breaking:**` marking at :543–545) uses the same notion of a break, but does not point to the new definition. A changelog author who classifies breaks there gets no help with result-shape or extended-failure cases. Taste: the changelog takes its outcomes from slot 4, where the breaks are already classified.
- **Index entries:** `marketplace.json` and the root `apm.yml` descriptions are unchanged. They describe the package generically ("which reader each part serves, what goes where"), so no scope widening is missed. No sentence counts a set that this change grows (the "Five slots" and "Six slots" counts still hold).

## Findings
| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Slot-3 "Breaks come first" and checklist "breaks first" contradict the new lead outside a major | Substantive | SKILL.md:226, :845 | Add "where the next release is a major (below)", or the lead's condition, to both |
| "takes the body's shape instead" contradicts the rule-5 body opening with its breaks | Substantive | SKILL.md:310 | Qualify it the way :86–88 is qualified |
| Case READMEs quote a rule wording that SKILL.md does not contain | Substantive | cases/pgjdbc-4367-breaks/README.md:7–8; cases/pgjdbc-4392-no-break/README.md:6–7 | Quote the committed heading |
| No case where the next release is a major, which is the control for "unless"; no case for an unknown release | Substantive | research/change-description-authoring/cases | Add a 4367 variant with a major version file (and one with no version), or narrow the commit message's claims |
| Commit-body order and the rule-5 lead are claimed, but no prompt exercises them | Substantive | SKILL.md:257–260; commit message ¶3 | A case whose merge model is squash with "title and description", and one asking for the commit message; or drop the claim from the message |
| "not in the Scope slot" conflicts with the Scope rule for a break whose intent is open | Substantive | SKILL.md:238–240 vs :487–492 | The clause in the table above |
| "the trailer decides" does not say what it decides | Substantive | SKILL.md:247–248 | State whether the trailer makes the release a major (breaks stay in slot 3) |
| Rule-5 lead lines carry no `User-visible:` label, so the grep reason given one sentence earlier fails there | Substantive | SKILL.md:257–260 | "…opens with its breaks, under `User-visible:`, and then its problem" |
| §8 "Breaks" line checks placement, not classification (result shape, extended failure) | Substantive | SKILL.md:849–852 | Add: "is every changed result shape and every failure extended to inputs that worked before among the breaks, and none in Scope?" |
| Control case has no baseline run, so its growth cannot be attributed | Substantive | cases/pgjdbc-4392-no-break | Add `opus/baseline` and `haiku/baseline` runs on 4f69810 |
| `git archive <rev> <path>` as written copies nothing out; the companion style skill's revision is not recorded | Substantive | cases/pgjdbc-4367-breaks/README.md:23–26 | The full form (`… \| tar -x -C <dir>`) or a script, plus the style skill's tree id |
| Commit message says both models ran at effort high; the README says Opus ran at the session default | Substantive | commit message ¶3 vs README:26–27 | Make the message match the README |
| Version bumps not claimed by any sentence | Taste | apm.yml:168; agent-packages/change-description-authoring/apm.yml:2; .claude-plugin/marketplace.json:291 | One clause in the message, or leave it as the repository's convention |
| "(below)" points by position | Taste | SKILL.md:198 | Name the rule by its bold lead |
| 0.x projects not addressed by "unless … a major" | Taste | SKILL.md:243–250 | Optionally a clause for pre-1.0 versioning |
| Changelog break marking does not point to the new definition | Taste | SKILL.md:506, :543 | Optionally "(a break as defined in §2, pull request description)" |

I did not re-run the model trials, did not run `make test` beyond the marketplace round trip, did not fetch the cited pgjdbc pull request or comment (no network), and did not do a style-only pass over the prose.
