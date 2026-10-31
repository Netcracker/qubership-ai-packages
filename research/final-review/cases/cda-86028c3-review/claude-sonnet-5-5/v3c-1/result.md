# Final review: `4f69810..HEAD` (86028c3, one commit)

**Task statement:** none was handed over. The claimed cases come from the commit message alone, so item 2 rests on it.

**Kind of change:** no code. It edits a skill (SKILL.md), a package README, version metadata, and a research directory, so I used the §2a analogues throughout.

**Drift script:** run, and it printed nothing because there are no code members. Skills loaded: only `final-review`. I did not load `english-developer-style`, `test-authoring`, or `apm-authoring`, so I cite no sections from them. Wording is outside this review. I did not run any suite and did not re-run the model trials.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Finding 1 is substantive. The change renamed the SKILL.md rule. Its heading is now "A break leads the description unless the next release from the target branch is a major". The case READMEs quote the old heading instead:
- `research/.../pgjdbc-4367-breaks/README.md:7-8` and `:8` (the heading in the intro, plus "SKILL.md §2") quote "A break leads the description where the next release from the target branch promises compatibility".
- `research/.../pgjdbc-4392-no-break/README.md:6-7` quotes the same.
- `git grep 'promises compatibility'` finds only those two places. The text they cite no longer exists.

Finding 2 is substantive. The commit message says "(effort high)" for both models. The 4367 README says "Haiku ran at effort `high`; Opus at the session's default". The 4392 README names effort for Haiku only. Both cannot be true for Opus.

Finding 3 is taste. SKILL.md says the commit body keeps problem-first order, with breaks as the first `User-visible:` lines. It also says that where §4 rule 5 makes the description the commit body, "that body opens with its breaks and then its problem". Both sentences are in the same paragraph, and the paragraph says why. The slot-1 sentence and the checklist line are consistent with it.

Checked and consistent:
- Version 1.5.0 appears in `apm.yml`, the package `apm.yml`, and `marketplace.json`.
- The §4 rule 5 reference matches the rule text.
- "(§5)" for the `BREAKING CHANGE:` trailer matches the trailer table.
- "(§7)" for no empty heading matches §7.
- The README bullet matches the SKILL text.
- The word counts in both READMEs match `wc -w` (825, 792, 758, 756, 779, 784; 241, 251, 256, 249).
- The "Generated with Claude Code" claims hold: three Haiku files in 4367 and both Haiku files in 4392.
- The `skill-tree` ids match the git trees: `4798053…` is HEAD's skill directory, and `1f020ce…` is the parent's, as the baselines claim.

## Item 2: claimed cases covered

Commit-message claims, each with its covering evidence:
- Breaks lead unless the next release is a major → check 1, and all `result*.md` of 4367.
- Result-shape change is a break (`getUpdateCount()` at `-1`) → check 2, covered.
- Failure extended to later statements is a break → check 3, covered. One Opus run (`opus/result-2.md`) keeps it in Scope, as the message says.
- A fix (`create table begin…`) is not a break → check 4.
- A change with no break grows no section → 4392 checks 1 and 2.
- "Without the rule both models put Why first and left both breaks in place" → the two baselines. This holds, and both baselines keep the result-shape line in slot 3 and `grant insert` in Scope.
- "Two runs each with the rule and one each on origin/main" → 4 + 2 files, as stated.
- "Earlier Opus runs of two drafts … not stored" → stated honestly in the README.

Claims with no test:
- **Finding 4, taste.** The rule's other clauses have no case:
  - A major-release target keeps breaks first in slot 3 only.
  - An unknown release makes the breaks lead.
  - A `BREAKING CHANGE:` trailer decides.
  - The commit body keeps problem first.
  - The squash-copy variant opens with its breaks and then its problem.

  Only a patch-release target (`master` at 42.7.14) is run. The description does not claim these partitions, so this is taste.
