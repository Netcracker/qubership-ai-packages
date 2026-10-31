# Final review: `4f69810..86028c3`, one commit

`feat(change-description-authoring): lead the description with breaks unless the next release is a major`

There was no separate task statement, so the claimed cases come from the commit message alone. The change has no code: a skill, a package README, three version bumps, and a research directory of cases. I filled the form through the §2a analogues and loaded the developer-style skill. The repository's copy of `apm-authoring` has no rule *Fix a bad output where the rule stops*, so I cite final-review §2a for that rule instead. I ran `comment-drift.py 4f69810 HEAD`. It printed nothing, because it does not parse Markdown or YAML. There is no previous report.

Below, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`, and `cases/` means `research/change-description-authoring/cases/`.

## Item 1: comments consistent with the code and with each other

Analogue: statements one file makes about another file or a rule, and other statements in `SKILL.md` about where a break goes.

- **The checklist contradicts the new rule.** `SKILL.md:843-845` (the "Caller" line, unchanged) asks whether the description carries "one line per distinct outcome under 'User-visible changes', breaks first". The new "Breaks" line at `:848-850` asks whether "slot 3 keep[s] only the other outcomes". A reviewer who applies the Caller line flags every description that correctly leads with its breaks.
- **Under §4 rule 5, the breaks lose the label that R4 and R5 search for.**
  - `:252` puts the lead "under a `Breaking changes` heading where the description has headings". A description that §4 rule 5 copies into the commit "takes the body's shape" (`:307`), and the checklist (`:855-857`) says headings are absent there.
  - `:258-260` says such a body "opens with its breaks and then its problem", and slot 3 "keeps the other outcomes".
  - So the break lines open the commit with no `User-visible:` label. Yet `:258` gives the reason the commit body keeps them under that label: "the label is what R4 and R5 search for".
  - `:209-210` also still says that under rule 5 slot 3 "is written there as `User-visible:` … lines". Nothing says how the leading break lines are labeled there.
- **The trailer sentence can be read two ways.** `:247-248` says: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." It does not say what the trailer decides.
  - §5 (`:706`) says to write the trailer whenever the tool is present. One reading is therefore "every break makes the next release a major, so the breaks never lead in such a repository".
  - The other reading is "the trailer, not the version file, says whether this is a major". Under that reading the reviewer's ship-or-not decision, which the rule exists for, is exactly the one this repository faces.
- **The case READMEs quote a rule that is no longer the committed one.** `cases/pgjdbc-4367-breaks/README.md:8` and `cases/pgjdbc-4392-no-break/README.md:6` quote "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` is "…unless the next release from the target branch is a major". The 4367 README says itself that the committed version was "reworded after review".
- **The commit message misstates the effort level.** It says "on Opus and Haiku (effort high)". `cases/pgjdbc-4367-breaks/README.md:26-27` says "Haiku ran at effort `high`; Opus at the session's default".
- **Another rule in the file pulls the other way.** `SKILL.md:488-492` (Scope, unchanged) says to keep "whether a compatibility break is intended … in the Scope slot as a question". The new `:239-240` says an extended failure "goes with the breaks, not in the Scope slot". Both can hold at once (the break line leads, and the question stays in Scope), but neither sentence says so. The one Opus run that left `grant insert` in Scope is the reading this allows.
- Checked and consistent:
  - The `Problem` slot text (`:86-87`) and the Problem checklist line (`:830-831`) state the same exception as `:258-260`.
  - The package README bullet matches the rule.
  - The research README file list now includes `cases/`.
  - §3's changelog rule ("marked in place … a separate top block is a house option") governs a different artifact and does not conflict.
- Taste: `cases/*/prompt.md` says `gradle.properties` holds `42.7.14` and the latest tag is `REL42.7.14`. In that case the version file names the last release, not the next one. The result is the same (not a major), and I could not check these facts offline.
- No sentence narrates the change.

## Item 2: claimed cases covered

Claims from the commit message, each with the section that handles it and the run that covers it:

