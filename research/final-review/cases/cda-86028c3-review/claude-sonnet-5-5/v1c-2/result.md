## Final review: `4f69810..HEAD` (commit 86028c3)

**Inputs.** The change has no code: it is a skill (`change-description-authoring`, 1.4.0 to 1.5.0), its package README, the version entries in the marketplace and `apm.yml`, and two research cases. I used the §2a analogues under every item. I did not run the drift script, because there are no members for it to parse. There is no task statement, so the claimed cases come from the commit message alone. There is no previous report. I loaded `english-developer-style`. `test-authoring` does not apply to a change with no tests. Two of the skills final-review names are not among the three provided: `apm-authoring` and `docs-page-authoring`. I did not load them, so the rule names I cite from `apm-authoring` come from final-review's text, not from reading that skill.

### Item 1: comments consistent with the code and with each other

Five findings:
- **Moved breaks, unmoved sentences.** The change moves the breaks out of slot 3, but two sentences elsewhere still put them there:
  - `SKILL.md:226`: "Breaks come first and add the version…", written of slot 3.
  - `SKILL.md:845` (checklist): "carry one line per distinct outcome under 'User-visible changes', breaks first".
  - Both contradict `SKILL.md:253-254` ("Slot 3 keeps the other outcomes") and the new `Breaks` checklist item at `:849`. A reader following the old checklist line puts the breaks back into slot 3.
- **Stale quoted rule name.** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The skill's text is "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`).
  - `pgjdbc-4367-breaks/README.md:6` also says "SKILL.md §2" without naming the package.
  - `pgjdbc-4392-no-break/README.md:6` carries the same stale quote.
  - The two differ on a release that is neither a patch nor a major, and on an unknown release.
- **Effort level disagrees with the commit message.** The commit message says "Opus and Haiku (effort high)". The 4367 README (`:33`) says "Opus at the session's default". The 4392 README names only Haiku's effort.
- **Misleading verb.** The rule opens with "A break **changes** what code that works on the released version gets" (`SKILL.md:235`). It means that a break is a change in what such code gets, and "gets" is the wrong word for a result.
- **Table versus prose.** `SKILL.md:198` (table row for slot 3) says "ahead of slot 1 unless the next release is a major". That is the lead rule, but it sits in a row whose slot number says the breaks come third. The prose below resolves it, but the table alone misleads.

No comment narrates the change (`now`, `no longer`, `used to`) outside the case READMEs, where recording history is their job. The cross-references `§7`, `§5`, and `§4 rule 5` all resolve (§7 says no empty headings; §5 lists `BREAKING CHANGE:` and `!`; rule 5 is at `:637`).

The first sentence of the new paragraph ("A break leads the description unless…") stands alone and states the rule. The package README bullet (`README.md:23-25`) matches the rule.

### Item 2: claimed cases covered

Claims from the commit message, each with the case that exercises it:

| Claim | Case |
| --- | --- |
| Without the rule, both models put Why first and leave both breaks in place | `opus/baseline`, `haiku/baseline` of `pgjdbc-4367-breaks` (README table) |
| With the rule, all four runs lead with breaks and mark the result shape | `opus/result`, `opus/result-2`, `haiku/result`, `haiku/result-2` (checks 1 and 2) |
| Three of four move the extended failure out of Scope; one Opus run left it there | Check 3, `opus/result-2` (README table says "fails: in Scope"; `result-2.md:35` confirms) |
| The control grows no section in any run | `pgjdbc-4392-no-break`, four results (checks 1 and 2) |
| Earlier Opus runs of two drafts are summarized, not stored | README, "Three versions of the rule were run on Opus" |
| Skill tree id recorded per run | The ids match `HEAD:…/change-description-authoring` (4798053…) for every rule run and the control. The baseline id (1f020ce…) equals `HEAD~1`. |

