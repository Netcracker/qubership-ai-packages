# Final review of `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

**Inputs.** I had no task statement. Per §1 of the skill, the claimed cases below come from the commit message alone. The change has no code: it edits a skill, a package README, three version fields, and the research index, and adds two regression cases. So the form is filled through the §2a analogues for a skill. Skills loaded: `final-review`, `english-developer-style`, and `test-authoring` (not cited, since there are no tests). `apm-authoring` was not loaded, because I was told not to load copies other than those three, so its rules are not cited. The drift script `comment-drift.py 4f69810 HEAD` ran and printed nothing, as expected for Markdown and YAML. No previous report exists.

## Item 1: comments consistent with the code and with each other

Analogue: the statements one changed file makes about another file and about the skill itself.

- **Scope rule contradicts the new break rule.**
  - `SKILL.md:238-239` says a failure the change extends to new inputs "goes with the breaks, not in the Scope slot".
  - `SKILL.md:488-491`, the table at `:200`, and the checklist "Discussion" item at `:869` all say: "as with whether a compatibility break is intended, keep it in the Scope slot as a question".
  - The test case's own input hits this conflict: the `grant insert` paragraph is a break whose intent a maintainer must settle. In one of the two Opus runs (`opus/result-2.md`) it stayed in Scope.
  - Substantive.
- **Under §4 rule 5 the breaks lose the `User-visible:` label that `:258` gives as their reason.**
  - `:257-258`: the commit body keeps breaks as the first `User-visible:` lines, because "the label is what R4 and R5 search for".
  - `:258-260` and `:86-87`: under §4 rule 5 the body "opens with its breaks and then its problem". `:253-254` says slot 3 keeps only the other outcomes. The heading checklist item says a rule-5 body has no headings.
  - Result: a rule-5 body has unlabelled break lines at the top, and its `User-visible:` paragraph lacks them. A `grep User-visible:` finds no break.
  - `:206-208` ("slot 3 is written there as `User-visible:` … lines") now says something different about the same fact.
  - Substantive.
- **Two "first" statements about the reviewer now disagree.**
  - `:204`: "the reviewer's first question is why that version should change".
  - `:243`: "the reviewer's first decision is whether the change may ship in it at all".
  - Substantive, minor.
