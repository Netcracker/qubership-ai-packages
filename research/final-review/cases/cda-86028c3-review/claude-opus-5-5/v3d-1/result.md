# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

There was no task statement, so the claimed cases come from the commit message and the two case READMEs. The change has no code: it is a skill (`change-description-authoring` SKILL.md), its package README, version bumps, and two research cases. Every item below uses the §2a analogue. I didn't run the drift script because there are no members for it to parse. I loaded `english-developer-style` (the copy under the tmp `skills/` directory) and the repository's `apm-authoring`. No previous report exists.

## Item 1: comments consistent with the code and with each other
*Analogue used: the statements one file makes about another file.*

- **The case READMEs quote a rule that isn't in the skill.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` cite the rule as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". The `skill-tree` files hold `4798053…`, which is HEAD's tree, so the runs used the committed wording and the quote comes from an earlier draft. The two conditions also differ where the release is unknown: "promises compatibility" would not lead, "is a major" leads.
- **"the trailer decides" (SKILL.md:247-248) doesn't say what it decides.** A reader can take it as "the trailer makes the breaks lead" or as "the trailer makes the next release a major, so the breaks stay in slot 3". The second reading is the intended one, given "it is written whatever the description does".
- **Under §4 rule 5, the lead loses its grep label.** SKILL.md:252-260 has the lead open "under a `Breaking changes` heading". It also says the label is what R4 and R5 search for, and that under rule 5 "that body opens with its breaks". But §2 (SKILL.md:205-207) and rule 5 make that body take the commit body's shape, where outcomes sit under `User-visible:`. Nothing says whether the leading break lines in such a body carry `User-visible:`. A writer following the text can produce a squash body whose breaks R4/R5 can't find by the label.
- SKILL.md:86-89 (slot 1) and the checklist line at :831-832 agree with :258-260. No `now`/`no longer` narration of the change was found.

## Item 2: claimed cases covered
*Analogue used: the case or section that covers each claim.*

| Claimed case | Covered by |
| --- | --- |
| Breaks lead when the next release is not a major (patch, read from `gradle.properties`) | `pgjdbc-4367-breaks`, check 1; 4/4 with the rule, 0/2 baseline (verified in the result files) |
| A result-shape change is a break | 4367 check 2 |
| A failure extended to inputs that worked before is a break, not Scope | 4367 check 3; 3/4 runs (`opus/result-2.md` puts it in Scope, as the README says) |
| A fix is not a break | 4367 check 4 |
| A change with no break grows no section | `pgjdbc-4392-no-break`, 4/4 runs |
| Next release is a major → breaks stay first in slot 3 | **none** |
| Release unknown → breaks lead | **none** |
| A release tool's `BREAKING CHANGE:`/`!` decides | **none** |
| Commit body keeps the problem first, breaks as the first `User-visible:` lines | **none** (both prompts ask for the PR description only) |
| §4 rule 5 squash: the lead stays in the body | **none** (both prompts give a merge model where rule 5 does not apply) |
| Removed option, changed default, changed error code count as breaks | **none**; these are partitions of the definition, owed only as far as the message claims them |

- The change documents no runnable command lines; the case READMEs describe a `git archive <rev> …` setup only in prose. Nothing to list.
- Hunks against claims: the SKILL.md, package README, research README and case hunks are claimed. The `1.4.0 → 1.5.0` bumps in `apm.yml`, `agent-packages/change-description-authoring/apm.yml` and `.claude-plugin/marketplace.json` are claimed by no sentence. This follows the repository convention (`apm-authoring` *Versions*: bump on a contract change).

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the partitions are the release kinds and merge models the change claims; the control is 4392 plus the instruction table.*

- **Only one release partition was tried.** Both cases target a 42.7.x patch release. Three claimed partitions have no evidence: major release (no lead), unknown release (lead), and a release-tool trailer. The commit-body and rule-5 partitions, which this change rewrites (SKILL.md:86-89, :257-260), are also untested.
- **The negative control has no baseline arm.** 4392 ran only on the new skill (241–256 words against a 209-word draft). That shows no section was added, but not that the output didn't grow compared with the old skill.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Lead under a `Breaking changes` heading where the description has headings (SKILL.md:252-253) | A repository whose PR template has its own breaking-change field (e.g. "Does this PR introduce a breaking change?") | A second, untemplated `Breaking changes` heading above the template, repeating the field; this conflicts with SKILL.md:301-302, "use its headings" | none. Request: "…or in the template's own breaking-change field, first, where it has one" |
| Under rule 5 the lead stays in the commit body (SKILL.md:258-260) | A squash with "title and description" of a patch-release break | Break lines at the top of the body with no `User-visible:` label | none; filed under Item 1 |
| Breaks lead unless the next release is a major (SKILL.md:243-250) | A 0.x crate or package (`Cargo.toml` is one of the named sources), where a minor release may break by policy | A lead that is meant to settle "may it ship here?", a question the versioning policy already answers | none; the artifact doesn't address 0.x versions, so this is **taste** |

Not findings:
- A behavior added after the last release and then changed: ended by "code that works on the released version" (SKILL.md:235).
- A change with no break: ended by "A change with no break has neither the lead nor an empty heading (§7)".
- The R2 reader of a rule-5 body who meets the breaks before the problem: ended by "because the reviewer reads the description before it becomes a body".

