# Final review of 86028c3: change-description-authoring, breaks lead the description

**Inputs.** There was no task statement, so the claimed cases come from the commit message alone, plus the checks in the two case READMEs. This change has no code: it touches a skill, its README, the manifests, and a research directory. I filled every item through its §2a analogue and say which one each time. The drift script ran and printed nothing, because nothing in the change is code it can parse. I loaded `english-developer-style` from the given skills directory and `apm-authoring` from `agent-packages/apm-authoring`. That copy has no rule named *Fix a bad output where the rule stops*, so I cite final-review §2a step 3 for that rule instead. There was no earlier report to re-read against.

## Item 1: comments consistent with the code and with each other
*Analogue: what each changed file says about another file or about the skill.*

- **Stale rule quote in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:5-7` quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility". The committed §2 rule (SKILL.md:234) says "…unless the next release from the target branch is a major". The quote is an earlier draft's wording. The README itself says that wording was reworded after review.
- **The checklist contradicts itself.** The §8 "Caller" item (SKILL.md:845-846) still asks for one line per outcome under "User-visible changes", "breaks first". The new "Breaks" item (SKILL.md:849-851) and §2 (SKILL.md:252-254) take the breaks out of slot 3 when the release is not a major. This matters: the parent commit's message records that drafting agents check their work against §8, so they meet two opposite instructions.
- **The "first question" now has two answers.** SKILL.md:203-204 says "the reviewer's first question is why that version should change". The new SKILL.md:243-244 says that in a release that is not a major, "the reviewer's first decision is whether the change may ship in it at all".
- **Taste:** SKILL.md:68 still says "the body is problem-first". Under §4 rule 5, a body copied from the description now opens with its breaks.
- **Taste:** the commit message reads "on Opus and Haiku (effort high)", which sounds as if both ran at high. The case README says only Haiku ran at high and Opus ran at the session default.
- The other cross-references hold: §7, §5's `BREAKING CHANGE:` row, §4 rule 5, the slot-1 sentence at SKILL.md:86, and the §8 "Problem" item. The recorded `skill-tree` ids also match the actual trees: `4798053…` is the skill at 86028c3 and `1f020ce…` is the skill at the base 4f69810.

## Item 2: claimed cases covered
*Analogue: each situation the commit message claims, against the case that exercises it.*

| Claim (commit message) | Covered by |
| --- | --- |
| Breaks lead when the next release is not a major | `pgjdbc-4367-breaks`, checks 1 and 5 |
| The next release is read from the version file | `pgjdbc-4367-breaks` (`gradle.properties` in the prompt) |
| …or from the milestone or the branch name | none |
| A major release keeps the breaks in slot 3 | none |
| Breaks lead "where nothing says which release it is" | none |
| A result-shape change is a break | `pgjdbc-4367-breaks`, check 2 |
| A failure extended to inputs that worked is a break | `pgjdbc-4367-breaks`, check 3 (passes in 3 of 4 runs, as the README says) |
| A new failure is a break | `pgjdbc-4367-breaks` (the `42703` and `0100E` lines) |
| A removed option, changed default, or changed error code is a break | none (named only as examples) |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | none: both prompts ask only for a PR description |
| Under a squash that copies the description into the commit, the lead stays | none: both prompts describe a one-commit PR that a squash would not turn into a description body |
| A change with no break grows no section | `pgjdbc-4392-no-break`, checks 1 and 2 |

**Commands the change tells someone to run.** `cases/pgjdbc-4367-breaks/README.md:31-32` says the skill is "copied out of the checkout with `git archive <rev> agent-packages/…`". Nothing in the repository runs that line, so the runner column is `none`. Run as written, `git archive` writes a tar stream to stdout and does not copy anything into a directory. The README also doesn't name `scripts/skill-tree.sh`, which is what produces the `skill-tree` files.

**Hunks no sentence claims.** The version bumps 1.4.0 → 1.5.0 appear in `marketplace.json`, `apm.yml`, and the package's `apm.yml`, and no sentence of the message claims them. This is **taste**: every earlier commit to this package does the same, `apm-authoring` *Versions* asks for the bump, and the gate confirms the bumps agree. Every other hunk maps to a sentence.

## Item 3: boundaries, partitions, and the negative control
*Analogue: partitions are the situations the change claims. The negative control is the cases plus the table below.*

- **The negative control for the rule's own condition is missing.** `pgjdbc-4392-no-break` controls for "no break". Nothing controls for "unless the next release is a major". The missing case is the same breaking input with a version file that names a major (for example `43.0.0-SNAPSHOT`), where the breaks should stay first in slot 3. Without it, nothing shows the condition ever stops the lead.
- **Four more claimed partitions have no evidence:** an unknown release, a milestone or branch name as the source, the commit-body form, and the §4 rule 5 body. The 4367 prompt also covers only the headings form, not the prose form ("after at most a short paragraph").

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Read the next release from the target branch: its version file …" (SKILL.md:244-246) | The version file holds the release already out, not the next one. This is true of the case's own prompt (`pgjdbc.version=42.7.14` beside tag `REL42.7.14`). Just after 5.0.0 ships, the file says `5.0.0`. | It reads 5.0.0 as a major and keeps the breaks in slot 3, although the next release is 5.0.1 or 5.1.0. That is the "break missed in a patch release ships" outcome the rule exists to prevent. | "A version equal to the latest release tag is the release already out; the next one is unknown unless a milestone or `-SNAPSHOT` says otherwise." **Substantive.** |
| "…under a `Breaking changes` heading where the description has headings" (SKILL.md:252) | The repository has a template (`## Summary`, `## Testing`). SKILL.md:300-302 says to use the template's headings. | Either a heading the template lacks, placed above `Summary`, or the breaks buried inside `Summary`. The two rules ask for opposite things on the same input. | Say where the lead goes in a template, for example "the break lines open the template's first section". **Substantive.** |
| "Where §4 rule 5 makes the description the commit body, the lead stays … that body opens with its breaks" (SKILL.md:258-260) | A repository whose squash copies "title and description" into the commit, with a break, targeting a patch release. | A body with no headings (rule 5) that opens with unlabeled break lines. Slot 4's `User-visible:` paragraph then lists only the other outcomes, so a grep for `User-visible:` (which SKILL.md:258 calls "what R4 and R5 search for") misses the breaks. | "There, the lead is the `User-visible:` paragraph, breaks first." **Substantive.** |
| "A break changes what code that works on the released version gets: …" (SKILL.md:235-241) | The skill's own slot-4 example (SKILL.md:116): `Pool.acquire() waits up to acquireTimeout instead of failing at once`. | Either reading: a wait is a different outcome for fail-fast code (a break), or a failure that now succeeds is a fix (not a break). | One clause on whether a changed timing or blocking behavior counts. **Taste:** leading with it costs a paragraph, by the rule's own reasoning. |
| "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer … the trailer decides" (SKILL.md:247-248) | A release-please repository. | It is unclear what "decides" refers to. One reading: the trailer makes the next release a major, so breaks never lead in such repositories. | "…the trailer makes the next release a major, and the breaks stay in slot 3." **Taste.** |

