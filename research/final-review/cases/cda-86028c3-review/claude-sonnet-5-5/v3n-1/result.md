# Final review: `4f69810..HEAD` (one commit, 86028c3)

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message alone. That message claims:
- the break lead and its exceptions;
- the definition of a break;
- the commit-body order;
- `pgjdbc-4367-breaks` on Opus and Haiku (two runs each with the rule, one each on origin/main);
- the `pgjdbc-4392-no-break` control, two runs each;
- "all four runs lead with the breaks", "three of four move the extended failure out of Scope", "the control grows no section in any run".

There is no previous report.

The change is a skill, package metadata and research cases, so §2a applies. The drift script was not run, because there are no code members. Developer-style and `apm-authoring` were read from the supplied copies only as far as the form cites them.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

Two findings.
- **Stale rule name.** `cases/pgjdbc-4367-breaks/README.md:8` and `cases/pgjdbc-4392-no-break/README.md:7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". No such sentence exists in SKILL.md. The committed rule is "A break leads the description unless the next release from the target branch is a major" (SKILL.md:234), and the README's pointer to "SKILL.md §2" matches that. The README even says it was "reworded after review". A reader who searches the skill for the quoted sentence finds nothing. `git grep "promises compatibility"` hits only these two lines.
- **Effort level contradicts the commit message.** The commit message says "on Opus and Haiku (effort high)". The 4367 README says "Haiku ran at effort `high`; Opus at the session's default", and the 4392 README says only "Haiku at effort `high`". The two statements about Opus conflict. Which one is true is not something I could check.

Checked and consistent:
- Versions: `1.5.0` appears in `apm.yml`, `agent-packages/change-description-authoring/apm.yml` and `marketplace.json`, and each file previously held `1.4.0`. The umbrella `qubership-repo-essentials` pins by path, so it does not need a bump.
- Cross-references: §2, §4 rule 5, §5 and §7 all exist, and §7 does cover "no empty section for an absent concern".
- Counts: the 4392 README's word counts (241, 251, 256, 249) match `wc -w`. The 4367 README's 756, 825, 792, 758, 779 and 784 also match.
- `skill-tree` files: the rule runs hold `4798053…`, which equals `HEAD:<skill dir>`. The baselines hold `1f020ce…`, which equals the tree at `4f69810`.

Wording inside SKILL.md: line 193 still says "Six slots, in order", while line 198 and line 252 now put slot 3's break lines ahead of slot 1. Line 252 resolves it, but the table header and the "in order" claim are not qualified (taste, see the table below).

## Item 2: claimed cases covered

Claimed cases, and the evidence for each. For a skill the detection is the case README's checks, graded against the committed results.

| Claim | Evidence |
| --- | --- |
| Lead with breaks (patch release) | Check 1. The four rule runs open with `## Breaking changes` (`haiku/result*.md`, `opus/result.md`) or with a short paragraph and then the heading (`opus/result-2.md`). Both baselines open with `## Why`. |
| Result-shape change is a break | Check 2. Present in the Breaking changes list of all four rule runs. In both baselines it sits in slot 3 without a **Breaks:** label. |
| Extended failure (`grant insert`) is a break | Check 3. In the lead in 3 of 4 runs. `opus/result-2.md:35` leaves it in Scope, and the README discloses that. |
| The control grows no section | All four 4392 results have no `Breaking changes` heading. |
| A change that now succeeds is not a break | Check 4. |
| Literals kept | Check 6. 42703, 0100E, "A result was returned…" and 42601 are each present once in every 4367 result. |
| Commit body keeps problem first | The commit-body hunks are not covered by any case. Both cases are pull request descriptions. |
| Where §4 rule 5 copies the description, the lead stays | Not covered. |
| Next release read from the version file, milestone, branch name | No case. |
| "Where nothing says which release it is, the breaks lead" | Not covered. Both cases target `master` of a repository whose prompt apparently names the patch line. |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer…" | Not covered. |
| Major-release branch: breaks stay first in slot 3 | No case, so a partition with no evidence. |

Commands the change tells someone to run: none. The README's `git archive … | tar` recipe was not altered by this change.

Hunk-to-claim mapping:
- The slot-1 sentence (line 86) is claimed by the commit-body sentence.
- The checklist "Problem" and "Breaks" items are claimed by the new rule.
- The research README line and the package README bullet are unclaimed by name but follow from the cases and the rule.
- The version bumps follow the repository's convention.

No unclaimed hunk.

AGENTS.md says a change to a skill re-runs every case of that skill. There are only these two cases, and both ran.

## Item 3: boundaries, partitions, negative control

Partitions the change claims:
- **Patch or minor release, major release, unknown release.** Only the patch case is run (substantive, see the table below). The control is a patch-line change with no break, which is good. A major-release control is absent.
- **Pull request description, commit body, squash-copied body.** Only the pull request description is run.
- **Break kinds.** The definition lists a new failure, a different return value or result shape, a removed or renamed option, a changed default, a changed error code, and an extension to inputs that worked before. The case exercises three of these: a new failure, a result shape and an extension. A removed option, a changed default and a changed error code have no case.

The README's noise caveat is honest: one run per cell on the rule, and `opus/result-2.md` fails check 3. The conclusion "three of four" rests on two runs per cell, which meets the AGENTS.md minimum.

