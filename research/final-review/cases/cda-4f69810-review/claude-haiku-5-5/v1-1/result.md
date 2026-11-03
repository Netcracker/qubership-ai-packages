## Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring)

**Inputs.** The range is one commit: `4f69810`. It changes `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` (the rules), its `README.md`, and version fields in three `apm.yml`/`marketplace.json` files. No task statement was handed over, so claimed cases come from the commit message alone. No previous report was given, so there is no §4 table. The change has no tests, so the test-class comments claim nothing.

**Skills loaded.** `final-review` was read in full. `english-developer-style` was loaded from the skills copy. The authoring skill for a skill package is `apm-authoring`, which is not among the three copies. I read the repo copy at `agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md` (lines 200–310 only). `test-authoring` was not loaded because there are no tests.

**Drift script.** `comment-drift.py d79c43d… HEAD` ran with exit 0 and printed nothing. The change is Markdown and YAML, with no members to parse, so the empty output is no evidence either way.

Line numbers below refer to `SKILL.md` unless another file is named.

### Item 1: comments consistent with the code and with each other
Analogue: §2a, statements the changed files make about each other and about the rules they cite.
- **F1 (substantive).** The Translation checklist item (826–827) says to delete each What-slot sentence "where the diff still says it." That deletes a sentence naming a public identifier the diff shows, which the exception at 344–347 says to keep. The reader would lose the only place the identifier is named. The item also tests against "the diff" where the rule says "one hunk."
- **F2 (substantive).** The After example (353–354) says "a caller that runs before startup completes fails at once." This restates an outcome slot 3 carries, which 231 forbids ("A fact stated in slot 3 is not restated in slot 2"). The note at 357–359 sends that same fact to "User-visible changes." The caller is also made the subject of a failure that `Pool.acquire()` performs, against english-developer-style §4 ("Give the action to the component that performs it").
- **F3 (substantive).** The second sentence of the same After example (354–355), "with the pool open from startup it sends directly," is the hunk translation ("Y now calls Z") that 342–345 says to cut. The reason ("only to reopen a closed pool") is already there, so the edit clause can go.
- **F4 (substantive).** The "Skip when" cell for slot 2 (81) carries "for a defect an audit or a code reading found, the body names what found it." That is an instruction, not a skip condition. A reader scanning the column reads an audit-found defect as a case where the slot is skipped.
- **F11 (taste).** New "(measured: …)" parentheticals (100–101, 463–465) put measurement history into the skill. apm-authoring's "Encode platform-specific knowledge, nothing else" would leave that out. The file already uses this pattern throughout, so the preferred reading is to move the measurements to the commit message. Expect this to be declined.

### Item 2: claimed cases covered
Analogue: the same item, applied to the commit message's claims and to every hunk.
- **F6 (substantive).** The commit says "Each fix … has a checklist item." The changelog exception at 475 ("for a defect an audit or a code reading found, the condition alone") has no item. The Changelog checklist (842–843) does not check it, and the Symptom item (803–806) covers only the body.
- **F7 (substantive).** The version bump 1.3.0 → 1.4.0 in `.claude-plugin/marketplace.json:291`, `agent-packages/change-description-authoring/apm.yml:2`, and `apm.yml:168` is claimed by no sentence. This is the case §2 names ("a version bump carried over"). The three values agree with each other.
- **F8 (substantive).** The `README.md` bullets added at lines 26–35 are not claimed by any sentence of the commit message.
- Commands: the change adds no command line, so none are listed.
- Claims that do hold: §7 points to the What-slot rule (763); the slot 2 and What-slot examples exist (92–93, 349–355); the §8 items for Symptom, Alternatives, Discussion, and Translation exist (803–838).

### Item 3: boundaries, partitions, and the negative control
Analogue: the table of added instructions (§2a).

| Instruction | Input it does not serve | What the agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (91–93); changelog "the condition alone" (475) | A defect a user reported with a log line or exception, which a code reading also located | "A code reading found this," with the reported diagnostic dropped | "…and no symptom has been observed" |

- **F5 (substantive).** No example or control covers a reported defect that a code reading also located. The rule as written drops an observed diagnostic that R3 greps for.
- Limits, state, and mode checks: not applicable to this change.

