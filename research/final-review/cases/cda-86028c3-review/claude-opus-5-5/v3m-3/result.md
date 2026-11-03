# Final review: 4f69810..86028c3, one commit (`feat(change-description-authoring): lead the description with breaks unless the next release is a major`)

There was no separate task statement, so the claimed cases come from the commit message alone. The change has no code: it edits a skill, a package README, two version files and the marketplace index, and adds research cases. The form was therefore filled through the §2a analogues, with `apm-authoring` and `english-developer-style` as the skills it applies. The drift script ran (`comment-drift.py 4f69810 HEAD`) and printed nothing, because the change contains no source it parses. There is no previous report.

Line numbers refer to `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` unless another file is named.

## Item 1: comments consistent with the code and with each other
*Analogue: statements one file makes about another, and statements that conflict inside the skill.*

1. **The case READMEs quote a rule that is not the one committed.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` quote "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". This is the wording of a draft the README itself says was replaced after review. A reader looking for the rule under test searches for text that isn't there.
2. **"the trailer decides" (:247-248) can be read two ways.** In a release-please or semantic-release repository (§4 rule 7, §5), a `!` or `BREAKING CHANGE:` makes the next release a major.
   - One reading: the trailer makes the release a major, so the breaks stay in slot 3, after Why and What. In those repositories the breaks would then never lead.
   - The other reading: the trailer settles the version number and nothing else. The breaks still lead, because the reviewer's first decision (:243) is now whether to accept a major release at all.
   - The second reading serves that input, and the text doesn't say which reading is meant.
3. **A Scope rule pulls against the new placement rule.** :489-490 keeps "whether a compatibility break is intended" in the Scope slot as a question for the maintainer. :238-240 says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". `opus/result-2.md` left `grant insert` in Scope, which is the Scope rule's reading. A clause at :489 that says the break line itself still leads, and only the question of intent stays in Scope, would end the conflict.
4. **The shape of a §4 rule 5 body that leads with breaks is unclear.** :257-260 and :86-87 say such a body "opens with its breaks and then its problem". :258 says the `User-visible:` label "is what R4 and R5 search for", and headings are absent from such a body (:310, checklist). The text doesn't say whether the leading break lines carry the `User-visible:` label, or whether a second label follows slot 3 for the other outcomes. On the reading where the lead is unlabeled, the breaks are exactly the lines the label search misses.
5. **Template headings vs. the new heading.** :302 says that where a template exists, its headings are used. :252 asks for a `Breaking changes` heading "where the description has headings". For a template with its own compatibility field, the two rules ask for different things.

The other cross-references hold:
- §3's `**Breaking:**` sorting.
- §5's trailer row.
- §7's "no section for an absent concern".
- §3:538, which already makes R5 a reader of compatibility, so :258's "R4 and R5" is consistent.
- The package README bullet, which matches :234-260.
- The research README entry and dated note.
- The `skill-tree` ids: `4798053…` equals `HEAD:<skill dir>`, and `1f020ce…` equals the parent commit's tree.

## Item 2: claimed cases covered
*Analogue: each claimed situation against the section that handles it.*

| Claim (commit message) | Section | Trial evidence |
| --- | --- | --- |
| Opens with breaks when the next release is not a major | :234, :252 | 4367, 4 runs |
| Next release read from version file, milestone or branch name | :244-247 | 4367 (version file only) |
| Breaks lead when nothing says which release | :248-250 | none |
| Major release: breaks stay first in slot 3 | :254-255 | none |
| Definition of a break (result shape, extended failure, …) | :234-241 | 4367, checks 2 and 3 |
| Commit body keeps problem first, breaks first under `User-visible:` | :257-258 | none |
| Squash copies the description: the lead stays | :258-260, :86 | none |
| No break: no section | :255 | 4392, 4 runs |

The skill and the cases document no command to run, apart from `git archive` in the 4367 README; that one is a provenance step, not a promised outcome.

The other direction, hunks with no claiming sentence: the version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2` and `.claude-plugin/marketplace.json:291` has no sentence in the message. The two earlier commits on this package each carry a "Version 1.x.0 to 1.y.0." line.

## Item 3: boundaries, partitions, and the negative control

- **No-break control:** present (`pgjdbc-4392-no-break`).
- **Missing partitions:** three branches the commit claims have no run.
  - The major-release branch. It is the only control for the "unless" clause.
  - The unknown-release branch.
  - The commit-body / §4 rule 5 branch. Both prompts say the merge model is `squash 3 plain 37` with one commit, so rule 5 never fires.
