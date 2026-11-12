I reviewed `4f69810..HEAD` (commit 86028c3) and found eight substantive findings and three taste findings; the main table is at the end. The change has no code: it edits `change-description-authoring` SKILL.md, the package README, three version fields, and adds two regression cases under `research/change-description-authoring/cases/`. So the form is filled through its no-code analogues for a skill. There was no task statement, so I took the claimed cases from the commit message alone. I loaded `english-developer-style` and `test-authoring` from the given directory. `apm-authoring` is not among the three copies I was allowed to load, so where the form cites its rules I applied them as the form quotes them. The drift script ran and printed nothing, as expected for Markdown and YAML.

## Item 1: comments consistent with the code and with each other
*Analogue used: statements one file makes about another, and rules that conflict.*

- **`SKILL.md:844-848`, the "Caller" checklist line (unchanged)** still asks whether every outcome sits under "User-visible changes", breaks first. The new "Breaks" line at `:849-852` asks that slot 3 keep only the other outcomes. Take a patch-release description that leads with its breaks, which is what the new rule produces. The Caller line fails it and the Breaks line passes it.
- **`SKILL.md:487-493` against `:238-240`.** The Scope rule says that where only a maintainer can tell whether a compatibility break is intended, the question goes in the Scope slot, because "the code shows the break". The new rule says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot." Take a break whose intent is open, like the `grant insert` case (the draft keeps it in Scope and argues why it is not narrowed). Two rules then send it to two places. The one Opus run that left `grant insert` in Scope (`opus/result-2.md`) fits that reading.
- **`SKILL.md:247-248`.** "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does" can be read two ways:
  - The trailer decides that the next release is a major. Then in every repository running release-please or semantic-release (both named in §5), the breaks never lead, even though the reviewer's first decision, whether to accept a major bump, is the one the rule's own reason says must come first.
  - The trailer decides only the bump. Then "decides" says nothing about the lead.
- **`pgjdbc-4367-breaks/README.md:6-7` and `pgjdbc-4392-no-break/README.md:5-6`** quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility". The committed rule (`SKILL.md:234`) says "unless the next release from the target branch is a major". The runs used the committed text: the `skill-tree` id `4798053…` equals `HEAD:` of the skill directory. So only the quote is stale, and a reader searching SKILL.md for it finds nothing.
- **Commit message against `pgjdbc-4367-breaks/README.md:28`.** The commit says "on Opus and Haiku (effort high)". The README says Haiku ran at effort `high` and Opus at the session's default.

No sentence narrates the change ("now", "no longer") inside SKILL.md; the "now" in the commit message is fine there.

## Item 2: claimed cases covered
*Analogue used: the section that handles each case, and the case that tests it.*

Taken from the commit message alone, since there was no task statement:

| Claimed case | Section | Test |
| --- | --- | --- |
| Breaks lead when the next release is not a major (known from the version file) | `:234-255` | `pgjdbc-4367-breaks` check 1, 4/4 runs |
| Read from the milestone | `:245` | **none** (prompt says "no milestone") |
| Read from a maintenance-branch name | `:246` | **none** |
| Breaks lead where nothing says which release it is | `:248-250` | **none** |
| Next release is a major: breaks stay first in slot 3 | `:254-255` | **none** |
| Break kinds: new failure | `:235-236` | 4367 (`42703`, `0100E` lines) |
| Break kinds: result shape | `:236-237` | 4367 check 2, 4/4 |
| Break kinds: removed option, changed default, changed error code | `:237-238` | **none** (claimed as a list; one exemplar per kind is not owed, noted) |
| Break kinds: failure extended to later inputs | `:238-240` | 4367 check 3, 3/4 |
| A fix is not a break | `:241` | 4367 check 4 |
| Commit body keeps the problem first, breaks as the first `User-visible:` lines | `:257-258` | **none** (both prompts ask for a PR description only) |
| Under squash "title and description", the lead stays in the body | `:259-260`, `:86-87` | **none** (both prompts give `merge 0 squash 3 plain 37`, so the description is never copied) |
| No break grows no section | `:255` | `pgjdbc-4392-no-break`, 4/4 |

**Commands:** `pgjdbc-4367-breaks/README.md:22-23` says to copy the skill out with `git archive <rev> agent-packages/…`. I ran it locally: it emits a tar stream that lists SKILL.md and `references/merge-model.md`, so it "copies out" only when piped to `tar -x`. No script or CI job runs it.

**Hunks no sentence claims:** the version bump 1.4.0 → 1.5.0 in `.claude-plugin/marketplace.json:291`, `apm.yml:168`, and `agent-packages/change-description-authoring/apm.yml:2`. Earlier commits in this series state it ("Version 1.2.0 to 1.3.0."); this one does not. The package README bullet and the research README rows are covered by the rule and case sentences.

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the claimed modes as partitions, the control arm, and the table of added instructions.*

- The negative control exists: `pgjdbc-4392-no-break`, on the same `master`, passes 4/4 with no heading and no compatibility sentence.
- **Partitions with no evidence:** next release is a major; release unknown; release read from a milestone or a branch name; the commit-body order; the lead surviving rule 5. That is six claimed situations, one of which has a trial. Both prompts fix the same target (`42.7.14`, no milestone) and the same rebase-like merge model.
- Pre-existing state does not apply: there is no persisted format, only an installed skill text.

Added instructions: 6, no rows. They are: `:86` the problem right after the breaks; `:198` the table cell; `:234` the break definition; `:243` read the next release; `:252` open with the break lines; `:257` the commit-body order. The checklist lines `:831` and `:849` restate them.

