I'm writing the report now. I've read the diff, the skill text and both case READMEs, and I ran the drift script, which printed nothing because no code changed.

# Final review: `4f69810..HEAD` (`86028c3`)

**Inputs.** There is no separate task statement, so the claimed cases come from the commit message alone, as the skill allows. This is a change with no code: a skill, a package README, version bumps, and a research directory. Each item below uses the §2a analogue. `comment-drift.py` was run and found no members, as expected for Markdown and JSON. I loaded `english-developer-style` and `final-review`. `test-authoring` did not apply, because the change has no tests. I did not load `apm-authoring`, which is not among the three skills I was given. I cite the apm rules only through the form's own references to them.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Two findings.
- **Stale rule name in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md` (line 8) and `cases/pgjdbc-4392-no-break/README.md` (line 7) quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The README for 4367 cites it as "SKILL.md §2". The committed heading is "A break leads the description unless the next release from the target branch is a major", at `SKILL.md:234`. The two wordings test different conditions: "promises compatibility" versus "is not a major". A reader who greps the skill for the quoted sentence finds nothing. Substantive.
- **Circular "the trailer decides" sentence (`SKILL.md:247-249`).** It says that where a release tool bumps the major on `BREAKING CHANGE:`, the trailer decides. If the trailer makes the next release a major, the "unless major" exception applies and the lead is dropped. Yet the break is exactly what the lead is for. The reader cannot tell which way it goes. Substantive: say whether such a repository gets the lead or not.

Checked and consistent:
- Versions are 1.5.0 in the package `apm.yml`, the root `apm.yml`, and `marketplace.json`.
- The §2 table row, the line-86 pointer, the slot-3 prose, the §8 checklist item, and the package README all agree on the rule. They also agree with the `Breaking changes` heading and with §7, which says no empty heading is written.
- No narrating `now` or `no longer` in the new text.
- The cross-references (§4 rule 5, §5, §7) exist.

## Item 2: claimed cases covered

| Claim (commit message) | Where covered |
| --- | --- |
| Break is the full list of kinds | `SKILL.md:234-241`. A detection exists (checks 2 and 3). |
| Failure extended to inputs that worked before | check 3, `grant insert`. |
| Result-shape change is a break | check 2. |
| Lead unless the next release is a major, read from version file, milestone, or name | Only the 42.7.14 patch case runs. |
| Breaks lead where nothing says which release | No run. |
| Commit body keeps the problem first, breaks as the first `User-visible:` lines | No run. |
| Squash copies the description and the lead stays | No run. |
| A change with no break grows no section | 4392, four runs. |
| 4367: two runs per model with the rule, one per model on `origin/main` | The files match. |
| "All four lead, mark the result shape; three of four move the extended failure out of Scope" | The table agrees: the opus `result-2` fails check 3. |
| Earlier Opus runs summarized, not stored | The README paragraph says so. |

Findings:
- **Effort statement.** The commit message says "Opus and Haiku (effort high)". The 4367 README says "Opus at the session's default". Both cannot be true. Substantive: the claim about how the evidence was produced is inconsistent.
- **Untested claims.** The cases do not exercise "next release is a major", "release unknown", or the commit-body and squash-copy order. These belong under Item 3.

No commands are given for a reader to run, other than the `git archive` recipe in the README, which is a recipe and not a promised outcome.

Hunk-to-claim check: every hunk maps to a sentence of the commit message. The `cases/` row in the research README and the dated paragraph are claimed by "Two regression cases under research/…". The version bumps are claimed implicitly by the feat. Nothing is unclaimed.

## Item 3: boundaries, partitions, negative control

**Partitions and the control.**
- The control `pgjdbc-4392-no-break` exists. It is a four-run check on the new skill only, with no baseline, which is fine because the control must stay quiet.
- Missing partitions, all claimed in the rule:
  - next release is a major, where the breaks stay first in slot 3;
  - release unknown, where the breaks lead;
  - a `BREAKING CHANGE:` tool repository;
  - the commit-body or squash-copy shape.

  Substantive: add a 4367 variant with `pgjdbc.version=43.0.0`, or a note that these are untested.
- The ordering in `SKILL.md` has no run for the commit-body shape either.

**Added-instruction table.**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "The description then opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings" | A patch-release change with one break and a four-paragraph prose description with no template | A lone `Breaking changes` heading on an otherwise headingless description | "Where the description has headings" ends it. The skill also says headings are the exception. |
| "Where nothing says which release it is, the breaks lead" | A break in a repository with no version file or milestone, such as a new repo on its first release | Leads with the break, which costs a paragraph | "a break read first in a major release costs a paragraph" accepts this. |
| "after at most a short paragraph that says which code breaks" | A break with only one affected caller, whose line already says which code breaks | A redundant sentence before the line | None. Taste: add "only where the break lines do not already name the code". |
| "A failure the change extends to inputs that worked before is a break … goes with the breaks, not in Scope" | A failure extended only to inputs that never worked in a documented way, such as undefined behavior | A break line for a non-break | "Whether the old behavior was right does not decide it" cuts the other way. It is covered by "inputs that worked before". |

Only the third row is anything, and it is taste.

**Prior state, values users pass, replaced mechanism, limits.** None apply.

## Item 3a: level, placement, environment

None found. The case directories sit under the research directory beside the existing phase files, and the two cases share the same layout and run recipe. The README records that no installed skill copy was used. I did not run the repository's gate; I only compared the three versions by hand, and they agree.

## Item 4: names by content

None found. Case names are `pgjdbc-4367-breaks` and `pgjdbc-4392-no-break`, and the checks are numbered but referred to by content. The table of runs in the README refers to `(1)`, `(2)` and `(3)`, but the column titles name the check, so this is fine.

## Item 5: the failure report

The detection list is the six checks. Check 5 ("Stated once") is only partly mechanical, since the rule's text does not say outright that a break is not repeated in Why. This is taste: the rule says "the Why slot follows the breaks", and "A fact stated in slot 3 is not restated in slot 2" is already in the skill. No finding.

## Item 6: what the writer says it verified

The change states the evidence: a baseline on `origin/main` per model, two runs each with the rule, a negative control, and the failures in the table. That is the red run, and the result files back it. It also admits one Opus run did not move the failure. Four cases with N=2 is thin; the README says so ("most of the time and not always"). The rule was reworded after review, and the final wording is the one run. Conforming.

## Item 7: siblings of the change

- A member added to a set: no set. The only enumerating surfaces are the package `apm.yml`, the root `apm.yml`, and `marketplace.json`; all three are bumped.
- Not updated: the package `description:` (unchanged and not claimed). The changelog slot in the skill (`SKILL.md:506`, "breaking or not, what the reader must do") has no placement rule for breaks and is not changed. Is a changelog entry in a patch release a sibling of the lead? The changelog already carries "Breaking changes are marked in place and sorted first" (`:543`), so the skill is consistent.
- Pull request title: the `!` marker (§5, line 706) is mentioned only through the tool sentence. This is in the same finding as the circular trailer sentence.
- Old counts: no stale count, as nothing was counted.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| Case READMEs quote a rule name the skill does not contain ("promises compatibility", "SKILL.md §2") | Substantive | `research/.../pgjdbc-4367-breaks/README.md:8`, `pgjdbc-4392-no-break/README.md:7` | Quote the committed heading, or rename the rule. |
| "The trailer decides" is circular with "unless the next release is a major" | Substantive | `SKILL.md:247-249` | State whether a repository whose tool bumps the major on the trailer gets the lead. |
| Effort statement differs between commit message and README | Substantive | commit message; `pgjdbc-4367-breaks/README.md` "Running it" | Say which effort Opus ran at. If it was the default, fix the message in the follow-up. |
| The major, unknown-release, and commit-body or squash-copy partitions of the rule have no run | Substantive | `cases/` | Add a major-version variant of 4367 and a squash-merge run, or say in the README that they are untested. |
| "A short paragraph that says which code breaks" can repeat what the line says | Taste | `SKILL.md:252-253` | Add "only where the break lines do not already name the code". |

## What was not checked

I did not run the drafting agents or re-score the result files against the six checks, I did not run the repository's own gate, and I did not do a style-only pass over the prose.
