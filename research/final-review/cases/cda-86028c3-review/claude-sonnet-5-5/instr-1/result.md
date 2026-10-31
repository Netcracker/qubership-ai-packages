# Final review: `4f69810..HEAD` (commit `86028c3`)

**Inputs.**
- There is no task statement. Item 2 takes its claimed cases from the commit message alone.
- No earlier report exists.
- I did not run the drift script's output through the form. It printed nothing, because the changed files are Markdown, YAML and JSON with no members to parse.
- Every item below therefore uses the §2a analogue for a change with no code.
- I loaded `apm-authoring` and `english-developer-style` from the given skills directory. The change is a skill plus research cases, so no `docs-page-authoring` applies.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **Stale quote of the rule's heading.**
  - `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:8` and `pgjdbc-4392-no-break/README.md:7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - `SKILL.md:234` reads "A break leads the description unless the next release from the target branch is a major".
  - The quote is false, and it contradicts the mechanism: the rule is now keyed on "a major", not on "promises compatibility". A reader who greps for the quoted heading finds nothing.
- **"In order" against a lead that precedes slot 1.**
  - `SKILL.md:192` says "Six slots, in order".
  - Line 198 and lines 252–255 now place slot 3's break lines ahead of slot 1.
  - Line 86 (commit slot 1) and line 831 (checklist) were both updated for the new order, but the table's own statement "in order" and the next sentence, "The Why slot has no skip condition" (line 210), were not.
  - A reader can take the table as the order of the description. The lead is defined in prose below the table, so this is one more rule to hold.
- **"The trailer decides" (`SKILL.md:247–248`) reads two ways.**
  - It can mean that the trailer makes the release a major, so the breaks need not lead.
  - It can also mean that the trailer is written and the lead still applies. "Written whatever the description does" supports the second reading, but the sentence before it does not.
  - For a description that carries a trailer, the two readings give different outputs. This is taste: I prefer one explicit clause stating whether the lead still applies once the trailer is present.
- **Cross-references.** I checked these: `§2` (pull request description), `§4 rule 5` (`SKILL.md:637`), `§5` (the `BREAKING CHANGE:` row, line 706), and `§7` (line 787, "No section for an absent concern"). All resolve.
- **Narration.** There is none (`now`, `no longer`, `used to`) in the added skill text. The case READMEs narrate runs, which is their job.

## Item 2: claimed cases covered (analogue: sections and runs that cover each claim)

The commit message claims these cases:

| Claim | Covered by |
| --- | --- |
| Breaks lead the description in a non-major release | 4367 check 1 and the runs `opus/result.md`, `opus/result-2.md`, `haiku/result.md`, `haiku/result-2.md` |
| The result shape counts as a break | 4367 check 2 and the same four runs |
| A failure extended to later statements counts as a break | 4367 check 3 and the same four runs (`opus/result-2.md` fails it, and the README says so) |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | None. No case produces a commit body. |
| Squash copies the description, so the lead stays | None. |
| Leads where nothing says which release it is | None. The 4367 prompt targets `master` at 42.7.x. |
| Next release is a major, so no lead and the breaks stay first in slot 3 | None. |
| A change with no break grows no section | 4392 checks 1 and 2, four runs |
| Without the rule, Why comes first and both breaks stay in place | Both `baseline/result.md` files |

- **Run settings.**
  - The commit message says "on Opus and Haiku (effort high)".
  - The case README (`pgjdbc-4367-breaks/README.md`, "Running it") says "Haiku ran at effort `high`; Opus at the session's default".
  - These two statements disagree about Opus.
- **Counts.** I checked the numbers against the stored files and they match:
  - 6 runs for 4367 and 4 for 4392.
  - Word counts of 756, 825, 792, 758, 779 and 784, and 241, 251, 256 and 249.
  - Haiku: a `Generated with` line in all three 4367 runs and both 4392 runs.
  - Skill-tree ids: baselines `1f020ce…` are the parent's tree, and the other runs `4798053…` are `HEAD`'s tree, so the runs used the committed skill.
- **Commands.** The change tells a reader to run no command.
- **Hunks.** Every hunk belongs to a sentence of the commit message. The version bumps in `apm.yml`, `marketplace.json` and the package `apm.yml` are consistent with each other (1.4.0 to 1.5.0), and the research README lines are claimed by "Two regression cases".

## Item 3: boundaries, partitions, and the negative control (analogue: genres, modes, state)

- **Partitions the change claims but no run exercises.**
  - The partitions are: next release is a major; the release is unknown; a `BREAKING CHANGE:` trailer is present; the commit-body shape; and the squash-copy shape.
  - The only trial is the PR description targeting a 42.7.x patch release.
  - The negative control (4392) varies the change, not the release. It targets the same `master`.
  - So "unless … a major" has no control arm, and the "unknown" branch has no run.
- **Pre-existing state.** None applies. This is a skill upgrade, and the case prompts are fresh drafts.
- **Existing settings reaching a new consumer.** None.
- **Limits and replaced mechanisms.** None.

Added instructions: 2, rows follow.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:252` "opens with slot 3's break lines, under a `Breaking changes` heading … after at most a short paragraph that says which code breaks" | A break that is a single line, in a tiny description with no template | A heading plus an intro paragraph for one line | "only where the breaks run to more than one line" |
| `:857–860` the commit body "opens with its breaks and then its problem" when a squash copies a leading description | A description whose only break is one sentence | A commit body that starts with the break before the problem, against R2 | The paragraph two lines earlier says "problem first"; the squash-copy case needs a stated exception to `:257` |

