# Final review: `4f69810..HEAD` (86028c3, change-description-authoring 1.4.0 → 1.5.0)

I found eight substantive problems and two taste notes. Three are worth fixing first. The rule's own "major release" and "unknown release" branches were never run. The `BREAKING CHANGE:` sentence doesn't say what it decides. And the new rule conflicts with the existing Scope rule on the exact case one Opus run got wrong.

**Inputs.** There was no task statement, so the claimed cases come from the commit message alone. There is no earlier report. This is a change with no code (a skill, a README, manifests and research cases), so each item below uses the §2a analogue. I didn't run the drift script on it, because it parses code members and none changed. I loaded `english-developer-style` from the given skills directory and the repository's `apm-authoring`, as §2a asks for a skill package.

## Item 1: comments consistent with the code and with each other

Analogue: what one file says about another, and what the skill says in other places about the same fact.

- **Stale rule quote in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` says "…unless the next release from the target branch is a major". Someone searching the skill for the quoted text finds nothing.
- **"Breaks first in slot 3" is still stated as unconditional.** `SKILL.md:226` ("Breaks come first…") and checklist `SKILL.md:845` ("under 'User-visible changes', breaks first") weren't changed. The new text at `SKILL.md:252-254` and checklist `:851` says slot 3 keeps *only the other outcomes* unless the next release is a major. An agent applying `:845` on a patch release puts the breaks in slot 3, which is the exact baseline failure. Both lines need the "where the next release is a major" condition.
- **Conflict with the Scope rule.** `SKILL.md:238-240` says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". `SKILL.md:489-492`, unchanged, says that where only a maintainer can decide "whether a compatibility break is intended", the break stays "in the Scope slot as a question". The `grant insert` case matches both. `opus/result-2.md:35` follows the Scope rule ("This change keeps that rule, because … rely on it"), which is the one run the case README marks as failing check 3.
- **The `User-visible:` label under §4 rule 5.** `SKILL.md:257-258` keeps breaks under `User-visible:` because "the label is what R4 and R5 search for". `SKILL.md:259-260` says that under rule 5 the body "opens with its breaks and then its problem". Rule 5 bodies have no headings (`:857`) and slot 3 lines go under `User-visible:` (`:208`). So the lead either repeats the label above the problem, or the breaks lose the label the paragraph says readers search for. The text doesn't say which.
- Checked with no problem found: `:86-89` (the Slot 1 change), `:198` (table row), `:831` (checklist), the package README bullet, `research/.../README.md:49,86`, and the three version strings, which agree.

## Item 2: claimed cases covered

Claimed cases, taken from the commit message:

| Claim | Where it is handled | Evidence |
| --- | --- | --- |
| Description opens with breaks when the next release is not a major | `SKILL.md:234,252` | 4367: 4/4 runs lead; baseline 0/2 |
| Read from version file, milestone or branch name | `:245-246` | Version file only; the prompt says there is no milestone and the branch is `master` |
| Breaks lead when nothing says which release | `:248-250` | **None**: no case leaves the release unknown |
| Next release is a major: breaks stay in slot 3 | `:254-255` | **None** |
| Definition: result shape is a break | `:236` | 4367 check 2, 4/4 |
| Definition: a failure extended to later statements is a break | `:238-240` | 4367 check 3, 3/4 |
| Definition: removed option, changed default, changed error code | `:237-238` | Not exercised (not separately claimed by the trial) |
| Commit body keeps the problem first, breaks first under `User-visible:` | `:257-258` | **None**: the prompts ask only for a description |
| Under rule 5 the lead stays | `:258-260` | **None**: both prompts give `squash 3 plain 37` with commit bullets, so rule 5 doesn't apply |
| A change with no break grows no section | `:255`, `§7` | 4392: 4/4 |
| Model and run counts (Opus, Haiku; 2+1 and 2) | Case dirs | Files present; `skill-tree` 4798053 = `HEAD:` tree and 1f020ce = `4f69810:` tree (checked with `git rev-parse`) |

Commands the change tells someone to run:

- `cases/pgjdbc-4367-breaks/README.md:31-32` says to copy the skill out "with `git archive <rev> agent-packages/…`". Nothing in the repository runs this.
  - The outcome depends on where the output goes: `git archive` without `--output` writes a tar stream to stdout and copies nothing.
  - The documented form needs `| tar -x -C <dir>`, or should be replaced by a script that runs it, as `research/blackbox-test-design/cases/run-case.sh` does for its sibling cases.

Hunks no sentence claims: the version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2` and `.claude-plugin/marketplace.json:291`. Earlier commits in this series state it ("Version 1.2.0 to 1.3.0."); this message doesn't.

## Item 3: boundaries, partitions, and the negative control