| Claim | Section | Run |
| --- | --- | --- |
| The breaks lead unless the next release is a major | `SKILL.md:234`, `:252-255` | `pgjdbc-4367-breaks`, 4 runs with the rule, 2 baseline runs |
| The release is read from the version file, the milestone, or the branch name | `:244-247` | The 4367 prompt gives a version file only |
| The breaks lead where nothing says which release it is | `:248-250` | none |
| The definition of a break: new failure, return value or result shape, removed option, changed default or error code, extended failure | `:234-241` | 4367 covers a new failure, a result shape, and an extended failure; none of the other kinds is covered |
| The commit body keeps the problem first, with the breaks as the first `User-visible:` lines | `:257-258` | none |
| Where a squash copies the description, the lead stays | `:258-260` | none |
| A change with no break grows no section | `:255`, §7 | `pgjdbc-4392-no-break`, 4 runs |
| The results as stated (4 of 4 lead, 3 of 4 move `grant insert`, the control grows nothing) | the case READMEs | Verified against the result files; `skill-tree` matches `HEAD:<skill dir>` (`4798053`), and the baseline tree matches `HEAD~1` (`1f020ce`) |

**Commands.** `cases/pgjdbc-4367-breaks/README.md:22-23` says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". Nothing in the repository runs that command. As written, `git archive` writes a tar stream to stdout and copies nothing to disk unless the output is piped to `tar -x` or written with `-o`. The documented form differs from any form that copies the files.

**Hunks no sentence claims.** The version bump `1.4.0` → `1.5.0` in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and the package `apm.yml:2` is unclaimed. The previous commit did the same, and `apm-authoring` "Versions" asks for a bump when the contract changes. Taste.

## Item 3: boundaries, partitions, and the negative control

Analogue: the modes the change claims, and the control arms of its trials.

The trials cover two partitions: a non-major release with breaks (4367), and a non-major release without breaks (4392, the control). These partitions are claimed but have no run:

- **The next release is a major.** This is the branch that `unless` creates, and so the control for the rule itself. A substantive finding: a 4367 variant whose prompt says the version file holds `43.0.0`, run to check that the breaks stay in slot 3.
- **Unknown release.** No version file, milestone, or branch name.
- **Description copied into the commit body** (§4 rule 5).
- **The commit body**, with breaks first among the `User-visible:` lines.
- **A release tool that reads `BREAKING CHANGE:`.**

Only the major-release partition is filed as a finding. The others are listed for completeness.