Pre-existing state, the values users already pass and replaced mechanisms: not applicable (a skill, with no persisted format, no setting and no mechanism).

**Table of added instructions.** I counted 6 instructions:
1. break leads unless the next release is a major;
2. what counts as a break, plus the "extended failure" clause;
3. how to read the next release;
4. the opening shape (heading, short paragraph);
5. the commit-body order;
6. the checklist item.

Instruction 6 restates 1 and so is not counted separately. Instructions 3 and 5 are exercised by no input of the cases.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:252` "opens with slot 3's break lines, under a `Breaking changes` heading where the description has headings" | a description whose template has fixed headings (a `Summary`/`Testing` repository template, line 265) | a `Breaking changes` heading that the template does not have, or a lead above the template's first heading | "only where the template has no section that fits; otherwise the lines go under the template's first heading" |

Not findings: `:236` (a change with no break grows no section, which ends the lead), `:235` (the "a failure that now succeeds is a fix" definition), `:259` (already limits the commit-body lead to squash-copy).

## Item 3a: level, placement, environment

- The case READMEs sit under `research/…/cases/`, as AGENTS.md prescribes.
- Both new cases use the same layout (`prompt.md`, `<model>/result*.md`, `skill-tree`) as the convention.
- `make check-descriptions` passes ("all 27 skill descriptions within 1020 characters").
- `make check` only completed a dry run of marketplace generation here, so I did not treat it as evidence.
- The 4392 README says "as in `pgjdbc-4367-breaks`". That is a link, not a duplicated fixture.

## Item 4: names by content, not position

None in the committed prose. One finding: result files are `result.md` and `result-2.md`, an ordinal, though there is no content difference to name them by. This is the convention across the case, so it is taste, not a request.

## Item 5: failure report

The checks in the case READMEs name what to look for ("`grant insert on t to bob` after a `;`… is a break line, not left in Scope"). The per-run table names the failing check. Check 5 "Stated once" is graded passes for `opus/result.md`. That result lists `grant insert` in the lead (line 8) and again in Scope (line 44), where it restates the `explain insert` reasoning. This is not the same sentence, but it is the same fact, so the "passes" grade is generous (taste). Check 1's "at most a short paragraph" is not measured by the snippet, and the README grades it by reading.

## Item 6: what the writer says it verified

The red run on the base is present: the baseline runs fail checks 1 to 3, and the rule runs pass them (3 of 4 for check 3). The control passed in all four runs. Noise is stated and the mutated drafts are summarized. Evidence for this item is satisfied, apart from the commit-message and README mismatch above.

## Item 7: siblings

- Other places that list or route to the skill: the package README (updated with a new bullet), `apm.yml` and `marketplace.json` (both updated), and the umbrella (pinned by path, so no change). The `english-developer-style` text mentions `change-description-authoring` only by name.
- Other places in the skill that state the Why-first order: line 86 (updated), line 193 "in order" (not updated), the checklist "Problem" item (updated), the line-257 commit-body sentence (consistent), and the §4 rule 5 text at line 637. Rule 5 still says "shape it as §2's commit body" without pointing at the lead exception that §2 now carries. That is a reader-facing seam; the exception is stated in §2 only. Taste.
- The changelog-entry section (§2, `**Breaking:**` at line 543) already sorts breaks first within a category, so it is not affected.
- The set-size check: no sentence counts the slots or rules as a set of the old size.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule name ("promises compatibility") that is not in the skill | Substantive | `research/…/cases/pgjdbc-4367-breaks/README.md:8`, `…/pgjdbc-4392-no-break/README.md:7` | Quote the committed rule: "unless the next release from the target branch is a major" |
| Commit message says both models ran at effort high; the 4367 README says Opus ran at the session default | Substantive | commit message vs `…/pgjdbc-4367-breaks/README.md` "Running it" | Make them agree with what was run (amend the message or the README) |
| Major-release branch, unknown release, the commit-body order, squash-copied body, and the other break kinds have no case | Substantive | `SKILL.md:234-259` | State in the README that these partitions are untested, or run at least the major-release control (a break in a major release stays first in slot 3 with no lead) |
| The lead instruction has no condition for a repository template with fixed headings | Substantive | `SKILL.md:252`, with the template at `:265` | Add "only where the template has no section that fits" (see the table) |
| Table header "Six slots, in order" is unqualified now that slot 3 can lead | Taste | `SKILL.md:193` | Add "; slot 3's break lines move ahead of slot 1 (below)" |
| §4 rule 5 does not mention that the lead stays in the copied body | Taste | `SKILL.md:637` | Add a pointer to §2's lead |
| Check 5 grades `opus/result.md` as passing although `grant insert` appears in both the lead and Scope | Taste | `…/pgjdbc-4367-breaks/README.md` results table | Grade it as a partial fail, or say why Scope's restatement does not count |
| `result.md` / `result-2.md` are ordinal names | Taste | case dirs | Leave (it is the existing convention) |

This review did not run the drafting models or the suite beyond `make check-descriptions`, did not re-grade every check of the committed results line by line beyond the literal, lead and `grant insert` placement checks, and did not do a style pass over the prose.
