I've read the skill, the diff and the case files, and I'm now writing the report. No files were changed.

# Final review: `4f69810..86028c3` (one commit, "lead the description with breaks unless the next release is a major")

**Inputs.**
- There is no separate task statement, so the claimed cases come from the commit message alone, and item 2 rests on that.
- The change has no code, so each item uses the §2a analogue. The skills loaded were `apm-authoring` and `english-developer-style`, from the supplied copies.
- I ran `comment-drift.py 4f69810 HEAD`. It printed nothing, which is expected because it parses no Markdown. The comment analogue was done by hand.
- There is no previous report for this change.
- The files touched are `SKILL.md` (+44/−8), the package README, `apm.yml` ×2, `marketplace.json`, the research README, and two case directories.

## Item 1: Comments consistent with the code and with each other

Analogue used: the statements one changed file makes about another, and the skill's own rules against each other.

**Finding 1 (Substantive).** `cases/pgjdbc-4367-breaks/README.md:7` and `cases/pgjdbc-4392-no-break/README.md:6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility", in "SKILL.md §2".
- The text that shipped is "unless the next release from the target branch is a major" (`SKILL.md:234`).
- The two conditions differ. A branch that "promises compatibility" is not the same as "not a major". The version file is the criterion in the shipped text, and the prompt gives only a version file.
- A reader would test the cases against a rule the skill does not contain.
- Request: quote the shipped sentence in both READMEs.

**Finding 2 (Substantive).** `cases/pgjdbc-4367-breaks/README.md:33-34` says "Haiku ran at effort `high`; Opus at the session's default". The commit message says "on Opus and Haiku (effort high)". Both statements cannot be true. Request: make the commit message and the README agree on the Opus effort, or state it per run.

**Finding 3 (Substantive).** `SKILL.md:247-248` says "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does."
- "Decides" has two readings. One is that the trailer settles whether the next release is a major, so the breaks do not lead. The other is that the trailer is written regardless of what the description does.
- On a patch branch the first reading cancels the lead exactly where the rule exists. The change itself would make the next release a major, and the reviewer's decision is whether it may.
- Request: say which reading holds, for example "the trailer is written in every case and does not move the lead".

**Finding 4 (Substantive).** `§4 rule 5` (`SKILL.md:637-638`) still says "shape it as §2's commit body". Line 310, "Under §4 rule 5 the description is the commit body and takes the body's shape instead", is also unchanged.
- The new text (`:86-87`, `:257-260`, `:831`) says that under rule 5 "the lead stays". The result is a body that opens with its breaks and then the problem.
- The commit body's own slot order, "Problem" first, is untouched.
- An agent that follows rule 5 or line 310 writes the body problem-first. An agent that follows `:257` writes it breaks-first.
- Request: add the exception to rule 5 and to line 310, or word `:257` as an exception to them.

Everything else checked consistent:
- The slot-3 table cell, the checklist line at `:831` and the new "Breaks" line at `:849` agree with the new paragraphs.
- The §5 and §7 references resolve (§5 is trailers, §7 is "When to write nothing").
- `getUpdateCount()` returning `-1` matches the case prompt.
- The three version bumps (`SKILL` package `apm.yml`, root `apm.yml`, `marketplace.json`) all say 1.5.0.
- The skill-tree ids in the case directories match the committed trees: `47980534…` for the HEAD skill and `1f020ce5…` for the baseline at HEAD~1.
- The word counts in the 4367 table match `wc -w` for every row.
- The three-of-four count in the commit message follows from the table.

## Item 2: Claimed cases covered

Analogue used: the covering section, or the case run, for each claim. The commit message claims:

| Claim | Covered by |
| --- | --- |
| Break leads unless the next release is a major | `pgjdbc-4367-breaks` check 1, runs `opus/result.md`, `result-2.md`, `haiku/result.md`, `result-2.md` |
| Result-shape change (`-1`) is a break | check 2, same four runs, all pass |
| Extended failure (`grant insert`) is a break | check 3, passes in three of four runs. `opus/result-2.md` leaves it in Scope, and the README says so. |
| Fix that now succeeds is not a break | check 4 |
| Negative control grows no section | `pgjdbc-4392-no-break` checks 1 and 2, four runs |
| Commit body keeps problem first, breaks as the first `User-visible:` lines | No case. |
| "Where the next release is a major, the breaks stay first in slot 3" | No case. |
| "Where nothing says which release it is, the breaks lead" | No case. Both prompts give a version file. |
| "Where squash copies the description into the commit, the lead stays" | No case. |

**Finding 5 (Substantive).** Four of the claimed partitions have no run: the commit body, the major target, the unknown-release target, and the squash copy. These are branches of the rule that the commit message states, not incidental ones. The README does not say they are unexamined. Request: either add a run for each (the major target is one more prompt where `gradle.properties` says `43.0.0-SNAPSHOT`), or say in the commit message and the README that these are untested.

Command lines: the `git archive …` line in `pgjdbc-4367-breaks/README.md` is the only one added. It is a recipe, with no script or CI job that runs it, and its outcome is a file tree that can be checked. No finding.

Reverse reading: every hunk is claimed by the message. The research README entries and the package README bullet follow the rule. No stray bumps.

## Item 3: Boundaries, partitions, and the negative control

Analogue used: the genres and situations the change claims, and the negative control as a table of the added instructions.

- The negative control is present (`pgjdbc-4392-no-break`, four runs). The with-rule versus baseline arms exist for 4367 only. The 4392 control has no baseline, so it shows that nothing grew but not that the rule did not cause growth. The README compares against the draft's word count (209 against 241 to 256), and that is the only control.
- The rule has no pre-existing state to meet.

**Added instructions: 5.** Rows follow, then the `Not findings:` line.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:249` "Where nothing says which release it is, the breaks lead" | a continuously deployed internal service with no versions | a `Breaking changes` lead plus a "short paragraph that says which code breaks" before the Why | "only where the repository publishes versioned releases" |

