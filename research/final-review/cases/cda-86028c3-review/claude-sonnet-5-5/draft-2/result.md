# Final review: `4f69810..HEAD` (86028c3, "lead the description with breaks unless the next release is a major")

**Inputs.**
- No task statement was handed over. The claimed cases come from the commit message alone.
- This is a change with no code, so §2a applies. Under each item I name the analogue I used.
- The drift script was not run: the diff has no members to parse.
- Skills loaded: `apm-authoring` and `english-developer-style`, from the given directory.
- There is no previous report.
- I did not run markdownlint; it is not installed here. `git diff --check` was clean.

## Item 1: comments consistent with the code and with each other

Analogue: every statement one changed file makes about another file, a section, or a count.

Two findings.

- **F1. `SKILL.md` contradicts itself on the shape of a description that becomes the commit body.**
  - Line 259 says that where §4 rule 5 makes the description the commit body, "the lead stays". The body then "opens with its breaks and then its problem".
  - Line 310 says that under rule 5 "the description is the commit body and takes the body's shape instead". Line 636 says "shape it as §2's commit body", which is Problem first (`:78`).
  - The commit message says the commit body "keeps the problem first". The new lead exception (`:259`, `:86`) is not stated at the rule that governs the case (`:636`, `:310`).
  - The new text also says the `User-visible:` label "is what R4 and R5 search for", which is why the commit body keeps it. A squash body that opens with a `Breaking changes` heading has no such label.
  - Two readings are possible: the squashed body leads with breaks, or it is problem-first with a `User-visible:` paragraph. An agent following `:636` gets the second, and one following `:259` gets the first.
  - Request: state the exception once at `:636` and `:310`, or drop it from `:259`. Say whether the squashed body keeps the `User-visible:` label as well as the lead.
  - Substantive.
- **F2. Both case READMEs quote a rule that no longer exists.**
  - `cases/pgjdbc-4367-breaks/README.md:7` (the intro paragraph) and `cases/pgjdbc-4392-no-break/README.md:6` quote SKILL.md §2 as "A break leads the description where the next release from the target branch promises compatibility".
  - The committed rule reads "A break leads the description unless the next release from the target branch is a major" (`SKILL.md:234`).
  - A reader who searches the skill for the quoted sentence finds nothing.
  - Request: quote the committed sentence.
  - Substantive.

I checked the rest of the file against its own cross-references. §7, §4 rule 5, and §5 `BREAKING CHANGE:` (`:706`) exist and say what the new text cites. The marketplace entry and the package `apm.yml` also say 1.5.0, as do the root `apm.yml` and `marketplace.json`. No `1.4.0` of this package is left outside `research/`. The package README bullet and the checklist item "Breaks" match the rule.

A sentence-level ambiguity at `SKILL.md:247` is filed as F5 under Item 3.

## Item 2: claimed cases covered

Analogue: the cases the commit message claims, each against the case or run that covers it. No command line is added for a reader to run. The `git archive` recipe in the case README is a recipe, not a documented run.

| Claimed | Covered by |
| --- | --- |
| Break leads when the target is a patch release | `pgjdbc-4367-breaks`, check 1, and the six runs in its table |
| Result-shape change is a break | check 2 |
| Extended failure leaves Scope (`grant insert`) | check 3. Opus `result-2` fails it, and the commit message says so |
| The fix is not a break; each break line appears once; literals kept | checks 4 to 6 |
| A change with no break grows no section | `pgjdbc-4392-no-break`, checks 1 to 3, four runs |
| No lead when the release is a major | none |
| The lead holds when nothing says which release it is | none |
| `BREAKING CHANGE:` trailer decides | none |
| A squash that copies the description keeps the lead | none |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | none. Both cases ask for a pull request description |

The uncovered rows are filed as F4 under Item 3.

Checks I made against the committed files:
- Word counts in both READMEs match `wc -w`: 756, 825, 792, 758, 779, 784 for 4367 and 241, 251, 256, 249 for 4392.
- The table cells match the results I read. `opus/result-2.md` leaves `grant insert` in Scope.
- Every `skill-tree` file matches `git rev-parse HEAD:<skill dir>` (`4798053…`) for the runs with the rule, and `1f020ce…` (the base tree) for the baselines.
- The Haiku "Generated with Claude Code" claim holds for the results I read.

One claim fails: the commit message says "Opus and Haiku (effort high)". The case README says "Haiku ran at effort `high`; Opus at the session's default", and the 4392 README gives effort only for Haiku. Opus's effort is not recorded the same way in the two places (F3).

Reading claims the other way: every hunk is claimed by the commit message. The version bump to 1.5.0 appears in four files, and the package README bullet and the research README `cases/` line are claimed with the change.

## Item 3: boundaries, partitions, and the negative control

Analogue: the partitions are the modes the rule names, and the negative control is its "does not apply" arm.