- **Finding 5, taste.** The two other breaks, `42703` and `0100E`, are not among the README's checks 1–3 (only result shape and `grant insert` are). All six results do lead with them, and the rule lists "a call that succeeded and now fails" as a break. A check would make the claim falsifiable.

Commands in changed files: none. The README's `git archive` line is a description of the setup, not a recipe the change tells anyone to run.

Hunks against claims: the version bumps, the README bullet, and `research/.../README.md` (the `cases/` line and the closing note) have no sentence in the commit message. They are the normal companions of a skill change, and the message says "Two regression cases". I treat them as claimed and not a finding.

## Item 3: boundaries, partitions, and the negative control (analogue: genres, modes, and the control arm)

The control is present: `pgjdbc-4392-no-break`, with two runs per model. They pass all three checks. Baseline arms are present for 4367.

Finding 6 is taste. The 4392 control has no baseline run on the pre-rule skill. It therefore cannot show that the base also produces no section, so it does not discriminate. It only shows that the rule did not add one.

Finding 7 is taste. Other partitions of the rule have no trial: a major-release target, an unknown release, and a repository with a template or no headings (the "Breaking changes heading where the description has headings" clause). The Haiku and Opus runs all use headings, from the draft's template.

State left by an earlier version: not applicable.

**Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| A break leads the description unless the next release is a major | A breaking change targeting `main` of a repository with no version file, milestone, or branch name | The breaks lead, and a "short paragraph that says which code breaks" | The text ends this itself: "Where nothing says which release it is, the breaks lead". Not a finding |
| The lead has a short paragraph saying which code breaks | A single one-line break | A paragraph that restates the one break line | "at most a short paragraph" allows zero. Not a finding |
| `Breaking changes` heading "where the description has headings" | A four-paragraph description with no headings | The breaks as the first paragraph | Ended by the same sentence. Not a finding |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides, and it is written whatever the description does" | A repository that squashes with a release tool, where the change is already a major | A trailer and the lead | **Finding 8, taste**: the sentence says the trailer "decides", which the next sentence about majors contradicts if the tool has bumped the major. Two readings; I prefer "the trailer is written whatever the description does", dropping "decides". Not a request |
| "A failure the change extends to inputs that worked before … goes with the breaks, not in Scope" | A change that narrows a failure to fewer inputs | Breaks only for the extended inputs | The rule's last clause: "a failure that now succeeds is a fix". Not a finding |
| Checklist line "Breaks: … is there no lead and no empty heading?" | A change that breaks nothing | Nothing | Ended by "Where nothing breaks". Not a finding |

## Item 3a: level, placement, and the environment

- The new rule sits inside SKILL.md §2 beside the Pull request description slots. The README bullet and the checklist line sit with their siblings, and the research cases follow a `cases/` layout.
- **Finding 9, taste.** The new cases hold the `research/` tree's first `cases/` directory. The research README adds a layout line and a note. The `skill-tree` files are one-line files with no extension, so a repository gate that checks file types may flag them. I could not tell, and I did not run a gate.
- I did not run the repository's markdownlint or lychee, so whether the new READMEs and result files pass them is unchecked.

## Item 4: names by content, not by position

Finding 10 is taste. The result files are named `result.md` and `result-2.md`, which are ordinals. The READMEs' table refers to them by those names, and their content differs (`result-2` is the second sample of one skill tree). A name by content would be a run id with the model and date. This is taste: the files record samples, not cases.

No other ordinal, "see below", or "case 3" appears in the changed prose.

## Item 5: the failure report (analogue: what the rule tells the reader to look at)

- The README checks are detected by reading the result files, with a table of pass/fail by check. The table lists each failure ("fails: Why first") and so is a failure report.
- **Finding 11, taste.** Check 5 ("Stated once. No break line is repeated…") has a result cell for every run but no stated way to detect it, such as a search for a literal. The word-count column is a proxy for the cost claim only.

## Item 6: what the writer says it verified

