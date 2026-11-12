# Final review: `4f69810..HEAD` (one commit, 86028c3)

**Inputs.** There is no task statement, so the claimed cases come from the commit message alone. The only extra claims are the case READMEs. I loaded `english-developer-style`. `apm-authoring` is not among the three skills I was given, so I used the analogues in §2a without it. The change is a skill, a package README, version bumps, and research files. The drift script was **not run**, because it parses code members and none changed. No previous report exists. I did not run the suite or any model run.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **Contradiction inside SKILL.md, substantive.** The new paragraph at `SKILL.md:258-261` says that where §4 rule 5 makes the description the commit body, "the lead stays" and "that body opens with its breaks and then its problem". Under the `Breaking changes` heading rule at line 252, that body carries a heading. Three other sentences still say the opposite:
  - Rule 5 (line 637): "shape it as §2's commit body". That body is problem first, with breaks as `User-visible:` lines in slot 4.
  - Line 310: "Under §4 rule 5 the description is the commit body and takes the body's shape instead", meaning no headings.
  - Checklist line 857: headings are "absent from a description that §4 rule 5 makes a commit body".

  An agent following the squash case gets two opposite instructions: heading and breaks first, or no heading and problem first. The reader gets it wrong either way. The line-86 edit ("puts the problem right after them") leans on the new reading, so it does not settle the conflict.
- **Stale quote, substantive.** Both case READMEs cite the rule as "A break leads the description where the next release from the target branch promises compatibility" (`pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6`). The committed heading at `SKILL.md:234` reads "…unless the next release from the target branch is a major". The quoted text appears nowhere in the repository. The two phrasings differ on an unknown release: the old one implies no lead, the new one says the breaks lead. A reader who greps for the quote finds nothing.
- Section references are correct: §5 holds the `BREAKING CHANGE:` row (line 706), and §7 holds the "no empty section" rule.
- Narration (`now`, `no longer`, `used to`): none in the new SKILL text. The one use in the 4392 README describes the input draft ("used to reach the server verbatim"), which is acceptable.

## Item 2: claimed cases covered

| Claim (commit message) | Evidence | Result |
| --- | --- | --- |
| Without the rule both models put Why first and leave both breaks in place | `opus/baseline`, `haiku/baseline`: lead fails, shape fails, `grant insert` fails | holds |
| With the rule all four runs lead with the breaks and mark the result shape | four rows in the results table (opus ×2, haiku ×2) | holds |
| Three of four move the extended failure out of Scope | `opus/result-2` is the one that fails | holds |
| The control grows no section in any run | 4392 README: four runs pass | holds |
| "Opus and Haiku (effort high)" | 4367 README: "Haiku ran at effort `high`; Opus at the session's default"; 4392 README mentions only Haiku at `high` | **contradicts the README** |
| Two runs each with the rule, one each on baseline | files match | holds |
| The skill trees recorded are the committed ones | `skill-tree` of the rule runs is `47980534…`, which equals `HEAD:` the skill dir; baseline `1f020ce5…` equals `HEAD~1:` | holds |

- **Effort claim, substantive.** The commit message says Opus ran at effort high, and the README says it ran at the session default. One of the two is wrong. The request is to correct the commit message or the README.
- **Unclaimed fact.** Four Haiku results, not "all three", end with a "Generated with Claude Code" line. The baseline `haiku/baseline/result.md` has it too, and the 4367 README says "All three Haiku results". The 4392 README is correct with its "Both". This is a small miscount. I rate it taste.
- **Words column.** The counts in the README (756, 825, 792, 758, 779, 784; 241, 251, 256, 249) match `wc -w`.
- **Commands.** The change tells no one to run a command except `git archive <rev> …` in the "Running it" section. It is a recipe for the drafting setup, and no script or CI job runs it (`none`). The cost figures (token counts, list prices) cannot be checked from the repository.
- **Hunks.** Every hunk belongs to a sentence of the commit message: the SKILL edits, the package README bullet, the 1.4.0→1.5.0 bumps in three files, and the research cases. The `research/…/README.md` `cases/` line is the one hunk the message does not mention by name. It is a layout entry for the added directory, so I rate it taste.

## Item 3: boundaries, partitions, negative control (analogue)

Partitions the rule claims:
- Next release is not a major and the change breaks something: covered by `pgjdbc-4367-breaks` (a patch release).
- Next release is a major: **no case.**
- Release unknown ("breaks lead"): **no case.**
- Release tool bumps on a `BREAKING CHANGE:` trailer or `!`: **no case.**
- Description that becomes a commit body (rule 5): **no case.** This is the partition where the contradiction in Item 1 sits.
- Heading versus no heading: the 4367 draft has headings, so a prose description is untested.

Negative control: `pgjdbc-4392-no-break` has no break and passes in four runs.