Rule claims in the skill with no run:
- **A release that is a major.** "Where the next release is a major, the breaks stay first in slot 3" (`SKILL.md:254-255`) has no case. This is the partition the rule's own condition turns on.
- **A release that is not named.** "Where nothing says which release it is, the breaks lead" (`:248`) has no case. Both cases state `42.7.14` outright.
- **The `BREAKING CHANGE:` or `!` path.** "The trailer decides, and it is written whatever the description does" (`:246-248`) has no case.
- **The commit body.** The commit message claims "The commit body keeps the problem first, with the breaks as the first User-visible lines". The cases only draft pull request descriptions. Nothing exercises the commit-body rule or the squash-copy sentence (`:258-260`).
- **A description without headings.** "Under a `Breaking changes` heading where the description has headings" has no case with a template.

The README table is read from the results as recorded, and I did not rerun any model. The commit message's "three of four" is consistent with the table.

There are no command lines to list. Hunk-to-claim: every hunk belongs to a sentence of the commit message. That covers the version bumps in `apm.yml`, `marketplace.json`, and the package `apm.yml`, the README bullet, the research README entry, and the cases. I did not run the gate that compares them, and the commit message does not mention the 1.5.0 bump. The bump is a normal consequence of a skill change, but no sentence claims it.

### Item 3: boundaries, partitions, and the negative control

- **Negative control.** Present: `pgjdbc-4392-no-break`, two runs on each of two models, checking that no lead and no empty heading appear. It covers the "no break" side of the rule.
- **Partitions the rule names.** The release-kind partitions (major, patch, unknown) and the signal partitions (version file, milestone, branch name, trailer) have one run each at most: patch, from a version file. Findings are in Item 2.
- **Break kinds.** The rule lists five: a new failure, a changed return value or shape, a removed or renamed option, a changed default, a changed error code. The case contains two of them: a new failure and a result shape. Options, defaults, and error codes have no case.
- **Pre-existing state.** The skill is read by an agent that drafts text, and no earlier version leaves state on the target. N/A.
- **Sample size.** Two runs per model per arm: enough to show the direction, not a rate. The README says so for the `grant insert` line ("not always"), which is the honest claim.

