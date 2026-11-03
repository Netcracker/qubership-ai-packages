I didn't change or commit anything. The marketplace gate passes, but I found nine substantive problems, listed in the table at the end.

**Inputs.** There was no task statement, so the claimed cases come from the commit message of 86028c3 and from the two case READMEs. There was no previous report. The change has no code: it edits a skill (SKILL.md), a package README, two version manifests, and the research tree. Every item therefore uses the §2a stand-in for code ("analogue"), and I did not run `comment-drift.py` because it has nothing to parse. I loaded `english-developer-style`. The `apm-authoring` skill named in §2a is not among the three skills I was given, so I cite the rules of `final-review` §2a directly.

## Item 1: comments consistent with the code and with each other

Analogue: statements that one changed file makes about another file, and the other statements in SKILL.md about the same facts.

- **Wrong quote of the rule in both case READMEs.** `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` both quote the rule as "A break leads the description where the next release from the target branch promises compatibility". SKILL.md:234 says "…unless the next release from the target branch is a major". The quoted sentence does not exist in the skill, and the two conditions differ. A reader of the case would test the wrong condition (see the 0.x row in Item 3).
- **Two checklist lines disagree.** SKILL.md:844-846 (Caller) still asks for "one line per distinct outcome under 'User-visible changes', breaks first". The new Breaks line at :849-852 and the rule at :252-254 say that slot 3 keeps only the other outcomes when the breaks lead. On a breaking change aimed at a patch release, the two lines give opposite answers.
- **Two sentences disagree on the reviewer's first question.** SKILL.md:204 says "the reviewer's first question is why that version should change". The new :243 says "the reviewer's first decision is whether the change may ship in it at all". They are 40 lines apart and neither one qualifies the other.
- **Checked and consistent:**
  - the package README bullet;
  - the research README index row and its closing paragraph;
  - the `skill-tree` ids: `47980534…` is `HEAD:<skill dir>` and `1f020ce5…` is `HEAD~1:<skill dir>`, as the case README says;
  - the result tables against the result files (I checked the opening lines, where `grant insert` sits, and the word counts from `wc -w`).
- No sentence narrates the change ("now", "no longer") in the skill text.

## Item 2: claimed cases covered

Analogue: claims from the commit message, matched to the section that handles each one and the case that tests it.

| Claimed case | Section | Test (case and check) |
| --- | --- | --- |
| Breaks lead the description unless the next release is a major | SKILL.md:234, :252 | 4367 check 1 |
| Next release read from the version file | :244-246 | 4367 prompt (`gradle.properties`) |
| … read from the milestone or the branch name | :246-247 | none |
| Breaks lead when nothing says which release it is | :248-250 | none |
| Break kinds: a new failure | :235-236 | 4367 check 1 (the `42703` line) |
| Break kinds: result shape | :236-237 | 4367 check 2 |
| Break kinds: a failure extended to inputs that worked before | :238-240 | 4367 check 3 |
| Break kinds: removed option, changed default, changed error code | :237-238 | none |
| The commit body keeps the problem first, with breaks as the first `User-visible:` lines | :86-88, :257-258 | none: both prompts ask only for the PR description |
| Under squash, the lead stays in the commit | :258-260 | none: both prompts' merge model is the default squash |
| A change with no break grows no section | :255 | 4392 checks 1 and 2 |
| Run counts and pass rates (3 of 4 for `grant insert`) | 4367 README results table | matches the files |

- **Commands.** One command is documented: 4367 README:22-23, `git archive <rev> agent-packages/change-description-authoring/...`. Nothing runs it (`none`), but its outcome depends only on `<rev>`, so it is not a finding.
- **Hunks with no claim.** Every hunk is claimed except the bumps from 1.4.0 to 1.5.0 in `apm.yml`, `.claude-plugin/marketplace.json`, and the package `apm.yml`. These follow the precedent of 4f69810 and are gated by `make check` (Taste T4).

## Item 3: boundaries, partitions, and the negative control

Analogue: the situations the change claims to handle; the no-break case is the negative control.

- **Partitions with no evidence.** All six runs, and all four runs of the control, cover one partition only: a version file that says 42.7.x, headings, and the PR description. The following partitions are claimed but untested:
  - the next release is a major, so the breaks stay in slot 3. This is the control for the word "unless", and it is the more telling one.
  - the release is unknown;
  - the release is read from the milestone or the branch name;
  - a `BREAKING CHANGE:` trailer decides it;
  - a prose description with no headings;
  - the commit body order;
  - the lead under §4 rule 5.
- The control 4392 itself is present and passes.