The "major" branch of the rule has no negative control. Its sentence "Where the next release is a major, the breaks stay first in slot 3" is not tested by any run. This is substantive (a claimed mode with no evidence). The request is one case with a major-release target, or a sentence in the commit and README saying the branch is untested.

**Added-instruction table** (§2a):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "The description then opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings" | A squash-merge "title and description" repository, where rule 5 says no headings | A heading in a body that rule 5 says has none | Quoted text at line 637 says the body takes §2's commit-body shape. That contradicts the new sentence rather than ending it. **Substantive**, request: add "…, and under §4 rule 5 the breaks are the first `User-visible:` lines instead", or drop the lead-stays sentence. |
| "A failure the change extends to inputs that worked before is a break… it goes with the breaks, not in the Scope slot" | A change that extends a failure only to inputs that never worked before | Moves a non-break into the lead | "to inputs that worked before" ends it. Not a finding. |
| "Where nothing says which release it is, the breaks lead" | A change with no break | An empty section | Last sentence of the paragraph, "A change with no break has neither the lead nor an empty heading". Not a finding. |
| "Read the next release from the target branch: version file…" | A repository with no version file, milestone, or maintenance-branch name | Falls to "nothing says", so the breaks lead | Covered by the previous row. Not a finding. |
| "after at most a short paragraph that says which code breaks" | A break that is a single obvious line | A paragraph restating the line | `at most` allows none. Taste only. |

## Item 3a: level, placement, environment

Placement matches the sibling `cases` layout. The `cases/` directory is new, so there is no earlier case to compare it with. The registration entries (`apm.yml`, `marketplace.json`, package `apm.yml`) agree on 1.5.0. I did not run the repository's own gate. Result: none.

## Item 4: names by content, not position

`result-2.md` names a run by its ordinal and says nothing about what differs. It is a file name and the README table cites it by path, so I rate it taste. SKILL.md has no new ordinals.

## Item 5: the failure report (analogue: each rule's detection)

The six checks in the 4367 README detect the rule. Check 2 (result shape) and check 3 (`grant insert`) are specific. The checks do not cover "the heading appears only where the description has headings", or the rule 5 body shape. So the rule's rule 5 sentence has no detection. Substantive, tied to Item 3.

## Item 6: what the writer says it verified

The message and the README state the red runs on baseline (`origin/main` skill tree `1f020ce5`) next to the green runs, and the control. They also say that earlier Opus runs of two drafts are "summarized, not stored". That makes those figures unverifiable from the repository. The README labels the results 1–6 correctly. The 1/2 Opus pass on check 3 is stated openly. The evidence is adequate for check 1 and check 2. Check 3 holds in 3 of 4 runs, which the message states faithfully.

## Item 7: siblings

- Other places that list or repeat the rule: the package `README.md` was updated; marketplace and `apm.yml` bumped; the Review checklist (line 849) was updated; line 86 was updated.
- **Not updated:** §3 line 543 ("Breaking changes are marked in place and sorted first within their category") concerns changelog entries, so it is unaffected. Line 388 and line 845 say "User-visible changes, breaks first" but do not mention the new lead, which is consistent. No sentence counts the slots in a way the change makes stale.
- Rule 5, line 310, and line 857 are the three siblings the change missed (see Item 1).
- No other package pins `change-description-authoring` by version (the grep found only name mentions), so there is no pin to bump.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The commit-body-from-description case: new text says the body opens with breaks under a heading; rule 5, line 310, and the checklist say the body takes §2's commit shape without headings | substantive | `SKILL.md:258-261` vs `:637`, `:310`, `:857` | Pick one reading and update all four places; add a case or state it untested |
| 2 | Both case READMEs quote a rule heading that no longer exists ("promises compatibility") and imply a different unknown-release behavior | substantive | `pgjdbc-4367-breaks/README.md:7`, `pgjdbc-4392-no-break/README.md:6` | Quote the committed heading |
| 3 | Commit message says Opus ran at effort high; the README says the session default | substantive | commit body vs `pgjdbc-4367-breaks/README.md` ("Running it") | Correct whichever is wrong |
| 4 | Major-release, unknown-release, trailer-bump, and prose-description partitions have no case; the control only covers "no break" | substantive | `research/…/cases` | Add a major-target case or say it is untested |
| 5 | "All three Haiku results" is four files (baseline included) | taste | `pgjdbc-4367-breaks/README.md` | Count the baseline |
| 6 | `cases/` layout line is the one hunk the message does not name | taste | `research/…/README.md:49` | Mention it or ignore |

Not checked: the suite and the model runs were not re-run, the stated costs and the unstored earlier-draft runs could not be verified, `apm-authoring` was not available, and I did not do a style-only prose pass.
