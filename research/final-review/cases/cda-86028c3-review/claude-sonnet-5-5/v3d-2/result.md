# Final review: `4f69810..86028c3` (one commit, "lead the description with breaks unless the next release is a major")

**Task statement:** none was handed over, so the claimed cases come from the commit message alone (item 2).

**Previous report:** none.

**Change type:** no code. It is a skill, a package README, version bumps, and a research directory. I used the §2a analogues under every item. The drift script was not run, because there are no members to parse. I loaded `english-developer-style`; `apm-authoring` and `docs-page-authoring` are not among the three skills I was given, so they were not loaded.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **Stale rule quote (substantive).** Both case READMEs quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility". The shipped rule is "A break leads the description unless the next release from the target branch is a major" (SKILL.md:234). The two differ on the unknown-release case. See `pgjdbc-4367-breaks/README.md:7` and `pgjdbc-4392-no-break/README.md:6`.
- **Sibling rule not updated (substantive).** The new text says the lead stays when the description becomes the commit body (SKILL.md:259-260). Two sentences still say the opposite or are silent:
  - §4 rule 5 (SKILL.md:637-638) says "shape it as §2's commit body", and §2 puts the problem first.
  - SKILL.md:310 says the description "takes the body's shape instead".

  A reader following rule 5 drops the lead.
- **Section references (none).** I checked `§4 rule 5` (line 637), `§5` (trailers, line 691), `§7` (line 787), and the table's "(below)". All resolve.
- **Count and file list (none).** No sentence still counts the old number of slots.
- **Narration (none).** No "now" or "no longer" outside the one place a regression comment may use them.

## Item 2: claimed cases covered

| Claim from the commit message | Covered by |
| --- | --- |
| Break leads when the release is not a major | `pgjdbc-4367-breaks`, Opus and Haiku, two runs each |
| Result shape (`getUpdateCount()` `-1`) is a break | check 2 of the same case |
| Extended failure is moved out of Scope, "three of four" | check 3; the README table gives 3 of 4 passes (`opus/result-2.md` fails). Matches. |
| No lead and no section when nothing breaks | `pgjdbc-4392-no-break`, four runs |
| Baseline on `origin/main` fails | `opus/baseline` and `haiku/baseline` |
| Release read from a version file, milestone, or name | The prompts supply the version file and "no milestone". Partly. |
| Major release: breaks stay first in slot 3 | **No case.** |
| Nothing says which release: breaks lead | **No case.** |
| Commit body keeps problem first with breaks as the first `User-visible:` lines | **No case.** |
| Description becomes the commit body under squash: the lead stays | **No case.** |
| Effort: "Opus and Haiku (effort high)" | **False for Opus.** The case README says "Opus at the session's default". |

- The effort claim is a substantive finding: the commit message and the README disagree about the Opus runs.
- Four claimed branches of the rule have no case; they are listed under item 3.

**Commands the change tells someone to run:** none. The `git archive <rev> ...` line in the case README is a recipe. No script or CI job runs it, and it promises no outcome the change depends on.

**Hunk to claim:**
- The `1.4.0` to `1.5.0` bumps (three files), the package README bullet, and the research README lines are claimed by no sentence of the message. The bump is justified but unclaimed, so I label it taste.
- The `cases/` line added to the research README tree is unclaimed too.

## Item 3: boundaries, partitions, and the negative control

- **Control arm.** `pgjdbc-4392-no-break` is the control for "no break". It is the only one, and it targets a patch release, the same arm as the main case.
- **Missing partitions (substantive).** There are four, as listed under item 2: a major target, an unknown release, the commit-body shape, and the squash copy. The first of them is the one that checks the rule's own exception clause. No run shows the lead absent for a major release, so a model that always leads would pass every stored case.
- **Pre-existing state:** an install over 1.4.0 leaves nothing behind; the skill is replaced whole. Nothing to check.
- **Limits and replaced mechanisms:** not applicable.