Not findings:
- `:252` "A change with no break has neither the lead nor an empty heading" ends the lead for the 4392 input.
- `:254` "Where the next release is a major, the breaks stay first in slot 3" ends it for a major.
- `:221-222` with `:233` keeps slot 3 present and non-empty only when it has outcomes.
- The trailer input (release-please) and the open-intent break (Scope) are filed under item 1, not as rows.

## Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, and the repository's own gate.*

- Placement is right: the rule sits in §2 "Pull request description" beside slot 3, has a checklist line in §8, and the cases sit under the research directory's new `cases/` row.
- `scripts/check-skill-descriptions.py` passes (27 descriptions ≤ 1020 characters).
- The super-linter `FILTER_REGEX_EXCLUDE` covers the new `prompt.md` and `result*.md` files, so only the READMEs are linted, and they have H1s.
- I did not run `make check` (the `apm pack --check-versions` gate), because it needs `uvx` downloads. The three version fields agree by inspection.
- No sentence reads like a generic tutorial.

## Item 4: names by content, not by position
- Taste: `SKILL.md:257-258` says "the first `User-visible:` lines of slot 4" inside the pull-request-description section, where slot 4 is Verification; "commit body" in the same sentence disambiguates it. The file numbers slots throughout, so this is a convention.
- Taste: `pgjdbc-4367-breaks/README.md:19` "Checks 1 to 3 are the rule under test; 4 to 6 are the guard" refers to checks by number, though each check has a bold name.

## Item 5: the failure report
*Analogue used: whether the checklist reaches each rule, and whether each detection detects the rule.*

The checklist reaches the lead (`:849`) and the problem order (`:831`). But the Breaks line detects a weaker property than the rule. It asks whether the description "open[s] with the break lines". It does not ask whether every break under the `:234-241` definition is among them, such as a result-shape change or a failure extended to later inputs rather than left in Scope. Those two are the misses that motivated the commit, and a description that leads with only the obvious breaks passes the line.

## Item 6: what the writer says it verified
*Analogue used: an exemplar the rule passes and a bad case it fails.*

The evidence is present:
- The bad case fails without the rule: both `baseline/` runs fail checks 1-3.
- The rule fixes it: 4/4 runs pass checks 1-2, and 3/4 pass check 3.
- The rule was rewritten after review, and the committed tree was re-run: the `skill-tree` ids equal `HEAD`'s tree, and the baseline tree equals `HEAD~1`'s.
- On the input where the item is noise (4392), the check is that no section appears.

Taste: the control has no baseline run, so its growth (241-256 words against the 209-word draft) cannot be attributed. Check 2 already shows that none of the growth is a compatibility section.

## Item 7: siblings of the change
*Analogue used: places that list or route to the artifact.*

- The package README gets a matching bullet.
- The marketplace and `apm.yml` descriptions are unchanged, and the scope is not widened, so they need no change.
- The changelog's "Breaking changes are marked in place and sorted first within their category" (`:543`) is another artifact, and its rule stays consistent.
- The `english-*-developer-style` packages defer breaking-change placement to this skill (`:570`).
- The unchanged sibling statements inside the same file are the Caller checklist line and the Scope rule, both filed under item 1.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The Caller checklist line still puts breaks under "User-visible changes", which contradicts the new Breaks line | Substantive | `SKILL.md:844-846` | Add "or leading the description where §2 puts them there" |
| The Scope rule keeps an open-intent break in Scope; the new rule says an extended failure goes with the breaks, not in Scope | Substantive | `SKILL.md:238-240`, `:487-493` | Add a clause: the break line leads, and the question whether it is intended stays in Scope, pointing at that line |
| "The trailer decides" can be read two ways; the first reading turns off the lead in every release-please or semantic-release repository | Substantive | `SKILL.md:247-248` | State what the trailer decides and whether a change that triggers the major bump still leads with its breaks |
| Case READMEs quote a superseded rule title ("promises compatibility") | Substantive | `pgjdbc-4367-breaks/README.md:6-7`, `pgjdbc-4392-no-break/README.md:5-6` | Quote the committed bold sentence |
| Commit message says both models ran at effort high; the README says Opus ran at the session default | Substantive | commit body, paragraph 3; `pgjdbc-4367-breaks/README.md:28` | Make the commit message match the README |
| Claimed partitions have no trial: major, unknown release, milestone or branch-name source, commit-body order, lead under rule 5 | Substantive | `SKILL.md:243-260`; cases | Add cases for at least "major" (the control arm of the lead) and "rule 5 squash", or narrow the commit message to what was run |
| The Breaks checklist line detects only that some break lines lead, not that every break by the `:234` definition is among them | Substantive | `SKILL.md:849-852` | Add "is every break by §2's definition among them, including a result-shape change and a failure extended to new inputs, and none left in Scope" |
| The version bump in three files is not claimed by the message | Substantive | `apm.yml:168`, `.claude-plugin/marketplace.json:291`, package `apm.yml:2` | Add "Version 1.4.0 to 1.5.0." as earlier commits do |
| "Is a major" is undefined for a 0.x version in `Cargo.toml` or `package.json`, which the rule names as sources | Taste | `SKILL.md:243-246` | Say whether a 0.x minor counts as a major |
| "slot 4" sits in the pull-request-description section, where slot 4 is Verification | Taste | `SKILL.md:257-258` | Say "the commit body's Outcome slot" |
| `git archive <rev> …` alone writes a tar stream; checks are cited by number | Taste | `pgjdbc-4367-breaks/README.md:19`, `:22-23` | Add `\| tar -x`; refer to checks by name |

What this review did not check: I ran no regression case again, did not run `make check` (it needs network for `uvx`/`apm`), did not read the pgjdbc pull requests the cases cite (no network), and did not do a style-only pass over the prose.
