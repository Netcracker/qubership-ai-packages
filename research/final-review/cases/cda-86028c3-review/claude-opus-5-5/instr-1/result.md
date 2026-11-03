# Final review of `4f69810..HEAD` (86028c3, one commit)

There was no task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), the package README, three version fields, and the research README, and it adds two regression cases. I filled the form through the §2a analogues and did not run the drift script, because it parses program members and there are none here. Skills loaded: `apm-authoring` and `english-developer-style`.

## Item 1: comments consistent with the code and with each other
Analogue used: statements one file makes about another, and rules that conflict.

- **Case READMEs quote a rule that doesn't exist.**
  - `cases/pgjdbc-4367-breaks/README.md:7` and `cases/pgjdbc-4392-no-break/README.md:5` both quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - `SKILL.md:234` says "…unless the next release from the target branch is a major."
  - Someone searching the skill for the quoted text finds nothing. The condition also differs: "promises compatibility" and "is not a major" disagree for a 0.x project.
- **The new rule conflicts with the Scope rule.**
  - `SKILL.md:238-240` says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot".
  - `SKILL.md:488-491` (unchanged) says "whether a compatibility break is intended, keep it in the Scope slot as a question".
  - The `grant insert` case meets both conditions. `opus/result-2.md` kept it in Scope, which is the one failure the case README records.
- **The "Caller" checklist line contradicts the "Breaks" line.** `SKILL.md:845` asks for one line per outcome under "User-visible changes", breaks first. The new Breaks line at `:849-851` asks that slot 3 keep only the other outcomes.
- **"The trailer decides" reads two ways (`SKILL.md:247-248`).**
  - Reading A: the `!` or `BREAKING CHANGE:` the author writes makes the next release a major, so the breaks never lead under release-please or semantic-release.
  - Reading B: an existing release decision on the branch decides.
  - Under reading A the lead disappears exactly where the reviewer has to accept a major bump, which is the decision `:243-244` says the lead serves.
- Minor: `SKILL.md:68` ("the body is problem-first") and package `README.md:36` no longer hold for the body that §4 rule 5 makes from a lead-first description. Both are true in the default case, so this is taste.
- Counts checked: "Six slots… last three conditional" and "Five slots" are unchanged and still true. The skill-tree ids match: `4798053…` is HEAD's skill tree and `1f020ce…` is the tree at 4f69810.
- **The baseline label doesn't match its pin.** The case README (`:28`) and the commit message say the baseline ran "on `origin/main`". The pinned tree `1f020ce` is the parent commit 4f69810, which looks like part of an unmerged stack. `origin/main` is not available locally, so I couldn't confirm it, but the label and the pin disagree.

## Item 2: claimed cases covered
Analogue used: a section and a run per claim.

| Claim (commit message) | Section | Trial |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `:234-255` | `pgjdbc-4367-breaks`, 4 runs and 2 baselines |
| Release read from version file, milestone, or name | `:245-247` | version file only. The prompt says "no milestone", and no branch-name case exists |
| Breaks lead where nothing says which release it is | `:248-250` | none |
| Major release: breaks stay first in slot 3 | `:254-255` | none |
| Break definition: new failure, result shape, extended failure | `:234-241` | checks 1–3 |
| Break definition: removed option, changed default, changed error code | `:236-238` | none |
| Commit body keeps the problem first, breaks first under `User-visible:` | `:257-258`, `:86` | none. The prompt has one commit, and the outputs are descriptions only |
| Under squash "title and description", the lead stays | `:258-260` | none |
| A change with no break grows no section | `:255`, `§7` | `pgjdbc-4392-no-break`, 4 runs, all pass (spot-checked) |
| 3 of 4 runs move `grant insert`; all 4 lead | — | matches the README table and the files |

