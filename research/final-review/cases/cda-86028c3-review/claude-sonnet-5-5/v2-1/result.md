I'm checking the last details now (the case results match the README's word counts), and then I'll write the report. I did not run the drift script. This change has no code, so there are no members for it to parse. I could not load `apm-authoring` or `docs-page-authoring`, because only the three named skills were provided. I applied §2a with `english-developer-style` as the wording reference.

**Inputs.** There is no task statement. The claimed cases come from the commit message of 86028c3 alone. It claims:
- A break leads the description unless the next release is a major.
- The definition of a break.
- The commit body keeps the problem first.
- The lead stays when squash copies the description into the commit.
- A change with no break grows no section.
- Case `pgjdbc-4367-breaks`.
- Negative control `pgjdbc-4392-no-break`.
- The run counts and verdicts.

There is no previous report.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

**Finding A. The skill contradicts its own §4 rule 5.**
- SKILL.md:637 says that where the description becomes the commit body, "shape it as §2's commit body". That shape is problem first.
- The new text at SKILL.md:259–261 says that body "opens with its breaks and then its problem".
- SKILL.md:310 still says the description "takes the body's shape instead".
- SKILL.md:857 says headings are "absent from a description that §4 rule 5 makes a commit body". The new text says the lead goes "under a `Breaking changes` heading where the description has headings". An agent in the squash case cannot tell whether the heading is allowed.
- Rule 5 and line 310 were not touched. They must say that the lead is the exception to the body shape.

**Finding B. The case READMEs quote a rule that no longer exists.**
- Both READMEs (`pgjdbc-4367-breaks/README.md` line 7 and `pgjdbc-4392-no-break/README.md` line 6) quote the rule as "A break leads the description where the next release from the target branch promises compatibility". They also cite it as "SKILL.md §2".
- The shipped text is "unless the next release … is a major". It sits in §2 under *Pull request description*, but it is a different sentence.
- The commit message says the wording changed "after review", so the case README is stale against it.

Everything else checked is true:
- The `§4 rule 5` and `§5` references resolve. `BREAKING CHANGE:` and `!` are in §5 at line 706.
- The checklist "Problem" item and the new "Breaks" item agree with the body text.
- The slot-3 table cell says "ahead of slot 1 unless the next release is a major", which agrees with the prose.
- The word counts in the case README match `wc -w` for every result file.
- The `skill-tree` ids match: the committed skill tree is `47980534…` and the baselines are `1f020ce5…`, which is the tree at HEAD~1.

## Item 2: claimed cases covered

| Claim | Covered by |
| --- | --- |
| Break leads in a patch release | Check 1 of `pgjdbc-4367-breaks`, four runs, all pass |
| Result-shape change is a break | Check 2, passes in all four runs |
| Extended failure is a break, not Scope | Check 3, three of four runs pass. Opus `result-2` fails and the README says so |
| Fix that now succeeds is not a break | Check 4 |
| No section when there is no break | `pgjdbc-4392-no-break`, four runs |
| "Without the rule both models put Why first" | The two baselines |
| Next release is a major, so the breaks stay in slot 3 | No case |
| Release unknown, so the breaks lead | No case |
| Release read from a maintenance branch name, milestone, or `BREAKING CHANGE:` trailer | No case. Both prompts give only `gradle.properties` |
| Commit body keeps the problem first, with the breaks as the first `User-visible:` lines | No case |
| Squash keeps the lead | No case |

The commit message's "three of four" matches the results table. No command line in the changed files promises an outcome, so there are no commands to list. The commit message covers every other hunk: the version bumps are 1.4.0 to 1.5.0 in four places that agree, the package README line, and the research README entry.

The major-release branch, the unknown branch, and the commit-body claims are covered by none of the cases. See Item 3.

## Item 3: boundaries, partitions, and the negative control

**Partitions.** The condition has three branches: major, not major, and unknown. Only "not major" has cases.
- **Finding C.** The major branch is claimed in the body ("the breaks stay first in slot 3"). A case with a `pgjdbc.version=43.0.0-SNAPSHOT` prompt and breaks would test it.
- The negative control tests "no break". It does not test "break plus major", which is the arm that should stay green on the base commit.

