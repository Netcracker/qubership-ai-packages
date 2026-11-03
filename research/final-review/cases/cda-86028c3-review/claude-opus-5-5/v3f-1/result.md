# Final review: `4f69810..86028c3` (one commit, change-description-authoring 1.5.0)

**How I ran it.** There was no task statement, so the claimed cases come from the commit message alone. The change has no code: it touches a skill, a package README, the index entries, and research cases. So every item below uses the analogues in §2a. I did not run `comment-drift.py`, because it parses members and doc comments and this change has neither. I loaded `english-developer-style` and `test-authoring` from the given directory. I also read `apm-authoring` from the repository (`agent-packages/apm-authoring`), because the form names it for skill packages and it is not one of the three supplied skills. No previous report of this form exists, so there is no table of earlier findings.

## Item 1: comments consistent with the code and with each other

*(Analogue: what each changed file says about another file or about the repository.)*

- **Both case READMEs quote a rule the skill no longer has.** `cases/pgjdbc-4367-breaks/README.md:8` and `cases/pgjdbc-4392-no-break/README.md:6` quote SKILL.md §2 as "A break leads the description where the next release from the target branch promises compatibility". The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The quoted text is an earlier draft, which the README itself mentions ("reworded after review"). A reader who searches the skill for the quote finds nothing, and the old wording describes a different condition.
- **Two sentences now name different first questions for the reviewer.** `SKILL.md:203-204` (unchanged) says "the reviewer's first question is why that version should change". The new `SKILL.md:243-244` says "the reviewer's first decision is whether the change may ship in it at all". They now say different things about the same fact.
- **Checked and consistent:**
  - The skill-tree ids: the `*/skill-tree` value `4798053…` equals `HEAD:` of the skill, and `1f020ce…` equals `HEAD~1:`.
  - The word counts in both README tables.
  - "All three Haiku results" and "both Haiku results" end with the "Generated with" line.
  - The table of checks against the six 4367 results.
  - The commit message's "three of four", "one Opus run left it there", and "two drafts summarized, not stored".
  - The package README bullet.
  - The new `research/…/README.md` index line.
- **The §4 rule 5 exception is reachable.** Rule 5 says "shape it as §2's commit body", and §2 slot 1 now carries the exception, so the problem-first rule and the new lead do not contradict each other.

## Item 2: claimed cases covered

*(Analogue: the section that handles each claimed case, and the case that tests it.)*

| Claim (commit message) | Section | Evidence |
| --- | --- | --- |
| Breaks lead when the next release is not a major | `SKILL.md:234-255` | `pgjdbc-4367-breaks`, checks 1–3 |
| A result-shape change is a break | `SKILL.md:235-237` | 4367, check 2 |
| A failure extended to more inputs is a break, not Scope | `SKILL.md:238-240` | 4367, check 3 (3 of 4 runs pass) |
| A fix is not a break | `SKILL.md:240-241` | 4367, check 4 |
| No break grows no section | `SKILL.md:255` | `pgjdbc-4392-no-break` |
| The breaks stay in slot 3 when the next release is a major | `SKILL.md:254-255` | **none** |
| Breaks lead when nothing says which release it is | `SKILL.md:248-250` | **none** (see item 3) |
| The commit body keeps the problem first, breaks first under `User-visible:` | `SKILL.md:257-258` | **none** |
| When squash copies the description, the lead stays | `SKILL.md:258-260`, `:86-88` | **none**: the 4367 prompt has a one-commit squash with bullets, so §4 rule 5 does not fire |
| Removed option, changed default, changed error code count as breaks | `SKILL.md:237-238` | none (definition only; taste) |

**Commands the change tells a reader to run:**
- `cases/pgjdbc-4367-breaks/README.md:37-38` says to copy the skill out "with `git archive <rev> agent-packages/…/change-description-authoring`".
  - **Runs it:** nothing in the repository.
  - **Outcome promised:** a copy of the skill.
  - **What it does:** run as written, `git archive` writes a tar stream to stdout; no files are copied. The documented form needs `| tar -x -C <dir>`, or `-o <file>` and an extract step.
