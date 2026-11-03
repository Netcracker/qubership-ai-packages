# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

**Inputs.** I had no task statement, so the claimed cases in item 2 come from the commit message alone, plus the two case READMEs. No previous report exists for this change. The change has no code: it touches a skill (`SKILL.md`), a package README, three version fields, and a research directory. I used the §2a analogues and loaded `english-developer-style` from the given skills directory, plus `apm-authoring` from the repository as the authoring skill for a skill package. I did not load `test-authoring`, because the change has no tests. I did not run the drift script either: it parses code members, and this diff is only Markdown, YAML, and JSON.

## Item 1: comments consistent with the code and with each other

*Analogue: statements one file makes about another file, and statements within `SKILL.md`.*

- **Both case READMEs quote a rule wording that is not in the skill.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". `git grep 'promises compat'` finds that wording only in these two READMEs. The committed rule at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The skill-tree ids show the runs used the committed tree, so the quote is just stale. A reader looking for the rule under test searches for a sentence that doesn't exist, and gets a different condition ("promises compatibility" versus "is not a major").
- **The checklist's Caller item still puts breaks inside "User-visible changes".** `SKILL.md:845` asks whether the description carries "one line per distinct outcome under 'User-visible changes', breaks first". Under the new rule (`:252-254`), breaks leave slot 3 and lead the description unless the next release is a major. The new Breaks item (`:849`) asks the opposite of `:845` for the same input. A reviewer working through the checklist gets two answers.
- **The Scope rule and the new rule disagree about a break whose intent is open.** `SKILL.md:488-492` says that where only a maintainer can decide "whether a compatibility break is intended", the question stays in the Scope slot. `:239-240` says an extended failure "goes with the breaks, not in the Scope slot". The `grant insert` case is exactly such an input: the author kept the rule on purpose because `explain insert` relies on it. The text doesn't say whether the break line leads and the question of intent stays in Scope, or whether everything moves.
- **Two readings of "the trailer decides" (`:247-248`).** It can mean that a `BREAKING CHANGE:` trailer makes the next release a major. Since the same sentence says the trailer "is written whatever the description does", breaks would then never lead in a release-please or semantic-release repository. It can also mean that the trailer settles the question in place of the version file. These readings give opposite outputs for the same repository, and the commit message doesn't say which is intended.
- No sentence narrates the change ("now", "no longer") outside of descriptions of observed behavior. The `§4 rule 5`, `§5`, and `§7` cross-references all resolve to the sections they name.

## Item 2: claimed cases covered

*Analogue: the section that handles each claimed case, and a case or run as its test.*

