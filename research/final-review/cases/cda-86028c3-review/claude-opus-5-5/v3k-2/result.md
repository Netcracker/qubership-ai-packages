No previous report of this form exists for this change, so there is no table of earlier findings. There is no task statement either: the claimed cases come from the commit message `86028c3` alone. The change is a skill plus research files, with no code, so every item below uses the §2a analogue it names. I did not run the drift script, because there are no members for it to parse. Skills loaded: `final-review`, `english-developer-style` (the copy under the task's skills directory), and `apm-authoring` from `agent-packages/apm-authoring` in place of a doc-comment skill.

## Item 1: comments consistent with the code and with each other
*Analogue used: what one changed file says about another file or about the repository.*

- **Stale rule quote in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` quotes the rule as "A break leads the description where the next release from the target branch promises compatibility". `cases/pgjdbc-4392-no-break/README.md:5-6` quotes the same words. The committed rule at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The `skill-tree` files show the runs used the committed tree (`47980534…` = `HEAD:…/change-description-authoring`), so only the quote is stale. Someone who greps for the quoted rule finds nothing, or thinks the case tests a different condition.
- **New Scope rule contradicts the existing one.** `SKILL.md:238-240` says an extended failure "goes with the breaks, not in the Scope slot". `SKILL.md:488-491`, unchanged, says that where "only a maintainer can answer… whether a compatibility break is intended, keep it in the Scope slot as a question." When a break's intent is an open question (the `grant insert` case is one candidate), the agent gets two opposite instructions. The new text needs a clause saying the break line leads while the question of intent stays in Scope.
- **The Caller checklist line was not updated.** `SKILL.md:844-845` still asks for "one line per distinct outcome under 'User-visible changes', breaks first". With the lead, `:253` moves the breaks out of slot 3. A reviewer who follows the checklist would flag a correct description, or would put the breaks back in slot 3.
- **"the trailer decides" (`SKILL.md:247-248`) has no object.** One reading: a `BREAKING CHANGE:` trailer makes the next release a major, so the breaks do not lead. Another reading: the trailer decides what goes in the description. Under the first reading, any repository that runs release-please never gets the lead, which works against the rationale at `:243-244`. The request is to say what the trailer decides.
- **Lead under §4 rule 5 has no label.** `SKILL.md:252`, `:259-260` and `:310`: the breaks lead "under a `Breaking changes` heading where the description has headings". When §4 rule 5 makes the description the commit body, there are no headings (`:310`, `:857`). `:258` says the `User-visible:` label "is what R4 and R5 search for". Nothing says whether the leading break lines in such a body carry that label, so a body built this way can open with unlabeled breaks that a grep for `User-visible:` misses.
- **Commit message vs case README on effort.** The commit message says "on Opus and Haiku (effort high)". The README (`pgjdbc-4367-breaks/README.md`, Running it) says Opus ran "at the session's default".
- I checked these and they hold: the slot-3 table row (`:198`), the slot-1 exception (`:86-88`), the Problem checklist line (`:831-832`), the package README bullet, the research README's `cases/` line, the case counts in the commit message ("two runs each", "three of four", "one Opus run left it there"), the per-run table against the six result files (literals, `grant insert` placement, slot-3 contents), and the skill-tree ids against the base and HEAD. I could not fetch the cited exemplar (the maintainer's rewrite on pgjdbc#4367) because there is no network, so I did not check the rule against it.

## Item 2: claimed cases covered
*Analogue used: the sections that handle each claim, the runs as tests, and every hunk claimed.*

| Claim (commit message) | Where it is handled | Evidence |
| --- | --- | --- |
| Lead with the breaks when the next release is not a major | `:234`, `:252` | `pgjdbc-4367-breaks`: 4/4 runs pass, 2/2 baselines fail |
| Read the release from the version file, milestone, or branch name | `:244-247` | Version-file path only (gradle.properties in the prompt); no run for milestone or branch name |
| Breaks lead when the release is unknown | `:248-250` | **none** |
| What a break is: result shape, extended failure | `:235-241` | Checks 2 and 3; extended failure moved in 3 of 4 runs |
| Commit body keeps problem first, breaks first under `User-visible:` | `:257-258` | **none**: both prompts ask only for a PR description |
| Under squash-as-body (§4 rule 5), the lead stays | `:258-260` | **none** |
| No break: no section | `:255`, `:787` | `pgjdbc-4392-no-break`: 4/4 runs pass |
| Next release is a major: breaks stay in slot 3 | `:254-255` | **none** (see Item 3) |

- Commands the change tells someone to run: the case README says the skill is copied out "with `git archive <rev> agent-packages/…/change-description-authoring`". That form writes a tar stream to stdout and copies nothing until it is piped to `tar -x`. No script in the repository runs it. The request is the full pipeline that produced the copy, or a script that does it.
- Unclaimed hunks: the version bump 1.4.0 → 1.5.0 in `apm.yml`, `.claude-plugin/marketplace.json` and the package `apm.yml`. No sentence in the commit message claims it, while earlier commits in this package state their bump ("Version 1.2.0 to 1.3.0.").

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the situations the change claims; the no-break case is one control; the table of added instructions.*

- `pgjdbc-4392-no-break` is the control for "has a break". There is no control for the "unless the next release is a major" condition. That would be the same `pgjdbc-4367` draft on a target whose version file names a major (for example `43.0.0-SNAPSHOT`), where the breaks should stay first in slot 3. As committed, no run shows that the rule stops anywhere except when there is no break.
- Three claimed partitions have no run at all: release unknown, commit body order, and description-as-body under §4 rule 5. The release-tool-trailer partition has none either.
- Both cases put the target on `master` with one merge-model reading. Nothing exercises an existing description being edited (§7a) after the rule.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:234` "A break leads the description unless…" | patch release fixing a regression: restores the 42.7.12 return value that 42.7.13 changed | `Breaking changes` heading over a regression fix; reviewer reads it as a new break | "except a change that restores the behavior of the release before; that line says so, first in slot 3" |

Not findings: `:238` "a failure a caller may catch", `:255` "neither the lead nor an empty heading", `:257` "keeps its order, problem first", `:243` "from the target branch".

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, layout against the sibling directories, and the repository's own gates.*

- The rule sits in §2 under Pull request description, beside slot 3, and the checklist carries it at `:849`. That placement fits.
- I ran the offline gates: `make check-descriptions` (all 27 descriptions within 1020 characters) and `make test` (PASS). The result and prompt files fall under `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` (`results?[^/]*`, `prompt[^/]*`). I did not run `apm pack --check-versions` because it needs network.
- The case layout `<model>/result*.md` differs from the sibling `research/blackbox-test-design/cases/<case>/results/<variant>/` with `grading.json` and `run.txt`. Both layouts work (taste).
- No sentence reads like generic tutorial material.

## Item 4: names by content, not by position
*Analogue used: unchanged, applied to the change's headings, cross-references and case names.*

- The new text adds two more references to "§4 rule 5" (`:86`, `:258`). That follows the file's existing convention; naming the setting ("title and description") would survive renumbering (taste).
- The case checks are numbered and also named ("Lead (1)"); the case names describe their content.

## Item 5: the failure report
*Analogue used: the checklist reaches the rule, and the detection detects the rule rather than a weaker property.*

- The Breaks checklist line (`:849-852`) reaches the rule, but it detects a weaker property: whether the description opens with *the* break lines. The defect the commit message names was a description that never classified the result-shape change and the extended failure as breaks. The line should also ask whether every changed return value or result shape, and every failure extended to inputs that worked before, is among the breaks (`:235-240`).

## Item 6: what the writer says it verified
*Analogue used: an exemplar the rule passes and a bad case it fails, both named in the change.*

- An exemplar (`pgjdbc-4367-breaks`, rule runs) and a bad case (the baselines) are both present, run on the committed tree, and the README states that the rewording after review was re-run.
- Gap: the noise input `pgjdbc-4392-no-break` was measured only against the draft (209 words → 241-256). It has no baseline run on the base tree, so nothing shows whether the rule made that output grow. The request is two baseline runs of 4392 on tree `1f020ce5…`.

## Item 7: siblings of the change
*Analogue used: the places that list or route to the artifact.*

- Inside the skill, the siblings are `:226` (slot-3 prose), `:844` (Caller checklist) and `:488` (Scope question). `:226` holds; `:844` and `:488` are findings under Item 1. `references/merge-model.md` and the instructions file say nothing about breaks.
- The package README, `apm.yml` and the marketplace entry are updated for the version. The skill's `description:` is unchanged, which is right because the trigger surface did not widen.
- The developer-style skills only defer to this skill on where a break is marked (`english-*-developer-style/SKILL.md:570`). That is still true.
- No count of the set changed: still "Six slots" and "Five slots".

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| New "not in the Scope slot" contradicts "keep it in the Scope slot as a question" | Substantive | `SKILL.md:238-240` vs `:488-491` | Add a clause: the break line leads, and an open question of intent stays in Scope |
| Caller checklist still puts the breaks first under "User-visible changes" | Substantive | `SKILL.md:844-845` | Add "or in the lead (Breaks below)" |
| "the trailer decides" has no object; one reading never leads under release-please | Substantive | `SKILL.md:247-248` | Say what the trailer decides |
| Under §4 rule 5, the leading breaks have no heading and no `User-visible:` label is specified | Substantive | `SKILL.md:252`, `:258-260` | Say the leading break lines in a body carry `User-visible:` |
| Breaks checklist doesn't check that result shapes and extended failures are classed as breaks | Substantive | `SKILL.md:849-852` | Add that question to the line |
| Both case READMEs quote a superseded wording of the rule | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:5-6` | Quote `:234` as committed |
| No control for "next release is a major"; unknown release, commit body and rule-5 body have no runs | Substantive | `research/change-description-authoring/cases/` | Run 4367 on a major-version target; run or drop the other claims from the message |
| No baseline for the noise input, so growth is unmeasured | Substantive | `cases/pgjdbc-4392-no-break/README.md` (Results) | Two baseline runs on `1f020ce5…` |
| A regression fix that restores an earlier release's behavior leads as a break | Substantive | `SKILL.md:234-241` | The restore clause in the Item 3 table |
| Commit message says Opus ran at effort high; README says session default | Substantive | commit `86028c3` body | Make the two agree |
| `git archive <rev> <path>` as written copies nothing | Substantive | `cases/pgjdbc-4367-breaks/README.md` (Running it) | Give the full pipeline, or a script |
| Version bump 1.4.0 → 1.5.0 not claimed in the commit message | Substantive | `apm.yml:168`, `.claude-plugin/marketplace.json:291`, package `apm.yml:2` | Add "Version 1.4.0 to 1.5.0." as earlier commits do |
| Case layout differs from `blackbox-test-design/cases` | Taste | `research/change-description-authoring/cases/` | Optional `results/<variant>/` layout |
| A 0.x library or a beta API gets the lead on a minor release | Taste | `SKILL.md:234`, `:243-247` | Optional clause on pre-1.0 and unstable APIs |
| More "§4 rule 5" references by number | Taste | `SKILL.md:86`, `:258` | Optional: name the setting |

What this review did not check: I did not run the drafting trials or `apm pack --check-versions`, I could not fetch the cited pgjdbc#4367 rewrite (no network), I did not run the drift script (no code), and I did not do a style-only pass over the prose.
