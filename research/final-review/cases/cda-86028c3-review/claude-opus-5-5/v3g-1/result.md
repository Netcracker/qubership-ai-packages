# Final review of `4f69810..86028c3` (one commit): change-description-authoring 1.5.0, breaks lead the description

I did not receive a separate task statement, so the claimed cases come from the commit message alone. The change contains no code: it edits a skill, its package README, three version fields, and a research README, and adds two regression cases. Because the change is a skill, I filled the form through the §2a analogues and name the analogue under each item. I did not run the drift script, because the change has no members for it to parse (Markdown, YAML, and JSON only). I loaded `english-developer-style` from the given skills directory. `apm-authoring` is not among the three given skills, so I read the repository's own copy under `agent-packages/apm-authoring`.

`S` below is `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
*Analogue: every statement a changed file makes about another file or about the repository.*

- **Stale quote of the rule in both case READMEs.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote the rule under test as "A break leads the description where the next release from the target branch promises compatibility". `S:234` states it as "…unless the next release from the target branch is a major". A reader who greps the skill for the quoted rule finds nothing.
  - Both READMEs record the skill tree `47980534…`, which I confirmed equals `HEAD:` of the skill directory, so the runs are on the committed text. Only the quote is stale. The baseline tree `1f020ce5…` equals the base commit's tree.
- **The new break rule contradicts the unchanged Scope rule.** `S:487-492` says that where only a maintainer can settle "whether a compatibility break is intended", the writer keeps it "in the Scope slot as a question". `S:238-240` says an extended failure "goes with the breaks, not in the Scope slot". The `grant insert` case meets both: the draft keeps the behavior on purpose because `explain insert` relies on it. That is plausibly why `opus/result-2.md:35` left it in Scope.
- **Two other statements in the file still say the description takes the commit body's shape.**
  - `S:637-639` (§4 rule 5) says "shape it as §2's commit body", and `S:310` says it "takes the body's shape instead".
  - `S:258-260` now says that under rule 5 the lead stays, which is an exception. Neither of the older places mentions it, so a reader who lands in §4 builds a problem-first body.
- **Two checklist lines contradict each other.** `S:845` ("Caller") still asks for "one line per distinct outcome under 'User-visible changes', breaks first". `S:849-852` ("Breaks") asks that slot 3 keep "only the other outcomes" when the breaks lead. On the same input, a patch-release break, a reviewer who follows "Caller" flags the layout that "Breaks" requires.
- **Unclear sentence about the release-tool trailer.** `S:247-248` reads "the trailer decides, and it is written whatever the description does". It does not say what the trailer decides. One reading: the change's own `BREAKING CHANGE:` makes the next release a major, so in every release-please or semantic-release repository the lead never fires. That is circular, because the break itself causes the major. Another reading: the tool, not the version file, says which release is next. A reader cannot tell which is meant.
- No sentence narrates the change ("now", "no longer"). The commit message's "now" is not in the skill.

## Item 2: claimed cases covered
*Analogue: the section that handles each claimed case, and how a reader detects it.*

| Claimed case (commit message) | Section | Trial / detection |
| --- | --- | --- |
| Breaks lead unless the next release is a major | `S:234`, `S:252-255` | `pgjdbc-4367-breaks` (patch release); checklist `S:849` |
| Next release read from the version file, milestone, or name | `S:243-246` | Version file only. No trial with a milestone or a branch name |
| Unknown release, so the breaks lead | `S:248-250` | No trial |
| Definition of a break: new failure, result shape, removed option, changed default or error code, extended failure | `S:234-241` | Result shape and extended failure are tried (checks 2 and 3). No checklist line detects either one (Item 5) |
| Commit body keeps problem first, breaks as the first `User-visible:` lines | `S:257-258` | No trial |
| Squash copies the description, so the lead stays | `S:86-88`, `S:258-260` | No trial. The prompts' merge model (`plain 37 squash 3`, one commit) does not exercise rule 5 |
| No break, so no section | `S:255`, `S:851` | `pgjdbc-4392-no-break`, all four runs pass |
| Result numbers: 4/4 lead, 3/4 move `grant insert`, control clean | case READMEs | Confirmed against the result files: `opus/result-2.md:35` is the one in Scope; `haiku/result-2.md:8` and `opus/result.md:8` lead with it |

**Commands the artifact tells a reader to run:** `git archive <rev> agent-packages/…/change-description-authoring` (`cases/pgjdbc-4367-breaks/README.md:29`). Nothing in the repository runs it, so the runner column is `none`. The promised outcome is "the skill copied out of the checkout". `git archive` writes a tar stream to stdout in every git version, and nothing is copied unless the stream is piped to `tar -x -C <dir>`. The documented form does not produce the stated outcome.

**Hunks no sentence claims:** the version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. `d79c43d` and `51b35c9` claimed theirs ("Version 1.2.0 to 1.3.0."). `4f69810` did not claim its own.

## Item 3: boundaries, partitions, and the negative control
*Analogue: the modes the change claims, and the added-instruction table.*

The trials covered two partitions: a patch release read from a version file, with breaks; and the same with no break, as the negative control. These claimed partitions have no evidence:
- the next release is a major, where the breaks stay in slot 3;
- nothing says which release it is;
- a milestone or branch name as the source;
- the commit body;
- a body that §4 rule 5 copies from a description.

The major-release arm is the control for the lead itself. The no-break case controls a different condition: whether there is a break, not which release is next.

No pre-existing state applies.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| A break leads unless the next release is a major (`S:234`, `S:242-255`) | A 0.x library whose next release is 0.5.0, where SemVer lets a minor break | A `Breaking changes` lead for a reviewer with no ship-or-not decision to make | "or a 0.x minor, which SemVer lets break" |
| An extended failure goes with the breaks, not in Scope (`S:238-240`) | An extended failure whose intent only a maintainer can settle (the `grant insert` draft) | The lead under one rule, a Scope question under `S:487-492` | Conflict; one rule must name the other |
| Under rule 5 the body opens with its breaks (`S:257-260`, `S:86-88`) | A squash with "title and description" in a repository whose readers grep `User-visible:` | Leading break lines with no label, and a `User-visible:` paragraph without them | "and the leading lines keep the `User-visible:` label" |
| Release-tool trailer decides (`S:246-248`) | A release-please repository with a patch-minded maintainer | Either no lead ever, or a lead; the text does not say which | the object of "decides" |

Not findings:
- A change with no break, ended by "A change with no break has neither the lead nor an empty heading".
- A major release, ended by "Where the next release is a major, the breaks stay first in slot 3".
- A fix, ended by "a failure that now succeeds is a fix, not a break".
- A break against an unreleased API, ended by "code that works on the released version".

## Item 3a: level, placement, and the environment
*Analogue: which file each rule lives in, and the repository gate.*

None. The rule sits in §2 "Pull request description", beside slot 3, which it modifies. The checklist line sits beside "Caller". The cases follow the existing `research/change-description-authoring` layout, and the research README lists `cases/`. `make check` (`apm pack --check-versions --check-clean --dry-run`) exits 0, and `make check-descriptions` prints `ok: all 27 skill descriptions are within 1020 characters`. No sentence reads like generic tutorial text: the extended-failure clause carries measured, repository-specific knowledge.

## Item 4: names by content, not by position
None that matters. The case READMEs refer to "Checks 1 to 3" and "4 to 6", but each check also carries a bold name and the table columns pair the two ("Lead (1)"). "Three versions of the rule… The first… The second" in the 4367 README names each version by its content too. "§4 rule 5" follows the skill's existing numbered-rule convention.

## Item 5: the failure report
*Analogue: is each rule reached by the checklist, and does each detection catch the rule?*

- The "Breaks" checklist line (`S:849-852`) checks the lead, the split of slot 3, and the absence of an empty heading. It does not check the definition of a break. A description that leads with two breaks, leaves the result-shape change in slot 3, and keeps the extended failure in Scope passes the line. That is exactly the case's baseline failure on checks 2 and 3, so the detection catches a weaker property than the rule.
- The "Caller" checklist line contradicts the "Breaks" line (filed under Item 1).

## Item 6: what the writer says it verified
- **Red and green runs exist.** The baseline runs on the base tree fail checks 1 to 3, and the runs on the HEAD tree pass, except `opus/result-2` on check 3, which is stated. I confirmed both tree ids.
- **No baseline for the negative control, so growth there is unmeasured.** `pgjdbc-4392-no-break` has no baseline run. Its results grow from 209 words in the draft to 241–256. Without a run on the base tree, nobody can tell whether the rule added any of that growth. The control checks only for "no section".
- **The rewrite was re-run.** The reworded rule was run again (tree matches HEAD), and the README says it moves `grant insert` "most of the time and not always".

## Item 7: siblings of the change
*Analogue: the places that enumerate or route to the artifact, and other sections of the file on the same fact.*

- **Updated:** the package README, the marketplace version, root `apm.yml`, and the research README index. The umbrella `qubership-repo-essentials/apm.yml:10` references the package by path with no pin.
- **Fine as is:** the frontmatter description and the marketplace description are generic, so no scope widened unseen. No set count changed ("Six slots" still holds). The changelog's in-place `**Breaking:**` rule (`S:543`) is a different artifact and is consistent.
- **Missed siblings:** `S:310` and `S:637-639` (rule 5's "shape it as §2's commit body"), `S:487-492` (Scope keeps break-intent questions), and `S:845` ("Caller", breaks first under "User-visible changes"). All are filed under Item 1.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Case READMEs quote a rule wording that is not in the skill | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote `S:234` as committed |
| New rule sends an extended failure to the lead; the unchanged Scope rule keeps a break of uncertain intent in Scope | Substantive | `S:238-240` vs `S:487-492` | One rule names the other's case, e.g. "a break whose intent is open still leads, with the question in Scope" |
| "Caller" checklist asks for breaks first in slot 3; "Breaks" asks for them out of it | Substantive | `S:845` vs `S:849-852` | Make "Caller" defer to "Breaks" where the breaks lead |
| Rule 5 and the headings paragraph still say the description takes the body's shape, without the lead exception | Substantive | `S:310`, `S:637-639` | Add the exception or a pointer to `S:258-260` at both places |
| "The trailer decides" has no object; one reading switches the rule off in every release-tool repository | Substantive | `S:247-248` | Say what the trailer decides and whether a change's own break counts |
| Under rule 5, the leading break lines' `User-visible:` label is unspecified, though the label is the stated reason for the commit order | Substantive | `S:257-260` | A clause saying whether the leading lines keep the label |
| The "Breaks" checklist does not check the definition of a break (result shape, extended failure out of Scope) | Substantive | `S:849-852` | Add the two definition checks to the line |
| No trial for the major-release arm, the unknown-release arm, milestone or branch-name sources, or either commit-body form | Substantive | case READMEs | A case for the major-release arm at least, as the control for the lead |
| Negative control has no baseline, so the 209 → 241–256 word growth is not attributed | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs of 4392 on the base tree |
| Documented `git archive <rev> <path>` copies nothing as written | Substantive | `cases/pgjdbc-4367-breaks/README.md:29` | Give the form that runs, e.g. `git archive <rev> <path> \| tar -x -C <dir>` |
| 0.x minor release treated as "not a major" | Substantive | `S:234`, `S:242` | A clause for 0.x minors, which SemVer lets break |
| Version bump hunks unclaimed by the commit message | Taste | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | One line, "Version 1.4.0 to 1.5.0.", as `d79c43d` has |

This review did not do a style-only pass over the prose, did not re-run any model trial, did not run `make test`, and did not fetch the cited pgjdbc pull requests or comment, because there is no network.
