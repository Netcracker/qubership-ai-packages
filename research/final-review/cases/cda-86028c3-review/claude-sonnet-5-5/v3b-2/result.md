# Final review: `4f69810..HEAD` (86028c3, `change-description-authoring` 1.5.0)

**Inputs.** The diff was read in full. The claimed cases come from the commit message alone, because no separate task statement was handed over. There is no previous report. This change has no code, so the drift script was not run. Each item below uses the analogue from §2a. I did not load `english-developer-style` or `test-authoring`: nothing here is wording-only, and no test code changed. I did not load `apm-authoring` either; the checks below use its rules only through the §2a text.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **Finding.** `cases/pgjdbc-4367-breaks/README.md` (intro) and `cases/pgjdbc-4392-no-break/README.md` (intro) quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed SKILL.md §2 heading is "A break leads the description unless the next release from the target branch is a major". The two conditions differ. "Promises compatibility" is the earlier draft's wording, and the READMEs say the results are on the committed tree.
- **Checked, no finding:**
  - The `skill-tree` ids match `git rev-parse HEAD:<skill dir>` (4798053…) for the rule runs and the base tree (1f020ce…) for the baselines.
  - The word counts in the 4367 README table match `wc -w`.
  - "All three Haiku results end with Generated with Claude Code" is true for 4367. That line also appears in both 4392 Haiku results, and the 4392 README says so.
  - The version bump to 1.5.0 is consistent in `apm.yml`, the package `apm.yml` and `marketplace.json`.
  - The §4 rule 5 and §7 cross-references resolve.
  - The new SKILL sentence in slot 1 and the checklist "Problem" and "Breaks" lines agree with the new rule.
  - The package README bullet matches the rule.
- **Not narration:** none of the added text narrates the change with "now", "no longer" or "used to" outside the case results, where quoting the draft's old behavior is the content.

## Item 2: claimed cases covered (analogue: sections and runs that handle each claim)

| Claim in the commit message | Evidence |
| --- | --- |
| Breaks lead unless the next release is a major | Four rule runs on 4367 lead with the breaks, and the baselines do not |
| Result-shape change is marked | The rule runs list it in the lead; the baselines have it in slot 3 |
| Extended failure leaves Scope, in "three of four" runs | `opus/result.md` and both Haiku runs do. `opus/result-2.md` leaves `grant insert` in Scope, as the commit says |
| Control grows no section | Four 4392 runs, no `Breaking changes` heading |
| "Next release from a version file, milestone or name" | Only the version-file source is exercised (see Item 3) |
| "A change with no break grows no section" | The 4392 control |

- **Commands:** the new text tells the reader to run none.
- **Hunks:** each belongs to a sentence of the commit message. The research README `cases/` row and the dated paragraph are claimed by "Two regression cases under research/…". The package README bullet and the four version bumps are claimed by the rule itself.

## Item 3: boundaries, partitions, and the negative control

- **Partitions the rule claims:** next release is a major; is not a major; is unknown. Only "not a major" (`gradle.properties` says 42.7.14) is exercised, in the 4367 runs. The control 4392 uses the same non-major target and has no break.
- **Not exercised:** the major arm ("breaks stay first in slot 3") and the unknown arm ("breaks lead where nothing says which release it is") have no run, and the commit does not claim them. The milestone and branch-name sources are also unrun.
- **Other partitions:** the commit-body arm (breaks as the first `User-visible:` lines, problem first) and the squash-copies-description arm have no run. The rule changes the commit body's order and the `Problem` checklist line, and the commit message claims it, so I treat this as claimed and untested.
- **Control scope:** the 4392 control has no baseline run on `origin/main`, so a drift in unrelated output cannot be separated from the rule's effect. The commit claims only that "the control grows no section", which the runs support. Word counts (241 and 251 for Opus, 256 and 249 for Haiku, against a 209-word draft) show no growth that can be attributed to the rule.
- **Sample size:** each cell is one or two runs, and one of two Opus runs missed the `grant insert` check. The README says the sentence "moves the case most of the time and not always". That is stated, not hidden.
- **Instruction table (§2a), one row per instruction added:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where nothing says which release it is, the breaks lead" | A change with a break aimed at a repository with no version file, milestone or branch naming, where all releases are majors by convention | A `Breaking changes` lead of a few lines before Why (a "paragraph" cost, in the skill's own words) | Ended by the text: "A break read first in a major release costs a paragraph". Not a finding |
| "Open with slot 3's break lines under a `Breaking changes` heading, after at most a short paragraph" | A one-paragraph description with no headings, where the repository has no template | A single `Breaking changes` heading above a paragraph | "Under a `Breaking changes` heading where the description has headings" ends it. Not a finding |
| "A failure extended to inputs that worked before goes with the breaks, not in Scope" | A failure that existed only because a stricter validation now applies to the same input class | The extended failure listed under both breaks and Scope | "Stated once" is not in the skill. The slot-3 rule "A fact stated in slot 3 is not restated in slot 2" covers part of it. Taste |
| "The commit body keeps problem first, with breaks as first `User-visible:` lines" | A commit that contains only a break and no other outcome | `User-visible:` with one line, after the problem | The slot 4 text: present whenever there is an outcome. Not a finding |