- **Commands:** `cases/pgjdbc-4367-breaks/README.md:25` describes copying the skill "out of the checkout with `git archive <rev> …`". No script or CI job runs it. `git archive` writes a tar stream to stdout, so on its own it doesn't produce the files the agent is given to read. It needs `| tar -x -C <dir>`.
- **Hunk with no claim:** the version bump 1.4.0 → 1.5.0 (`apm.yml`, the package's `apm.yml`, and `marketplace.json`) has no sentence in the message. The previous two commits each say "Version 1.x.0 to 1.y.0."

## Item 3: boundaries, partitions, and the negative control
- **Only one of the claimed modes has a trial.**
  - Both cases target one configuration: pgjdbc `master`, 42.7.x, a version file, one commit, and a description that isn't copied into a commit body.
  - The major-release partition, the unknown-release partition, the §4 rule 5 body, and the commit-body order have no trial, though the message claims all four.
  - The control (`pgjdbc-4392`) covers "no break". It does not cover "a break, but a major release", which is the other value of the setting that triggers the rule.

Added instructions: 6.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:252` "opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings" with `:259` "the lead stays" | a squash "title and description" body (§4 rule 5), which has no headings | bare break lines first, then `User-visible:` without them, so a grep for `User-visible:` misses the breaks | "under §4 rule 5 the lead opens with the `User-visible:` label" |

Not findings: `:254`, `:255`, `:257`.

## Item 3a: level, placement, and the environment
None. The rule sits in §2 next to slot 3 and has a checklist line in §8. The cases sit under `research/change-description-authoring/cases/` and are indexed in the research README. The offline gates pass: `make check-descriptions` ("27 skill descriptions are within 1020 characters"), `make test` ("PASS"), and `make verify-docs` (exit 0). No sentence is generic tutorial material; the version-file names are lookup places, not pinned versions.

## Item 4: names by content, not by position
None. Headings and case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) refer by content. "(below)" in the slot-3 table cell at `:198` points to the bold rule a few lines down, and the rule's name would be clearer. That is taste.

## Item 5: the failure report
Analogue used: detection and checklist reach.

- The new checklist line at `:849` reaches the lead and the no-break case.
- No checklist line checks the commit-body half, "breaks as the first `User-visible:` lines" (`:257`). The "Caller" line asks only that each commit carry the outcome, not that the breaks come first.
- The case READMEs state each check and what a failure looks like. That is fine.

## Item 6: what the writer says it verified
- **Present:** the baselines fail checks 1–3 in both models, the rule passes them in all four runs (3 of 4 on check 3), and the control passes in all four runs. The pinned tree ids show the runs used the committed text.
- **Missing:** the control has no growth check against a baseline, so there is no evidence the rule doesn't add text where it's noise. The README gives word counts against the draft (209 words) but no baseline run.

## Item 7: siblings of the change
- **The heading set leaves out the new heading.** `:252` introduces a `Breaking changes` heading. The heading-name set at `:301-303` ("`Why`, `What`, `User-visible changes`, `How to verify`, and `Scope` is one set that matches the slots") doesn't list it. The headings rule at `:307-309` doesn't say the lead is a reason for headings.
- **Routing surfaces are fine.** The package README has a new bullet. The marketplace and `apm.yml` descriptions are still broad enough to cover the rule.
- `research/…/README.md` gained the `cases/` row.
- `phase2_result.md`/`phase3_result.md` say "PR body = problem-first". They are dated research, and the README says the canonical rules live in the skill, so this is not a finding.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "where … promises compatibility", which the skill doesn't contain | substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:5` | Quote `SKILL.md:234` as written |
| The Scope rule keeps "whether a compatibility break is intended" in Scope; the new rule says the extended failure is not in Scope | substantive | `SKILL.md:238-240` vs `:488-491` | One clause: the break line leads and only the intent question stays in Scope |
| The "Caller" checklist line says breaks first under "User-visible changes"; the "Breaks" line says slot 3 keeps only the other outcomes | substantive | `SKILL.md:845` | Qualify it with "or ahead of the Why slot (Breaks)" |
| "The trailer decides" reads two ways; under one reading the lead never fires with release-please | substantive | `SKILL.md:247-248` | State what the trailer decides and when it applies |
| Under §4 rule 5 the leading breaks carry no label | substantive | `SKILL.md:252`, `:259` | See the table row: the clause on the label |
| Major, unknown-release, rule-5-body, and commit-body partitions have no trial | substantive | `cases/` | A case per claimed partition, or narrow the message's claims |
| The baseline is labeled `origin/main`; its tree is the parent commit 4f69810 | substantive | `cases/pgjdbc-4367-breaks/README.md:28`, commit message | Say "on 4f69810" |
| `Breaking changes` heading is missing from the heading set | substantive | `SKILL.md:301-309` | Add it to the set and to when headings are used |
| Version bump has no sentence in the message | substantive | `apm.yml`, `marketplace.json`, the package's `apm.yml` | Add "Version 1.4.0 to 1.5.0." |
| `git archive <rev> <path>` writes a tar stream, not files | substantive | `cases/pgjdbc-4367-breaks/README.md:25` | Show `\| tar -x -C <dir>` |
| No checklist line checks that breaks come first in the commit body | substantive | `SKILL.md:849` | Extend the Breaks line to the commit's `User-visible:` lines |
| The control has no baseline to show the output didn't grow | taste | `cases/pgjdbc-4392-no-break/README.md` | A baseline run with its word count |
| "the body is problem-first" doesn't hold for the rule-5 body | taste | `SKILL.md:68`, package `README.md:36` | "problem-first, after any breaks" |
| "(below)" points to the rule by position | taste | `SKILL.md:198` | Name the rule |

Not checked: I didn't re-run the model trials, couldn't confirm what `origin/main` points to (no remote locally), didn't fetch the pgjdbc pull request the case cites (no network), and didn't do a style-only pass over the prose.
