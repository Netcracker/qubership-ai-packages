# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

There was no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill (`change-description-authoring` SKILL.md), its package README, the version manifests, and a research directory with two regression cases. I used the §2a analogues and loaded `english-developer-style` and `apm-authoring` (from this repository) in place of the doc-comment skill. I did not run the drift script because it has no members to parse. There is no previous report.

## Item 1: comments consistent with the code and with each other
Analogue: statements one file makes about another.

- **Stale rule quote.** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility" (`pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:6-7`). SKILL.md has no such sentence. It says "…unless the next release from the target branch is a major" (`SKILL.md:234`). The quote is from a draft that was reworded after review (`4367 README:51`).
- **Baseline mislabeled.** `4367 README:33` and the commit message say the baseline runs used `origin/main`. Both `*/baseline/skill-tree` files hold `1f020ce…`, which is the skill tree at the parent `4f69810`. It is not the tree at `8c8eb00`, the last commit that carries a PR number (`2670ea8…`). Without network I can't see `origin/main`, so this is plausible rather than certain. It still holds unless `origin/main` already contains the four unnumbered `change-description-authoring` commits.
- **Two rules disagree on the same input.** The Scope rule (`SKILL.md:487-492`) says that where "whether a compatibility break is intended" is open, you "keep it in the Scope slot as a question". The new rule (`:238-240`) says an extended failure "goes with the breaks, not in the Scope slot". The `grant insert` input is exactly this case: the draft defends not narrowing the rule. `opus/result-2.md` followed the Scope reading.
- **`:247-248` reads two ways.** "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides." It doesn't say what it decides. One reading: the trailer makes the next release a major, so the breaks stay in slot 3. The other: the trailer only replaces the version file as the source of the answer. A release-please repository on 1.4.x with a break gets opposite outputs from the two readings.
- **Checked and consistent:** `:86` matches `:257-260`; §4 rule 5 (`:637`) and `:310` defer to §2's commit body, which now carries the exception; the package README bullet matches the rule.
- **Narration:** none in the skill text.

## Item 2: claimed cases covered
Analogue: the sections and trial runs that handle each claim.

| Claimed case (commit message) | Where it is covered |
| --- | --- |
| Next release is not a major (read from the version file), so the breaks lead | `pgjdbc-4367-breaks`, check 1, four runs |
| Read from the milestone or the branch name | none |
| Next release is a major, so no lead | **none** |
| Nothing says which release, so the breaks lead | none |
| A result-shape change is a break | 4367, check 2 |
| A failure extended to inputs that worked before is a break | 4367, check 3 (3 of 4 runs) |
| Removed option, changed default, changed error code | none (definitional examples) |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | **none**: no case writes a commit body |
| Where squash copies the description into the commit, the lead stays | **none**: the case's merge model (`squash` with commit details) does not fire §4 rule 5 |
| A change with no break grows no section | `pgjdbc-4392-no-break`, checks 1–2 |

**Commands.** `4367 README:29-30` says the skill was copied out "with `git archive <rev> agent-packages/…`". No script runs this, so the coverage is `none`. `git archive` writes a tar stream to stdout and copies nothing out without `| tar -x -C <dir>`. Sibling research directories ship a `run-case.sh` for this step.

**Unclaimed hunks.** The version bump 1.4.0→1.5.0 in `.claude-plugin/marketplace.json`, `agent-packages/change-description-authoring/apm.yml`, and `apm.yml` has no sentence in the message. The earlier commits in this series carry one ("Version 1.2.0 to 1.3.0.").

## Item 3: boundaries, partitions, and the negative control
- The partitions the rule claims are: patch or minor, major, unknown, the commit body, and the description used as the body under §4 rule 5. Only the patch arm has evidence.
- `pgjdbc-4392-no-break` controls a different condition (whether a break exists). The control for the rule's own condition is a change with breaks on a branch whose next release is a major, and it is missing. The suite tests only the firing corner of "unless … is a major".
- No pre-existing state applies: the package is a file set with nothing persisted.