| Claimed case (commit message) | Section | Evidence |
| --- | --- | --- |
| Breaks lead when the next release is not a major (version file) | `:234-255` | `pgjdbc-4367-breaks`, checks 1-3, 4 runs |
| Next release read from the **milestone** or the **branch name** | `:244-246` | none |
| Breaks lead when **nothing says** which release it is | `:248-250` | none |
| Next release **is a major**, so breaks stay first in slot 3 | `:254-255` | none (this is the condition's control, see item 3) |
| A break includes a result-shape change | `:235-237` | 4367, check 2 |
| A break includes a failure extended to inputs that worked before | `:238-240` | 4367, check 3 (3 of 4) |
| A break includes a removed option, a changed default, or a changed error code | `:237-238` | none (definitional; taste) |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | `:257-258` | none |
| Under squash with "title and description", the lead stays | `:258-260` | none |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`, 4 runs |

**Commands.** No changed file tells a reader to run a command. The `git archive <rev> …` line in `4367/README.md:28-29` describes how the cases were run, and no script in the repository runs it, so it is `none`. Its outcome depends only on `<rev>`, and the recorded `skill-tree` ids (`4798053…` for HEAD, `1f020ce…` for the base) match `git rev-parse <rev>:<skill dir>`.

**Hunks the message doesn't claim.** Three hunks move the version from 1.4.0 to 1.5.0 (`apm.yml`, `agent-packages/change-description-authoring/apm.yml`, `.claude-plugin/marketplace.json`), and no sentence of the message claims them. The earlier commits in this series state their version change ("Version 1.2.0 to 1.3.0."). Every other hunk belongs to a sentence of the message.

**The message disagrees with the README on effort.** The message says "on Opus and Haiku (effort high)". `4367/README.md:33` says "Opus at the session's default". As written, the message says Opus ran at high effort.

## Item 3: boundaries, partitions, and the negative control

*Analogue: the claimed situations as partitions, the no-break case as the control, and the table of added instructions.*

- The rule's condition has three branches: not a major, a major, and unknown. Only "not a major, read from the version file" has evidence. "The next release is a major", the branch where the rule must **not** fire although a break exists, has no case. `pgjdbc-4392-no-break` controls the *no break* condition, not the *major release* condition. The "unknown" branch and the commit-body branches (`:257-260`) also have no evidence.
- The control case has no baseline run, so nobody checked that the rule left the no-break output unchanged (item 6).
- Pre-existing state, values users already pass, replaced mechanisms, and limits: none apply. The change is prose plus a version bump, and the gate (item 3a) shows the version fields stay aligned.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:252` "The description then opens with slot 3's break lines" | a repository template with its own "Breaking changes" section lower down | moves the template section to the top, or writes it twice; `:302` says to use the template | "where the template has a breaking-changes section, that section leads" |
| `:258-260` "Where §4 rule 5 makes the description the commit body, the lead stays" | a squash with "title and description", a patch release, one break | a body that opens with unlabeled break lines; grepping `User-visible:` misses the break | "the lead's lines carry the `User-visible:` label" |
| `:234` "A break leads the description…" | a change whose whole purpose is the break (removing a deprecated option) in a minor release | a break line, then a Why that says the same removal again | "where the break is the change itself, the Why opens with it" |

Not findings: `:241` "a failure that now succeeds is a fix", `:255` "A change with no break has", `:254` "Where the next release is a major", `:248` "Where nothing says which release".

Inputs I left out of the table: a 0.x project under semver, where a minor release may break, is a kind of project the artifact never mentions, so it is taste. The trailer input is covered by the ambiguity finding in item 1.

## Item 3a: level, placement, and the environment

*Analogue: where each rule lives, the layout, and the registration gate.*

- The rule sits in §2 next to the slot-3 rules it amends. The checklist line and the package README bullet are added in the matching places, and the cases go under `research/<package>/cases/`.
- I ran `apm pack --check-versions --check-clean --dry-run` offline (the `make check` gate). It printed "Version alignment OK" and "Marketplace working tree clean", exit 0.
- `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` excludes `prompt.md` and `result*.md` under `research/` and still lints the case `README.md` files. `4367/README.md:17` is 121 characters, while the repository wraps Markdown at 120 (`markdown-line-length-120`). I couldn't confirm offline whether markdownlint enforces MD013, so this is taste.
- No added sentence is generic tutorial material. Each one is specific to this skill's slot model.

## Item 4: names by content, not by position

- `SKILL.md:198`, the table cell says "ahead of slot 1 unless the next release is a major (below)". "(below)" could instead name the rule by its bold heading. This is taste, because the target is a few lines further on in the same section.
- The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the check names ("Lead", "Result shape is a break") describe their content. "Checks 1 to 3" and "4 to 6" refer to numbered checks that also carry those names. None otherwise.

## Item 5: the failure report

*Analogue: whether the checklist reaches each rule, and whether each detection checks the rule rather than a weaker property.*

- The new Breaks checklist item (`:849-852`) asks whether the description "open[s] with the break lines". It doesn't ask whether a failure extended to inputs that worked before is among them rather than in Scope. That is exactly the miss the case measured (one Opus run of four left `grant insert` in Scope). A reviewer who doesn't count that line as a break passes the check, so the detection is weaker than the rule at `:238-240`.
- The commit-body half of the rule (`:257-258`) is reached only through the Caller item (`:845`), which conflicts with the new rule (item 1).
- The case's checks 4-6 guard against the rule *losing* facts but not against it *adding* them. `opus/result.md` adds a remedy to each break ("Call `execute()` and read each result with `getMoreResults()` instead", "Execute such a statement without generated keys") that the draft doesn't carry, although `prompt.md` says "add none that it does not carry". The README counts these sentences as "growth" without saying they are facts the input lacks.

## Item 6: what the writer says it verified

- **Red/green:** this is stated and holds up. The baselines on the base tree (`1f020ce…`) fail checks 1-3 on both models, and the runs on HEAD's tree (`4798053…`) pass them, except that `opus/result-2.md` fails check 3. I re-read all six 4367 results against the README table and agree with it; the word counts match `wc -w`.
- **The rule was rewritten after review**, and only the committed version was run twice per model. The README says so.
- **Noise input:** `pgjdbc-4392-no-break` shows the lead and heading don't appear. But it has no baseline run, so "did not grow" is unmeasured. The README compares 241-256 words to the 209-word draft, not to output from the base skill.

## Item 7: siblings of the change

- **Places that list or route to the skill:** the package README gained a bullet. The marketplace and `apm.yml` descriptions don't list rules, so they need nothing. The instruction trigger's scope is unchanged. The research README gained the `cases/` row and a paragraph.
- **Other skills:** `english-*-developer-style/SKILL.md:570` hands "where a breaking change is marked" to this skill, which is consistent. The Russian examples have a "Breaking changes" block for a changelog, a different artifact.
- **In-file siblings:**
  - Checklist `:845` and Scope `:490` conflict with the new rule (item 1).
  - §4 rule 5 (`:638`, "shape it as §2's commit body") doesn't mention that the lead stays. The exception is stated in §2 (`:86`, `:258-260`), so this is taste.
  - The changelog's own "sorted first within their category" rule (`:543`) is a different artifact and is consistent.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote a rule wording ("promises compatibility") that is not in the skill | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote `SKILL.md:234` as committed |
| The checklist's Caller item still says breaks go first under "User-visible changes" | Substantive | `SKILL.md:845` | "breaks first, or ahead of the Why slot where §2 says they lead" |
| The Scope rule keeps a break of open intent in Scope; the new rule moves it out | Substantive | `SKILL.md:490` vs `:239-240` | One clause: the break line leads, and the question of intent stays in Scope |
| "The trailer decides" can mean that breaks never lead under release-please | Substantive | `SKILL.md:247-248` | Say which way the trailer decides |
| No case for "the next release is a major" (the condition's control), "unknown", the milestone or branch name, or the commit-body order | Substantive | `research/change-description-authoring/cases/` | A case on a major-release target where the breaks stay in slot 3, or narrow the commit message's claim |
| The no-break control has no baseline, so "did not grow" is unmeasured | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs on `1f020ce…`, with their word counts |
| A repository template with its own breaking-changes section conflicts with the lead | Substantive | `SKILL.md:252` vs `:302` | The clause in the instruction table |
| A body under §4 rule 5 opens with unlabeled break lines that a `User-visible:` grep misses | Substantive | `SKILL.md:258-260` | The clause in the instruction table |
| The Breaks checklist item doesn't check extended failures, the measured miss | Substantive | `SKILL.md:849-852` | Add "and is a failure extended to inputs that worked before among them, not in Scope?" |
| Remedies the input doesn't carry are recorded as "growth", with no check for them | Substantive | `cases/pgjdbc-4367-breaks/README.md:52-53` | Say that the added remedies are not in the draft, or add a check for them |
| The commit message says "(effort high)" for both models; the README says Opus ran at the default | Substantive | commit message; `4367/README.md:33` | Put "(Haiku at effort high)" in the message |
| The version bump 1.4.0 → 1.5.0 is unclaimed | Substantive | `apm.yml`, package `apm.yml`, `marketplace.json` | Add "Version 1.4.0 to 1.5.0." as the earlier commits in the series do |
| When the break is the change's whole purpose, the lead repeats the Why | Taste | `SKILL.md:234` | "where the break is the change itself, the Why opens with it" |
| "(below)" refers by position | Taste | `SKILL.md:198` | Name the rule by its heading |
| §4 rule 5 doesn't mention the lead exception | Taste | `SKILL.md:638` | A cross-reference to §2 |
| A line is 121 characters, over the 120 wrap | Taste | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap |

I did not re-run any model, did not check the pgjdbc facts or links against the network, did not run markdownlint or super-linter, and did not do a style pass over the prose.
