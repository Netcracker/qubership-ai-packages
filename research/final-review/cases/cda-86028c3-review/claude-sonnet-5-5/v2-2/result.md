# Final review: `4f69810..HEAD` (one commit, 86028c3)

**Sources of the claimed cases.** I had no task statement. The claimed cases come from the commit message alone, and item 2 is answered on that basis.

**No-code form (§2a).**
- The change is a skill (`SKILL.md`), its README, version bumps in three manifests, and a research directory.
- I did not run `comment-drift.py`. There are no code members to parse.
- I loaded `english-developer-style`.
- I did not load `apm-authoring`, because only the three named skills were permitted.
- I read the `SKILL.md` diff against the rest of the file, and the case READMEs against the skill.

## Item 1: comments consistent (analogue: statements one file makes about another)

- The skill, `README.md`, `apm.yml` ×2 and `marketplace.json` all say 1.5.0, and the old 1.4.0 is gone from all of them. The package README bullet matches the rule.
- Both case READMEs misquote the rule. They call it "A break leads the description where the next release from the target branch promises compatibility", at "SKILL.md §2". The skill's lead sentence is "A break leads the description unless the next release from the target branch is a major". The polarity differs, and "promises compatibility" appears nowhere in the skill. This is the stale first draft of the rule (`pgjdbc-4367-breaks/README.md` line 7, `pgjdbc-4392-no-break/README.md` line 6).
- Opus effort is stated two ways. The commit message says "Opus and Haiku (effort high)". The case README says "Haiku ran at effort `high`; Opus at the session's default".
- `SKILL.md` line 247 says: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does."
  - That tool bumps the major because of the break, so with it every break makes the next release a major, and the lead never applies.
  - The sentence does not say whether the trailer's bump counts as the "next release is a major".
  - An agent can read it either way.
- `SKILL.md` line 490 says a break whose intent only a maintainer can settle "stays in Scope as a question". The new rule says a failure extended to working inputs "goes with the breaks, not in the Scope slot". Nothing says which wins for a break whose intent is in doubt. In the 4367 draft, `grant insert` was exactly that kind of case.
- `SKILL.md` line 257 says the commit body keeps problem first because "R2 opens the commit for the reason". Line 259 then says a body made from a squashed description opens with its breaks. The exception is stated, but the reason is not reconciled.
- The "(§7)" and "(§5)" references resolve. "Below" resolves. The slot 1 and §8 checklist edits agree with the rule.
- No comment narrates the change.

## Item 2: claimed cases covered

| Claim | Covered by |
| --- | --- |
| Lead with breaks unless the release is a major | `pgjdbc-4367-breaks` check 1. Runs: opus/result, result-2, haiku/result, result-2. |
| Result shape is a break | Check 2, all four runs pass. |
| Extended failure moves out of Scope | Check 3. Three of four runs pass; opus/result-2 fails, as the commit message says. |
| Control grows no section | `pgjdbc-4392-no-break`, all four runs. |
| Version read from the version file, milestone, or branch name | No case. |
| Release is a major | No case; `prompt.md` has a patch release only. |
| Release is unknown, so the breaks lead | No case. |
| `BREAKING CHANGE:` trailer decides | No case. |
| Commit body keeps problem first, with breaks as the first `User-visible:` lines | No case. |
| Rule 5 squash body leads with breaks | No case. |

- The "on origin/main" baselines exist for 4367 only, and the commit message says so.
- Every hunk belongs to a sentence of the commit message. The research README index and note are covered by "Regression cases".
- No command is told to run, apart from the `git archive` recipe in the case README. The case README is its own check, and no CI job runs it.

## Item 3: boundaries, partitions, negative control (with the table of added instructions)

