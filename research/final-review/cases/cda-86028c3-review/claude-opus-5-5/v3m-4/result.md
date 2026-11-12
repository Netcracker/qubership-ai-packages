# Final review: `4f69810..86028c3` (one commit: "lead the description with breaks unless the next release is a major")

No task statement was provided, so I took the claimed cases from the commit message and the two case READMEs. The change has no code: it edits a skill (`SKILL.md`), its package README and version files, and adds two regression cases under `research/`. I filled the form through the §2a analogues, and each item below names the analogue it used. I did not run the drift script because it parses code members and there are none here. I loaded `english-developer-style` from the provided folder. I read `apm-authoring` from the repository (the path under `agent-packages/apm-authoring/`), because the provided folder has no copy.

## Item 1: comments consistent with the code and with each other
*Analogue: what each changed file says about another file, and what `SKILL.md` says about the same fact in two places.*

- **Both case READMEs quote a rule that no longer exists.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:5-6` quote it as "A break leads the description where the next release from the target branch **promises compatibility**". The committed heading at `SKILL.md:234` reads "…**unless the next release from the target branch is a major**". A search for the quote finds nothing. The two conditions also differ for a minor release, which is not a major but does not promise compatibility either.
- **The break lead under §4 rule 5 contradicts two sentences the change left alone.**
  - `SKILL.md:257-260` says that where §4 rule 5 makes the description the commit body, "that body opens with its breaks and then its problem".
  - `:128` still says the `User-visible:`/`Not changed:` labels "sit after slot 3 and before the trailers".
  - `:638` (§4 rule 5) still says "shape it as §2's commit body", and `:310` says the description "takes the body's shape instead".
  - Take a repository that squashes with "title and description" and a break aimed at a patch release. An agent can't tell from these sentences whether the break lines open the body under a `User-visible:` label (so the label appears twice), under a heading (which the body shape doesn't have), or after slot 3 as `:128` says.
- **Two sentences now say different things about the reviewer's first question.** `:203-204` says "the reviewer's first question is why that version should change". `:243` says "the reviewer's first decision is whether the change may ship in it at all". Only one of them can be first.
- The other statements check out: the slot-1 paragraph (`:86-89`), the table row at `:198`, the checklist lines at `:831` and `:849`, the package README bullet, the `cases/` line in the research README, the skill-tree ids (the four with-rule runs record `4798053`, the tree of `86028c3`; the baselines record `1f020ce`, the tree of `4f69810`), and the word counts in both results tables (`wc -w` matches all ten).

## Item 2: claimed cases covered
*Analogue: the section of `SKILL.md` that handles each claim, and the case that tests it.*

| Claim (commit message) | Section | Trial |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `:234`, `:243-250` | `pgjdbc-4367-breaks` (42.7.x), checks 1–3 |
| No lead when the next release is a major | `:254-255` | **none**: both prompts target 42.7.14 |
| Release read from version file / milestone / branch name | `:244-246` | version file only; milestone and branch name: **none** |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| A result-shape change is a break | `:236` | 4367 check 2 |
| A failure extended to inputs that worked before is a break | `:238-240` | 4367 check 3 (fails in 1 of 2 Opus runs, as the README says) |
| Removed option, changed default, changed error code count as breaks | `:237-238` | none; definitional, so lower priority |
| Commit body keeps the problem first, breaks first under `User-visible:` | `:257-258` | **none**: both prompts ask only for a PR description |
| Under squash, the description that becomes the commit keeps the lead | `:258-260` | **none**: both prompts give a merge model where rule 5 does not apply |
| A change with no break grows no section | `:255` | `pgjdbc-4392-no-break`, checks 1–2 |

- **Commands.** `cases/pgjdbc-4367-breaks/README.md:28-29` tells the reader to run `git archive <rev> agent-packages/…/change-description-authoring` to copy the skill out. No script runs it. As written, `git archive` writes a tar stream to stdout, so the files are not copied out without `| tar -x -C <dir>` or `-o`. The `./gradlew` lines are inside the prompt inputs and are data, not instructions.
- **Hunks no sentence claims.** The version bump 1.4.0 → 1.5.0 in `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and the package `apm.yml:2` has no sentence in the commit message. Earlier commits on this skill say it in one line ("Version 1.2.0 to 1.3.0.", "Version 1.1.0 to 1.2.0."). Every other hunk is claimed.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the partitions are the release situations the change claims; the controls are the 4392 case and the table below.*

- **Missing partitions.** The trials cover one partition: a version file that says patch. The three other partitions the rule claims have no run:
  - **Major next release.** This is the negative control for the condition in the rule's own heading. A rule that always leads would pass every trial in this change.
  - **Unknown release.**
  - **Commit body and rule-5 squash forms.** The second item-1 finding shows these are ambiguous.
