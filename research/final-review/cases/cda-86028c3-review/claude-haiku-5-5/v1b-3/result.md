## Final review: `4f6981065fe77b7b8a5055fd5a7bbc2e80663dc7..HEAD` (one commit, 86028c3)

**Claimed cases** come from the commit message only. No task statement was handed over, so item 2 is answered from the message and the case READMEs.
**Analogue used:** the change has no code, so the form ran through §2a. The doc-comment skill is replaced by `english-developer-style` (loaded from the scratch skills directory), and I did not load `apm-authoring`, because it is not among the three copies I was given. I cited none of its rules.
**Drift script:** run, no output, exit 0. The change has no code members, so it does not apply.
**Previous report:** none.

### Item 1: comments consistent with the code and each other
Findings 1–3. I also checked the cross-references (§4 rule 5, §5 trailer table, §7, the §8 checklist line), and they resolve.

### Item 2: claimed cases covered
The claimed cases are covered: the lead, result shape, later-statement failure, fix-not-a-break, literals, and the no-break control. Run counts match the commit message. The `Generated with [Claude Code]` claim holds for all five Haiku results, not the three-or-two the README counts. Commands: finding 4. Hunks: finding 7.

### Item 3: boundaries, partitions, and the negative control
Findings 5 and 6. Limits: none set. Pre-existing state: none, since each run starts from a fresh copy of the skill and the target-branch version file comes in through the prompt.

### Item 3a: level, placement, environment
none. The `cases/` layout matches `agent-packages/AGENTS.md`. `make check` (exit 0, version alignment OK) and `scripts/check-skill-descriptions.py` (27 descriptions OK) both pass.

### Item 4: names by content
Finding 8.

### Item 5: failure report
none. The new §8 "Breaks" line is reached from the checklist and covers both the lead and the empty-heading parts.

### Item 6: what the writer says it verified
The 4367 baseline runs on origin/main are the red evidence for the lead. The control has no base run (finding 6). The writer states that the earlier draft runs are summarized, not stored, which is honest.

### Item 7: siblings
none. The package README, the §8 checklist, and the research README were all updated. A grep for "breaks first" and "Breaking changes" across `agent-packages/` and `research/` finds no other copy of this rule. The changelog rule at SKILL.md:543 is a separate artifact and does not contradict it.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| 1. The case README quotes a rule heading that no longer exists. It quotes "A break leads the description where the next release from the target branch promises compatibility". The current heading at `SKILL.md:234` reads "A break leads the description unless the next release from the target branch is a major." | substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:8`; `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md:6-7` | Quote the current heading in both files. |
| 2. Two sentences conflict. `SKILL.md:257` says the commit body "keeps its order, problem first" with no qualifier. Lines 259–261 say a description that §4 rule 5 makes the body "opens with its breaks and then its problem". A reader can take the first as general. | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:257-261` | Qualify the first: "A commit body written apart from the description keeps problem first." |
| 3. "The trailer decides, and it is written whatever the description does" does not say what the trailer decides, so the reader must infer the major-release link. | substantive | `SKILL.md:247-248` | State it: a `BREAKING CHANGE:` trailer or `!` makes the next release a major, so the breaks stay in slot 3. |
| 4. The recipe does not copy anything. `git archive <rev> <path>` writes a tar stream to standard output. The repo's own form in `agent-packages/AGENTS.md:43` pipes it to `tar -x -C <dir> --strip-components=<depth>`. The 4392 README says "as in" the 4367 one, so it inherits the error. | substantive | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:29-30` | Use the AGENTS.md form, with the pipe to tar. |
| 5. Partitions with no case. The rule has a major branch, where the breaks "stay first in slot 3" (`SKILL.md:252-254`), and an unknown-release branch. No case runs either. The rule names removed option, changed default, and changed error code, and no case exercises any of them. | substantive | `SKILL.md:245-254`; the case list under `cases/` | Run the 4367 input with the target set to a major, and with the target unknown. Add one case with a removed option or a changed default. |
| 6. The negative control has no base-commit run. The control claims the rule adds nothing when nothing breaks, but there is no run on the pre-change skill (tree `1f020ce`, which is `HEAD~1`). The README also records that the draft is 209 words while the results are 241–256, and the commit does not mention that growth. | substantive | `research/change-description-authoring/cases/pgjdbc-4392-no-break/README.md:23-25`; commit message | Run the control on the base skill, once per model, or state why not. Name the word growth in the commit. |
| 7. The version bumps have no claiming sentence. `1.4.0` → `1.5.0` appears in three files and the commit message does not mention them. The log shows each feat commit in this package bumps `apm.yml`, so the bump is probably intended. | taste | `.claude-plugin/marketplace.json:291`; `apm.yml:168`; `agent-packages/change-description-authoring/apm.yml:2` | Name the bump in one body sentence, or accept it as the per-commit convention. |
| 8. Positional names. "Checks 1 to 3 are the rule under test; 4 to 6 are the guard" refers to checks that have names. The 4367 README also uses "The first… The second… The version committed here" for rule versions. | taste | `research/change-description-authoring/cases/pgjdbc-4367-breaks/README.md:25`, and the rule-versions paragraph in the Results section | Name them by content: "Lead, result shape, and later-statement failure are the rule under test." |

### Not checked
I did not re-run any case, since that needs a model and there is no network. The `origin/main` baseline is not verifiable here because the clone has no `origin/main` ref; `HEAD~1` has the tree id the baseline `skill-tree` files record. I did not count the baseline word totals in the 4367 table, and I did not run markdownlint, which is not installed. I did not load `apm-authoring` or `test-authoring`, as noted above.