Instructions the change adds or widens: 4. The checklist line at `:848`, the Problem-slot sentence at `:86`, and the package README bullet restate them.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:243` "Read the next release from the target branch" | a 0.x project whose minor releases are where it ships breaks | breaks lead every 0.x description, since `0.7.0` is not a major | "or a 0.x release where the project's policy lets minors break" |
| `:234` "A break leads the description…" | a change to an API the project documents as unstable (`@Beta`, `internal`) | a `Breaking changes` lead for an API with no compatibility promise | "a break in an API the project exempts from compatibility does not lead" |

Both rows are taste: the artifact does not address these inputs at all.

Not findings:

- `:234`, a break introduced and removed again since the last release, is ended by "code that works on the released version".
- `:254`, a release that is a major, is ended by "Where the next release is a major, the breaks stay first in slot 3".
- `:255`, a change with no break, is ended by "A change with no break has neither the lead nor an empty heading".
- `:252`, a §4 rule 5 description, is filed under item 1 (the label).

## Item 3a: level, placement, and the environment

- The rule sits in §2 next to the slot it changes, which is the right level. It is specific to this skill's slot model, not tutorial text.
- `python3 -I scripts/check-skill-descriptions.py` printed `ok: all 27 skill descriptions are within 1020 characters`.
- The result and prompt files match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`. The two case READMEs are linted. `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters, but other files in the repository already exceed 120, so I could not tell whether MD013 fails here. markdownlint is not installed.
- Taste: the sibling case directories name each model by its full ID (`research/problem-report-authoring/cases/*/claude-opus-5-5`, `claude-haiku-4-5`). This change uses `opus/` and `haiku/`, and those names will not say which Haiku once the next one ships.
- I did not run `apm pack --check-versions --check-clean`, because it needs `uvx` with network access. The three version strings agree.

## Item 4: names by content, not by position

- Taste: `SKILL.md:198`, a table cell, says "ahead of slot 1 unless the next release is a major (below)". It could point to the rule by its bold opening, "A break leads the description…".
- The `slot N` and `§N` references follow the skill's own numbering scheme throughout. The case checks are both numbered and named ("Lead (1)"). No other findings.

## Item 5: the failure report

- **The extended-failure clause has no checklist question.** The `:848` "Breaks" line asks whether the description opens with the break lines. It does not ask whether a failure extended to inputs that worked before is among them rather than in Scope. That is the one clause the case README shows runs still miss (1 of 4).
- The case checks say what failure looks like ("fails: in Scope", "fails: Why first"). Check 2 detects the result shape as a break line, not merely as present.

## Item 6: what the writer says it verified

- The exemplar passes and the bad case fails: 4367 with the rule passes checks 1–2 in 4 of 4 runs, and the baseline fails them in 2 of 2. The rule as committed is the one that ran: the `skill-tree` ids equal the committed tree.
- **The noise input has no baseline, so "did not grow" is not established.** The 4392 README compares word counts (241–256) with the author's draft (209), not with runs on `HEAD~1`. That leaves open whether the rule itself, rather than the rewrite, adds the 15–20 %. A substantive finding: two baseline runs per model on 4392, with word counts.

## Item 7: siblings of the change

Checked:

- The package README is updated.
- The instructions file and the frontmatter `description` (the surfaces that decide whether the skill loads) do not need a wider scope.
- The marketplace and root `apm.yml` entries are bumped together.
- The umbrella `qubership-repo-essentials` refers to the package by path and was not bumped by the previous bumps either.
- `english-*-developer-style` §"Changelog and release notes" defers breaking-change placement to this skill, so it does not conflict.
- `docs-page-authoring` and `test-authoring` only route to this skill.

No sentence counted the research directory's contents in a way that is now stale. None.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| The "Caller" checklist line puts all outcomes, breaks first, under "User-visible changes", which contradicts the new "Breaks" line | Substantive | `SKILL.md:843-845` | Add "or, where they lead, before the Why slot (§2)" to the Caller line |
| Under §4 rule 5 the leading break lines carry no `User-visible:` label, though `:258` says that label is what R4 and R5 search for | Substantive | `SKILL.md:252`, `:258-260`, `:209-210` | Say which label the break lines carry when they open a rule-5 body, for example the `User-visible:` paragraph moved to the top |
| "The trailer decides" has no object: either breaks never lead in a release-please repository, or the trailer replaces the version file | Substantive | `SKILL.md:247-248` | State what the trailer decides and what happens to the lead |
| The case READMEs quote a superseded wording of the rule | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed heading from `SKILL.md:234` |
| The commit message says both models ran at effort high; the README says Opus ran at the session default | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md:26-27` | Make the commit message match the README |
| No run for a next release that is a major, the control for `unless` | Substantive | `cases/` | Add a 4367 variant with a major version file, and check that the breaks stay in slot 3 |
| The negative control's growth is measured against the draft, not against a baseline run | Substantive | `cases/pgjdbc-4392-no-break/README.md:23-25` | Run `HEAD~1` on 4392, two runs per model, and record word counts |
| The checklist does not reach the extended-failure clause, the one runs still miss | Substantive | `SKILL.md:848-851` | Add "is a failure extended to inputs that worked before among the breaks, not in Scope?" |
| The `git archive <rev> …` command as written writes a tar stream to stdout and copies nothing | Substantive | `cases/pgjdbc-4367-breaks/README.md:22-23` | Give the form that runs, for example `git archive <rev> <path> \| tar -x -C <dir>` |
| The Scope rule on a break's intent and the new "not in the Scope slot" sentence are not reconciled | Taste | `SKILL.md:488-492`, `:239-240` | One clause saying the break line leads and only the question stays in Scope |
| 0.x projects and APIs documented as unstable are not addressed | Taste | `SKILL.md:234`, `:243` | A clause, if wanted |
| The version bump is unclaimed in the commit message | Taste | `apm.yml:168` and two siblings | A sentence, or leave it as the house convention |
| The model directories are `opus/` and `haiku/`, not full model IDs as in the sibling cases | Taste | `cases/*/opus`, `cases/*/haiku` | Rename to `claude-opus-5-5` and `claude-haiku-5-5` |
| "(below)" is a position reference | Taste | `SKILL.md:198` | Name the rule by its opening words |

I did not run the model trials, markdownlint, or `apm pack --check-clean` (no network or tool), I could not open the pgjdbc pull requests cited as the source of the cases, and I did not review the prose for style alone.
