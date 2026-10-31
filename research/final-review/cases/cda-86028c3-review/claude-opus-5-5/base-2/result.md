# Final review: `4f69810..86028c3`, one commit

There was no task statement, so I took the claimed cases from the commit message (`feat(change-description-authoring): lead the description with breaks unless the next release is a major`). I found no previous report of this form.

This change has no code. It changes a skill (`SKILL.md`), the package README, version files, and adds two research regression cases. So the form uses the §2a analogues, and I loaded `english-developer-style` as the style skill. The `apm-authoring` skill was not among the three I was told to load, so I did not load it. I ran the drift script: it printed nothing, because it parses no Markdown or YAML. I mapped Item 1 by hand.

## Item 1: comments consistent with the code and with each other

(Analogue: statements one changed file makes about another file, or about the same skill.)

- **The Scope paragraph contradicts the new rule.** `SKILL.md:487-491` still says that where "only a maintainer can answer… whether a compatibility break is intended, keep it in the Scope slot." The new rule at `SKILL.md:238-240` says an extended failure "goes with the breaks, not in the Scope slot." The `grant insert` case is exactly a break whose intent is open, and `opus/result-2.md` kept it in Scope. A reader of line 490 does what that run did.
- **Two checklist items disagree.** The Caller item at `SKILL.md:844-845` asks for one line per outcome "under 'User-visible changes', breaks first." The new Breaks item at `SKILL.md:849-851` asks that "slot 3 keep only the other outcomes" when the breaks lead. On a description that leads with its breaks, the first item fails and the second passes.
- **The commit body under §4 rule 5 has no stated shape.** `SKILL.md:206-208` says the copied slot 3 is written as `User-visible:` lines. `SKILL.md:301-302` says that under rule 5 the description "takes the body's shape," which has no headings. The new `SKILL.md:257-260` says "the lead stays" but does not say whether the leading breaks carry the `User-visible:` label or a `Breaking changes` heading. That label is what the same paragraph says "R4 and R5 search for." Also, `SKILL.md:86` ("Slot 1 opens the body") and `SKILL.md:192` ("Six slots, in order") are stated with no condition, and the condition sits in a later sentence. That is `english-developer-style` §4, "Keep a truth condition in the sentence it limits."
- **"The trailer decides" can be read two ways.** At `SKILL.md:246-248` it can mean a `BREAKING CHANGE:` trailer already on the target branch, or the one this change writes "whatever the description does." Under the second reading, any break in a release-please repository forces a major, so the lead never applies, even on a maintenance branch.
- **Both case READMEs quote the rule in wording the skill does not contain.** `pgjdbc-4367-breaks/README.md:7-8` and `pgjdbc-4392-no-break/README.md:6-7` quote "A break leads the description where the next release from the target branch promises compatibility." The committed sentence says "unless the next release from the target branch is a major." The two disagree when the release is unknown: the committed rule leads there, and the quoted one does not.
- **Checked and consistent:**
  - The package README bullet (`README.md:23-25`).
  - The research README's `cases/` row and closing paragraph.
  - The `skill-tree` ids: `4798053…` equals `HEAD:<skill dir>`, and `1f020ce…` equals the parent's tree.
  - The word counts in both case READMEs match `wc -w`.
  - The count of "Generated with Claude Code" lines: three Haiku results in 4367 (baseline included) and two in 4392.
  - The commit message's tallies against the results table: four of four lead, and three of four move `grant insert` out of Scope.

## Item 2: claimed cases covered

| Claimed case (from the commit message) | Evidence |
| --- | --- |
| Breaks lead when the next release is not a major (patch, read from `gradle.properties`) | `pgjdbc-4367-breaks`, checks 1 to 3; `opus/result*.md`, `haiku/result*.md` |
| A result-shape change is a break | 4367 check 2: four runs pass, two baselines fail |
| A failure extended to inputs that worked before is a break, not Scope | 4367 check 3: three of four runs pass, and `opus/result-2.md` fails, as the README says |
| A change with no break grows no section | `pgjdbc-4392-no-break`: four runs |
| A fix is not a break | 4367 check 4 |
| **Breaks stay in slot 3 when the next release is a major** | **none** |
| **Breaks lead "where nothing says which release it is"** | **none** |
| **Release read from a milestone or a branch name** | **none**: both prompts give only `gradle.properties` |
| **The commit body keeps the problem first, with the breaks as the first `User-visible:` lines** | **none**: no case writes a commit |
| **Under squash "title and description", the lead stays** | **none**: both prompts give the default squash |

**Commands:**
- The case README's `git archive <rev> agent-packages/…/change-description-authoring` recipe is run by no script (`none`). It writes a tar stream to stdout and copies nothing until it is piped to `tar -x`. The outcome the README promises, "copied out of the checkout," needs that second step.
- The `./gradlew` lines are inside the prompts' input drafts, not commands this change asks anyone to run.

**Hunks the description doesn't claim:** the bump from `1.4.0` to `1.5.0` in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and `agent-packages/change-description-authoring/apm.yml:2`. No sentence claims it. Earlier commits to this package say "Version 1.2.0 to 1.3.0." and similar. Every other hunk belongs to a sentence.

## Item 3: boundaries, partitions, and the negative control

