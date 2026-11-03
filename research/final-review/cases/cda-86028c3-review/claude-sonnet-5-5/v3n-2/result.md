# Final review: `4f69810..86028c3` (change-description-authoring 1.5.0)

**Inputs.**
- No separate task statement was handed over. The claimed cases come from the commit message alone, and item 2 is answered from it.
- The change has no code: it edits a skill, a README, manifests and research cases. §2a applies.
- The drift script was run and printed nothing, because it parses code and this change has none.
- I loaded `apm-authoring` and used its rules 2 and 4. I did not load `english-developer-style`, since wording enters only where a sentence reads wrongly.
- There is no previous report for this change.

## Item 1: comments consistent with the code and with each other

Analogue: every statement a changed file makes about another file or section.

Checked and consistent:
- The version bump is 1.5.0 in the package `apm.yml`, the root `apm.yml` and `marketplace.json`.
- §4 rule 5 and §7 exist as cited.
- The case `skill-tree` ids match `git rev-parse HEAD:<skill dir>` (`4798053…`) and `HEAD~1` (`1f020ce…`).
- The results tables match the result files:
  - The first heading of each 4367 run is `Breaking changes` or `Why` as the table says.
  - Opus `result-2` leaves `grant insert` in Scope.
  - Each Haiku result carries a `Generated with` line.
  - Word counts match.

Findings:
1. **Rule 5 contradicts the new commit-body paragraph (substantive).**
   - `SKILL.md:637-638` says a description that becomes the commit body is shaped "as §2's commit body". That body is problem first, with the breaks as `User-visible:` lines.
   - `SKILL.md:257-260` says that under rule 5 "the lead stays" and the body "opens with its breaks and then its problem".
   - An agent that follows rule 5 writes one body; an agent that follows `:257` writes another.
   - The lead is a heading with no `User-visible:` label. The same paragraph says that label is what R4 and R5 search for.
   - `:86` and `:849` assume the lead version.
2. **"The trailer decides" has two readings (substantive).**
   - `SKILL.md:247-248`: "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides, and it is written whatever the description does."
   - It does not say what the trailer decides. It could mean the release is a major, so no lead. Or it could mean the break is a break, so the lead stays on a patch branch.
   - The two readings give opposite descriptions for the same input.
3. **The case READMEs quote the old rule name (substantive).**
   - Both `pgjdbc-4367-breaks/README.md` and `pgjdbc-4392-no-break/README.md` cite "A break leads the description where the next release from the target branch promises compatibility".
   - The committed heading is "…unless the next release from the target branch is a major" (`SKILL.md:234`).
   - The README for 4367 also says the rule is in "SKILL.md §2", which is correct, but the quoted name is not.
4. **Effort setting is stated two ways (substantive).**
   - The commit message says "Opus and Haiku (effort high)".
   - The 4367 README says "Haiku ran at effort `high`; Opus at the session's default", and the 4392 README names effort only for Haiku.
   - One of these is wrong about how the runs were made.

No `now`, `no longer` or `used to` narration was added to the skill. The case READMEs narrate the drafts' history ("reworded after review"), which is acceptable in a research record.

## Item 2: claimed cases covered

Analogue: the cases the commit message names, and the section or case that handles each.

| Claim | Covering case |
| --- | --- |
| Break leads (check 1) | 4367 runs `opus/result`, `opus/result-2`, `haiku/result`, `haiku/result-2`, with baselines that fail |
| Result shape is a break | Same runs; baselines fail |
| Extended failure leaves Scope | 3 of 4 runs; one Opus run still fails. The commit message and README both say so. |
| No section when there is no break | 4392, four runs |
| Literals kept | Check 6 in 4367 and check 3 in 4392 |
| Release read from version file, milestone or name | Only the version file is tested. The prompt supplies `gradle.properties` at 42.7.14. |
| Next release is a major: no lead, breaks stay first in slot 3 | No case |
| Nothing says which release it is: breaks lead | No case |
| `BREAKING CHANGE:` trailer / `!` | No case |
| "Where squash copies the description into the commit, the lead stays" | No case |
| Commit body keeps problem first, breaks as the first `User-visible:` lines | No case |
| "A failure that now succeeds is a fix, not a break" | Check 4 in 4367 (`create table begin(atomic int)…`) |
| Changed default, removed option, changed error code | No case. Only the result shape and a later-statement failure are exercised. |

Commands the change tells someone to run: none. The README's `git archive <rev> agent-packages/...` is a recipe for the case runner. I did not run it, and the repository has no script or CI job for it. That is a gap, not a finding.

Hunk-to-claim check: every hunk belongs to a sentence of the commit message. The `research/…/README.md` index line and the date note are covered by the sentence that names the cases. The checklist item, the README bullet and the version bumps are covered by the rule itself.

## Item 3: boundaries, partitions, and the negative control

Partitions the change claims:
- **Major release.** There is no case, so the negative control for the condition's other branch is missing. The 4392 control varies the content (no break), not the release type. A run with a prompt that says `pgjdbc.version=43.0.0` is the control the rule's own condition needs.
- **Unknown release.** There is no case.
- **Squash and commit-body path.** There is no case, and it is the path that finding 1 shows is contradictory.
- **Breaks other than result shape and later-statement failure.** There are no cases. This is taste: the rule lists five kinds and one case cannot cover them all.

