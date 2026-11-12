# Final review: `4f69810..86028c3` (one commit, change-description-authoring 1.5.0)

The change has no code: it edits a skill and adds research cases. I filled the form through the §2a analogues and loaded `apm-authoring` and `english-developer-style`. The drift script found no members to report, which is expected here, since there is no source code to parse. There was no task statement, so I took the claimed cases from the commit message alone, plus the two case READMEs.

I found six substantive problems. In brief:
- The case READMEs quote a rule sentence that is not in the skill.
- The review checklist still contradicts the new lead rule.
- The squash path and the Scope rule each leave the agent two readings.
- The checklist's Breaks item checks only the lead, not whether every break was classified.
- Several modes the commit message claims have no run behind them.

## Item 1: comments consistent with the code and with each other
Analogue: statements one changed file makes about another, and about the skill's own sections.

- **Stale rule quote in both case READMEs.** `pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` say the cases test the rule *"A break leads the description where the next release from the target branch promises compatibility"*. SKILL.md:234 actually says *"A break leads the description unless the next release from the target branch is a major."* That wording is not in the skill.
  - **What goes wrong:** a reader who greps for the quoted sentence finds nothing. The quoted condition also differs from the shipped one: "promises compatibility" versus "is not a major", and the quote has no "unknown → lead" branch.
  - **Request:** quote the committed sentence.
- **The checklist's "Caller" item contradicts the new rule.** SKILL.md:844-846 still asks for "one line per distinct outcome under 'User-visible changes', breaks first". In the default case (not a major, or unknown), :252-254 moves the breaks out of slot 3, and the new "Breaks" item at :849-851 checks that "slot 3 keep[s] only the other outcomes".
  - **What goes wrong:** an agent running the checklist on a correct lead fails the Caller item. It then restores the breaks under "User-visible changes", which duplicates them (case check 5, "Stated once").
  - **Request:** make the Caller item read "breaks first, or in the lead (Breaks below)".
- **The squash path (§4 rule 5) has two readings.** When the description becomes the commit body:
  - :211 says slot 3 is written there as `User-visible:` lines.
  - :257-258 justifies keeping breaks under that label because "the label is what R4 and R5 search for".
  - :259-260 says the body "opens with its breaks and then its problem".

  **What goes wrong:** nothing says whether the leading breaks carry the `User-visible:` label. One reading gives two `User-visible:` paragraphs. The other gives unlabeled breaks that the R4/R5 search in :258 misses.

  **Request:** one clause stating the label on the lead in a body that rule 5 copies.
- **The extended-failure rule conflicts with the Scope rule.** :238-240 says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". :489-492 keeps "whether a compatibility break is intended" in Scope as a question.
  - **What goes wrong:** for the `grant insert` input, whose intent the draft leaves to the maintainer, the agent can read either rule as governing. `opus/result-2.md:35` left that break in Scope, and the case README attributes it to the draft's "known limitation" framing.
  - **Request:** a clause saying the break line leads even where the question of its intent stays in Scope.

The other cross-references hold:
- `§4 rule 5` exists (merge-model rule 5).
- `§5` is the trailer table with the `BREAKING CHANGE:` row at :706.
- `§7` is the "No section for an absent concern" line at :787.
- The package README bullet matches :234-260.
- The six `skill-tree` files match `git rev-parse` of the skill directory at HEAD (`4798053…`) and at HEAD~1 (`1f020ce…`) for the baselines.
- I spot-checked the results table in the breaks case README against the four rule runs and `opus/baseline`. Lead, `grant insert` placement, and headings all match.

## Item 2: claimed cases covered
Analogue: claimed situations against the section that handles them and the case that exercises them. The claims come from the commit message only, because there was no task statement.