- The `./gradlew` and classifier commands inside `prompt.md` are input data to the drafting agent, not instructions to a reader.

**Hunks that no sentence claims:** the version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and `agent-packages/change-description-authoring/apm.yml:2`. Earlier commits in this package say "Version 1.2.0 to 1.3.0." in the message; this one does not. Every other hunk is claimed.

## Item 3: boundaries, partitions, and the negative control

*(Analogue: the modes the change claims, the no-break control, and the table of added instructions.)*

- **The "unless major" branch has no case.** Both cases target a non-major release. A rule that said "always lead with breaks" would pass `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break` exactly as the committed rule does. Nothing shows that an agent reads the version and keeps the breaks in slot 3 when the next release is a major.
- **The version input does not separate "patch" from "unknown".** Both prompts give `gradle.properties` as `42.7.14`, which equals the latest tag `REL42.7.14`. So the version file names the released version, not the next one, and the two branches give the same output here.
- **The commit-body partition has no run, and neither does the §4 rule 5 partition.**
- **The control's growth has no baseline.** `pgjdbc-4392-no-break` was not run on `origin/main`. The 241–256 words are compared only with the 209-word draft, so growth caused by the rule cannot be told apart from what the model does anyway.

**Table of added instructions:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Extended failure "goes with the breaks, not in the Scope slot" (`:238-240`) | An extended failure whose intent only a maintainer can settle | The break leads, while the Scope rule at `:488-491` still demands the question in Scope; the agent picks one | "; whether it is wanted stays in Scope as the question" |
| "the trailer decides, and it is written whatever the description does" (`:247-248`) | A release-please repo, a patch line, a break not yet accepted | `BREAKING CHANGE:` written, a forced major, no lead | "once a maintainer accepts the break" |
| Under §4 rule 5 "the lead stays" (`:258-260`) | A squash "title and description" repo, so the body has no headings | A body opening with bare break lines and no `User-visible:` label | "as the first `User-visible:` lines, ahead of the problem" |
| "Where nothing says which release it is, the breaks lead" (`:248-250`) | A continuously deployed service with no versions | A `Breaking changes` lead, with "the version it worked in" invented or blank (taste) | "where the branch ships versioned releases" |

The first three rows are substantive. In the first two, another rule asks for the opposite on the same input. In the third, the new paragraph's own reason ("the label is what R4 and R5 search for") is not met under rule 5.

**Not findings:**
- "A change with no break has neither the lead nor an empty heading", ended by its own condition.
- "after at most a short paragraph that says which code breaks", ended by "at most".
- "a failure that now succeeds is a fix, not a break", ended by its own text.

## Item 3a: level, placement, and the environment