- **Partitions with no evidence:** next release is a major, next release unknown, a commit body, and a description that rule 5 makes the body. The trial covers one partition of the rule's condition (patch release, plain description). The rule's own "unless" branch was never run.
- **Negative control:** 4392 (no break, patch target) covers "no lead, no empty heading". There is no control for "break present, next release a major", which would show that the rule doesn't fire.
- Earlier state: not applicable, since this skill isn't installed over persisted state.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:247` "Where a release tool bumps the major … the trailer decides" | A break in a release-please repo whose version file says a minor is next | Unclear: the trailer makes it a major, so the breaks stay in slot 3, and the reviewer's "may this force a major" decision isn't led with | State what the trailer decides, e.g. "the breaks lead, because the reviewer decides whether the change may force a major" |

Not findings: `:235` "code that works on the released version", `:252` "after at most a short paragraph", `:255` "neither the lead nor an empty heading".

## Item 3a: level, placement, and the environment

- The rule sits in §2 next to slot 3 and is restated in the §8 checklist; that's the right place.
- The cases use a `<model>/result*.md` plus `skill-tree` layout. The sibling `research/blackbox-test-design/cases` uses `results/` and `run-case.sh`. It's a different layout, but both are documented in their READMEs.
- The repository's gate, `apm pack --check-versions --check-clean --dry-run`, ran offline with exit code 0 using the local `apm`.
- The new result and prompt files match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`.
- The rule doesn't read like generic tutorial text: it cites pgjdbc-style version files and branch names, and a real maintainer rewrite.

## Item 4: names by content, not by position

None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`), the check names (Lead, Result shape, `grant insert`, …) and the section references (§2, §4 rule 5, §7) all name things by content. I didn't find "above" or "below" pointing at a position, except `:198` "(below)", which points within the same subsection.

## Item 5: the failure report

- Each case README check says what to look at and what a failure looks like ("fails: Why first", "fails: in Scope").
- The new checklist line `:849-852` reaches the rule, but checklist line `:845` still asks for the weaker, contradicting property (see Item 1).
- No check covers "is the next release correctly identified". Check 1 assumes a patch target and doesn't test that the agent read it.

## Item 6: what the writer says it verified

- **Exemplar and bad case:** the baseline on `4f69810` fails checks 1–3 on both models, and the committed tree passes on 4/4 (3/4 for check 3). The `skill-tree` ids confirm the results are for the committed text. The README also reports the earlier drafts of the rule.
- **Growth on the control:** the 4392 control word counts (241–256) are compared with the author's draft (209), not with a pre-rule baseline run. So the claim that the rule adds nothing where nothing breaks isn't measured against the skill without the rule.

## Item 7: siblings of the change

- The package README is updated. `marketplace.json`, `apm.yml` and the package `apm.yml` agree on 1.5.0. The research README lists `cases/`.
- The changelog rule (`SKILL.md:543`, breaks marked in place) is a separate artifact, and its wording stays consistent.
- The skill's `description:` isn't widened, and doesn't need to be.
- `git grep` for "breaks first" or "break … lead" finds only the in-file sites already listed in Item 1, plus the two stale README quotes.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The rule's "major" and "unknown release" branches, the commit-body ordering and the rule-5 lead have no run | Substantive | `cases/`, `SKILL.md:248-260` | Add a case for a major-release target with a break (control) and one with no version signal, or narrow the commit message's claim |
| The new rule and the Scope-question rule both match a maintainer-decided extended failure, and ask for opposite placements | Substantive | `SKILL.md:238-240` vs `:489-492` | Say which wins, e.g. the break line leads and the Scope slot keeps only the question of intent |
| `:226` and checklist `:845` still put breaks first in slot 3 unconditionally | Substantive | `SKILL.md:226`, `:845` | Add "where the next release is a major", or point to `:252` |
| "the trailer decides" doesn't say what it decides | Substantive | `SKILL.md:247-248` | State the outcome for a break in a repository whose release tool reads the trailer |
| Under rule 5 the lead's breaks have no `User-visible:` label, against the reason `:258` gives | Substantive | `SKILL.md:257-260` | Say whether the lead carries the label in a rule-5 body |
| Case READMEs quote a rule wording that isn't in the skill | Substantive | `pgjdbc-4367-breaks/README.md:7-8`, `pgjdbc-4392-no-break/README.md:6-7` | Quote `SKILL.md:234` as committed |
| No baseline run for the control, so growth isn't measured against the pre-rule skill | Substantive | `pgjdbc-4392-no-break/README.md` | Run the control on 1f020ce and compare word counts |
| `git archive <rev> <path>` writes a tar to stdout and copies nothing | Substantive | `pgjdbc-4367-breaks/README.md:31-32` | Write `git archive <rev> <path> \| tar -x -C <dir>`, or add a run script |
| Version bump to 1.5.0 isn't claimed in the commit message | Taste | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." as the earlier commits do |
| Pre-1.0 SemVer (is 0.y → 0.y+1 "a major"?) isn't addressed | Taste | `SKILL.md:234,243` | Optionally say how a 0.y release counts |

This review didn't re-run any model trials or check the pgjdbc facts against upstream (there was no network), and it didn't do a style pass over the prose.