- **Pre-existing state:** none applies; this is a prose rule with no persisted state.

Added instructions: 3, no rows.

Not findings: `:255`, `:254`, `:258`.

## Item 3a: level, placement, and the environment

- **Layout:** the new `cases/` directory is listed in the research README (:49).
- **Lint exclusion:** the result and prompt files match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, which I checked against every changed path. The READMEs are linted.
- **Gates:** `make check` exits 0, `make check-descriptions` prints `ok: all 27 skill descriptions are within 1020 characters`, and `make test` passes.
- **Not run:** markdownlint with the CI config, because that config is fetched from `netcracker/.github`, which isn't reachable offline.
- **Tutorial content:** no sentence reads like generic tutorial text.

## Item 4: names by content, not by position

- :198 says "ahead of slot 1 unless the next release is a major (below)". The target has a name it could be cited by, the bold rule "A break leads the description".
- The case READMEs name the checks by content and number together ("Lead (1)"), which is fine.
- The README's "The first, … The second" refers to draft runs that aren't stored and are described by content, which is fine.

## Item 5: the failure report
*Analogue: the checklist reaches each rule, and each detection detects the rule.*

- The new checklist item (:849-852) reaches the lead rule.
- It doesn't reach the instruction at :238-240 (an extended failure goes with the breaks, not in Scope). That is the one clause the trial shows failing (1 run of 4).
- :831 is updated for the rule 5 body.

## Item 6: what the writer says it verified

- **Bad case:** both baselines fail checks 1 to 3.
- **Exemplar:** the committed rule (tree id matches HEAD) passes checks 1 and 2 in 4 of 4 runs and check 3 in 3 of 4, and the README reports that honestly.
- **Noise input:** 4392 checks that no section appears. Its word counts (241–256) are compared with the author's draft (209), not with the skill before the rule. No baseline run of 4392 exists, so it is not shown that the output did not grow.

## Item 7: siblings of the change

- **Places that route to the package:**
  - The package README bullet is added.
  - The frontmatter description is unchanged, and its scope isn't widened.
  - The versions in `apm.yml` and the marketplace agree, and `make check` confirms it.
- **Other skills:** `git grep` across the other packages for break ordering found only the changelog sentence in `english-developer-style` §7, which defers to this skill, and a Russian changelog example. Neither conflicts.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote the replaced draft wording "…promises compatibility" | Substantive | `cases/pgjdbc-4367-breaks/README.md:7`, `cases/pgjdbc-4392-no-break/README.md:6` | Quote the committed rule text from :234 |
| "the trailer decides" can mean either "the breaks never lead under release-please" or "the version only" | Substantive | SKILL.md:247-248 | Say whether a break that itself triggers the major still leads |
| The Scope rule keeps "whether a compatibility break is intended" in Scope; the new rule moves extended failures out of it; 1 of 4 runs followed the Scope reading | Substantive | SKILL.md:489, :238-240 | A clause at :489: the break line leads, and only the question of intent stays in Scope |
| A §4 rule 5 body that opens with breaks: whether those lines carry `User-visible:` is unstated | Substantive | SKILL.md:257-260, :86 | State the label (or none) for the leading lines and where the other outcomes go |
| A `Breaking changes` heading vs. "use the template's headings" | Substantive | SKILL.md:252, :302 | Say which wins where a template exists |
| No run for the major-release, unknown-release, and commit-body / rule 5 partitions the message claims | Substantive | `research/change-description-authoring/cases/` | A case per partition (at least the major-release control), or narrow the claim |
| The checklist doesn't check the extended-failure placement, the clause that failed in the trial | Substantive | SKILL.md:849-852 | Add "and is no break left in Scope" |
| 4392 has no baseline run, so the absence of growth on the noise input isn't shown | Substantive | `cases/pgjdbc-4392-no-break/README.md` | Baseline runs of 4392 with word counts |
| The version bump 1.4.0 → 1.5.0 isn't claimed in the message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | A "Version 1.4.0 to 1.5.0." line, as in the previous commits |
| "(below)" refers to the rule by position | Taste | SKILL.md:198 | Cite the rule by its bold text |

This review did not run markdownlint with the CI config, which needs the network; did not re-run any model trial; and did not do a style-only pass over the prose.