## Item 3a: level, placement, and the environment
*Analogue used: file placement and the repository's gates.*

- The rule sits in §2 next to slot 3. The cases sit under `research/change-description-authoring/cases/`, and the research README index lists them. The result and prompt files match `FILTER_REGEX_EXCLUDE` (`results?[^/]*`, `prompt[^/]*`) in `.github/super-linter.env`; the case READMEs are linted.
- **`cases/pgjdbc-4367-breaks/README.md:17` is 121 characters.** The repository pins MD013 at 120 (the `markdown-line-length-120` package). I couldn't read the upstream `.markdownlint.json`, so whether the linter fails on it is unverified.
- I didn't run `make check`: it goes through `uvx`, which needs the network.
- No sentence reads as generic tutorial material.

## Item 4: names by content, not by position
*Analogue used: unchanged, applied to the change's headings, cross-references and case names.*

None. Case names are content-based (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). Checks are numbered, but each is also titled by content and the results table refers to them by title. Cross-references use `§4 rule 5` and `§7`, which are stable section anchors that already exist in the skill.

## Item 5: the failure report
*Analogue used: what each rule tells the reader to look at.*

- **The checklist doesn't reach the break definition.** The checklist line (SKILL.md:849-852) asks whether the description opens with the break lines. It doesn't ask whether a result-shape change or an extended failure was classified as a break, or whether anything was left in Scope. That classification is the part of the rule that failed in `opus/result-2.md`, and the commit message names its absence as the original defect. As written, a draft that leads with two breaks and leaves the third in Scope passes the checklist. Request: add "is every outcome that changes what working code gets, including a changed result shape and a failure extended to inputs that worked before, among the break lines, and none of them in Scope?"

## Item 6: what the writer says it verified
*Analogue used: an exemplar the rule passes and a bad case it fails, both named in the change.*

- Present: the baseline runs on the base tree (`1f020ce…`, which I confirmed is 4f69810's tree) fail checks 1–3. The runs on HEAD's tree pass, with one stated miss on check 3. The control passes 4/4. The README reports the word growth and the earlier rule drafts.
- Missing: the control's did-not-grow comparison against a baseline (see Item 3).
- Minor: both prompts give `pgjdbc.version=42.7.14` and say the latest tag is `REL42.7.14`. So the version file names an already-released version, and the input to the "read the next release" step contradicts itself (taste).

## Item 7: siblings of the change
*Analogue used: the places that list the members of the same set.*

- **The heading set at SKILL.md:300-301 omits `Breaking changes`.** It lists "`Why`, `What`, `User-visible changes`, `How to verify`, and `Scope` is one set that matches the slots", and doesn't include the heading the new rule introduces.
- SKILL.md:192, "Six slots, in order", is no longer literally true when slot 3's breaks move ahead of slot 1. The table row mentions this, so it's taste.
- The package README is updated. The marketplace and `apm.yml` descriptions need no change because the scope is unchanged. The changelog rule in §3 (SKILL.md:543) is about a different artifact and is consistent. `english-*-developer-style:570` defers the breaking-change question to this skill. The Russian style examples don't mention release kind; that's out of scope.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The case READMEs quote the rule as "promises compatibility", which is not the committed wording and differs for an unknown release | Substantive | `research/…/cases/pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:6-7` | Quote SKILL.md:234 as committed |
| Under rule 5 the lead has no stated `User-visible:` label, though the same paragraph says R4/R5 search for it | Substantive | SKILL.md:252-260 | State that in a rule-5 body the leading break lines go under `User-visible:` (or say what replaces the label) |
| The `Breaking changes` heading conflicts with "use the template's headings" | Substantive | SKILL.md:252-253 vs :301-302 | Add the clause in the Item 3 table |
| "the trailer decides" is ambiguous | Substantive | SKILL.md:247-248 | "the trailer makes the next release a major, so the breaks stay first in slot 3" |
| The checklist doesn't detect the break classification (result shape, extended failure out of Scope) | Substantive | SKILL.md:849-852 | Add the classification question from Item 5 |
| No case for major, unknown, release-tool, commit-body, or rule-5 partitions | Substantive | `research/…/cases/` | At least a major-release case (expect no lead) and a rule-5 squash case, or say in the case README that these are untested |
| The control has no baseline arm, so growth isn't measured | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs of 4392 on `1f020ce`, with word counts |
| The heading set omits `Breaking changes` | Substantive | SKILL.md:300-301 | Add it to the set |
| Line of 121 characters (MD013 at 120, upstream config not seen) | Substantive | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap |
| "Six slots, in order" vs the lead | Taste | SKILL.md:192 | Mention the lead exception |
| 0.x minor releases treated as non-major | Taste | SKILL.md:243-250 | Optional clause for versioning that lets a minor break |
| Prompt version file equals the latest tag | Taste | both `prompt.md` | Use `42.7.15-SNAPSHOT`, or the next version, in the version file |
| Version bumps not claimed in the message | Taste | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | One sentence, or leave it as house convention |

What this review didn't check: I re-ran no model, didn't run `make check` or super-linter (no network), didn't open the cited pgjdbc#4367 maintainer comment (no network), and didn't review the prose for style.
