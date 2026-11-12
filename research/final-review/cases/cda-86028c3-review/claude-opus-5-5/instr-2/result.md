I reviewed the one commit, `86028c3` (`4f69810..HEAD`), against the final-review form. There was no separate task statement, so I took the claimed cases from the commit message alone. The change has no code: a skill, a package README, version bumps, and research cases. So I used the §2a analogues. I loaded `apm-authoring` and `english-developer-style` from the given folder. I did not run the drift script, because it parses code members and this diff has none.

## 1. Comments consistent with the code and with each other
*Analogue: what each changed file says about another file.*

- **The case READMEs quote a rule name that no longer exists.** `cases/pgjdbc-4367-breaks/README.md:7-8` and `cases/pgjdbc-4392-no-break/README.md:6-7` both cite the rule as "A break leads the description where the next release from the target branch promises compatibility". The committed rule at `SKILL.md:234` says "…unless the next release from the target branch is a major." `git grep 'promises compatibility'` finds only these two READMEs. A reader looking for the rule under test finds nothing.
- **The new rule and the existing Scope rule ask for opposite things on the same input.** `SKILL.md:238-240` says a failure extended to inputs that worked before "goes with the breaks, not in the Scope slot". `SKILL.md:488-491` (unchanged) says that where "a compatibility break is intended" is a maintainer's question, the agent should "keep it in the Scope slot as a question".
  - The `grant insert` case fits both: the draft presents it as a known limitation whose intent is open.
  - `opus/result-2.md` left it in Scope. The README says the first version of the rule did the same in both runs.
  - One reading of the two rules allows that output. The request is a clause in `:488-491`: the break line goes with the breaks, and only the question of intent stays in Scope.
- Checked with nothing found:
  - The cross-references from the new text: §4 rule 5 (`:637`), the `BREAKING CHANGE:`/`!` row of §5 (`:706`), §7 (`:787`), and "(below)" in the slot 3 table row.
  - The new slot 1 sentence (`:86-87`) agrees with `:257-260`.
  - The package README bullet agrees with the rule.
  - The `cases/` line in the research README, and the claims in the 4367 README about three Opus versions and token counts.
  - No sentence narrates the change.
  - Each `skill-tree` file matches its run: HEAD's tree `4798053…` for the rule runs, HEAD~1's `1f020ce…` for the baselines (both checked with `scripts/skill-tree.sh`).

## 2. Claimed cases covered
*Analogue: each claim in the commit message, set against the case or section that shows it.*

| Claim | Evidence |
| --- | --- |
| Breaks lead when the next release is not a major (patch, read from the version file) | 4367 check 1: 4 of 4 rule runs pass, 2 of 2 baselines fail |
| Read from milestone or branch name | none |
| Next release unknown → breaks lead | none |
| Next release is a major → no lead, breaks first in slot 3 | none (see item 3) |
| A result-shape change is a break | 4367 check 2: 4 of 4 pass |
| A failure extended to inputs that worked before is a break | 4367 check 3: 3 of 4, reported honestly |
| Removed option, changed default, changed error code are breaks | none; these are definition entries, owed no case of their own |
| Commit body keeps the problem first, with breaks as the first `User-visible:` lines | none |
| Where squash copies the description into the commit, the lead stays | none |
| A change with no break grows no section | 4392 checks 1–2: 4 of 4 pass |

- **Commands:** the 4367 README's `git archive <rev> agent-packages/…/change-description-authoring` has no CI job behind it. I ran it on HEAD and it lists `SKILL.md` and `references/merge-model.md` as promised, so no finding.
- **A hunk no sentence claims:** the version bump 1.4.0 → 1.5.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The three commits before this one (`4f69810`, `d79c43d`, `51b35c9`) all bump the version too, and the two older ones say "Version X to Y." in the body. The request is that sentence.

## 3. Boundaries, partitions, and the negative control

- **Only one side of the rule's condition was run.** The rule turns on "the next release is a major". Both cases use the same setup: `master`, `pgjdbc.version=42.7.14` (a patch), mostly-plain history, one commit.
  - Untested: the other value of that condition (a major → the breaks stay in slot 3), "unknown" (→ lead), and the trailer clause.
  - The no-break control varies a different input, whether anything breaks. It is not the control for this condition.
  - Also untested: the commit-message claims (problem first, with the breaks as the first `User-visible:` lines) and the squash "title and description" case (lead stays).
  - The request is at least the 4367 prompt with a major in `gradle.properties` (for example `43.0.0`), plus one run that writes the commit message.

