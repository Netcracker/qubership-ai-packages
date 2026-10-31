# Final review: `4f69810..86028c3`, a skill change with no code

**Inputs.** I had no task statement, so the claimed cases come only from the commit message of 86028c3. The change touches only a skill (`change-description-authoring` SKILL.md), its README, version bumps and research cases, so I used the §2a analogues throughout. I did not run `comment-drift.py` because the change has no source members for it to parse. Skills loaded: final-review, english-developer-style (the copies you named), and the repository's `apm-authoring` as the artifact's authoring skill. I had no previous report.

## Item 1: comments consistent with the code and with each other
The analogue here: every statement one file makes about another.
- **Both case READMEs quote a rule name the skill doesn't have.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` call the rule "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". That is the earlier draft's wording, and anyone searching SKILL.md for the quoted text finds nothing.
- **The commit message misstates the effort level.** It says "on Opus and Haiku (effort high)", which reads as both models at high. The case README (`:33-34`) says Haiku ran at `high` and Opus at the session default.
- **Consistent:**
  - Tree ids: the with-rule `skill-tree` files (`4798053…`) equal `HEAD:<skill dir>`. The baseline ones (`1f020ce…`) equal `HEAD~1:<skill dir>`.
  - Word counts: the README tables match `wc -w`.
  - Narrative: "two drafts summarized in the README" matches README `:49-52`.
  - Lint: the lint exclusion regex `results?[^/]*|prompt[^/]*` already covers the new `result*.md` and `prompt.md` files.
  - Cross-references: §4 rule 5, §5's `BREAKING CHANGE:` row and §7's "no section for an absent concern" all say what the new text cites them for.
- **Conflict between two rules:** see the Scope-slot finding under item 3.

## Item 2: claimed cases covered
Claims from the commit message, with the evidence for each:

