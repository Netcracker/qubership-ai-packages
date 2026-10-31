# Final review: `4f69810..HEAD` (one commit, 86028c3)

**Inputs.** I had no separate task statement, so the claimed cases come from the commit message alone. This is the first review of the change, so there is no previous report to compare against. The change has no code: it edits a skill (`change-description-authoring` SKILL.md), adds package metadata, and adds research regression cases. That means the form is filled through the §2a analogues. The drift script was not run because it parses source members, and the change has none.

Skills loaded:
- `english-developer-style`, from the copy under the provided skills directory.
- `apm-authoring`, from `agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`. It is the authoring skill for a skill package, and it is not one of the three restricted copies.

## Item 1: comments consistent with the code and with each other
*Analogue: statements that one changed file makes about another, and statements inside SKILL.md that cover the same fact.*

- **SKILL.md:204 contradicts SKILL.md:243.** Line 204 says "the reviewer's first question is why that version should change". The new line 243 says "In a release that is not a major, the reviewer's first decision is whether the change may ship in it at all". An agent reading §2 top-down meets the old claim first, and it is the reason given for the Why slot having no skip condition.
- **The §8 checklist contradicts itself.** The *Caller* line (SKILL.md ~843) still asks for "one line per distinct outcome under 'User-visible changes', breaks first". The new *Breaks* line (~849) asks that "slot 3 keep only the other outcomes" when the target release is not a major. A reviewer following *Caller* on a patch-release description will ask for the breaks to be put back into slot 3. "Six slots, in order" (SKILL.md:192) also no longer holds when the lead applies.
- **Both case READMEs quote a rule that is not in the skill.** `cases/pgjdbc-4367-breaks/README.md:7` and `cases/pgjdbc-4392-no-break/README.md:6` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed text (SKILL.md:234) says "…unless the next release from the target branch is a major". Grepping for the quoted text finds nothing. The README itself says the rule was "reworded after review", which explains how the quote went stale.
- **Statements I checked that are true:**
  - The tree ids in `skill-tree` match: `47980534…` is `HEAD:<skill dir>`, and `1f020ce5…` is `4f69810:<skill dir>`, the "origin/main before the rule" baseline.
  - The results table matches the six result files: I checked lead, heading, and where `grant insert` sits in each.
  - "All three Haiku results end with `Generated with Claude Code`" is true (result, result-2, and baseline).
  - The research README's line "a prompt, the checks, and each model's result" matches the layout.
  - The version is 1.5.0 in all three files.
  - No sentence in the skill narrates the change.

## Item 2: claimed cases covered
*Analogue: the section of SKILL.md that handles each case, and the regression case that detects it.*

| Claimed case (commit message) | Section | Detection (case/check) |
| --- | --- | --- |
| Breaks lead when the next release is not a major | §2 PR description, SKILL.md:234–256 | pgjdbc-4367-breaks check 1; 4 of 4 runs pass |
| Breaks do not lead when the next release is a major | SKILL.md:255 | **none** |
| Breaks lead when nothing says which release it is | SKILL.md:248–250 | **none** |
| Next release read from version file | SKILL.md:244–246 | pgjdbc-4367 (`gradle.properties`) |
| Next release read from milestone or branch name | same | **none** |
| `BREAKING CHANGE:` / `!` decides | SKILL.md:247 | **none** (not claimed in the commit message) |
| Break kind: new failure, changed error code | definition, SKILL.md:235–239 | 4367 breaks 1 and 2 |
| Break kind: result shape | same | 4367 check 2 |
| Break kind: failure extended to inputs that worked | SKILL.md:239–241 | 4367 check 3 (3 of 4 runs; the README states this) |
| Break kind: removed option, changed default | same | **none** |
| A fix is not a break | SKILL.md:242–243 | 4367 check 4 |
| Commit body keeps the problem first, breaks first under `User-visible:` | SKILL.md:257–258 | **none**: the prompt asks only for a PR description |
| Squash copies the description and the lead stays | SKILL.md:259–260, 86–88 | **none**: the prompt's merge model (squash default, one commit) does not trigger §4 rule 5 |
| No break means no section | SKILL.md:256 | pgjdbc-4392-no-break checks 1–2; 4 of 4 runs pass |

**Commands the change tells a reader to run.** `git archive <rev> agent-packages/…/change-description-authoring` (4367 README, "Running it") promises that it copies the skill "out of the checkout". No script or CI job in the repository runs it, so the runner is `none`. The outcome depends on where `git archive` sends its output: it writes a tar stream to stdout, so the command as written copies no files unless `-o` or `| tar -x -C <dir>` is added.