There is one row for the instructions the change adds:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:246-248` "Where a release tool bumps the major on a `BREAKING CHANGE:` trailer or a `!` (§5), the trailer decides" | a release-please repo whose next release is a minor; the agent adds `feat!:` itself for this break | it reads the release as a major, so the breaks stay in slot 3 after Why and What | "a trailer this change adds does not count; read the release from the branch before it" |

Added instructions: 4, 1 row.

Not findings: `:254`, `:255`.

## 3a. Level, placement, and the environment
*Analogue: which file each rule lives in, and the repository's own gates.*

- **A rule for the commit body sits only in the pull request section.** The commit-body ordering (breaks as the first `User-visible:` lines of slot 4) appears only at `SKILL.md:257-260`, under "Pull request description". The commit body's own slot 4 text (`:107-115`) and the "Caller" checklist line (`:844-847`) do not say breaks come first in a commit. An agent writing only a commit message reads §2 "Commit body" and does not see it. The request is a sentence in the slot 4 paragraph.
- The rest checks out:
  - The case layout (`cases/<case>/{prompt.md,README.md,<model>/…}`) is close to `research/blackbox-test-design/cases/`.
  - `result*.md` and `prompt.md` fall under `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env:14`.
  - `make check` and `make check-descriptions` both exit 0 offline ("ok: all 27 skill descriptions are within 1020 characters").
  - No new sentence could appear unchanged in a general tutorial.

## 4. Names by content, not by position
None. The case names (`pgjdbc-4367-breaks`, `pgjdbc-4392-no-break`) and check names ("Lead", "Result shape", …) refer by content. The results table's "(1)…(6)" sit next to names. "slot 3" in the table is the skill's own fixed slot numbering.

## 5. The failure report
*Analogue: what each rule tells the reader to look at, and whether its check tests that rule.*

None. Every new rule is reached by the checklist: the "Breaks" line at `:849-852` and the "Problem" line at `:831-832`. Each case check tests its own rule: check 3 looks for the `grant insert` line, not just a heading.

## 6. What the writer says it verified

- **The bad case is shown failing.** Both baseline runs fail checks 1–3, and the rule runs used the committed tree.
- **The no-break control has no baseline run.** `apm-authoring` asks for a check that output on an input where the new rule is noise did not grow. The 4392 README compares 241–256 words only against the 209-word draft, a 15–22% increase. Without an `origin/main` run, nothing shows whether the rule added that growth. The request is one baseline run per model on 4392, with word counts.

## 7. Siblings of the change

None. The umbrella `qubership-repo-essentials/apm.yml:10` pins the package by relative path, so it needs no change. The marketplace and `apm.yml` descriptions don't list the rules. The package README gained a bullet. The `english-*-developer-style` skills defer change content to this skill. No sentence in the changed files counts the slots or the cases differently from before.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| Case READMEs quote a rule name ("promises compatibility") that the skill no longer has | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed rule from `SKILL.md:234` |
| The new "not in the Scope slot" rule conflicts with the existing "keep it in the Scope slot as a question" rule | Substantive | `SKILL.md:238-240` vs `:488-491` | In `:488-491`, say the break line goes with the breaks and only the question of intent stays in Scope |
| The major-release side of the condition, the unknown release, the commit body, and the squash-copy claims have no case | Substantive | `research/change-description-authoring/cases/` | Run the 4367 prompt with a major version; add a commit-message run |
| The trailer clause lets the agent's own `!` cancel the lead | Substantive | `SKILL.md:246-248` | See the item 3 row |
| The commit-body ordering is stated only in the pull request section | Substantive | `SKILL.md:257-260`, `:107-115` | Add the ordering to the commit body's slot 4 paragraph |
| The no-break control has no baseline, so output growth is not measured | Substantive | `cases/pgjdbc-4392-no-break/README.md:22-25` | Baseline runs on 4392, with word counts |
| The version bump is not claimed in the commit message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291` | Add "Version 1.4.0 to 1.5.0." as the earlier commits do |

I did not rerun any model case and did not fetch the pgjdbc pull requests or the maintainer comment the case cites (no network). I did no style-only pass over the prose. I changed no files.