Not findings:
- A break in a feature added since the last release: ended by "code that works on the released version".
- An extended failure on inputs that were only accidentally accepted: ended by "Whether the old behavior was right does not decide it".
- A change with no break: ended by "A change with no break has neither the lead nor an empty heading".

## Item 3a: level, placement, and the environment
*Analogue: where the rule lives, the repository layout, and the gate.*

None. The rule sits in §2 under the PR description, with its checklist line in §8 and a bullet in the package README. The research `cases/` directory follows the repository's provenance layout, and `.github/super-linter.env` `FILTER_REGEX_EXCLUDE` covers `prompt.md` and `result*.md`. The gate passes offline: `apm pack --check-versions --check-clean --dry-run` exited 0, and `scripts/check-skill-descriptions.py` reported "all 27 skill descriptions are within 1020 characters". No sentence of the new rule could appear unchanged in a generic tutorial.

## Item 4: names by content, not by position
*Analogue: unchanged, applied to headings, cross-references, and case names.*

None. The slot numbers are the skill's own defined identifiers. The case names describe their content (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`). The README's "the first", "the second", and "the version committed here" are each defined in the same paragraph.

## Item 5: the failure report
*Analogue: does the checklist reach the rule, and does the check detect the rule or something weaker?*

The checklist reaches the rule ("Breaks", SKILL.md:849). But it checks something weaker. It asks whether the description opens with the break lines, assuming the breaks were already recognized. The cases show recognition is where drafts actually fail: the baselines put the `getUpdateCount()` result shape in slot 3 and the `grant insert` failure in Scope (checks 2 and 3). Nothing in §8 asks whether a changed return value, a changed result shape, or a failure extended to inputs that worked was counted as a break, or whether one was left in Scope. **Substantive.**