**Hunks the commit message does not claim.** The version bump 1.4.0 → 1.5.0 in `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and `agent-packages/change-description-authoring/apm.yml:2` is not mentioned. All the other hunks are claimed.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the claimed modes (major, not a major, unknown), the two artifacts (PR description, commit body), and the merge model.*

- **Partitions with no evidence.** Only one partition was exercised: not a major, read from the version file, on a PR description, with no rule-5 squash. These claimed partitions have no run:
  - the next release is a major (the "unless" branch);
  - the next release is unknown;
  - the commit body;
  - a squash under "title and description".
- **Negative control.** `pgjdbc-4392-no-break` is the control for "no break", and it passes. There is no control for "a break, but the next release is a major". That is the control that would stay unchanged on the base tree.
- **Pre-existing state.** The package is installed over 1.4.0, but a skill text keeps no state, so there is nothing to check. No setting reaches a new consumer, no mechanism is replaced, and no limit is involved.

**Instructions this change adds**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Under §4 rule 5 the lead stays in the commit body (SKILL.md:86–88, 259–260) | Squash "title and description" repo, patch release, one break | A body that opens with bare break lines: headings are absent from a rule-5 body (§2 Headings, §8) and no text puts `User-visible:` above them, so the label R4 and R5 grep for is missing | "…that body opens with its breaks **under `User-visible:`**, then its problem" |
| Break definition: "a different return value… Whether the old behavior was right does not decide it" (SKILL.md:234–243) | A patch fix whose defect is a wrong returned value (for example, an off-by-one count corrected) | A `Breaking changes` lead that restates the fix, followed by a Why that states it again. Only "a failure that now succeeds" is excluded, and §2 "not restated in slot 2" covers What, not Why | "a value the Why slot names as the defect is stated there once, as the fix" (or state that such a fix does lead, and add a case for it) |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!`, the trailer decides" (SKILL.md:247–248) | A release-please repo with a break on a maintenance branch | The text does not say which way the trailer decides: writing the trailer makes the release a major, so the lead disappears. It calls `!` a trailer | Taste: "the trailer or `!` marks the release as a major, so the breaks stay in slot 3" |

**Not findings:**
- "Breaks lead" for a change with no break is ended by "A change with no break has neither the lead nor an empty heading (§7)".
- "Breaks lead" for a major release is ended by "Where the next release is a major, the breaks stay first in slot 3".

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, the layout, and the gate.*

- The rule sits in §2 under the PR description, where slot 3 is defined. The commit-body counterpart is in §2 Commit body, and the check is in §8. The placement is right.
- The cases follow the `research/<pkg>/cases/` convention of `blackbox-test-design`. That convention uses `results/<variant>/`; this change uses `<model>/result*.md`. Both are matched by `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, and I checked the regex against the new paths.
- The case READMEs are still linted. `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters of prose. Since `markdown-line-length-120` exists, the limit is likely MD013 = 120, but the markdownlint config comes from `netcracker/.github` and is not in the checkout, so I could not confirm it.
- `make check` needs `uvx` with network access, so it was not run. Instead I checked by grep that the three versions agree.
- No sentence in the change reads like a generic tutorial.

## Item 4: names by content, not by position
None found. The new text uses the skill's existing slot numbering ("slot 3's break lines", "ahead of slot 1"), which is the file's own convention and is labeled in the tables. The case checks carry a name as well as a number ("**Lead.** (1)"). The commit message's "one Opus run left it there" is named by file (`opus/result-2.md`) in the README.

## Item 5: the failure report
*Analogue: whether the checklist reaches the rule, and whether its detection matches the rule.*

The new §8 *Breaks* line reaches the rule, but it detects a weaker property. It asks whether the description "open[s] with the break lines". It does not ask whether every outcome that meets the break definition is among them. The baseline failure the change was made for passes that question: the lead holds the two obvious failures, and the result shape and the extended failure stay in slot 3 and Scope. Checks 2 and 3 of the case catch it; the skill's own checklist does not.

## Item 6: what the writer says it verified
- **Bad case and exemplar.** The bad case is the baseline on the base tree: both models fail checks 1–3. The exemplar is the runs on the HEAD tree: 4 of 4 pass checks 1–2, and 3 of 4 pass check 3, which the README states.
- **Earlier drafts.** The rule was rewritten after review, and the README reports results for the final wording, which is good.
- **Noise input.** The control has no run on the base tree. The README reports 241–256 words against a 209-word draft, but without a base-tree run nobody can tell whether the rule made the control grow. The form asks for exactly that comparison on a noise input.
- **Rule-5 sentence.** The commit-body / §4 rule 5 sentence has no exemplar at all (see item 2).

