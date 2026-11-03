# Final review: `4f69810..86028c3`, change-description-authoring breaks lead (1.5.0)

**Bottom line:** the rule is coherent, and the two cases support the main claim: with the rule, all four `pgjdbc-4367` runs lead with the breaks, and the control runs grow no section. I found eight substantive findings to fix before this is final:
- Both case READMEs quote a version of the rule that was not committed.
- One new linted line is 121 characters.
- The skill now names two different "first" things for the reviewer.
- Three claimed arms have no case, and the control has no baseline run.
- The pre-1.0 input needs an ending clause.
- The version-bump hunks have no sentence in the commit message.

No previous report was handed over. There was no separate task statement either, so the claimed cases come from the commit message alone, plus the case READMEs. This is a skill change with no code, so every item uses the §2a analogue. I ran the drift script (`comment-drift.py 4f69810 HEAD`). It printed nothing because the change is Markdown and YAML only, so the analogues stand in for it. I loaded `english-developer-style` from the given path and `apm-authoring` from the repository.

## Item 1: comments consistent with the code and with each other
*Analogue: cross-file statements, section references, quoted rules.*

- **Stale rule quote.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` both quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` is "…unless the next release from the target branch is a major".
  - A reader who searches for the quote finds nothing.
  - The two conditions also differ for a pre-1.0 or calendar-versioned project.
  - The 4367 README says the committed wording was "reworded after review", so the quote predates it.
- **Two "first" statements.** `SKILL.md:204` says "the reviewer's first question is why that version should change". `SKILL.md:243` says that, for a non-major release, "the reviewer's first decision is whether the change may ship in it at all". These are two different first things for the same reader.
  - The slot table at `:198` still gives slot 3 the readers "R3, R4", while the lead is justified by R1.
- **Checked and consistent:**
  - The §4 rule 5, §5 and §7 references (`:86`, `:247`, `:255`, `:259`, `:831`).
  - The checklist line at `:849`.
  - The package README bullet.
  - The `skill-tree` ids: 4798053… is the HEAD tree of the skill and 1f020ce… is the base tree, as the READMEs say.
  - The word counts, the "Generated with" counts, and the pass/fail table cells, which I checked against each result file.

## Item 2: claimed cases covered
*Analogue: each claim of the commit message mapped to the section that handles it and the run that shows it.*

| Claim (commit message) | Handled in | Evidence |
| --- | --- | --- |
| Breaks lead unless the next release is a major | `SKILL.md:234-255` | 4367 with the rule, 4 runs |
| Next release read from version file, milestone, or name | `:243-247` | 4367 prompt (`gradle.properties` 42.7.14) |
| Breaks lead where nothing says which release it is | `:248-250` | **none**: every case states the version |
| Major next release: breaks stay first in slot 3 | `:254-255` | **none** |
| Definition of a break: result shape | `:235-237` | 4367 check 2 |
| Definition of a break: extended failure | `:238-240` | 4367 check 3, 3 of 4 runs |
| Commit body keeps the problem first, breaks first in `User-visible:` | `:257-258` | **none**: both prompts ask only for a PR description |
| Under squash the lead stays in the body | `:258-260`, `:86-87` | **none** |
| No break, no section | `:255`, §7 | 4392, 4 runs |
| Claims about the runs and the earlier drafts | 4367 README | matches the stored files |

- **Unchecked commands and prices.** The 4367 README ("Running it") gives the command `git archive <rev> agent-packages/…`. No script runs it, and `git archive` writes a tar stream that has to be extracted, which the README does not say (taste). I could not check the Opus and Haiku prices at `README.md:60` offline. The arithmetic from them is correct.
- **Effort level.** The commit message says "on Opus and Haiku (effort high)". README `:33-34` says only Haiku ran at `high` and Opus ran at the session default. A reader takes "effort high" to cover both models.
- **Unclaimed hunks.** The version bumps 1.4.0 → 1.5.0 in `apm.yml:168`, the package `apm.yml:2` and `marketplace.json:291` have no sentence in the commit message. The earlier commits in this series state them ("Version 1.2.0 to 1.3.0."). Every other hunk is claimed.

## Item 3: boundaries, partitions, and the negative control
*Analogue: claimed situations as partitions; the control arm; the table of added instructions.*