- **The noise-input control has no baseline.** `pgjdbc-4392-no-break` checks that no section appears, but compares its length only to the author's draft (209 words). It has no run on the base tree, so nothing shows whether the rule grew the output on an input where it should do nothing. §2a asks for that comparison.
- No earlier installed state applies. The umbrella `qubership-repo-essentials` refers to the package by path, not by version.

Added instructions: 4, no rows.

Not findings: `:240`, `:254`, `:255`.

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, whether the layout matches its siblings, and whether the repository's gate passes.*

- The rule sits in §2, beside the slot it reorders. The cases sit under `research/change-description-authoring/cases/`, which the research README now lists.
- `make check` (`apm pack --check-versions --check-clean --dry-run`) ran offline and reported no error.
- `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` covers every new `prompt.md` and `result*.md`. The READMEs are still linted.
- **Line length.** `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters in a list item. The umbrella installs `markdown-line-length-120`. I couldn't read the markdownlint config, which lives in `netcracker/.github`, so whether super-linter fails on it is unconfirmed.
- No sentence in the rule is generic tutorial advice. The release-reading paragraph names files and branch patterns specific to this skill.

## Item 4: names by content, not by position
*Unchanged analogue: headings, cross-references, and case names.*

None. Checks are numbered but named by content ("Lead", "Result shape"). Cross-references use section numbers and quoted phrases ("§4 rule 5", "(below)" at `:198` points to a bolded rule header). Run files are named `result.md`/`result-2.md`, which is ordinal, but the results tables name each one by path.

## Item 5: the failure report
*Analogue: whether each rule's detection is reached by the skill's checklist, and whether it detects the rule rather than something weaker.*

The new checklist line `:849-852` reaches the rule. It detects "opens with the break lines" and "no lead, no empty heading". The case READMEs carry the same checks with literal pass/fail criteria. None of these detections covers the break classification or the commit-body order, because those have no trial (see item 2).

## Item 6: what the writer says it verified
*Analogue: an exemplar the rule passes and a bad case it fails, both named in the change.*

- **Stated.** The bad case is the base-tree baselines: both models fail checks 1–3. The exemplar is the with-rule runs, which pass checks 1 and 2 in 4/4 and check 3 in 3/4. The rule was reworded after review, and the reworded version (tree `4798053` = HEAD) is the one that was run. The README reports honestly that the rewording dropped Opus from 2/2 to 1/2 on check 3.
- **Missing.** No growth check on a noise input (item 3).
- **Wording.** Both the commit message and the README say the baselines ran "on `origin/main`". The `skill-tree` files record the tree of `4f69810`, the parent commit. There is no remote ref here, so I couldn't confirm that the two are the same tree.

## Item 7: siblings of the change
*Analogue: the places that list or route to the skill.*

- The package README bullet is updated.
- The marketplace and `apm.yml` descriptions and the trigger instruction `.apm/instructions/change-description-authoring.instructions.md` say nothing about ordering, so the rule's scope widened nowhere that decides whether the skill loads.
- `problem-report-authoring` has no ordering rule that the change contradicts.
- No sentence counts the description's slots differently: "Six slots" still holds.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "where the next release … promises compatibility" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:5-6` | Quote the committed heading at `SKILL.md:234` |
| Breaks-first body under §4 rule 5 conflicts with label placement and "shape it as §2's commit body" | Substantive | `SKILL.md:257-260` vs `:128`, `:310`, `:638` | Say in which form the breaks open that body (label or heading), and add the exception at `:128` and `:638` |
| "Reviewer's first question is why" vs "first decision is whether it may ship" | Substantive | `SKILL.md:203-204` vs `:243` | Qualify `:204`, e.g. "where nothing breaks" |
| No trial with a major next release, the control for the rule's own condition | Substantive | `cases/` | Add a case whose version file says the next release is a major; check the breaks stay in slot 3 |
| No trial for unknown release, commit-body order, or rule-5 squash | Substantive | `SKILL.md:248-250`, `:257-260` | A run per claimed form, or drop the claim from the commit message |
| Control case has no baseline, so output growth on the noise input is unmeasured | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Run the control on tree `1f020ce` and compare word counts |
| Version bump 1.4.0 → 1.5.0 not stated in the commit message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." as earlier commits do |
| `git archive <rev> <path>` writes a tar to stdout, copies nothing | Substantive | `cases/pgjdbc-4367-breaks/README.md:28-29` | Give the full form, e.g. `git archive <rev> <path> \| tar -x -C <dir>` |
| README list item is 121 characters | Substantive (unconfirmed) | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap to ≤ 120 |
| Baseline called "origin/main" but recorded as the parent's tree | Taste | commit message; `cases/pgjdbc-4367-breaks/README.md:31` | Say "the parent commit" or name the tree id |

Not checked: I ran no model trials. I couldn't check the pgjdbc pull requests, the maintainer's comment, or the token prices cited in the README, because there was no network. I could not read the markdownlint configuration from `netcracker/.github`. I did not make a pass over the prose for style alone.