**Table of added instructions**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Open with "at most a short paragraph that says which code breaks" | one break whose own line already names the code | a paragraph that restates the line | none; taste, "only where the break lines do not name the code" |
| "The trailer decides, and it is written whatever the description does" | a patch-branch change carrying `BREAKING CHANGE:` | ambiguous: the tool makes the release a major, so the lead is dropped, or the trailer is written and the lead stays | none; taste, state which |
| Read the release from the version file, milestone, or branch name | a repo with none of the three | breaks lead | already ended by "Where nothing says which release it is" |
| Break lines under a `Breaking changes` heading | a description with no headings | no heading | already ended by "where the description has headings" |
| Commit body: breaks as the first `User-visible:` lines | a change with no break | nothing | already ended by "A change with no break has neither the lead nor an empty heading" |

Not findings: the three rows ended by quoted text above. The reading of "failure extended to inputs that worked before" is a rule the stored cases exercise.

## Item 3a: level, placement, and the environment

- **Placement.** The rule sits in §2 next to slot 3, and the checklist line is in §8. The package README and the marketplace entry carry the same version.
- **Gate.** `make check` runs the version-alignment check as a dry run and passes; the description check passes (27 skills ≤ 1020 characters). I could not run the marketplace sync against `origin`, because the repository has no remote here.
- **Trees.** `skill-tree` for the with-rule runs equals `HEAD:` the skill tree (`4798053…`). The baseline tree (`1f020ce…`) equals the base commit's tree. The recorded runs match the committed text.

## Item 4: names by content, not by position

None. Run files are `result.md` and `result-2.md`. That is an ordinal, but the README table names each by path and the tree id disambiguates them, so I did not file it.

## Item 5: the failure report

The detection for each rule is a check list with named pass or fail per run in the README table. Each check detects the property it is attached to; check 4 (the fix stays out) is the guard against over-marking. No finding.

## Item 6: what the writer says it verified

- **Red evidence:** the baseline runs fail checks 1 to 3 on both models.
- **Noise check:** the control runs show no growth.
- **Rewritten rule:** the rule was reworded after review, and the final wording was run: one of two Opus runs and both Haiku runs. The README says so ("moves the case most of the time and not always"), and the commit message agrees.
- **Not run:** nothing was re-run for this review.

## Item 7: siblings of the change

- **Places that name the rule:**
  - the package README (updated);
  - the marketplace and root `apm.yml` entries (version only);
  - the instruction file `change-description-authoring.instructions.md`, which does not mention breaks, so there is nothing to update there;
  - SKILL.md §4 rule 5 and line 310 (finding in item 1);
  - the changelog section (line 543), where breaks are "sorted first within their category". That stands unchanged and is consistent, because the new rule is about descriptions.
- **Set size:** no sentence counts slots or rules in a way the change invalidates.
- **Twin paths:** the UK and US style packages and `english-developer-style` are not touched and do not describe this rule.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the rule as "where the next release … promises compatibility"; the rule reads "unless the next release … is a major" | substantive | `research/.../pgjdbc-4367-breaks/README.md:7`, `.../pgjdbc-4392-no-break/README.md:6` | Quote the shipped sentence |
| Commit message says "Opus and Haiku (effort high)"; the README says Opus ran at the session default | substantive | commit message; `pgjdbc-4367-breaks/README.md` "Running it" | Make the two agree, with the effort that was actually used |
| §4 rule 5 and the sentence at line 310 still send a squash-copied description to the commit body's shape, which contradicts "the lead stays" | substantive | `SKILL.md:637-638`, `SKILL.md:310` | Add the exception to both, or say in line 259 that it overrides them |
| No case for a major target, an unknown release, the commit-body shape, or the squash copy | substantive | `research/.../cases/` | Add a case with a major target as the control arm for the exception, and name the others as follow-up in the description |
| "The trailer decides" does not say what it decides | taste | `SKILL.md:247` | State whether the lead is dropped or kept |
| Version bump and `cases/` tree line are claimed by no sentence | taste | `apm.yml`, `marketplace.json`, `research/.../README.md` | One clause in the message |
| "At most a short paragraph" restates a break whose line already names the code | taste | `SKILL.md:252-253` | "Only where the lines do not name the code" |

**Not checked:** I did not run the stored prompts again or the marketplace sync against a remote; the wording was reviewed only where a sentence reads wrongly (no style-only pass); `apm-authoring` and `docs-page-authoring` were not available to load.