Not findings: `:241` (a fix is not a break, ended by its own definition), `:255` (a change with no break grows no section), `:236` (code that works on the released version, which ends the rule where nothing is released).

## Item 3a: Level, placement, and the environment

Analogue used: file placement, the layout of sibling cases, and the registration entries.

- The layout matches `cases/` conventions. The package README, `apm.yml`, root `apm.yml` and `marketplace.json` entries are consistent.
- `skill-tree` files hold tree ids that resolve at HEAD.
- The rule is stated at the level the skill uses, and nothing in it reads as generic tutorial text.
- The research README's directory listing gains the `cases/` line. None.

## Item 4: Names by content, not by position

Analogue used: headings, cross-references and case names.

- Case names are by content (`pgjdbc-4367-breaks`, `-no-break`). The `result-2.md` suffix is an ordinal, but the README names each file in its table. Taste, and not requested.
- `§4 rule 5` and `§2` references name a rule or a section by number. They are existing house style in this file.

None otherwise.

## Item 5: The failure report

Analogue used: whether each check says what to look at and what failure looks like.

- The checks in `pgjdbc-4367-breaks/README.md` each say what to look for: "before the Why slot", "`getUpdateCount()` at `-1`". The results table names the failing check per run.
- A rule check is attached to the weaker property in one place. Check 1 ("opens … before the Why slot") passes `opus/result.md`, but check 5 ("No break line is repeated") only compares text and does not apply to the lead sentence.
- The rule has no checklist beyond `SKILL.md:849`, which does reach it.

None.

## Item 6: What the writer says it verified

The change carries evidence that the rule can fail and can pass.
- Baseline runs on `origin/main` fail checks 1 to 3. Runs with the rule pass, with the stated exception of `opus/result-2.md`.
- The negative control passes in four runs.
- Earlier drafts of the rule were run on Opus, but the README says they are "summarized, not stored", so those runs cannot be inspected.

The evidence is thin. The baseline is one run per model against two with the rule. Opus passes check 3 in one of two runs, and the README says so rather than claiming the rule always works.

## Item 7: Siblings of the change

Analogue used: the places that enumerate or route to the skill.

- The package README bullet, the marketplace entry, both `apm.yml` files and the research README are updated.
- The marketplace and `apm.yml` descriptions are unchanged ("Structure and content rules for commit messages, pull request descriptions, and changelog entries"). They still describe the scope, so they need no change.
- Prose that counted the slots: "Six slots", "Five slots", "four claims" are unchanged and still true.
- Other statements of the same fact: `:226` "Breaks come first" now lives beside a rule that puts breaks ahead of slot 1. It is not contradictory, since it is about order within slot 3. Rule 5 and line 310 are the siblings missed (finding 4).
- Case names `pgjdbc-4367-breaks` and `-4392-no-break` are listed in the research README. None missing.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "promises compatibility", but the shipped rule says "unless … is a major" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`; `cases/pgjdbc-4392-no-break/README.md:6` | 1 |
| Opus effort: commit message says `high`, README says session default | Substantive | `cases/pgjdbc-4367-breaks/README.md:33` | 1 |
| "The trailer decides" has two readings, one of which cancels the lead where it matters | Substantive | `SKILL.md:247` | 1 |
| §4 rule 5 and line 310 still say the description takes the commit body's shape, against "the lead stays" | Substantive | `SKILL.md:637`, `:310`, `:257-260` | 1 |
| Commit body, major target, unknown-release and squash-copy partitions have no run and are not named as untested | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md` | 2 |
| "Nothing says which release it is" leads with breaks for a service with no versioned releases | Substantive | `SKILL.md:249` | 3 |

Not done: the drift script parses no Markdown and printed nothing, so every comment was read by hand. I could not fetch pgjdbc/pgjdbc#4367, since there is no network. I took the maintainer's rewrite as the prompt and README describe it.