## Item 3a: level, placement, and the environment (analogue: file, layout, registration)

- **Layout:** the new cases sit under `research/change-description-authoring/cases/`, as the research README now says. Their file layout matches between 4367 and 4392: `prompt.md`, per-model `result*.md` and `skill-tree`, and `baseline/` only for 4367.
- **Registration gate:** the registration entries (`apm.yml`, the package `apm.yml`, `marketplace.json`) agree on 1.5.0. I did not run the repository's own gate.
- **Level:** the rule paragraph states what to do for a non-major release and names the version file, milestone and branch name, which is platform-specific knowledge. No tutorial-level sentence found.

## Item 4: names by content, not by position

none. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) are content names built from a PR number plus the property. The files `result.md` and `result-2.md` are ordinal, but `result-2` is explained only by "two runs each". I would not file this as a finding: a run index is a run index, not a thing with a content name.

## Item 5: the failure report (analogue: what a failure looks like)

- Checks 1 to 3 in the 4367 README can be applied by eye to a result: lead, result shape, `grant insert` outside Scope. Each check is stated narrowly enough that a reader can tell pass from fail, and the README table does so per run.
- **Weak detection:** check 5, "Stated once", has no shown detection in the table. All six rule runs are marked passes (their row has no fail), but `haiku/result.md:8` and `opus/result.md:8` carry the `grant insert` line as an item in the lead, and the README does not say which grep or reading established that the line is not also in Scope. Not a rule finding, so I filed it as taste below.
- **Checklist:** the new `Breaks` checklist line in SKILL.md §8 reaches the rule (lead, slot 3 keeps the others, no empty heading when nothing breaks). Its detection is weaker than the rule on one point: it does not say the lead is dropped for a major release. It says "is not a major, or is unknown" in the condition, which covers it.

## Item 6: what the writer says it verified

The commit states red evidence: baselines on `origin/main` show Why first and both breaks in place, and with the rule all four lead with the breaks. It also states the control. It states that earlier drafts of the rule were run on Opus and are "summarized in the case README, not stored". The README does summarize them (three versions, first without the extended-failure sentence).

## Item 7: siblings of the change

- **Set grown:** the package gained a rule, not a member of a set. The places that enumerate or route to the skill are the marketplace entry, the umbrella `apm.yml` and the package README. All three were updated.
- **Description drift:** the description string of the skill is unchanged in all three. It does not mention breaks, and the rule is in the body, so the skill still loads on the same surface. That scope (the opening of descriptions) was already covered by "pull request descriptions".
- **Referencing siblings:** the `english-developer-style` copies (US, UK, `.agents`, `.claude`) only name the skill and do not describe its rules. No sibling states the old order. I searched for the old rule "Breaks first … in the outcome slot" and found it only in the one table cell the change edited.
- **Internal sibling:**
  - `SKILL.md` line 190–191 still says "Six slots, in order", and the table lists Why as slot 1, while slot 3 now says breaks go "ahead of slot 1". A reader sees the slot order contradicted in the same table.
  - The prose that follows (slot 3 "Breaks come first") reads as first within slot 3.
  - The new section reconciles it ("The description then opens with slot 3's break lines … the Why slot follows"), so a careful reader gets the answer. I filed it as taste.
- **Worked example:** the "After" example in §2 has no break, so it does not contradict the rule, and the closing sentence in that section ("without a template, its four paragraphs stand as prose") is unaffected.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote the rule's earlier heading, "where the next release from the target branch promises compatibility". The committed rule says "unless the next release from the target branch is a major". A reader of the case cannot tell which condition the runs tested. | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md` (intro, last sentence); `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md` (intro, last sentence) | Quote the committed heading in both |
| The commit-body arm of the rule (breaks as first `User-visible:` lines, problem first; and the squash-copy variant) is claimed in the commit message and has no run. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` (new paragraph, "The commit body keeps its order") | Add a run, or state in the commit or case README that only the pull request description arm was exercised |
| "Six slots, in order" with Why as slot 1, while slot 3 is "ahead of slot 1" unless the release is a major. | Taste | `SKILL.md` line 192 (table intro) and line 198 | Say in the table intro that slot 3's break lines may precede slot 1 (I prefer this; expect it to be declined) |
| The README marks check 5 as passing for six runs without saying how it was checked. | Taste | `cases/pgjdbc-4367-breaks/README.md` (Results) | One clause on how "stated once" was checked (grep for the lead's break lines in the later sections) |
| The major and unknown arms and the milestone/branch-name sources have no run. | Taste | `SKILL.md` (new paragraphs on the next release) | Not a request: the commit does not claim them. Mention as untested if the 1.5.0 notes list verified arms |

**Not checked:** I did not run the repository's registration gate, markdownlint or the line-length gate, and I did not re-run any drafting agent. I read only the headings and first lines of each stored result against the README table, not each result against all six checks. And I did not do a style-only pass over the prose.