Other points:
- **Runs per case.** The 4367 prompt gives the version file, so the "read from version file" step was never exercised without it. Two runs per cell is thin, and the README admits the sentence moves `grant insert` "most of the time and not always". Taste.
- **Pre-existing state, values users already pass, replaced mechanism, limits:** none apply. This is a skill update with no installer or settings.

Added instructions: 6.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:238-239` "a changed error code for a failure a caller may catch" | a patch that swaps `NullPointerException` for `IllegalArgumentException` on an input that already failed | a lead of one break line ahead of the Why slot | "only where code that worked on the released version now fails or returns something else" |

Not findings: `:234` (the major-release condition ends it), `:243-246` (the version-file read ends it), `:252-256` (the "no break, no lead" clause at `:255` ends it), `:849-852` (the checklist restates `:234`).

## Item 3a: level, placement, environment

Analogue: where each rule and file lives.
- The cases sit under `research/change-description-authoring/cases/`, beside the phase files, and are indexed in that README.
- The registration entries (package `apm.yml`, root `apm.yml`, `marketplace.json`) agree on 1.5.0.
- I found no other file that lists the package's version.
- Not run: the repository's registration gate. It was not necessary, because the three manifests were read by hand.
- The `cases/` README lines are a new category in the research directory. I did not check whether markdownlint excludes the unedited result files, as the research README says it does for phase results.

## Item 4: names by content, not by position

Analogue: the change's own headings, references and case names.
- Case names are by content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`).
- `result.md` and `result-2.md` are ordinal run names. They are acceptable as a run index, but the README tables point to them by those names. This is taste.
- The README refers to "the first" and "the second" version of the rule (Results, paragraph after the table). That is a position, not a content. Taste: name them by what they added (the sentence on a failure extended to inputs that worked before).

## Item 5: the failure report

Analogue: what the rule tells the reader to look at, and whether each rule has a detection.
- The case checks 1 to 3 detect the rule's three claims, and checks 4 to 6 guard against loss.
- The skill's own checklist (`:849`) reaches the rule.
- The detection for "unless a major" and for "unknown release" is absent. This follows from item 3.

## Item 6: what the writer says it verified

- The red run on the base: `opus/baseline` and `haiku/baseline` fail checks 1 to 3 on `HEAD~1`. This is stated, and the tree ids confirm the skill version used.
- The control arm: 4392, four runs. This is stated.
- Not stated: a run of the rule against a bad case where the added item is noise other than 4392. The 4392 word counts (241 to 256, against 209 in the draft) show some growth that the README does not explain. Taste.
- Not stated: a rerun of the existing worked example (§2 *After*, Why/What/Verification/Scope) against the rewritten rule. It has no break, so it passes unchanged.

## Item 7: siblings of the change

- Sibling surfaces that route to the package: `marketplace.json`, root `apm.yml`, package `apm.yml` (all updated), the package `README.md` (updated), and the `english-developer-style` and `docs-page-authoring` cross-references, which do not describe this rule and need no change.
- Count-prose search: I found no sentence that counts the slots or breaks as before. §2 still says "Six slots, in order", but slot 3's break lines now come ahead of slot 1. The "in order" claim is now false for the lead case. This is a substantive finding (see the table).
- The twin path is the commit body (`§2 Commit body`), and finding 1 covers it.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Rule 5 says the description is shaped as §2's commit body; the new paragraph says the lead stays and the body opens with breaks. The lead has no `User-visible:` label | Substantive | `SKILL.md:257-260`, `:637-638`, `:86`, `:849` | Pick one body shape for the squash path and state it in both places; keep the `User-visible:` label on the break lines |
| 2 | "The trailer decides" has two readings with opposite outputs | Substantive | `SKILL.md:247-248` | Say what it decides: that the release is a major (no lead) or that the break is written (lead stays) |
| 3 | Case READMEs quote a rule name that no longer exists | Substantive | `cases/pgjdbc-4367-breaks/README.md:5-6`, `cases/pgjdbc-4392-no-break/README.md:5-6` | Quote the committed heading |
| 4 | Effort setting differs between the commit message and the README | Substantive | commit message; `cases/pgjdbc-4367-breaks/README.md` (Running it) | Make them agree on how the Opus runs were made |
| 5 | No case for a major release, an unknown release, the squash path, or the trailer | Substantive | `cases/` | Add a major-release control (version file `43.0.0`) and a squash-path run, or narrow the commit message to what was run |
| 6 | "Six slots, in order" no longer holds when slot 3's breaks lead | Substantive | `SKILL.md:192` | Say "in order, except that the break lines lead (below)" |
| 7 | Changed error code on an already-failing input leads the description | Substantive | `SKILL.md:238-239` (added-instructions row) | End it with "only where code that worked on the released version now fails or returns something else" |
| 8 | "First/second version of the rule" in the README | Taste | `cases/pgjdbc-4367-breaks/README.md` (Results) | Name each version by what it added |
| 9 | Two runs per cell, with one of four still missing the extended-failure move | Taste | `cases/pgjdbc-4367-breaks/README.md` | More runs, or keep the "most of the time" wording |

## Not checked

I did not run the repository's lint or registration gate, re-run any case, or review the prose for style.
