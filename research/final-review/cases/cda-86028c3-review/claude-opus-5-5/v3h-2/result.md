I found nine things worth changing. The most serious: an unedited sentence in SKILL.md now contradicts the new rule, three of the six cases the commit claims were never run, and the skill's own checklist would pass the exact draft that motivated the change. The full report follows.

# Final review: `4f69810..86028c3` (one commit)

There is no previous report of this form for this change. There was no task statement either, so the claimed cases come from the commit message and the two case READMEs. The change has no code: it is a skill, a package README, version entries, and research cases. Each item below uses the §2a analogue, and the instruction table is under item 3. I ran `comment-drift.py` and it printed nothing, because nothing in the change is a code member it can parse. I loaded `english-developer-style` and read `apm-authoring` from the repository as the authoring skill.

## 1. Comments consistent with the code and with each other (analogue: statements one file makes about another)

- **SKILL.md:192 and :203–204 contradict the new rule** (substantive).
  - These sentences were not edited and are still there: "Six slots, in order" and "the reviewer's first question is why that version should change".
  - The new :243 says: "In a release that is not a major, the reviewer's first decision is whether the change may ship in it at all."
  - Together these give two different "first" questions for the same reviewer. The table also claims an order that the new lead overrides.
  - A reader of :204 would put Why first, which is the behavior the change set out to remove.
- **Both case READMEs quote a rule SKILL.md does not contain** (substantive).
  - `cases/pgjdbc-4367-breaks/README.md:7–8` and `cases/pgjdbc-4392-no-break/README.md:6–7` quote "A break leads the description where the next release from the target branch promises compatibility".
  - SKILL.md:234 actually reads "…unless the next release from the target branch is a major". The quote looks like the pre-review wording that README:49–52 mentions.
  - A reader who searches the skill for the quoted text finds nothing.
- **The commit message misstates the Opus effort** (substantive).
  - It says "on Opus and Haiku (effort high)", which reads as both models at effort high.
  - The case README:33–34 says Opus ran "at the session's default".
- **Checked and consistent:**
  - Cross-references: §4 rule 5 is :637, §5 is :706 (the `BREAKING CHANGE:` row), and §7 is :788 ("an empty heading is not a gap to fill").
  - The package README bullet agrees with the rule.
  - Version 1.5.0 is the same in all three places, and `make check` reports "Version alignment OK".
  - The `skill-tree` ids match: 4798053… equals `HEAD:<skill dir>`, and the baseline id 1f020ce… equals `4f69810:<skill dir>`.
  - The word counts in both results tables match `wc -w`.
  - "All three Haiku results" and "Both Haiku results" do each end with a "Generated with" line.

## 2. Claimed cases covered

Claims come from the commit message only, as there is no task statement.

| Claimed case | Covered by |
| --- | --- |
| Breaks lead when the next release is not a major | `pgjdbc-4367-breaks`, checks 1–3, four with-rule runs and two baseline runs |
| A result-shape change counts as a break | 4367 check 2 |
| A failure extended to inputs that worked before counts as a break | 4367 check 3; 3 of 4 runs pass |
| The next release is read from the version file, milestone, or branch name | 4367 only, from the version file; the milestone and branch-name paths are untested |
| Breaks lead when nothing says which release it is | **none** |
| The next release is a major, so breaks stay in slot 3 | **none** |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | **none** (both prompts ask only for a PR description) |
| Squash copies the description, so the lead stays in the body | **none** (the prompts give `squash 3 plain 37`, with no squash run) |
| No break means no section is added | `pgjdbc-4392-no-break`, checks 1–2 |

The missing rows are filed under item 3.

**Commands:** 4367 README:29–30 documents `git archive <rev> agent-packages/…/change-description-authoring`, saying the skill is "copied out of the checkout" with it. Nothing in the repository runs that form. As written, `git archive` writes a tar stream to stdout, so the copy the README promises needs `| tar -x -C <dir>`. Taste: the command is provenance, not a recipe.

**Unclaimed hunks:** the version bump from 1.4.0 to 1.5.0 in `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json` has no sentence in the commit message. The parent's parent, d79c43d, did state its bump ("Version 1.2.0 to 1.3.0"). Substantive, but small. The other hunks are all claimed.

## 3. Boundaries, partitions, and the negative control (analogue: the partitions the change claims, plus the added-instruction table)

- **Only the "patch release, version file" corner is exercised** (substantive). There is no run for these claimed partitions:
  - the next release is a major (the control in which breaks must **not** lead);
  - the next release is unknown;
  - a release tool reads `BREAKING CHANGE:` or `!`;
  - the commit body;
  - squash copying the description.

  The 4392 control covers "no break". It does not cover "break, but major", which is the other value of the setting that decides the rule. The request is one case on a branch whose version file names the next major, plus one commit-message case.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides" | a release-please repo at 2.3.1; the PR is `feat!: …` | "the trailer makes the next release a major", so no lead; the reviewer deciding whether to accept a 3.0 reads Why first | "the trailer marks the break; whether the next release may be a major is the maintainer's decision, so the breaks lead" (or state what the trailer decides) |
| `:243` "Read the next release from the target branch … unless … a major" | a SemVer crate at 0.4.2 whose next release is 0.5.0 | breaks lead, although under SemVer a 0.x minor bump is where breaks may ship | "a major, or a minor below 1.0" (taste: :249 accepts the cost of a paragraph) |

