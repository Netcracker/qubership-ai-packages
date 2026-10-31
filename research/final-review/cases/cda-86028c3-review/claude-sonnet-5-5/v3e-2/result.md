# Final review: `4f69810..86028c3` (one commit, "lead the description with breaks unless the next release is a major")

**Inputs.**
- There is no separate task statement. The claimed cases come from the commit message.
- There is no previous report.
- I did not run `comment-drift.py`. The change has no code, only a skill, its README, package and marketplace metadata, and a research directory (§2a).
- I loaded `english-developer-style` from the given skills directory. `apm-authoring` is not in that directory, so I checked the skill by reading it against the form.
- Each item below uses the §2a analogue.

## Item 1: statements consistent with each other and with what they cite

Two findings.

- **Stale rule title (substantive).** Both case READMEs quote the rule as "A break leads the description where the next release from the target branch promises compatibility".
  - `pgjdbc-4367-breaks/README.md:8` quotes it, and `pgjdbc-4392-no-break/README.md:7` has the same quote.
  - SKILL.md line 234 now reads "A break leads the description unless the next release from the target branch is a major". The old wording matches nothing in the skill (`grep -rn 'promises compatibility'` finds only these two lines).
  - The 4367 README also cites "SKILL.md §2", which is right, but the quoted title is not.
- **Squash-body order conflicts with §4 rule 5 (substantive).**
  - Line 257 says the commit body keeps "problem first, with the breaks as the first `User-visible:` lines", because "the label is what R4 and R5 search for".
  - Lines 258–260 then say that where rule 5 makes the description the body, "the lead stays". That body "opens with its breaks and then its problem" under a `Breaking changes` heading, with no `User-visible:` label.
  - Rule 5 (line 637) still says to "shape it as §2's commit body".
  - So one sentence says the body keeps the label and problem first, and the next says a squashed body does neither.
  - The skill does not say which rule wins, or what a squashed body does with the label.

Checked and consistent:
- The checklist items at lines 831 and 849 match §2.
- The slot 1 sentence (line 86) matches line 259.
- The `(§5)` reference matches the `BREAKING CHANGE:` row at line 706.
- The `(§7)` reference matches line 787.
- The version 1.5.0 appears in the same three places as 1.4.0 did: `apm.yml`, the package `apm.yml`, and `marketplace.json`.
- The word counts, the "3 of 4" figure, and the "all Haiku results end with a Claude Code line" claim match the files.
- The `skill-tree` ids match `git rev-parse` for `HEAD` (4798053…) and the base (1f020ce…).
- No comment narrates the change.

**Ambiguity (substantive).** Line 247 says that where a release tool bumps the major on a `BREAKING CHANGE:` trailer, "the trailer decides". The change's own trailer would then make the next release a major, which switches the lead off for exactly the change whose break the patch-release reviewer needs to see first. The sentence can be read either way. Say which: the trailer says the break is marked for the tool, and the lead still follows the target branch's version.

## Item 2: claimed cases covered

| Claim (commit message / skill) | Covered by |
| --- | --- |
| Break lines lead on a patch-release target | `pgjdbc-4367-breaks` checks 1–3: `opus/result.md`, `haiku/result.md`, `haiku/result-2.md` pass; `opus/result-2.md` fails check 3 |
| The result-shape change is a break | check 2: all four rule runs pass |
| A failure extended to later statements is a break | check 3: three of four pass |
| Without the rule, Why comes first | the two baselines |
| A change with no break grows no section | `pgjdbc-4392-no-break`, four runs |
| Literals are kept | checks 6 and 3 |
| A read of the release "from version file, milestone, or name" | the prompt supplies only `gradle.properties` (42.7.14), with no milestone |
| The release is a major, so breaks stay first in slot 3 | none |
| Nothing says which release it is, so breaks lead | none |
| A description without headings (prose, no template): the lead is a short paragraph | none; both prompts have headings |
| The commit body keeps its order, with breaks as the first `User-visible:` lines | none |
| The squashed description keeps the lead | none |

**Substantive.** The last four claims have no case, so the skill changes without evidence for them. They are the unknown-release branch, the major branch, the prose shape, and the commit-body and squash behavior. The commit message claims runs only for the patch-release case, but the SKILL.md text asserts all four. The request is to add one case for each of these four, or to narrow the text to the cases that ran.

The `Hunks claim` check passes: every hunk belongs to a sentence of the commit message.