- **Both case READMEs quote a rule title that no longer exists.**
  - `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote "A break leads the description where the next release from the target branch promises compatibility".
  - `SKILL.md:234` says "A break leads the description unless the next release from the target branch is a major".
  - Substantive.
- **The baseline is described as `origin/main`, but it ran on the parent commit.**
  - `cases/pgjdbc-4367-breaks/README.md` ("`<model>/baseline/` is the same on `origin/main`") and the commit message ("one each on origin/main") both say so.
  - The baseline `skill-tree` file holds `1f020ce`, which is the skill tree of `4f69810`, the parent commit.
  - `4f69810` sits four unpushed commits above `8c8eb00`, the latest merged commit, whose skill tree is `2670ea8`.
  - This clone has no remote refs, so I can't prove what `origin/main` was. On the evidence it was `8c8eb00`, not the tree that ran.
  - Substantive.
- **Checked and consistent:** the `skill-tree` of every result run equals the skill tree at `HEAD` (`4798053…`), so the results are of the committed text. The package README bullet matches the rule. The research README index line and paragraph match `cases/`. The results table matches the commit message's "three of four" and "one Opus run left it there". `§5` and `§7` exist and say what the new text cites them for.

## Item 2: claimed cases covered

Analogue: each situation the commit message claims, against the section that handles it and the case that tests it.

| Claimed case (commit message) | Section | Detection / case |
| --- | --- | --- |
| Description leads with breaks when the next release is not a major | `:234`, `:252-255` | `pgjdbc-4367-breaks` check 1; checklist `:849` |
| Release read from version file, milestone, or branch name | `:243-246` | 4367 (version file only); milestone and branch name not exercised |
| Breaks lead when nothing says which release it is | `:248-250` | **none** |
| Definition of a break: new failure, return value or result shape, removed option, changed default or error code | `:234-238` | 4367 checks 2 and 4 cover result shape and fix-not-break; option, default, and error code not exercised |
| A failure extended to inputs that worked before is a break | `:238-240` | 4367 check 3 (3 of 4 pass) |
| Commit body keeps the problem first, breaks as first `User-visible:` lines | `:257-258` | **none**: every case writes a PR description only |
| Under squash "title and description" the lead stays | `:258-260`, `:86-87` | **none**: both prompts say squash with `* subject` bullets and one commit, so rule 5 never fires |
| No break → no section | `:255` | `pgjdbc-4392-no-break` checks 1 and 2 |
| Next release is a major → breaks stay in slot 3 | `:254-255` | **none** |

The commit message does not tell the reader to run any command. The case READMEs describe a manual run (`git archive <rev> …`) that no script automates. `research/test-authoring/cases` has `run-case.sh` for the same purpose.

Unclaimed hunks: the version bump 1.4.0 → 1.5.0 appears in `.claude-plugin/marketplace.json`, `apm.yml`, and the package's `apm.yml`, and no sentence of the message claims it. The previous commits of this package state it (`d79c43d`: "Version 1.2.0 to 1.3.0."). Substantive, trivial: add one sentence.

## Item 3: boundaries, partitions, and the negative control

Analogue: the modes and situations the change claims; the no-break control; the table of added instructions.

Evidence covers one partition of each axis:
- **Target release:** only "not a major, read from `gradle.properties`". "Major" and "unknown" have no run.
- **Merge model:** only "description stays on the platform". The rule-5 body that opens with breaks and the commit body have no run.
- **Template:** only "no template".

The negative control `pgjdbc-4392-no-break` is present and passes. It has no baseline run, though (see item 6). The "major" partition is the control for the "unless" clause, and nothing exercises it. Substantive: the request is one case per unexercised claimed partition, at least "major" and "rule 5".

Pre-existing state: does not apply. The skill is read fresh each time, and the version bump passes `make check`.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247-248` "the trailer decides, and it is written" | release-please repo; contributor's unplanned break in a minor | `BREAKING CHANGE:` trailer forcing a major; breaks stay after Why | "where the maintainers planned the major (milestone, release PR); otherwise the breaks lead" |
| `:252-253` "under a `Breaking changes` heading" | repo template with its own breaking-change section or checkbox | an extra `Breaking changes` heading above the template's, with breaks stated twice | "where the template has a place for breaks, fill that place and put it first" |

Not findings: `:254` "Where the next release is a major"; `:255` "neither the lead nor an empty heading"; `:240` "a failure that now succeeds is a fix"; `:248` "Where nothing says which release"; `:849` (restates `:252`); `:831` (restates `:86`).

## Item 3a: level, placement, and the environment

- The rule lives in §2 "Pull request description" beside slot 3. It has a checklist item in §8 and a bullet in the package README, which is where the siblings put theirs.
- The version is consistent in all three files. `make check` (apm pack `--check-versions --check-clean --dry-run`) exited 0 offline. `make check-descriptions` printed "ok: all 27 skill descriptions are within 1020 characters".
- The case layout differs from the siblings: the directories are named `opus/` and `haiku/`, where `research/test-authoring/cases` and `research/problem-report-authoring/cases` use model IDs (`claude-opus-5-5`), and there is no runner script. The README explains its own layout. Taste.
- No sentence of the new text is generic tutorial content.

## Item 4: names by content, not by position

`:252` "slot 3's break lines", `:254` "first in slot 3", and `:86` "Slot 1" refer by slot number. That is the skill's established convention, and every slot is defined by name in its table, so this is not a finding. The case checks are numbered (1)–(6), but each has a bold content name. The results table also cites them by number, which is acceptable because each column header carries the name. None.

## Item 5: the failure report

Analogue: does each rule have a detection the checklist reaches, and does it detect the rule?

- The new checklist item `:849-852` reaches the lead rule and the no-empty-heading rule.
- It does not reach the commit-body half (`:257-260`: breaks as the first `User-visible:` lines, and the rule-5 body opening with breaks then problem). The "Problem" item `:831` covers the second only partly, and nothing checks the first.
- The "extended failure goes with the breaks, not Scope" sentence (`:238-240`) has no checklist line. The case README records that this sentence moves the case "most of the time and not always". The checklist's "Discussion" item points the other way (item 1).
- Substantive.

## Item 6: what the writer says it verified