The second row is closer to a conflict than a row. `:257` says the commit body keeps problem-first, and `:259–260` and `:87` say the copied body opens with breaks. The text does say the copied body is the exception. But the squash-copy exception is the only place R2 is overridden by a reviewer-order rule, and it has no run. It is filed as a finding under item 2 rather than adding to the rows.

Not findings: `:249–251` (the unknown-release default ends the "which release" question), `:238–240` (the extended-failure clause is supported by the 4367 runs and the `Scope` reference).

## Item 3a: level, placement, and the environment (analogue: file placement and registration)

- The rule sits in `SKILL.md` §2 and the checklist in §8. The package README bullet is added.
- Registration is consistent: the package `apm.yml`, the root `apm.yml` and `.claude-plugin/marketplace.json` all carry 1.5.0. I did not run a gate.
- The skill's frontmatter `description:` was not widened. It already says it governs "what each artifact says and for whom" and "the slots of a commit body and a description". So the surface that decides loading does not miss the new rule.
- Does the new text pass `apm-authoring` rule 1 ("Encode platform-specific knowledge, nothing else")? Mostly yes. The sentence "A Why and a What read before that decision are wasted on a reviewer who decides no" (`SKILL.md:243`) is a rationale a tutorial could carry. It has a level of its own here because it is the reason for the lead. This is taste, and I prefer keeping it.
- The new version-file list (`gradle.properties`, `pom.xml`, `package.json`, `Cargo.toml`) is the kind of ecosystem knowledge that rule 1 says to leave out, but it is the file list the agent reads, so it stays.

## Item 4: names by content, not by position

- None. Case directories are named by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). Checks are numbered 1–6 and 1–3 in the READMEs, and the results table refers to them by name (Lead, Result shape, `grant insert`), so the ordinals have a content name beside them.
- The README text "Checks 1 to 3 are the rule under test; 4 to 6 are the guard" uses the ordinals alone. This is taste: naming the checks by their column names would survive an insertion.

## Item 5: the failure report

- None applies: no assertions. The case tables name the failing check per run ("fails: in Scope"), so a failure is attributable.

## Item 6: what the writer says it verified

- The commit states the runs on the committed skill tree and on `origin/main` (baselines). Tree ids in `skill-tree` files confirm them.
- The bad case for the rule (baseline) fails checks 1–3, and the committed skill passes them in three of four runs. The commit message says so honestly ("one Opus run left it there").
- Evidence for the negative control exists (four runs, none grows a section).
- Missing: no run of the added checklist item (§8 "Breaks"), and no run of the rewritten Problem checklist item (`:831`). The writer does not claim them.
- The sample is small (one 4367 prompt, two runs per model). The commit message does not overclaim this.

## Item 7: siblings of the change

- Sibling skills that cite this one (`english-developer-style`, `docs-page-authoring`) only point at the package and do not restate the slot order.
- `git grep` for the old phrase "Breaks first" finds only `SKILL.md:198`, which was updated.
- The §8 checklist, the §2 table, the commit-body slot text (`:86`) and the package README bullet all carry the new rule.
- Sets: no members were added to a list.
- Not read: the changelog-entry section (§2 changelog entry and §3) carries its own "Breaking" prefix rule (`:543`). It is a different artifact and is unaffected, but I did not check that its wording is consistent with "breaks lead" for a changelog.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "…where the next release … promises compatibility"; the heading reads "…unless the next release … is a major" | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | Replace the quote with the current sentence |
| Commit message says Opus ran at effort high; the case README says Opus ran at the session's default | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md` "Running it" | Make the two agree (correct whichever is wrong) |
| "Major" branch, unknown-release branch, trailer, commit-body shape and squash-copy shape are claimed but have no run | Substantive | commit message; `SKILL.md:234–260` | Add a control run targeting a major (the lead absent), or say in the commit and case README that only the patch-release branch was tried |
| "Six slots, in order" and "The Why slot has no skip condition" read against a lead that precedes slot 1 | Substantive | `SKILL.md:192`, `:210` | State beside the table that the break lines may precede slot 1 (`(below)` already points there), or drop "in order" |
| "The trailer decides" can mean the lead is dropped or kept | Taste | `SKILL.md:247–248` | State in one clause whether the lead still applies when the trailer is written |
| Checks referred to by ordinal in "Checks 1 to 3 … 4 to 6" | Taste | `cases/pgjdbc-4367-breaks/README.md` | Name the checks by content |

**Not checked:** I did not run `apm compile`, markdownlint or any repository gate, did not run any case, and did not read the changelog-entry section for consistency. The drift script gave no output, and I did no pass over the prose for style alone.