**Added instructions table** (the skill and README add or widen these):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "The description then opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings, after at most a short paragraph that says which code breaks" | A change with no break | The text ends it already: "A change with no break has neither the lead nor an empty heading (§7)". Control case confirms. | Quoted, so not a finding |
| "Where nothing says which release it is, the breaks lead" | A repository where nothing says which release it is and the change has a break | Breaks lead; the text gives the reason (a missed break in a patch release ships). | Not a finding |
| "A failure the change extends to inputs that worked before is a break for those inputs … it goes with the breaks, not in the Scope slot" | A Scope-slot item the author has deliberately left unchanged, such as a failure that already behaved this way for these inputs | The agent moves it into the breaks, which is the intended behavior | Not a finding. The "inputs that worked before" condition limits it. |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!`, the trailer decides, and it is written whatever the description does" | A repository with no release tool | The agent is told to write a trailer for a tool the repository lacks | Substantive. Nothing limits the sentence to repositories that have the tool; the sentence "Where a release tool bumps…" opens it, but "it is written" in the main clause reads as unconditional. A clause such as "…and the trailer is written only where such a tool is configured" would end it. |
| "Whether the old behavior was right does not decide it" | A bug where the old behavior was wrong | The agent marks the correction of a wrong behavior as a break whenever calling code sees a different result; with the next sentence's "a failure that now succeeds is a fix", the line between the two rests on direction alone. A different value for a call that already succeeded is a break; that matches the rule. Fine. | Not a finding |

### Item 3a: level, placement, and the environment

- **Placement.** The new rule sits in §2, Pull request description, next to the slot table it modifies; the checklist item sits in §8; the README bullet sits in the matching list. This matches the sibling layout.
- **Registration.** The version is aligned in `apm.yml`, the package `apm.yml`, and `marketplace.json`. I ran `make check-descriptions`: all 27 descriptions pass. I did not run `make check` (`apm pack --check-versions`), which needs the `apm` tool.
- **Case layout.** Each model has its own `skill-tree` file and results, with a `baseline/` subtree; the control omits baselines, which the README does not explain.
- **Filler.** The sentence "In a release that is not a major, the reviewer's first decision is whether the change may ship in it at all" carries a fact particular to this skill, so it stays.

### Item 4: names by content, not by position

One finding, taste: `result.md` and `result-2.md` are named by ordinal. The README table and prose refer to them as such (`opus/result-2.md`). Naming by the content that differs is not possible here, since the runs differ only by sampling, so I leave it. No other ordinal names.

### Item 5: the failure report

Each of the six checks in the 4367 README says what a pass looks like in the draft's words (the literals, the `-1` result shape), and the results table names the failing check per run. The checks are prose and a reader must read each result by eye; there is no script. Taste: one line that greps the six literals of check 6 would make that check mechanical.

### Item 6: what the writer says it verified

The change carries its evidence: the baseline runs on the previous skill tree fail checks 1, 2, and 3 on both models, and the runs on the new tree pass them (apart from the `grant insert` line in `opus/result-2`). The control passes. Both are named in the commit message and README. Not stated: a rewrite of the final rule text was reviewed after the last run. The README says the committed version was "reworded after review" and that it "did [move the line] in one of two Opus runs and in both Haiku runs", so the committed text was run.

### Item 7: siblings of the change

- **Set members.** The change adds one member to the checklist (`Breaks`) and the lists that enumerate checklist items. I searched for the existing `Verification` and `Scope` items: they appear in the checklist, the slot table, and the README. The new item appears in the checklist and the README, as the rule needs.
- **Counts.** No sentence counts the slots or checks as a set of fixed size beyond "Six slots" (still true) and "Five slots" (commit body, unchanged).
- **Other paths with the same symptom.** The changelog entry (§3) has its own compatibility rule ("Breaking changes are marked in place and sorted first within their category", `:543`). The rule for the pull request description is separate and does not collide, but a reader might wonder whether the changelog needs the same patch-release condition. The commit message does not say. Taste: one sentence saying the changelog is unchanged.
- **Package umbrella.** The change updates the version in the umbrella index. I did not find a second place that pins 1.4.0 (`git grep '1\.4\.0'` finds no other site in this package's index entries). That check was not exhaustive across the repository.

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Two sentences still put the breaks in slot 3, contradicting the new lead rule | Substantive | `SKILL.md:226`, `:845` | State that, in a description that leads with its breaks, slot 3 carries only the other outcomes, or reword both sentences to "the breaks are the first lines of the description or of slot 3, per the rule below". |
| 2 | The case READMEs quote a rule name the skill no longer uses | Substantive | `pgjdbc-4367-breaks/README.md:6`, `pgjdbc-4392-no-break/README.md:6` | Quote the committed heading, "A break leads the description unless the next release from the target branch is a major". |
| 3 | The README's effort level for Opus differs from the commit message | Substantive | `pgjdbc-4367-breaks/README.md:33`, commit message | Make the README and the commit message state the same effort for each model, and add Opus's level to the control README. |
| 4 | No run covers the major-release partition, an unknown release, the trailer path, the commit body, or a template with headings | Substantive | `SKILL.md:246-260` | Add one case on a major-release target (the breaks stay in slot 3, no lead) as the control for the condition, or state in the README that these partitions are untested. |
| 5 | The break kinds list five; the case exercises two | Taste | `SKILL.md:235-239` | Prefer one more case with a changed default or removed option, so the list is not stated on one example. Expect it to be declined. |
| 6 | The trailer sentence reads as unconditional | Taste | `SKILL.md:246-248` | Prefer "where such a tool is configured, the trailer is written". |
| 7 | "A break **changes** what code … gets" | Taste | `SKILL.md:235` | Prefer "A break is a difference in what code that works on the released version gets". |
| 8 | The 1.5.0 bump is not claimed in the commit message | Taste | `apm.yml`, `marketplace.json`, package `apm.yml` | Add half a sentence naming the bump. |

**Not checked.** I did not rerun any model, did not run `make check` or the marketplace gate, did not verify the pgjdbc facts (PR numbers, the 42.7.14 version, the maintainer's rewrite) against the network, and did not do a style-only pass over the prose.