Added instructions: 4.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:244` "Read the next release from the target branch: its version file" | Version file equal to the latest tag, as in the case prompt (`42.7.14`), but at `43.0.0` | Reads "next is a major" and keeps the breaks in slot 3 of a patch PR | "where the version file names a tagged release, the next release follows it" |

Not findings: `:235`, `:241`, `:255`, `:258`.

## Item 3a: level, placement, and the environment
- **Gates run offline.** `make check` passes ("Version alignment OK … change-description-authoring 1.5.0 [matches]"). `scripts/check-skill-descriptions.py` passes. The result and prompt files fall under `FILTER_REGEX_EXCLUDE`.
- **Line length.** `pgjdbc-4367-breaks/README.md:17` is 121 characters, which is linted, and the repository's `markdown-line-length-120` rule wraps at 120. The markdownlint config lives in `netcracker/.github`, which I couldn't read offline.
- **Placement.** The break definition and "breaks as the first `User-visible:` lines" are stated only under *Pull request description* (`:234-260`). The *Commit body* section (`:74-172`), including the slot 4 row at `:83`, never says breaks come first and never says what a break is. An agent writing a commit message reads that section.
- **Layout (taste).** Model directories are `opus`/`haiku`, while sibling cases use model ids (`claude-opus-5-5`), and there is no `run-case.sh`.
- No generic-tutorial sentences.

## Item 4: names by content, not by position
- `SKILL.md:198` uses "(below)" for a rule 36 lines later that has a bold name it could cite instead (taste).
- The checks are numbered but each also has a name ("Lead (1)"), so that is fine. No other cases.

## Item 5: the failure report
Analogue: the detection for each rule.

The checklist line `:849-852` asks whether the description opens with the break lines. It does not ask whether a failure extended to inputs that worked before is among them rather than in Scope. `opus/result-2.md`, which fails README check 3, passes the checklist as written, so this detection checks a weaker property than the rule states.

## Item 6: what the writer says it verified
- **Bad case and exemplar.** The baselines fail checks 1–3, and the runs with the rule pass, including one recorded Opus failure on check 3. All rule runs are on the committed tree (`4798053…` = `HEAD:…/change-description-authoring`). Word counts match the files (`wc -w`).
- **Noise input.** `pgjdbc-4392-no-break` checks that no section appears. Its growth is measured only against the author's draft (209 → 241–256 words). It has no baseline run, so it can't show that the rule didn't grow the output.

## Item 7: siblings of the change
- Package README, research README `cases/` row, and manifests are updated.
- `english-developer-style` defers ordering to this skill, so it is fine.
- Set counts: `:192` "Six slots, in order" is still six, but the order now has an exception that only the table cell at `:198` names (taste).
- The commit-body sibling of the rule is missing; it is filed under item 3a.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The case READMEs quote a rule sentence that SKILL.md doesn't contain | substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote `SKILL.md:234` as committed |
| The baseline is called `origin/main`, but its tree is the parent commit's | substantive (plausible) | `cases/pgjdbc-4367-breaks/README.md:33`; commit message | Say "the parent commit 4f69810", or rerun on `origin/main` |
| Scope rule keeps an open-intent break in Scope; the new rule moves it out | substantive | `SKILL.md:489-492` vs `:238-240` | In the Scope rule: "the break line itself leads (§2); Scope keeps only the question" |
| "the trailer decides" reads two ways | substantive | `SKILL.md:247-248` | State the outcome, e.g. "the trailer makes the next release a major, so the breaks stay first in slot 3" |
| The major-release arm (the rule's own negative control) has no case; unknown release, commit body, and §4 rule 5 have none either | substantive | `research/change-description-authoring/cases/` | Add the 4367 input with a major next release, or state the gap in the README |
| The version bump in three files has no sentence in the message | substantive | `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, `.claude-plugin/marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." |
| The `git archive` command copies nothing out, and nothing runs it | substantive | `cases/pgjdbc-4367-breaks/README.md:29-30` | Give the full form (`… \| tar -x -C <dir>`) or add a runner script |
| Line over 120 characters in a linted file | substantive | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap |
| The checklist doesn't detect an extended failure left in Scope | substantive | `SKILL.md:849-852` | Add "Is a failure extended to inputs that worked before among the break lines, not in Scope?" |
| The commit-body section lacks "breaks first" and the break definition | substantive | `SKILL.md:83` | Add "breaks first (§2, pull request description)" to slot 4 |
| The control case has no baseline, so growth can't be attributed to the rule | substantive | `cases/pgjdbc-4392-no-break/README.md:22-25` | Add baseline runs, or compare to them |
| Version file equal to a tagged `X.0.0` misreads as a major | substantive | `SKILL.md:244` | See the item 3 row |
| "(below)" instead of the rule's name | taste | `SKILL.md:198` | Cite "A break leads the description" |
| "Six slots, in order" now has an unstated exception | taste | `SKILL.md:192` | Add "(breaks may lead, below)" |
| Model directories and the missing runner differ from sibling cases | taste | `cases/pgjdbc-4367-breaks/` | Use model-id directory names |

This review did not run any trial, did not fetch the cited pgjdbc#4367 maintainer comment or `origin/main` (no network), and did not run super-linter. It also did not do a pass over the prose for style alone. The `apm-authoring` rule *Fix a bad output where the rule stops* that the form cites does not exist in this repository's `apm-authoring`.