**Pre-existing state.** Authors on 1.4.0 will see the rule change the order of descriptions they already write. No stale state is involved.

**Table of added instructions.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Break leads the description | A change with one break, no Why content beyond the break, in a repository with no headings | A `Breaking changes` heading and a lead paragraph above a one-line fix | The text already says "after at most a short paragraph" and "where the description has headings". That bounds the paragraph and the heading. Not a finding. |
| Failure extended to inputs that worked before is a break | A new validation that rejects inputs the old code already rejected on other paths, with no input that worked before | A break line for a failure no caller newly meets | The definition says "for those inputs". It is bounded by "worked before". Not a finding. |
| Read the release from the version file, milestone, or branch name | A repository whose version file holds a development or snapshot version with no stated policy | Takes the version as a patch release or a major arbitrarily | "Where nothing says which release it is, the breaks lead". Not a finding. |
| Commit body keeps the problem first with breaks in `User-visible:` | A squash where the description leads with the breaks | See Finding A | The text says the lead stays for squash. This is the contradiction in Finding A. |

## Item 3a: level, placement, and the environment

- **Layout.** The cases follow the layout of the earlier `research/*` entries. The research README registers `cases/`.
- **Gate.** Nothing in the change shows `scripts/check-skill-descriptions.py` or `scripts/skill-tree.sh` run on it. I did not run them. The description frontmatter is unchanged, so the first gate is unaffected.
- The rule's four lines of wording sit in §2 under the PR description, and the commit-body variant sits in the same paragraph. That is placement the reader can find.

## Item 4: names by content, not by position

None. Results are named `result.md` and `result-2.md`. That is an ordinal, but it is the same convention the earlier results use. It is taste, and I am not requesting a change.

## Item 5: the failure report

Each check in the README names its pass condition and the literals to find. The table names the run and the check that fails. None otherwise.

## Item 6: what the writer says it verified

- Red runs on the base commit exist: the baselines on `origin/main` fail checks 1 to 3.
- **Finding D.** There is one baseline run per model for the break case and none for `pgjdbc-4392-no-break`. The negative control has no red or green evidence on the base. This is acceptable for a control, but the README should say why.
- Opus `result-2` fails check 3. The README and the commit message report it honestly.
- Samples are small: two runs per model with the rule, one without. The commit message states the counts.

## Item 7: siblings of the change

- **Set members.** The change adds one rule and one checklist item. The package README has one new bullet. The checklist has the Breaks item.
- **Old size.** SKILL.md:845 says "breaks first" in the Caller item. The new Breaks item sits right after it, so the two are consistent. The `Problem` item was updated.
- **Sibling skills.** I searched `change-description-authoring` outside the package. The other skills only refer to it by name. `english-developer-style` (all three copies) names it without describing the content. Nothing else describes the commit-body order.
- **Other paths with the same symptom.** The changelog entry (§3, line 543) already says breaking changes are marked in place and sorted first within their category. It is not an order conflict, but the new lead never mentions the changelog. This is taste. I do not request a change.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A. Rule 5 and line 310 say "shape it as §2's commit body" and "takes the body's shape". The new text makes the squashed body open with the breaks. Line 857 forbids headings in that body, but the lead is "under a `Breaking changes` heading where the description has headings". | Substantive | `SKILL.md:637`, `:310`, `:857`, `:259–261` | Add the lead as the stated exception in rule 5. Say whether the squashed body's lead carries the heading. |
| B. Both case READMEs quote the pre-review rule ("promises compatibility") and cite it as §2. | Substantive | `pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | Quote the shipped rule, or refer to it by its bold sentence. |
| C. The major-release and unknown-release branches have no case, and neither does the commit-body claim. | Substantive | Commit message; `SKILL.md:252–256` | Add a case with a major target, or state in the README that those arms are untested. |
| D. The negative control has no baseline run. | Taste | `pgjdbc-4392-no-break/README.md` | One line saying why none was needed. |
| E. `result-2.md` naming. | Taste | Case directories | No change. |

I did not run the suite, the skill gates, or any of the model runs. I did not do a style pass over the prose.