## Item 6: what the writer says it verified
*Analogue: an exemplar that passes and a bad case that fails.*

The evidence is stated:
- The baselines on 4f69810 fail checks 1–3 on both models.
- The rule runs on 86028c3 pass, apart from one Opus run on check 3, which the README discloses.
- The rewritten rule was run again after the review rewording.
- The control shows no new section in 4 of 4 runs.

Partly missing: for the control, the README gives word counts (241–256 against the 209-word draft) but has no baseline run on 4f69810. So nothing shows that the "no added item" input did not grow, which is the growth check §2a asks for beside the section check.

I spot-checked the results table against `opus/result.md`, `opus/result-2.md`, `haiku/result.md`, and both baselines, and it matches. The "Generated with Claude Code" note is accurate for all five Haiku files.

## Item 7: siblings of the change
*Analogue: every place that lists or routes to the package.*

None. The version agrees across `.claude-plugin/marketplace.json`, the root `apm.yml`, and the package's `apm.yml`, which the gate confirms. The umbrella `qubership-repo-essentials` refers to the package by path with no version and describes it at a level the change doesn't alter; earlier commits didn't bump it either. The package description and the instruction trigger don't list rules. The research README's file list gains `cases/`.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The case READMEs quote an earlier wording of the rule ("promises compatibility") | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:5-7` | Quote the committed heading at SKILL.md:234 |
| §8 "Caller" still says breaks first under "User-visible changes"; "Breaks" moves them out | Substantive | SKILL.md:845-846 | Qualify "breaks first" with "unless they lead (§2)" |
| "Reviewer's first question is why" contradicts "first decision is whether it may ship" | Substantive | SKILL.md:203-204 | Qualify line 203 for a description that leads with breaks |
| A version file that holds the released version is read as the next release | Substantive | SKILL.md:244-246 | Add the clause in the Item 3 table |
| Template headings conflict with the `Breaking changes` heading | Substantive | SKILL.md:252, 300-302 | Say where the lead goes in a template |
| A §4 rule 5 body loses the `User-visible:` label on the breaks that lead it | Substantive | SKILL.md:258-260 | The lead there is the `User-visible:` paragraph |
| The checklist detects the lead but not whether breaks were recognized | Substantive | SKILL.md:849-851 | Add a question on result shape and extended failures, and on none left in Scope |
| No major-release negative control; no case for an unknown release, milestone or branch name, commit body, or rule 5 body | Substantive | `research/change-description-authoring/cases/` | A major-version variant of `pgjdbc-4367-breaks` at least, or name the other partitions as untested in the README |
| The documented `git archive` command does not copy files on its own | Substantive | `cases/pgjdbc-4367-breaks/README.md:31-32` | `git archive <rev> <path> \| tar -x -C <dir>`, and name `scripts/skill-tree.sh` |
| No baseline word count for the control | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs on 4f69810, or say the growth was not compared |
| "the body is problem-first" | Taste | SKILL.md:68 | "…problem-first, after any breaks under §4 rule 5" |
| Whether a timing or blocking change is a break | Taste | SKILL.md:235-241 | One clause, using the skill's own `Pool.acquire` example |
| "the trailer decides" is ambiguous | Taste | SKILL.md:247-248 | State that it makes the next release a major |
| The effort level for Opus is ambiguous in the commit message | Taste | commit message | "Haiku at effort high, Opus at the default" |
| The version bumps are not claimed by any sentence | Taste | `apm.yml:168`, `marketplace.json:291`, package `apm.yml:2` | One sentence, or leave it as the repository convention |

I did not re-run any model case, check the per-token prices or the GitHub links cited in the case README (there was no network), run markdownlint (its config comes from another repository), or do a style-only pass over the prose.