| Claim | Evidence |
| --- | --- |
| Breaks lead when the next release isn't a major (patch target) | `pgjdbc-4367-breaks` check 1: 4 of 4 runs |
| A result-shape change counts as a break | check 2: 4 of 4 |
| A failure extended to more inputs counts as a break, not Scope | check 3: 3 of 4, as the commit says |
| A change with no break grows no section | `pgjdbc-4392-no-break`: 4 of 4 |
| Next release is a major, so the breaks stay in slot 3 | **none** |
| Nothing says which release, so the breaks lead | **none** (both prompts state `gradle.properties`) |
| Release read from the milestone or the branch name | **none** |
| The commit body keeps the problem first, breaks as the first `User-visible:` lines | **none** (both cases write only a PR description) |
| Where squash copies the description into the commit, the lead stays | **none** (both prompts give `squash 3 plain 37` with commit bullets, so §4 rule 5 doesn't apply) |
| Break kinds: removed option, changed default, changed error code | **none** |

**Commands the change tells someone to run.** `cases/pgjdbc-4367-breaks/README.md:29-31` says to copy the skill out with `git archive <rev> agent-packages/…/change-description-authoring`.
- Nothing in the change runs this command.
- As written, `git archive` writes a tar stream to stdout and copies nothing. Its sibling cases pipe it: `| tar -x -C <dir> --strip-components=5` in `research/problem-report-authoring/cases/nested-workflow-tag/README.md:58-60`, and the same in `research/test-authoring/cases/run-case.sh:53`.
- The README also doesn't record the instruction the drafting agent was given or the directory it ran from, both of which the sibling case records.
- This is a finding.

**Hunks with no sentence in the commit message.** The 1.4.0 → 1.5.0 bump in `apm.yml`, `agent-packages/…/apm.yml` and `marketplace.json` isn't mentioned. It is this package's own bump for a contract change, which `apm-authoring` *Versions* asks for, so I'm labelling it taste only. Every other hunk has a sentence that claims it.

## Item 3: boundaries, partitions, and the negative control
- **The release axis has no control.** `pgjdbc-4392-no-break` is a control on the break axis only: no break, same patch target. Nothing holds the break constant and varies the release: no "major next" input, no "unknown" input. That is the failing-corner pattern the form names, and it's substantive.
- **The no-break control has no baseline run.** §2a asks for "a check that the output there did not grow". The no-break results are compared only with the draft (209 words against 241–256), so I can't tell whether the rule added words there.
- **The Scope rule and the new rule disagree on one input.** `SKILL.md:488-492` says that where only a maintainer can say whether a compatibility break is intended, the agent keeps it in the Scope slot as a question. `SKILL.md:238-240` says an extended failure "goes with the breaks, not in the Scope slot". For a break whose intent is the open question, both rules fire and nothing settles it. The same `grant insert` case shows the strain: one Opus run put it in Scope.

Table of added instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Breaks lead under a `Breaking changes` heading (`SKILL.md:234,252-255`) | A repo whose PR template has its own "Breaking change?" section partway down | A new `Breaking changes` heading above the template's first heading, plus the template's section, against "use its headings" (`:301-302`) | None; asked for: "Where a template has a section for breaks, move it to the top or fill it in place" |
| Release-tool trailer "decides" (`:247-248`) | A semantic-release repo with a break that will carry `BREAKING CHANGE:` | The trailer makes the next release a major, so the breaks stay in slot 3, though the reviewer's first decision is whether to accept a major bump; "decides" can be read either way | None; asked for: say what the trailer decides and which order follows |
| Extended failure goes with the breaks, not in Scope (`:238-240`) | A break whose intent is the open question for the maintainer | Both a lead line and a Scope question, or either one | Conflicts with `:488-492`; asked for: one clause, e.g. "the break leads; the Scope question refers to it" |
| "A failure that now succeeds is a fix, not a break" (`:240-241`) | A validation that used to reject input that callers' tests expect to be rejected | No break line | None (taste: that reading is defensible) |
| Unknown release, so breaks lead (`:248-250`) | A continuously deployed service with no released version | A lead section in every PR with a behavior change | None; the artifact doesn't address this kind of repo (taste) |

Not findings:
- A no-break change: ended by "A change with no break has neither the lead nor an empty heading" (`:255`).
- A major next release: ended by "Where the next release is a major, the breaks stay first in slot 3" (`:254-255`).
- A heading inside a §4 rule 5 commit body: ended by "where the description has headings" (`:252-253`) together with "Under §4 rule 5 the description is the commit body and takes the body's shape instead" (`:310`).

## Item 3a: level, placement, and the environment
- **Placement:** the rule sits under §2 *Pull request description*, beside slot 3, with a mirrored checklist line. That fits the layout.
- **Rule split across sections (taste):** the commit-body side of the rule (`:257-260`) also lives there, while the commit-body table row 4 (`:83`) still doesn't say "breaks first". A reader of only §2 *Commit body* misses it.
- **Case layout differs from the siblings (taste):** model directories are `opus/` and `haiku/`, where sibling cases use model ids (`claude-opus-5-5`, `claude-haiku-4-5`). The model version appears only in the cost paragraph.
- **Gate:** `make check` and `make test` need `uvx`/`apm` from the network, so I didn't run them.
- No sentence fits every tutorial, so there are no filler findings.

## Item 4: names by content, not by position
None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`), the checks (named "Lead", "Result shape", …) and the cross-references (§2, §4 rule 5, §5, §7) all refer by content. The table's "(1)…(6)" columns sit next to the check names.

## Item 5: the failure report
- **Checks 4–6 test less than the README says.** README `:25` says checks 4–6 are "the guard against the rule costing other facts". They detect only that the fix line stays out, no line repeats, and the literals survive. Two results pass them anyway:
  - `haiku/result-2.md` drops that the `grant insert` statement succeeded before. Its line says only "sent without `RETURNING`".
  - `opus/result.md` adds remedies the draft never carried ("Call `execute()` and read each result with `getMoreResults()` instead"), although the prompt says "add none that it does not carry". README `:54` records this as growth, not as a failure.
- The checklist reaches the rule: the "Breaks:" line at `:849-852` matches the rule's condition.

## Item 6: what the writer says it verified
- **Present:** red runs on the base (Opus and Haiku baselines fail checks 1–3) and green runs on the rule. A reworded draft was re-run after review (README `:49-52`).
- **Missing:** a baseline for the noise input (item 3), and any evidence for the major or unknown partitions.
- **Not verifiable offline:** the price figures in README `:59-61`.

## Item 7: siblings of the change
- **Updated where they list the package or its rules:** the version appears in all three places that hold it (no other `1.4.0` remains), the package README has a bullet, and the research README lists `cases/`.
- **Description fields:** the marketplace and `apm.yml` descriptions are unchanged, which is right because the scope didn't widen.
- **Changelog section (`:543`):** "Breaking changes are marked in place and sorted first within their category" is a separate artifact and doesn't conflict.
- **Slot 3 text (`:226`):** "Breaks come first" still holds for the major case.
- **Old size:** no sentence counts slots or rules in a way the change made stale.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule name that isn't in SKILL.md | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed heading, "…unless the next release from the target branch is a major" |
| No case for the major-next or unknown-release partitions, or for the commit body / §4 rule 5 path, which the commit message claims | Substantive | `SKILL.md:247-260`; commit message | Add a "major next" input (e.g. the 4367 draft with a `43.0.0` version file) as the release-axis control, plus a squash "title and description" input; or narrow the commit message's claims |
| The Scope rule (maintainer question about a break) and the new "not in the Scope slot" rule conflict on one input | Substantive | `SKILL.md:238-240` vs `:488-492` | One clause saying which wins, e.g. "the break leads; the Scope question refers to it" |
| "The trailer decides" is ambiguous, and in semantic-release repos it keeps the breaks out of the lead exactly when merging forces a major | Substantive | `SKILL.md:247-248` | Say what the trailer decides and which order follows |
| A PR template's headings and the new `Breaking changes` lead aren't reconciled | Substantive | `SKILL.md:252-253` vs `:301-302` | Clause for a template, including one that has its own breaking-change section |
| Checks 4–6 claim to guard against lost facts but pass a dropped fact (`haiku/result-2.md`) and invented remedies (`opus/result.md`) | Substantive | `cases/pgjdbc-4367-breaks/README.md:25,54` | A check for "no fact beyond the draft, no draft fact lost" (or narrow the claim), and re-grade both results |
| The no-break control has no baseline run, so growth on the noise input isn't measured | Substantive | `cases/pgjdbc-4392-no-break/README.md:20-25` | Two baseline runs on the parent tree, compared with the with-rule runs |
| The "Running it" command is incomplete (`git archive` with no `| tar -x`), with no runner, no recorded agent instruction and no working directory | Substantive | `cases/pgjdbc-4367-breaks/README.md:29-34` | Use the sibling case's full command block and record the agent's instruction (see `problem-report-authoring/cases/nested-workflow-tag/README.md:50-60`) |
| Commit message "(effort high)" reads as both models | Substantive | commit message, third paragraph | "Haiku at effort high, Opus at the session default" |
| Model directories `opus/` and `haiku/` instead of model ids | Taste | `cases/*/opus`, `cases/*/haiku` | `claude-opus-5-5/`, `claude-haiku-5-5/` |
| The commit-body side of the rule lives in the PR section; row 4 of the commit-body table doesn't say "breaks first" | Taste | `SKILL.md:83`, `:257-260` | Add "breaks first" to row 4 |
| The version bump isn't mentioned in the commit message | Taste | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | A clause in the message, or leave as is |
| "A failure that now succeeds is a fix" ignores callers who rely on the rejection | Taste | `SKILL.md:240-241` | Optional exception for a rejection callers test for |

Not checked: I didn't run `make check` or `make test` (they need the network), didn't run the drift script (no code), didn't re-run any case, didn't verify the price figures or the cited pgjdbc pull requests and comment, and didn't do a style-only pass over the prose.