The control (4392) exists. The partitions the rule names are mostly untested; only the unrun ones are listed in Item 2. There are no pre-existing-state or limits concerns.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Lead with breaks, under a `Breaking changes` heading | A patch-release change whose only "break" is a failure that now succeeds | None. "A failure that now succeeds is a fix, not a break" ends it. | Already in the skill; not a finding. |
| Lead with breaks | A major release | Breaks first in slot 3. | Stated. |
| Lead with breaks | A release tool that bumps the major on the trailer | Unclear: either the lead or no lead. | Needs "where the trailer makes the next release a major, the breaks stay in slot 3". **Substantive.** |
| A failure extended to working inputs is a break, not Scope | A break whose intent only the maintainer can settle (line 490) | Two rules point opposite ways. | Needs "…; a break whose intent is in question still leads, and the question stays in Scope". **Substantive.** |
| Short paragraph before the breaks, "which code breaks" | A one-line change with a single break | A paragraph that restates the break line. | Needs "only where there is more than one break". **Taste.** |
| Commit body: breaks as the first `User-visible:` lines | A rule-5 squash body | Lead first, then problem. Stated at line 259. | Not a finding. |

## Item 3a: level, placement, environment

- The files sit beside their siblings: the skill, the package README, and the research `cases/` directory, which the research README index now lists.
- I did not run the repository gate (the markdownlint 120-column check) or any link check. No hand-written line over 120 columns in the changed `.md` files, apart from table rows (`SKILL.md` line 198 and the case README check 3 and its table), which these checks usually exempt. I did not confirm that they are exempt.

## Item 4: names by content

The case names `pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`, `result-2` and `Three versions of the rule` carry an ordinal. `result-2` names a second run, which is acceptable. None.

## Item 5: failure report

- Each README check says what to look at, and the tables list each failing check by name, so a reader can see which check fails.
- Check 5, "once", has no stated detection beyond reading.
- Check 4's detection is the fix string. That detects the property.
- No other findings.

## Item 6: what the writer says it verified

The commit message states two runs each with the rule, one on the baseline, and the control, and the case README gives per-run pass or fail. The baseline fails checks 1 to 3, which shows the checks can fail. The rule was reworded after review, and the README says only that the committed wording passed "in one of two Opus runs and in both Haiku runs". So there is no run of the final wording on the final wording's failing case beyond those four.

## Item 7: siblings

- The set of version carriers is consistent (see Item 1).
- `change-description-authoring.instructions.md` is only a loader, so it needs no change.
- `references/merge-model.md` has no mention of the break lead. Rule 5 in `SKILL.md` §4 also says nothing about the lead. Its edit is made from §2 (line 259) rather than at rule 5, which is where a reader of the merge model would look. **Taste.**
- §2 shows no worked *After* with a lead, so the only example of the new shape is in `research/`. **Taste.**
- The skill's cross-reference to `docs-page-authoring` and the sibling packages' lists need no change.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The case READMEs quote a rule title the skill does not contain ("promises compatibility") | Substantive | `cases/pgjdbc-4367-breaks/README.md` line 7; `cases/pgjdbc-4392-no-break/README.md` line 6 | Quote the actual lead sentence, "unless the next release from the target branch is a major". |
| Opus effort is stated differently in the commit message and the case README | Substantive | Commit message; `pgjdbc-4367-breaks/README.md` "Running it" | Say which; if Opus ran at the session default, the message is wrong. |
| `BREAKING CHANGE:` trailer sentence is circular for a tool that bumps the major on the trailer | Substantive | `SKILL.md` line 247 | State whether the bump makes the release a major. |
| Intent-in-doubt break: line 490 puts it in Scope, line 239 forbids Scope for extended failures | Substantive | `SKILL.md` lines 239 and 490 | One clause saying which wins. |
| Major, unknown-release, version-file, and trailer branches have no case | Substantive | `cases/` | A case for at least the major (the lead is absent there) and for the unknown-release path, or a sentence in the README that they were not tried. |
| Short paragraph before the breaks adds a restatement for a single-break change | Taste | `SKILL.md` line 252 | "Only where more than one break." |
| The squash lead is stated at line 259 but not at rule 5, and has no worked example in §2 | Taste | `SKILL.md` §4 rule 5; §2 | Optional pointer at rule 5. |

**Not checked:** I did not run the suite or the repository's lint and link gates. I did not re-run any case, and I did not read the stored result files beyond one opus result and the READMEs' own tables. The wording pass for style alone was not done.