(Analogue: the modes the rule names, and the control arm.)

- **The rule's "unless" has no control.** The rule has three release modes: not a major, a major, and unknown. Only "not a major" ran. The control that exists, 4392, varies whether the change breaks anything, not the release. So a rule that said "breaks always lead" would pass all ten runs, and nothing shows that the "unless major" clause or the unknown-release default does anything.
- **The commit-body modes are untested.** The plain commit body and the body under rule 5 are two more partitions the commit message claims, with no run.
- **One more untested partition:** a description with no headings. The rule says "under a `Breaking changes` heading where the description has headings," but both drafts had headings.
- **Earlier state:** none applies, since this is a prose rule and leaves no persisted state.

## Item 3a: level, placement, and the environment

- **Placement:** the result and prompt files match `FILTER_REGEX_EXCLUDE` in `.github/super-linter.env` (I checked with the regex itself). The case READMEs are linted, and no new line is over 120 characters. The `cases/` layout is new for this research directory; `research/blackbox-test-design/cases` has a `run-case.sh`, and this one has a manual recipe instead.
- **Gate:**
  - `make check-descriptions` passed: "ok: all 27 skill descriptions are within 1020 characters".
  - `make test` passed, ending in "PASS", with the marketplace roundtrip and "version bump reflected after re-pack".
  - `apm pack --check-versions` was not run.

## Item 4: names by content, not by position

None I would file. "Slot 3," "slot 1," and "§4 rule 5" follow the skill's existing numbered-slot convention, and the same paragraphs also use the content names ("the Why slot"). The case checks are numbered and named at once ("Lead (1)"). `result-2.md` names interchangeable runs.

## Item 5: the failure report

(Analogue: is each rule reached by the checklist, and does each check detect its rule?)

- The new Breaks item reaches the lead rule.
- What counts as a break (result shape, extended failure) is not in the checklist. Case checks 2 and 3 detect it, so I'm not filing it.
- The Caller/Breaks contradiction is filed under Item 1.

## Item 6: what the writer says it verified

The change states its evidence:
- Baselines on the parent tree fail checks 1 to 3, and runs on `HEAD`'s tree pass. I verified the tree ids.
- The 4392 control grows no section.
- The reworded rule was re-run: two runs per model on the committed tree.

The weak spot is the scope of that evidence: it says nothing about the major-release arm (Item 3).

## Item 7: siblings of the change

- **Versions:** the three version sites changed together, and `make test` confirms they agree. The umbrella `qubership-repo-essentials` points at `../change-description-authoring` by path and was not bumped, as with the earlier package bumps.
- **References:** `references/merge-model.md:86-89` says "write the description as a commit body," which agrees with the new rule. The three `english-*-developer-style` skills and the `docs-page-authoring` and `problem-report-authoring` READMEs only route to this skill.
- **Counts:** no sentence counts the slots differently. The lead is not a new slot. "Six slots, in order" is covered in Item 1.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The Scope paragraph still sends an open-intent compatibility break to Scope | Substantive | `SKILL.md:487-491` | Say the break line goes with the breaks, and only the question of whether it is intended stays in Scope. |
| The Caller checklist item asks for breaks under "User-visible changes" when they lead | Substantive | `SKILL.md:844-845` | Add "or ahead of the Why slot (Breaks below)" or similar. |
| The leading breaks in a §4 rule 5 commit body have no stated form, and "Slot 1 opens the body" and "Six slots, in order" lost their truth condition | Substantive | `SKILL.md:86, 192, 257-260, 301-302` | Say whether the leading breaks are `User-visible:` lines or a heading in that body, and put the condition in the sentences that state the order. |
| "The trailer decides" can mean an existing trailer or the one this change writes | Substantive | `SKILL.md:246-248` | Name which trailer, and what happens on a maintenance branch whose next release is known to be a patch. |
| The case READMEs quote the rule in wording the skill does not contain, with a different outcome for an unknown release | Substantive | `cases/pgjdbc-4367-breaks/README.md:7-8`, `cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the committed sentence. |
| No case for a major release, an unknown release, the commit body, or the rule 5 body, though the commit message claims each | Substantive | `research/change-description-authoring/cases/` | Add a major-release control (for example 4367 against a `43.0.0-SNAPSHOT` version file), or narrow the commit message to what ran. |
| The version bump `1.4.0` to `1.5.0` is not claimed in the commit message | Substantive | `apm.yml:168` and two siblings | Add "Version 1.4.0 to 1.5.0." as earlier commits do. |
| The `git archive` recipe does not copy anything without `\| tar -x -C <dir>` | Substantive | `cases/pgjdbc-4367-breaks/README.md` "Running it" | Give the full pipe. |
| "On Opus and Haiku (effort high)" reads as both models at high, but the README says Opus ran at the session default | Taste | commit message | "On Opus, and on Haiku at effort high." |
| The README records no revision for the style skill the runs read, and does not name `scripts/skill-tree.sh` as the source of the ids | Taste | `cases/pgjdbc-4367-breaks/README.md` "Running it" | Record both. |

I did not do a style-only pass over the prose, and I did not re-run any model case. I did not run `apm pack --check-versions` either, and I did not fetch the cited pgjdbc pull requests (no network), so the claim about what the maintainer rewrote is unchecked.