- **Untested arms.** Three claimed arms have no evidence: a major next release, an unknown release, and the commit body (plain or squash). The finding names all three.
- **Control has no baseline.** The no-break control `pgjdbc-4392-no-break` checks that no section grows. Its 241–256 words are compared only with the 209-word draft, because it has no `origin/main` baseline run. So the growth cannot be attributed to the rule or cleared of it.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:234` "A break leads the description unless the next release … is a major" | a break in a 0.x project whose next release is 0.6.0 | a `Breaking changes` lead, though 0.x minors may break by convention | "unless … is a major, or the version scheme allows breaks in it (0.x, calendar versions)" |

Not findings:
- `:252`, ended by "slot 3's break lines": only caller-observable outcomes qualify, so an internal helper's changed return value does not lead.
- `:255`, ended by "A change with no break has neither the lead nor an empty heading".
- `:259`, ended by "Where §4 rule 5 makes the description the commit body".

## Item 3a: level, placement, and the environment
*Analogue: file placement, layout, the gates.*

- **Overlong line.** `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters. This file is not excluded by `FILTER_REGEX_EXCLUDE`, and the repository pins MD013 at 120 (`markdown-line-length-120`), so the super-linter will flag it.
- **Placement and gates.** The result and prompt files match the exclusion regex. Placing the cases under `research/…/cases/` matches the existing research layout, and the research README now lists it. I did not run `make check` or `make check-descriptions`, which need `uvx` and the network. The description field is unchanged.

## Item 4: names by content, not by position
None. The case directories, checks, and headings are named by content (`pgjdbc-4392-no-break`, "Result shape is a break"). The checks are cited by number only inside the table of the README that defines them.

## Item 5: the failure report
*Analogue: each rule's detection.*

None. Checklist line `:849` reaches the new rule and checks both the lead and the absence of an empty heading. The problem line `:831` was updated for the reordered body. The six checks in the 4367 README each test the property they name.

## Item 6: what the writer says it verified
*Analogue: an exemplar that passes, a bad case that fails, and the noise input.*

- **Present:** the bad case (4367 baselines: Why first, result shape in slot 3, `grant insert` in Scope), the exemplar runs that pass, and the noise input (4392) with a check that no section appears.
- **Missing:** the output-did-not-grow check on 4392 against a baseline (item 3).
- **Partial pass, disclosed:** the README states that one of the two Opus runs still fails check 3.

## Item 7: siblings of the change
*Analogue: indexes, manifests, umbrella pins.*

None.
- The version is bumped consistently in all three places, and the umbrella `qubership-repo-essentials` refers to the package by path, not by version.
- The marketplace and frontmatter descriptions are unchanged and do not need the new rule to decide loading.
- The changelog section (`:543`) deliberately keeps breaks in place and does not contradict the new rule, because it serves a different reader.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote a rule wording that was not committed ("promises compatibility") | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote `SKILL.md:234` as committed |
| Line over 120 characters in a linted file | Substantive | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap |
| "Reviewer's first question" contradicts the new "first decision"; slot 3's Reader column omits R1 | Substantive | `SKILL.md:204`, `:198`, `:243` | Qualify `:204` (after any breaks) or reconcile the two; add R1 to slot 3's readers |
| Major-release, unknown-release, and commit-body or squash arms have no case | Substantive | `SKILL.md:248-260` | One case per arm, or drop the claim from the commit message |
| Negative control has no baseline, so word growth is unattributed | Substantive | `cases/pgjdbc-4392-no-break/README.md:22-25` | Run 4392 on the base tree and compare |
| No clause for version schemes where a non-major may break (0.x) | Substantive | `SKILL.md:234`, `:243` | Add the ending clause in the instruction table |
| Commit message says "effort high" for both models; Opus ran at the default | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md:33-34` | "Haiku at effort high" |
| Version-bump hunks not claimed by any sentence | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." as earlier commits do |
| "The trailer decides" does not say what it decides (whether the release is a major, so no lead?) | Taste | `SKILL.md:247-248` | Name the object: "the trailer makes it a major" |
| `git archive <rev> …` writes a tar stream that the README does not say to extract | Taste | `cases/pgjdbc-4367-breaks/README.md:29-30` | Add `\| tar -x -C <dir>` |

Not checked: I did not rerun any model, did not run `make check`, `make check-descriptions`, or super-linter (they need the network), did not verify the quoted model prices, and did not do a style-only pass over the prose.