No command lines are added for a reader to run.

## Item 3: partitions, negative control, pre-existing state

- The negative control `pgjdbc-4392-no-break` exists, with two runs per model. It has no baseline run on the old skill. That is taste, because the commit claims only that the control "grows no section".
- The partitions the change claims but does not test are the same four as in item 2 (major, unknown, prose, commit body).
- Pre-existing state: the package is installed over 1.4.0 with no other state to meet. The existing descriptions it applies to are not rewritten, so there is nothing further.

**Added instructions** (table from §2a):

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| A break leads, "where nothing says which release it is" | an application repository that deploys continuously and has no release numbering | a `Breaking changes` lead for a reviewer who is not deciding whether the change fits a patch release | "only where the target branch publishes numbered releases" |
| A failure extended to inputs that worked before goes with the breaks, not in Scope | a failure on inputs the caller can only reach through a bug, with no documented use | a break line for an input no code relied on | "where a caller could pass that input" |
| The `BREAKING CHANGE:` trailer "decides" | a patch-targeted change that carries the trailer | read either way (item 1) | filed under item 1 |
| The squashed description keeps the lead | a squash body (`git log --first-parent`) | a `Breaking changes` heading inside the commit body, without the `User-visible:` label | filed under item 1 |

The first two rows are **taste**, since the skill is not written for those inputs. The last two are filed under item 1.

Not findings: "A change with no break has neither the lead nor an empty heading (§7)", which ends the lead where nothing breaks. A failure that now succeeds is a fix, not a break, and the same sentence ends that case.

## Item 3a: level, placement, environment

None. The cases sit beside each other under `cases/` and follow the same layout. The research README (line 49) and the closing paragraph register the directory. I did not run the repository's own gate, because there is no network and I did not look for an offline one.

## Item 4: names by content

None substantive. The files `result.md` and `result-2.md` are numbered by ordinal, but the README table names each run by path. That is taste, and I am not requesting a change.

## Item 5: the failure report

Taste. The case READMEs name the failing check per run, such as "fails: in Scope". The per-check table gives a reader what to look at. There is no checklist entry in the skill that detects check 3 beyond the new "Breaks" line, which does cover it.

## Item 6: what the writer says it verified

The change states the red runs: `opus/baseline` and `haiku/baseline` fail checks 1–3 on the old skill, and the rule runs pass. One baseline run per model is thin. The README says outright that the `grant insert` case moves "most of the time and not always". The README says Haiku ran at effort `high` and Opus "at the session's default". The commit message says "Opus and Haiku (effort high)". **Substantive**: one of the two is wrong. Correct the commit message, or the README with the actual setting.

## Item 7: siblings

- The package README bullet was added, and `marketplace.json` and both `apm.yml` files were bumped together.
- `english-developer-style` (lines 502–509, 566–571) defers breaking-change placement to this skill without restating it, so it needs no change.
- Within SKILL.md, the commit-body table, the changelog section (§3, `**Breaking:**` in place), and the slot 3 text are updated or unaffected. The sibling that was missed is §4 rule 5 (item 1).
- The instructions trigger file needs no change, because the trigger is unchanged.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The rule title quoted in both case READMEs no longer exists in the skill | substantive | `cases/pgjdbc-4367-breaks/README.md:8`, `cases/pgjdbc-4392-no-break/README.md:7` | quote the current sentence ("A break leads the description unless the next release from the target branch is a major") |
| A squashed body opens with breaks and a heading, against "problem first, `User-visible:` label" and rule 5 | substantive | `SKILL.md:257–260`, `:637` | state which rule wins for a squash body and where the break lines carry the `User-visible:` label |
| The trailer "decides", and the sentence reads either way | substantive | `SKILL.md:247` | say whether the trailer turns the lead off |
| No case for the major, unknown-release, prose-without-headings, commit-body, or squash branches | substantive | `cases/` | add one case per branch, or narrow the text to the cases run |
| Effort setting for Opus differs between commit message and README | substantive | commit message, `cases/pgjdbc-4367-breaks/README.md:33` | make them agree on the real setting |
| Lead fires for a continuously deployed application, and for failures only a bug reaches | taste | `SKILL.md:234–250` | add the clause named in the table |
| No baseline for the control case | taste | `cases/pgjdbc-4392-no-break/` | optional |

This review did not run any case, test, or lint gate, and the pass over the prose was for the form only, not for style.