Not findings:
- `:234` the break definition, ended by "Whether the old behavior was right does not decide it, and a failure that now succeeds is a fix, not a break".
- `:252` the lead itself, ended by "A change with no break has neither the lead nor an empty heading".
- `:257` the commit-body order, ended by "The commit body keeps its order, problem first".
- `:86` the slot 1 amendment, ended by "A description that §4 rule 5 copies into the body and that leads with its breaks".
- The `:198` table cell is the same instruction as :234–255.
- The checklist line at `:849` is filed under item 5.

## 3a. Level, placement, and the environment

- **The case layout differs from its siblings** (substantive).
  - Sibling cases use the full model id as the directory name: `problem-report-authoring/cases/*/claude-opus-5-5/`, `claude-haiku-4-5/`, and `blackbox-test-design/.../with-skill-claude-opus-5-5/`.
  - This change uses `opus/` and `haiku/`. The exact model shows up only in the cost paragraph (README:60) and in the commit trailer.
  - The request is `claude-opus-5-5/` and `claude-haiku-5-5/`, or a sentence in the case README that names the ids.
- Lint coverage is correct: `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` excludes `prompt.md` and `result*.md`, and the case `README.md` files stay linted.
- `make check` passes offline, as does `scripts/check-skill-descriptions.py` ("all 27 skill descriptions are within 1020 characters").
- The rule lives in the PR-description section of §2, which is the section it governs.

## 4. Names by content, not by position

- `SKILL.md:198` "…unless the next release is a major (below)": "below" points by position. It could name the bold rule "A break leads the description…" instead. Taste: the target is close and unlikely to move.
- In the case README, "Checks 1 to 3 … 4 to 6" use numbers, but each check also has a name and the table pairs the two ("Lead (1)"). None.

## 5. The failure report (analogue: is each rule's detection reached by the checklist, and does it detect the rule?)

- **The checklist line at `SKILL.md:849–852` detects a weaker property than the rule** (substantive).
  - It asks only whether the description opens with the break lines and whether slot 3 keeps the rest.
  - Take a draft that leads with the two `**Breaks:**` lines, leaves the `getUpdateCount()` result-shape change in slot 3, and leaves `grant insert` in Scope. That draft passes the checklist line. It is the pgjdbc#4367 failure, and 2 of the 3 defects the commit message names.
  - The request is a clause such as: "is every result-shape change, changed default or error code, and failure extended to inputs that worked before among the breaks, and none left in Scope?"
- The Problem checklist line at :831 is amended consistently with :86.

## 6. What the writer says it verified

- **Stated:** the rule versus the baseline on 4367 (fails on the baseline, passes with the rule), runs on the committed tree, and the rewrite re-run after review. README:49–52 honestly reports the regression from 2/2 to 1/2 on Opus for `grant insert`.
- **The control has no baseline arm** (substantive).
  - Per §2a, the noise input owes "a check that the output there did not grow".
  - 4392 compares its with-rule outputs (241–256 words) only against the draft (209 words). There is no run on `4f69810`, so growth caused by the rule cannot be told apart from growth the skill already produced.
  - The request is two baseline runs of 4392, one per model, with word counts.

## 7. Siblings of the change

- The package README is updated. The marketplace and `apm.yml` descriptions are unchanged, and the change does not widen the skill's trigger scope, so that is correct.
- `english-us-developer-style` and `english-uk-developer-style` (:570) delegate the marking of breaking changes to this skill, so nothing there needs updating.
- No sentence anywhere counts the slots differently because of this change. The one stale statement, "Six slots, in order", is filed under item 1.
- `research/change-description-authoring/README.md` gains a `cases/` row and a paragraph, consistent with the files added.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| "reviewer's first question is why" and "Six slots, in order" contradict the break lead | substantive | `SKILL.md:192`, `:203–204` | Qualify both for the case where breaks lead |
| Case READMEs quote a rule wording SKILL.md does not have | substantive | `pgjdbc-4367-breaks/README.md:7–8`; `pgjdbc-4392-no-break/README.md:6–7` | Quote :234 as committed |
| The commit message says effort high for Opus; the README says session default | substantive | commit message ¶3 | Reword to "Haiku at effort high, Opus at the session default" |
| The major, unknown, trailer, commit-body, and squash partitions have no run; there is no "break, but major" control | substantive | `research/.../cases/` | Add a case with a major next release, and one commit-message case |
| "the trailer decides" names nothing decided; one reading exempts every `feat!` PR from the lead | substantive | `SKILL.md:247–248` | State what the trailer decides |
| The checklist line misses the break definition (result shape, extended failure) | substantive | `SKILL.md:849–852` | Add the definition check to the line |
| The control has no baseline arm, so its growth cannot be attributed | substantive | `pgjdbc-4392-no-break/README.md:22–25` | Run 4392 on `4f69810` and report word counts |
| The version bump is not claimed in the commit message | substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | One sentence: "Version 1.4.0 to 1.5.0." |
| Model directories are `opus/` and `haiku/`, not the model ids the siblings use | substantive | `pgjdbc-*/opus`, `/haiku` | Rename them, or name the ids in the README |
| A 0.x SemVer minor is treated as not a major | taste | `SKILL.md:243` | "a major, or a minor below 1.0" |
| `(below)` is a positional reference | taste | `SKILL.md:198` | Name the rule |
| The `git archive` recipe does not produce a copy without `tar -x` | taste | `pgjdbc-4367-breaks/README.md:29–30` | Add `\| tar -x -C <dir>` |

I did not re-run any model case, run super-linter or markdownlint (neither is installed), check the claims about pgjdbc#4367 and #4392 against GitHub (there is no network), or make a style-only pass over the prose.