- **Negative control:** present, and it is the right one. `pgjdbc-4392-no-break` has a patch-release target, no break, and no lead or heading, in four runs.
- **F4. The other arms of the rule have no case.**
  - Three arms are claimed in the commit message and `SKILL.md` and have no evidence: the next release is a major, the release is unknown, and the description becomes the squashed commit body.
  - The major arm is the exception the rule's title names. An agent could lead with breaks in a major release, and nothing shows otherwise.
  - Request: add one run on a target whose version file says a major, with the same draft as `pgjdbc-4367-breaks`. The rule predicts the breaks stay first in slot 3, after Why. A run on a squash-merge setting would cover the commit-body arm, tied to F1.
  - Substantive.
- **F5. `SKILL.md:247` reads two ways.** "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does." One reading is that the trailer makes the release a major, so the breaks need not lead. The other is that the trailer is written regardless of where the breaks go. On the first reading, every break in a repository with such a tool escapes the lead. That removes the reviewer's early decision the section sets out to protect. Request: say which reading is meant. Taste.

Added instructions: 6, one row.

Instructions I counted (the line is the start of each):
- `:234` the breaks lead unless major.
- `:234` the definition of a break.
- `:244` how to find the next release.
- `:247` the trailer decides.
- `:250` unknown means lead.
- `:252` the lead's shape.
- `:257` the commit body keeps its order.

The last two are rows of the same rule family, so the count above is six distinct instructions plus the review-checklist line, which restates `:234`.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:250` "Where nothing says which release it is, the breaks lead" | a change to a repository that publishes no releases, such as a script or a configuration repo, which the artifact does name in `:787` "no section for an absent concern" | a `Breaking changes` lead for a break to a file nobody versions | "only where the repository has a release the break would ship in" |

Not findings: `:234`, `:244`, `:252`, `:257`.

## Item 3a: level, placement, and the environment

Analogue: where each rule and file lives, and the registration entries.
- The new rule sits in the pull request description section, beside the slot table it modifies. The package README and the checklist (§8) both carry it.
- The cases sit under `research/change-description-authoring/cases/`, listed in the research README with a dated paragraph, as that README's layout block describes.
- Registration: `agent-packages/.../apm.yml`, root `apm.yml`, and `marketplace.json` all say 1.5.0 and agree with each other. The repository's own gate was not run.
- None.

## Item 4: names by content, not by position

Analogue: the change's own headings, cross-references, and case names.
- Case names are by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). The runs are named `result.md` and `result-2.md`, which is an ordinal, but the README table names each file with its model and run.
- "Three versions of the rule were run on Opus. The first … the second …" in the 4367 README is an ordinal telling a history that is not stored. The commit message says so. Taste, not filed.
- None otherwise.

## Item 5: the failure report

Analogue: what each rule tells the reader to look at, and whether a detection reaches it.
- The case checks 1 to 3 detect the rule under test, and the README says so ("Checks 1 to 3 are the rule under test; 4 to 6 are the guard").
- Check 3 does not detect the rule it is attached to when the failure is extended to inputs that worked before. The Opus run that left `grant insert` in Scope shows it detects its absence, and the README records that result.
- The `Breaks` checklist line (§8) names the lead and the exclusive-slot-3 condition, and the detection checks 1 and 5 test both.
- None.

## Item 6: what the writer says it verified

Analogue: an exemplar that passes and a bad case that fails.
- The commit message states it. Without the rule, both models lead with Why and leave the breaks in place (the baselines). With it, all four runs lead with the breaks, and three of four move `grant insert`.
- The negative control is stated.
- Two limits are stated honestly. The runs are small: two per arm. Three drafts of the rule were run on Opus, and two are summarized, not stored.
- Rewrite check: the rule was reworded after review. The `skill-tree` files show the committed text was the one run.

## Item 7: siblings of the change

Analogue: places that enumerate or route to the artifact, and the set's old size.
- Searched `change-description-authoring` outside `research/` and the skill. The hits were `marketplace.json`, `apm.yml`, the two `english-*-developer-style` packages, `docs-page-authoring`, `problem-report-authoring`, and `qubership-repo-essentials`. None of them describes the slot order or the break rule, so none needs an edit.
- Sibling sentences inside `SKILL.md` that describe the same fact are filed as F1 (`:310`, `:636`).
- I searched the prose for the old count. "Six slots" (`:192`) is unchanged, because the lead is not a slot. "Five slots" for the commit body is unchanged too.
- The changelog section (`:506`, "Compatibility and action") covers breaks in a changelog entry, a different artifact. None.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Rule 5 and the squash-body exception conflict: lead stays (`:259`) vs the body's shape (`:310`, `:636`) | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:259` | 1 |
| Both case READMEs quote a rule title that is not in the committed skill | Substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | 1 |
| Commit message says Opus ran at effort high; the case README says the session default | Substantive | commit message; `pgjdbc-4367-breaks/README.md` ("Running it") | 2 |
| No case for the major, unknown-release, or squash-body arms | Substantive | `research/change-description-authoring/cases/` | 3 |
| "The trailer decides" reads two ways | Taste | `SKILL.md:247` | 3 |
| `:250` leads with breaks in a repository that ships no releases | Substantive | `SKILL.md:250` | 3 (table) |

One check was not done: the repository's markdownlint and registration gates, since markdownlint is not installed here.
