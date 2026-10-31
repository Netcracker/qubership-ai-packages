# Final review: `4f69810..86028c3`, one commit

There was no separate task statement, so the claimed cases come only from the commit message, as the skill allows for a subagent. Nothing in the change is code. It touches a skill (`SKILL.md`), the package README, version manifests, and research case files, so every item below uses the §2a analogues. I did not run the drift script because there are no members for it to parse. I loaded `apm-authoring` and `english-developer-style` from the skills directory I was given. There is no previous report, so there is no table of earlier findings.

Paths are short: `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, and `cases/` means `research/change-description-authoring/cases/`.

## Item 1: comments consistent with the code and with each other

Analogue used: the statements that one file makes about another, and rules within the skill that contradict each other.

**1a. The case READMEs quote the rule under the wrong name (substantive).** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` both name the rule under test as "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` says "…unless the next release from the target branch is a major". Nothing in the repository contains the quoted wording. A reader who searches `SKILL.md` for the quote finds nothing. The two conditions also differ: "promises compatibility" is not the same test as "is not a major", and the committed rule makes the breaks lead when the release is unknown. **Request:** quote the committed heading in both READMEs.

**1b. The new rule conflicts with the existing Scope rule on the same input (substantive).** `SKILL.md:239-241` says that a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". `SKILL.md:488-491`, which this change leaves untouched, says that where only a maintainer can say "whether a compatibility break is intended, keep it in the Scope slot as a question". The `grant insert` case meets both rules: it is an extended failure, and the draft explains it as a choice the author made, kept because `explain insert …` relies on the same rule. `opus/result-2.md:35` followed the older rule and kept it in Scope, which is the one check that failed in the case table. **Request:** add a clause to `:239-241` saying that the break line goes with the breaks, and only an open question about whether the break is intended stays in Scope, citing `:488`.

**1c. Leading breaks in a squashed commit body read two ways (substantive).** `SKILL.md:257-260` keeps the breaks as the first `User-visible:` lines of the commit body, "because the label is what R4 and R5 search for". Then, where §4 rule 5 copies the description into the body, "the lead stays… that body opens with its breaks and then its problem". `SKILL.md:252-253` puts the lead under a `Breaking changes` heading where the description has headings, while §4 rule 5 (`:637-638`) shapes such a body as a §2 commit body. One reading puts the leading breaks under `User-visible:`, which splits the outcomes into two `User-visible:` paragraphs. The other puts them under `Breaking changes` or no label at all, and then the `User-visible:` search the paragraph just justified no longer finds them. **Request:** name the label that the leading break lines carry in that body. Item 3 covers the missing evidence for this case.

Apart from these, the other cross-references hold:
- `SKILL.md:86-87` and the checklist line `:831` match `:257-260`.
- The table cell at `:198` matches `:234-255`.
- The trailer reference in `:246` matches the `BREAKING CHANGE:` row of §5 (`:706`).
- The cross-reference to §7 at `:255` matches `:787`.
- The package README bullet matches the rule.
- Every `skill-tree` file matches its run: `4798053…` equals `git rev-parse HEAD:<skill dir>`, and `1f020ce…` equals the base tree.
- The commit message's counts match the results table.

## Item 2: claimed cases covered

Analogue used: each claim in the commit message, set against the case and check that cover it.

| Claimed case (commit message) | Covered by |
| --- | --- |
| The breaks lead when the next release is not a major, read from the version file | `pgjdbc-4367-breaks` check 1. All four runs pass, and both baselines fail. |
| A result-shape change is a break | `pgjdbc-4367-breaks` check 2 |
| A failure extended to inputs that worked before is a break | `pgjdbc-4367-breaks` check 3. 3 of 4 runs pass, as the message says. |
| A new failure is a break | The two `**Breaks:**` lines in the draft, carried over in every run |
| A removed option, a changed default, or a changed error code is a break | No case. These are definition list items, not separate claims of evidence, so no finding. |
| A change with no break grows no section | `pgjdbc-4392-no-break` checks 1 and 2 |
| No lead when the next release is a major | **No case.** See item 3. |
| Breaks lead when nothing says which release it is | **No case.** See item 3. |
| The release is read from a milestone or a branch name | No case. Both prompts give `gradle.properties`. |
| The commit body keeps the problem first, with the breaks as the first `User-visible:` lines | **No case.** See item 3. |
| Where squash copies the description into the commit, the lead stays | **No case.** Both prompts give `squash 3 plain 37` with bullet bodies, so §4 rule 5 does not apply. See item 3. |