Instructions the change adds or widens:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:234` "A break leads the description unless the next release … is a major" | a 0.x library whose minor releases break by convention (`0.6.0-SNAPSHOT`) | a `Breaking changes` heading ahead of Why for a routine 0.x minor | "where the next release promises compatibility (not a major, not a 0.x minor)" |
| `:257` "Where §4 rule 5 makes the description the commit body, the lead stays" | squash with "title and description", a patch target, one break, a body without headings | unlabeled break lines above the problem, `User-visible:` only on the later lines | "…opens with its breaks as a `User-visible:` paragraph" |

Not findings:

- `:86`, ended by "that leads with its breaks";
- `:243` "Read the next release…" on a change with no break, ended by "A change with no break has neither the lead nor an empty heading";
- `:252` "opens with slot 3's break lines", ended by the same sentence;
- `:849` and `:831`, which restate `:234` and `:257`.

## Item 3a: level, placement, and the environment

The rule sits in §2 next to the slot 3 text it changes. The cases follow the `skill-tree` convention that `scripts/skill-tree.sh` documents. `make check` (`apm pack --check-versions --check-clean --dry-run`) exits 0 offline. Super-linter's `FILTER_REGEX_EXCLUDE` covers `prompt.md` and `result*.md`, and markdownlint itself was not run locally. No sentence reads as general advice that could sit in any tutorial. None.

## Item 4: names by content, not by position

SKILL.md:198, the table cell "ahead of slot 1 unless the next release is a major (below)", points by position where it could name the bold rule at :234 (Taste T1). The README tables name each check and give its number together ("Lead (1)"), so that is fine.

## Item 5: the failure report

Analogue: what the checklist tells a reader to look for, and whether that detects the rule.

- The rule is reached by the checklist line at :849, but the detection is weaker than the rule.
- That line asks whether the description opens with break lines. It does not ask whether a result-shape change or a failure extended to new inputs is counted as a break rather than left in slot 3 or in Scope.
- That is exactly the failure the case measured: `opus/result-2.md` left `grant insert` in Scope, and a reader applying :849 would pass it.

## Item 6: what the writer says it verified

- **Evidence that exists.** A bad case fails on the base and passes with the rule: both baselines fail checks 1 to 3, and three of four runs with the rule pass all six checks. The commit message says this honestly.
- **No baseline for the control.** 4392 has no run on the base skill, so "grows no section" is measured against the author's draft (209 words, against 241 to 256 words in the results), not against the skill without the rule. §2a asks for a check that the output did not grow on the noise input.
- **Version not caught by the checks.**
  - Both Opus results date the old behavior to 42.7.13: `opus/result.md:5-6` writes "In 42.7.13…" and `opus/result-2.md:1` writes "Code that runs such strings on 42.7.13". The baseline runs do not.
  - The prompt says the latest release tag is `REL42.7.14`. The draft names 42.7.13 only as the driver it was checked with.
  - A reader on 42.7.14 could conclude they are not affected. No check catches this, and the README's growth paragraph (:42-44) does not mention it.
- **Earlier drafts.** The runs of the two earlier drafts are described but not stored (README:36-40), and the commit message says so.

## Item 7: siblings of the change

- **Updated where they should be.** The package README, both marketplace manifests, and the research README index all cover the new rule. The umbrella `qubership-repo-essentials` pins the package by path, not by version.
- **Changelog section (§3).** Its "marked in place, sorted first" rule governs a different artifact and does not conflict.
- **Russian developer-style skill (follow-up).** `russian-developer-style/modules/code-comments.md:130` lists **Breaking changes** as an optional block of a PR description with no position. Its example at `examples/before-after.md:554` has the same gap. Both predate this change; this is a follow-up, not something this change has to fix (Taste T5).
- **Old counts.** No sentence still counts the slots as before; "Six slots, in order" is qualified by the cell at :198.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| S1 | Both case READMEs quote a rule wording ("promises compatibility") that is not in the skill | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote SKILL.md:234 as written, or restore that wording in the skill (see S5) |
| S2 | The Caller checklist line still puts breaks first inside "User-visible changes" | Substantive | SKILL.md:844-846 | Qualify it: "breaks first, or ahead of Why where they lead (§2)" |
| S3 | "The reviewer's first question is why" contradicts "the reviewer's first decision is whether it may ship" | Substantive | SKILL.md:204 against :243 | Qualify :204 for a change that leads with breaks |
| S4 | Under §4 rule 5 the breaks leading the commit body have no `User-visible:` label, while :258 says that label is what R4 and R5 search for | Substantive | SKILL.md:257-260 | State that the leading lines carry the `User-visible:` label |
| S5 | The rule fires on 0.x minor releases, where breaks are expected and leading with them helps no reviewer | Substantive | SKILL.md:234, :243 | Add the clause "where the next release promises compatibility", which the README wording had |
| S6 | The Breaks checklist line does not detect break classification, which is the measured failure | Substantive | SKILL.md:849-852 | Add: "is a result-shape change or a failure extended to inputs that worked before among the breaks, not in slot 3 or Scope?" |
| S7 | Claimed partitions have no evidence: major target, unknown release, milestone or branch name, trailer, prose without headings, commit body order, rule 5 | Substantive | `research/.../cases/` | At least a case with breaks aimed at a major (the control for "unless"), and one asking for the commit message |
| S8 | Opus results date the old behavior to 42.7.13 while the prompt says the latest release is 42.7.14; no check catches it and the README says nothing | Substantive | `opus/result.md:5-6`, `opus/result-2.md:1`, README:42-44 | Note it in the results, or add a check that the version named is the released one |
| S9 | Control 4392 has no baseline run, so "grows no section" is not measured against the skill without the rule | Substantive | `cases/pgjdbc-4392-no-break/README.md:22-25` | Baseline runs of 4392 on the base skill, with word counts |
| T1 | "(below)" refers by position | Taste | SKILL.md:198 | "(see *A break leads the description*)" |
| T2 | "(effort high)" in the commit message reads as covering Opus, which ran at the default | Taste | commit message, third paragraph | "Haiku at effort high" |
| T3 | "the trailer decides" has no object | Taste | SKILL.md:247-248 | "the trailer makes the release a major, and the breaks stay in slot 3" |
| T4 | No sentence of the commit message claims the 1.4.0 → 1.5.0 bumps | Taste | `apm.yml:168`, `.claude-plugin/marketplace.json:291`, package `apm.yml:2` | One clause, or leave it as repository convention |
| T5 | The Russian developer-style skill's PR description block gives Breaking changes no position | Taste | `russian-developer-style/modules/code-comments.md:130` | Name it as a follow-up |

The review did not run the drift script (no code), markdownlint, super-linter, or any model run of the cases, and it did not check the prose for style.