## Item 7: siblings of the change
- **Done.** The index and marketplace entries were bumped in all three places. The package README has a new bullet. The instructions file (`.apm/instructions/change-description-authoring.instructions.md`) is only a trigger and needs no change. The frontmatter description is generic and still fits.
- **The heading set leaves out the new heading.** The set at SKILL.md ~260, "`Why`, `What`, `User-visible changes`, `How to verify`, and `Scope` is one set", does not list the new `Breaking changes` heading.
- **The changelog section does not get the new definition.** §3 (SKILL.md:543, "Breaking changes are marked in place…") and the changelog's Compatibility slot (SKILL.md:506) use "breaking", but the new definition of a break (result shape, extended failure) lives only in the PR-description section. A changelog writer reading §3 does not get it.
- **Russian sibling skill.** `russian-developer-style/modules/code-comments.md:120–130` prescribes a PR order of What, Why, How to verify, with "Breaking changes" as an optional trailing block. That is the opposite order for a patch release. Since it is another language's style skill, this belongs in a follow-up note rather than this change.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| "Reviewer's first question is why…" conflicts with the new "first decision is whether it may ship" | Substantive | SKILL.md:204 vs 243 | Limit line 204 to the case with no lead, or point it at the break rule |
| §8 *Caller* line still asks for breaks first under "User-visible changes"; *Breaks* line says slot 3 keeps only the others | Substantive | SKILL.md ~843 vs ~849; also "Six slots, in order" :192 | Add the not-a-major exception to the *Caller* line and to the order sentence |
| Case READMEs quote a rule wording that is not in SKILL.md | Substantive | cases/pgjdbc-4367-breaks/README.md:7, cases/pgjdbc-4392-no-break/README.md:6 | Quote the committed sentence ("…unless the next release from the target branch is a major") |
| Under §4 rule 5 the leading breaks have no `User-visible:` label (headings are absent there) | Substantive | SKILL.md:86–88, 259–260 | Clause: the body opens with its breaks under `User-visible:` |
| §8 *Breaks* detects "opens with break lines", not "every break by the definition is there" | Substantive | SKILL.md ~849 | Add "are the result-shape changes and the failures extended to inputs that worked before among them?" |
| Claimed partitions with no case: major release, unknown release, commit body, rule-5 squash | Substantive | cases/ | One case with a major target (the control of the "unless"), or a sentence in the commit message limiting the claim to what was run |
| Negative control has no base-tree run, so its growth cannot be attributed | Substantive | cases/pgjdbc-4392-no-break/README.md | Add Opus and Haiku runs of 4392 on tree `1f020ce5…` |
| A value-correcting fix counts as a break and leads, restating the fix | Substantive | SKILL.md:234–243 | A clause that ends it, or a case showing the lead is intended there |
| `git archive <rev> <path>` writes a tar to stdout and copies nothing | Substantive | cases/pgjdbc-4367-breaks/README.md ("Running it") | `git archive <rev> <path> \| tar -x -C <dir>` |
| Case README line is 121 characters (MD013 120, likely; config not in the checkout) | Substantive (plausible) | cases/pgjdbc-4367-breaks/README.md:17 | Rewrap |
| `BREAKING CHANGE:`/`!` "the trailer decides" does not say which way, and calls `!` a trailer | Taste | SKILL.md:247–248 | "…marks the release as a major, so the breaks stay in slot 3" |
| Version bump not claimed in the commit message | Taste | marketplace.json:291, apm.yml:168, package apm.yml:2 | One sentence naming the 1.5.0 bump |
| Heading set omits `Breaking changes` | Taste | SKILL.md ~260 | Add it to the set |
| Break definition is not reachable from the changelog section | Taste | SKILL.md:506, 543 | Point §3 at the definition in §2 |
| `russian-developer-style` PR order contradicts the lead | Taste | russian-developer-style/modules/code-comments.md:120–130 | Name it as follow-up |

**Not checked:** I did not run the marketplace gate (`make check`, which needs `uvx` and the network), markdownlint, or any model run. I did not fetch the cited pgjdbc pull requests or the maintainer's comment, so the claim that the maintainer rewrote the description with the breaks first was not verified against the source. I did no style-only pass over the prose.