- **Bad case fails:** the Opus and Haiku baselines fail checks 1–3.
- **Exemplar passes:** four runs with the rule pass checks 1–2; three of four pass check 3.
- **Control:** four no-break runs pass. All of this is named in the change.
- **Missing:** a check that the output did not grow on the noise input. The control's word counts (241, 251, 249, 256) are compared only to the author's draft (209), not to a baseline run of the same prompt. "Did not grow" is therefore unestablished. Request: one baseline run per model on `pgjdbc-4392-no-break`.
- The rule was reworded after the two earlier Opus drafts, and the committed wording was re-run (the `skill-tree` matches `HEAD`). Good.

## Item 7: siblings of the change

- **Places that route to or enumerate the skill:** `marketplace.json`, root `apm.yml`, package `apm.yml`, and the package README are all updated. The research README index is updated.
- **Other skills that prescribe PR description order:** in `agent-packages/english-{us,uk}-developer-style`, the description section (`:492-507`) delegates to `change-description-authoring`, so it does not apply.
- **`.claude/skills/english-developer-style/SKILL.md:179-181`** still says "Three short sections, in order: **Why** … Lead with the motivation". It is an installed copy pinned by `apm.lock.yaml` (`english-us-developer-style` 2.1.0), not package source, so this change cannot fix it. It will contradict the new rule for agents working in this repository until the lock is refreshed. Taste: name it as follow-up.
- **Changelog §2/§3 (`:543-544`)** already puts breaks first. Consistent.
- **No sentence counts a set that grew:** "Six slots" and "Five slots" are unchanged, and correctly so.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| A failure extended to new inputs is told to leave Scope; Scope rule and checklist say an unsettled break stays in Scope as a question | Substantive | `SKILL.md:238-240` vs `:488-491`, `:200`, `:869` | Say the break line leads and the intent question stays in Scope, pointing to it |
| Under §4 rule 5 the leading breaks carry no `User-visible:` label, though `:258` says the label is what R4/R5 grep | Substantive | `SKILL.md:257-260`, `:86-87`, `:206-208` | Keep the label on the leading lines in a rule-5 body, or keep breaks inside the `User-visible:` paragraph there |
| `:247-248` makes the `BREAKING CHANGE:` trailer decide the release is a major, so the lead never fires in release-please repos | Substantive | `SKILL.md:247-248` | Clause from the instruction table |
| `Breaking changes` heading conflicts with a template that has its own breaking-change section | Substantive | `SKILL.md:252-253`, `:301` | Clause from the instruction table |
| "Reviewer's first question is why" vs. "reviewer's first decision is whether it may ship" | Substantive | `SKILL.md:204`, `:243` | Qualify `:204` ("after any breaks") |
| Both case READMEs quote the rule by a superseded title | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote "unless the next release from the target branch is a major" |
| Baseline called `origin/main`, but its `skill-tree` is the parent `4f69810` | Substantive | `cases/pgjdbc-4367-breaks/README.md` (Running it), commit message | Name the commit the baseline ran on |
| Claimed partitions with no run: next release is a major, release unknown, rule-5 body, commit body | Substantive | `cases/` | One case per claimed partition, at least "major" and "rule 5" |
| Checklist does not reach the commit-body half of the rule or the extended-failure sentence | Substantive | `SKILL.md:849-852` | Extend the "Breaks" item to the commit body and to extended failures |
| No baseline on the no-break control, so "did not grow" is unestablished | Substantive | `cases/pgjdbc-4392-no-break/README.md` | One baseline run per model, with word counts |
| Version bump 1.4.0 → 1.5.0 unclaimed in the commit message | Substantive (trivial) | `apm.yml`, `marketplace.json`, package `apm.yml` | Add "Version 1.4.0 to 1.5.0." |
| A removed internal or unsupported API counts as a break by the definition | Taste | `SKILL.md:234-238` | Limit the definition to public API and documented behavior |
| Case directories `opus/`, `haiku/` and no runner script, unlike the sibling cases | Taste | `research/change-description-authoring/cases/` | Use model-id directory names |
| Installed `.claude/skills/english-developer-style` still says Why first | Taste | `.claude/skills/english-developer-style/SKILL.md:179-181` | Name as follow-up (lock refresh) |
| "on Opus and Haiku (effort high)" reads as both at high; the README says Opus ran at the default | Taste | commit message | "Haiku at effort high, Opus at the default" |

This review did not re-run any regression case or drafting model, did not check the cited pgjdbc pull request or comment (no network), and did not do a style pass over the prose beyond sentences that read wrongly.