| Claimed case | Section | Evidence |
| --- | --- | --- |
| Breaks lead when the next release is not a major (patch, read from the version file) | :243-250, :252-255 | `pgjdbc-4367-breaks` check 1; four runs pass, both baselines fail |
| A result-shape change is a break | :235-237 | check 2 |
| A failure extended to inputs that worked before is a break | :238-240 | check 3; three of four runs pass |
| A fix is not a break | :240-241 | check 4 |
| No break means no lead and no section | :255, §7 | `pgjdbc-4392-no-break` checks 1-2, four runs |
| Next release is a major: breaks stay in slot 3 | :254-255 | **none** |
| Unknown release: breaks lead | :248-250 | **none** (the prompts state `gradle.properties`) |
| Release read from a milestone or a branch name | :245-246 | **none** |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | :257-258 | **none** (both prompts ask for a description only) |
| Squash copies the description and the lead stays | :258-260 | **none** (the case's merge model is `plain 37 squash 3`, so rule 5 does not apply) |
| Other break kinds: removed option, changed default, changed error code | :237-238 | none; partitions, see item 3 |

Commands the change tells someone to run: the case README's `git archive <rev> agent-packages/change-description-authoring/.apm/skills/change-description-authoring`. I ran it at HEAD and it lists SKILL.md and `references/merge-model.md` as promised. No CI job runs it, and its outcome depends only on the path existing at `<rev>`.

The version bump to 1.5.0 (three files) is not mentioned in the commit message. It is still claimed with the change: the earlier commit `4f69810` bumped the same way, and `make check` enforces that the three versions agree. Nothing is unclaimed.

## Item 3: boundaries, partitions, and the negative control
- **Several claimed modes have no evidence.** The commit message claims all of these, and the item 2 table shows no run for any of them:
  - the major branch, which is the exception that keeps breaks in slot 3;
  - the unknown-release branch;
  - the commit-body order;
  - the squash (rule 5) body.

  This form counts that as a substantive finding.

  **Request:** for each claim, either a case (the same draft with `gradle.properties` at `43.0.0-SNAPSHOT`, the same draft with the version facts removed, a commit-message prompt, and a prompt whose classifier shows squash with "title and description") or narrower claims in the commit message.

The negative control `pgjdbc-4392-no-break` is present and passes.

Added instructions: 5, no rows.

Not findings: `:241`, `:788`.

## Item 3a: level, placement, and the environment
Analogue: file placement, layout, and registration. The rule sits in the PR-description section of the skill, next to slot 3, which is the right place. The cases sit under `research/change-description-authoring/cases/` and the research README indexes them. Registration is consistent:
- `make check` (the marketplace gate) exits 0.
- `scripts/check-skill-descriptions.py` reports `ok: all 27 skill descriptions are within 1020 characters`.

No sentence is generic tutorial material.

## Item 4: names by content, not by position
- The table row at SKILL.md:198 says "ahead of slot 1 unless the next release is a major **(below)**". The target has a name: the bold rule "A break leads the description…". (Taste)
- The case README's "Checks 1 to 3 are the rule under test; 4 to 6…" refers to checks by number even though each has a bold name. The list sits right next to it, so this is minor. (Taste)

## Item 5: the failure report
Analogue: is each rule reached by the checklist, and does the check detect the rule itself?

- **The Breaks check is weaker than the rule.** The checklist item at :849-852 asks only whether the description opens with the break lines. It does not ask whether every outcome that matches the break definition at :234-241 is among them.
  - **What goes wrong:** that definition is what the motivating case got wrong: a result-shape change left unmarked, and an extended failure left in Scope. A description that leads with the two obvious breaks and leaves those two behind passes the check.
  - **Request:** add "is every outcome that matches the definition (a different return value or result shape, a failure extended to inputs that worked) among the lead lines, and none in Scope?"

## Item 6: what the writer says it verified
There is evidence that the rule can fail and can pass:
- Baseline runs on HEAD~1 (both models) fail checks 1-3.
- Rule runs pass, with one Opus run still failing check 3, which is reported honestly.
- The control passes in all four runs.
- The earlier drafts of the rule are summarized but not stored, and the commit message says so.

The skill's own *After* example has no breaks and so still satisfies the rewritten rule.

One taste point: the commit message says "on Opus and Haiku (effort high)", which reads as covering both models. The case README says only Haiku ran at effort `high` and Opus ran at the session default.

## Item 7: siblings of the change
Analogue: places that list or route to the package. All three version lists move to 1.5.0 together:
- `apm.yml`
- `.claude-plugin/marketplace.json`
- the package's `apm.yml`

The package README gains a bullet, and the research README indexes `cases/`. A `git grep` for "breaks first" and "User-visible changes" outside the package and the research directory finds only the package README. `english-developer-style` hands breaking-change placement to this skill and needs no change. The one sibling inside the skill that was missed, the checklist's Caller item, is filed under item 1.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Both case READMEs quote a rule sentence ("promises compatibility") that the skill does not contain | Substantive | `research/.../pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | 1 |
| Checklist "Caller" still asks for breaks under "User-visible changes", contradicting the lead | Substantive | `SKILL.md:844` | 1 |
| Under rule 5 the leading breaks may or may not carry the `User-visible:` label | Substantive | `SKILL.md:257-260` | 1 |
| The extended-failure rule and the Scope rule for a break of open intent can each be read as governing | Substantive | `SKILL.md:238`, `SKILL.md:489` | 1 |
| Major, unknown-release, commit-body, and squash-body modes are claimed with no run | Substantive | `SKILL.md:248-260` | 3 |
| Breaks check does not detect breaks misclassified under the definition | Substantive | `SKILL.md:849` | 5 |
| "(below)" where the rule has a name | Taste | `SKILL.md:198` | 4 |
| Checks cited by number where each has a name | Taste | `pgjdbc-4367-breaks/README.md` (Checks) | 4 |
| "(effort high)" reads as covering Opus too | Taste | commit message | 6 |

The drift script was run, but it reports nothing for a change with no code. I could not fetch the cited pgjdbc#4367 maintainer comment because there was no network.