### Item 3a: level, placement, and the environment
Analogue: §2a. The file sits in the sibling layout of `agent-packages/*/.apm/skills/…`. The three version fields agree. `scripts/check-skill-descriptions.py` ran offline and passed: "all 27 skill descriptions are within 1020 characters," exit 0. The gate in `research/change-description-authoring/check-classifier-target-ref.sh` was not run because the bash block it tests is not in the diff.

### Item 4: names by content, not by position
Analogue: unchanged. **F10 (taste).** "the first sentence says why" (357–358) refers to the example by position. Naming the sentence by content ("the sentence that says the pool opens at startup") is the preferred reading. Expect this to be declined.

### Item 5: the failure report
Analogue: each rule's detection. The Symptom item (803–806) detects the slot-2 rule. The Translation item's detection is wrong (F1). The changelog exception has no detection (F6). The Discussion and Alternatives items (832–838) detect their rules.

### Item 6: what the writer says it verified
Analogue: an exemplar that passes and a bad case that fails, both named in the change. The bad and good cases for slot 2 and the What slot are named. The commit states that the current open-question rule and the What-slot example "were not re-run," and that the open-question measurement ran on an earlier wording.
- **F9 (substantive).** The open-question rule (458–465) and its Discussion item (835–838) have no evidence for their current wording. The What-slot example also fails its own rules (F2, F3). The request is a blind run of the current wording, or the text's "measured" claim limited to the earlier wording.

### Item 7: siblings of the change
Analogue: §2a. The change adds no member to a set, so the set-membership check does not apply. Slot counts ("Five slots", "Six slots") are unchanged. Section numbers are unchanged, so cross-references by number in other packages stay valid. I did not read the citations in the other packages that name this skill. No installed copy of the skill exists in the repo to go stale.

### Findings table

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | Translation checklist deletes a sentence naming a public identifier, against the exception that keeps it | substantive | `SKILL.md:826-827`, `344-347` | Exempt public identifiers in the item; test against one hunk, as the rule does |
| F2 | Worked example restates a slot-3 outcome in slot 2 and makes the caller the subject of the failure | substantive | `SKILL.md:353-354`, against `:231` and english-developer-style §4 | Cut the sentence and leave the outcome to the User-visible line |
| F3 | Worked example keeps the hunk translation "it sends directly" that the rule cuts | substantive | `SKILL.md:354-355`, against `:342-345` | Keep the reason, drop the edit clause |
| F4 | Slot 2 "Skip when" cell carries an instruction for audit-found defects | substantive | `SKILL.md:81` | Move the clause out of the skip column |
| F5 | Reported defect that a code reading also located: the rule drops the observed diagnostic; no example or control | substantive | `SKILL.md:91-93`, `475` | Add the clause "and no symptom has been observed"; add an example |
| F6 | Changelog audit exception has no checklist item; the commit says each fix does | substantive | `SKILL.md:475`, `842-843` | Add it to the Changelog or Symptom item |
| F7 | Version bump 1.3.0 → 1.4.0 in three files is claimed by no sentence | substantive | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168` | A sentence claiming it, or a separate commit |
| F8 | Added `README.md` bullets are claimed by no sentence | substantive | `README.md:26-35` | A sentence claiming them, or drop them |
| F9 | Current open-question rule and What-slot example have no run | substantive | `SKILL.md:458-465`, `349-355`; commit message | Run blind drafts on the current wording, or limit the "measured" claim to the earlier one |
| F10 | "the first sentence" refers to the example by position | taste | `SKILL.md:357-358` | Name the sentence by content |
| F11 | Measurement parentheticals added to a skill | taste | `SKILL.md:100-101`, `463-465` | Move the measurements to the commit message |

**Not checked.** I read only lines 200–310 of the apm-authoring `SKILL.md`, and I did not read its instructions file. The commit's own "Fix a bad output" citation is not in this change, so I did not check it. No blind-draft run or test suite was run. The drift script produced no output because no code member parses from Markdown. While running `scripts/check-skill-descriptions.py`, I wrote its output to `/tmp/unused`, outside the repo and the scratchpad. It is still there, and nothing in the repo changed.