*(Analogue: where each rule lives and the repository's own gate.)*

- **Placement:** the rule sits in §2 "Pull request description", beside the slot table it changes. The cases follow the layout of the research directory and are indexed in its README.
- **Gates:** `make check` exits 0 (the versions are aligned), and `make check-descriptions` passes.
- **Finding:** `cases/pgjdbc-4367-breaks/README.md:17` is 121 characters. The case READMEs are not covered by `FILTER_REGEX_EXCLUDE`, and the repository pins MD013 at 120. The markdownlint config comes from netcracker/.github and is not in the checkout, so I could not run the linter.
- No sentence is tutorial-generic.

## Item 4: names by content, not by position

none. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and the check names ("Lead", "Result shape", "`grant insert`") name their content. The cross-references use section numbers (§2, §4 rule 5, §5, §7), which is the skill's existing convention.

## Item 5: the failure report

*(Analogue: whether the checklist reaches the rule, and whether its check detects the rule.)*

The new checklist line `SKILL.md:849-852` reaches the rule, but it checks a weaker property. It asks whether the description opens with the break lines. It does not ask whether a result-shape change or an extended failure counted as a break, which is the failure the commit message names (`getUpdateCount()` left unmarked, and `grant insert` left in Scope). A self-check therefore passes a description that leads with two breaks and leaves the third in Scope, as `opus/result-2.md` does.

## Item 6: what the writer says it verified

- **Exemplar and bad case:** both are named. The baselines fail checks 1–3; the runs with the rule pass, on the committed tree (I verified the skill-tree ids).
- **Rewrite:** the reworded rule was re-run (the README says so, and the tree id matches HEAD).
- **Noise input:** `pgjdbc-4392-no-break` is the input where the rule is noise, and it grew no section. Its "did not grow" check has no baseline run (item 3).
- **Rule moves the case most of the time, not always:** the README states this honestly (one Opus run in two).

## Item 7: siblings of the change

- **Surfaces that list the package:** `apm.yml`, `marketplace.json`, the package `apm.yml` (all bumped), and the package README (bullet added). The skill description and the instructions file did not need a change; the scope did not widen.
- **Other places in the skill that talk about breaks:**
  - The changelog's "sorted first within their category" (`:543`) is consistent.
  - §7 "no section for an absent concern" is cited.
  - The Scope paragraph on open questions (`:488-491`) conflicts (item 3, row 1).
- **`english-us-developer-style` §7 commit/PR module:** no ordering rule that conflicts.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Both case READMEs quote a superseded wording of the rule | Substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed heading, "…unless the next release from the target branch is a major" |
| An extended failure whose intent is open: the break rule says "not in Scope", the Scope rule says keep the question there | Substantive | `SKILL.md:238-240` vs `:488-491` | Add "; whether it is wanted stays in Scope as the question" |
| "it is written whatever the description does" forces `BREAKING CHANGE:` before a maintainer accepts the break | Substantive | `SKILL.md:247-248` | Limit it: "once a maintainer accepts the break" |
| Under §4 rule 5 the leading break lines have no `User-visible:` label, yet the same paragraph says that label is what R4 and R5 search for | Substantive | `SKILL.md:258-260` | State that the leading lines carry the `User-visible:` label |
| "Reviewer's first question" vs "reviewer's first decision" | Substantive | `SKILL.md:203-204` vs `:243-244` | Qualify `:204` for the case where breaks lead |
| No case for the "next release is a major" branch; a rule that always leads passes both cases | Substantive | `research/…/cases/` | A case whose version file says the next release is a major (e.g. `43.0.0-SNAPSHOT`), checking that the breaks stay in slot 3 |
| No case for the commit body or for the §4 rule 5 description-as-body | Substantive | `SKILL.md:257-260` | One run each, or drop the claim from the commit message |
| The control has no baseline run, so its growth is not attributable to the rule | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Run 4392 on `origin/main` and compare word counts |
| The checklist line does not detect the break definition (result shape, extended failure in Scope) | Substantive | `SKILL.md:849-852` | Add "is every changed result shape and every failure extended to inputs that worked before among them, and none in Scope?" |
| The documented `git archive` form copies nothing on its own | Substantive | `cases/pgjdbc-4367-breaks/README.md:37-38` | Add `\| tar -x -C <dir>` (or `-o` and an extract step) |
| A line over the 120-character MD013 limit in a linted README | Substantive (not run: config is remote) | `cases/pgjdbc-4367-breaks/README.md:17` | Rewrap |
| The version bump is not claimed in the message (earlier commits say "Version X to Y.") | Taste | `apm.yml:168` and two siblings | Add "Version 1.4.0 to 1.5.0." |
| No case for the removed-option, changed-default, or error-code kinds of break | Taste | `SKILL.md:237-238` | A check line in a future case |
| An unversioned service meets "the version it worked in" with nothing to fill it | Taste | `SKILL.md:248-250` | "where the branch ships versioned releases" |

**Not checked:** I did not rerun any of the drafting runs or a markdownlint/super-linter pass (the config comes from netcracker/.github and there is no network). I did not fetch the pgjdbc pull requests, so the quoted maintainer rewrite and the PR facts are unverified. I did no style pass over the prose.