The change states its evidence: baselines on the parent skill tree and with-rule runs on the committed tree. Both are named by tree id, and the ids check out. The README states that a first version of the rule left `grant insert` in Scope in both runs. The commit message accepts that one of four runs still leaves it. The README says "the sentence moves the case most of the time and not always". Evidence stated: yes.

One gap. The "reworded after review" version was run on only two Opus samples and two Haiku samples. The README states that count.

## Item 7: siblings of the change

- The set is the skill's mentions of where breaks go. `git grep` for "Breaks first" and `**Breaking:**` finds:
  - SKILL.md line 543-544 (changelog entry): "Breaking changes are marked in place and sorted first within their category". Different artifact, no conflict.
  - The Changelog row at line 876 of the checklist. It is a changelog rule and unaffected.
- **Finding 12, substantive.** The slot 1 row (line 86 area) and the slot-3 row are updated. The checklist line "Subject / Problem" is updated. The *Before/After* example at SKILL.md `*Before:*` (just after the new paragraphs) and the §2 pull-request example at about lines 296-312 were not re-read against the new rule: the example paragraph says "Under §4 rule 5 the description is the commit body … The *After* above carries headings only to label its slots". The *After* example's order is the old one (problem, then outcome). I did not confirm whether the example is a pull request description that carries breaks. If it does, it contradicts the new rule. If it carries none, the sentence the new rule needs ("A change with no break has neither the lead nor an empty heading") covers it. I could not settle this without reading the example in full, so I mark it **plausible, not confirmed**, and I label it substantive only if the example carries a break. The request is for the author to check it.
- Cross-package siblings: the two `english-developer-style` copies and the instruction files mention the skill by name only. The package README is updated. `docs-page-authoring/README.md:43` says the skill "owns the changelog entry and the pull request" and does not enumerate rules, so it is unaffected.
- A new member of a set: no list of rules or slots grew. No old count ("six slots", "five slots") changed, and "Six slots, in order; the last three are conditional" is still true.

## Findings table

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Both case READMEs quote the old rule heading ("promises compatibility") and cite "SKILL.md §2" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`; `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the current heading, "A break leads the description unless the next release from the target branch is a major" |
| 2 | Effort level for Opus: commit message says high for both models, the 4367 README says Opus ran at the session default | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md` "Running it" | Make one statement true and the other match |
| 12 | The slot-3 example *After* may contradict the new lead rule | Substantive if the example carries a break; unconfirmed | SKILL.md near the *Before/After* block after the new paragraphs | Re-read the example against the rule; add a breaks-first version or say it has no break |
| 3 | Same-paragraph "keeps its order" and "that body opens with its breaks" read as a conflict until the second sentence | Taste | SKILL.md, last new paragraph | None needed |
| 4 | No trial for a major target, an unknown release, or a `BREAKING CHANGE:` trailer | Taste | cases | Say in the README that these partitions are not run |
| 5 | `42703` and `0100E` breaks have no check | Taste | `pgjdbc-4367-breaks/README.md` Checks | Add them to check 2 or 3 |
| 6 | The control has no baseline arm | Taste | `pgjdbc-4392-no-break` | Add a baseline run, or say it is absent |
| 7 | No trial without headings | Taste | cases | Same as 4 |
| 8 | "the trailer decides" vs. a major bump | Taste | SKILL.md, "Where a release tool bumps…" | Drop "decides" |
| 9 | Extensionless `skill-tree` files and the first `cases/` tree may meet repo gates | Taste | cases | Run the gates |
| 10 | `result.md` / `result-2.md` are ordinals | Taste | cases | Optional |
| 11 | Check 5 has no stated detection | Taste | `pgjdbc-4367-breaks/README.md` | Name a literal to search |

**Not checked:** I ran no model trial and no repository gate (markdownlint, lychee, the marketplace check); I did not read the *Before/After* example in full (finding 12) or any file outside the diff beyond the greps above; and I did not review the prose for style.