- **Commands:** the only command the change adds is the `git archive <rev> …` recipe at `cases/pgjdbc-4367-breaks/README.md:31-32`. It describes how the cases were produced, nothing runs it, and its outcome depends on no configuration this change creates. No finding.
- **Hunks with no claim:** the version goes from 1.4.0 to 1.5.0 in three files. That is the contract bump `apm-authoring` *Versions* asks for when a rule is added, so the claimed change needs it. The index line in the research README describes the new `cases/` directory. No finding.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the situations the change claims count as partitions, and `pgjdbc-4392-no-break` is the negative control.

**3a. Three claimed partitions have no evidence (substantive).** The trial covers one partition: a non-major target, read from a version file, with the description staying on the platform. It also covers the no-break control. These partitions have no run:
- A target whose next release is a major. The rule's "unless" clause is untested, and it is the arm that keeps the breaks inside slot 3.
- A target where nothing says which release it is.
- A repository where §4 rule 5 copies the description into the commit body. This is also where the ambiguity in 1c would show.

The commit message claims all three. **Request:** at minimum, a variant of `pgjdbc-4367-breaks/prompt.md` with `pgjdbc.version=43.0.0-SNAPSHOT` (expected: no lead, breaks first in slot 3), and one with a squash "title and description" history (expected: the body's label settled by 1c). Otherwise, the commit message should claim only the partition the trial ran.

**Added instructions: 2, no rows.**

Not findings: `:235`, `:255`.

## Item 3a: level, placement, and the environment

Analogue used: which file each rule lives in, whether the layout matches its siblings, and the repository's own gate.

None found. The rule sits in §2, *Pull request description*, beside slot 3, and its checklist line sits in §8. The cases sit under `research/change-description-authoring/`, the README indexes them, and the result and prompt files match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`. I ran `make check` offline and it passed (exit 0); the version entries are aligned and `marketplace.json` is in sync. The facts the rule encodes are not generic tutorial material: R1's ship-or-not decision in a patch release, and the sources the release is read from.

## Item 4: names by content, not by position

Analogue used: the change's own headings, cross-references, and case names.

None found. Case names describe their content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). Checks are referred to by name and number together ("Lead (1)"). Cross-references use section and rule numbers, which is the skill's own convention.

## Item 5: the failure report

Analogue used: whether each rule's detection is reached by the checklist, and whether it detects that rule.

None found. The new checklist line "Breaks" (`SKILL.md:849-852`) reaches the rule. It asks whether the description opens with the break lines and whether no empty heading is written, which detects the rule itself rather than a weaker property. The Problem line (`:831`) carries the exception for the commit body.

## Item 6: what the writer says it verified

Analogue used: an exemplar the rule passes and a bad case it fails, both named in the change.

The evidence is stated. The baselines on `origin/main` (tree `1f020ce…`) fail checks 1 to 3, and the runs on the committed tree pass them, with the one stated exception. Checks 4 to 6 guard against the rule costing other facts, and the word counts are recorded. For "the output did not grow where the item is noise", the control `pgjdbc-4392-no-break` records 241 to 256 words against a 209-word draft and no compatibility sentence. The README admits the rule was reworded after review and re-run only on the committed version.

## Item 7: siblings of the change

Analogue used: the places that enumerate or route to the artifact.

None found. `marketplace.json`, the root `apm.yml`, and the package `apm.yml` carry the same version and an unchanged `description`. The description still covers the widened scope, since the rule concerns what a pull request description says and in what order. The package README lists the new rule. The other places that name `change-description-authoring` route to it by artifact type, not by rule, so none needs a change. The changelog section (`SKILL.md:543`, "breaking changes … sorted first within their category") is a separate artifact, and the new rule leaves it alone.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Both case READMEs quote the rule under a wording ("promises compatibility") that the committed heading does not use | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | 1 |
| "Not in the Scope slot" conflicts with the unchanged rule that keeps an intended-break question in Scope | Substantive | `SKILL.md:239`, `SKILL.md:488` | 1 |
| The label for the leading breaks in a body copied by §4 rule 5 reads two ways | Substantive | `SKILL.md:257` | 1 |
| The major-release, unknown-release, and §4 rule 5 partitions are claimed with no run | Substantive | `cases/` | 3 |

I made no changes to any file.
