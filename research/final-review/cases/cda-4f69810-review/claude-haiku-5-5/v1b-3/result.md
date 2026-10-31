## Final review: `d79c43d..HEAD` (commit `4f69810`, change-description-authoring 1.3.0 → 1.4.0)

**Claimed cases:** No task statement was handed over, so item 2 was answered from the commit message alone. No previous report exists for this change.

**Analogues used:** The change has no code, tests, or members. The drift script was not run for that reason. I loaded `english-developer-style` from the skills folder. `apm-authoring` is not in that folder, so I did not load it, and I checked the rules the form names from it only by name. `test-authoring` was not loaded because the change has no tests.

### Item 1: comments consistent with the code and with each other
- F7 (taste).
- Otherwise none. I checked the new slot-2 paragraph (`SKILL.md:90–101`) against the slot-2 row (`:81`), the changelog row (`:475`), the Symptom checklist item (`:803–806`), and the README bullets (`README.md:23–35`). They agree on the rule.
- "now" and "no longer" appear only inside worked examples (`:353–357`), not as narration of the change.

### Item 2: claimed cases covered
- Slot-2 audit and derived-consequence rules, with Before/After: `:90–101`, covered by checklist Symptom.
- What-slot translation rule, with Before/After: `:342–357`, covered by checklist Translation (`:826`).
- Public identifier named once: `:345–347`. No checklist item covers it (see F2).
- "What changed that the diff does not show" in §2: present.
- Rejected alternative stated as a fact about the merged code: `:369–376`, covered by checklist Alternatives.
- Open-question rule: `:458–466`, covered by checklist Discussion (`:835`).
- Commands the change tells a reader to run: none.
- Hunks: the version bumps and the README edits have no sentence in the commit message (F3). The SKILL.md hunks are all claimed.

Instruction table, required for a skill:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
|---|---|---|---|
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (`:91–92`) | An audit-found defect that a report also describes with a quoted exception | "An audit of the retry paths found this." The quoted exception is dropped. | None in the text. Request: "where a report quotes an observed symptom, quote it" (F4). |
| "A consequence derived from the code earns a sentence only after it is traced…" (`:98–101`) | A return value a caller reads directly | A sentence stating that return value | None needed; "derived" already leaves direct reads outside the rule. |
| "A sentence the reviewer recovers from one hunk is translation… cut" (`:342–344`) | A one-hunk behavior change, such as a comparison a caller sees change | The behavioral sentence is cut, leaving the What slot with the reason only | None. Request: a clause that keeps caller-observed behavior (F1). |
| "A public identifier… is named once" (`:345–347`) | A renamed system property | Named once | None. |
| Checklist "where the diff still says it, leave it deleted" (`:826–827`) | A behavior sentence, or a named identifier | Both deleted | None. Request: the rule's own test (F2). |
| "The mechanism is stated as a fact about the merged code" (`:369–376`) | A rejected alternative whose mechanism is still in the code | The mechanism, as fact | None. |
| "Answered where the code… settles it"; maintainer questions kept in Scope (`:458–466`) | A question about intent that the code cannot answer | The question kept, with its decision | None; the rule's own clause applies. |
| Changelog row 3, "the condition alone" (`:475`) | As the first row | A condition-only entry that R3 cannot grep | None. Same clause as F4. |

### Item 3: boundaries, partitions, and the negative control
- F1: the translation test has no negative control. A behavior sentence a reviewer can recover from one hunk should stay, and the example's own lead sentence is one (`:353`).
- Audit-found defect with an observed symptom: the partition is missing (F4).
- Pre-existing state and limits: not applicable to text.

### Item 3a: level, placement, environment
- None. The rules sit in the skill and its README. No em-dashes were added.
- `make check-descriptions`: 27 descriptions within the limit.
- `apm pack --check-versions --check-clean --dry-run` ran offline and exited 0. The marketplace.json entry and both apm.yml files agree on 1.4.0.

### Item 4: names by content
- F8 (taste).

### Item 5: failure report
- F2: the Translation checklist item detects "the diff still says it", which is a different property from the rule's "recovers from one hunk". It would delete the example's own lead sentence and a named public identifier.

### Item 6: what the writer says it verified
- F6: the commit states that the final open-question rule and the final What-slot example were not re-run. The earlier measurements ran against version 1.0.1, which I confirmed is the package version at `985bf80^`. The counts in the commit message are not in the repo, so I did not check them.

### Item 7: siblings
- F5: the description's Why slot carries the symptom (`:195`, `:319`), but the audit and derived-consequence rules appear only in the commit-body slot 2 (`:91–101`).
- The three version fields and the README are updated consistently. No sentence counts the slots as before.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. The What-slot test cuts behavior too. The example's lead sentence "The pool opens at startup…" passes that test, and the What row (`:196`) asks for the behavioral change. | substantive | `SKILL.md:342–344`, `:353–356` | Restate the test as about the edit, not the behavior. Add the control that a behavior sentence stays, and check the After example against it. |
| F2. The Translation checklist item uses a different test from the rule and would delete the behavior sentence and the identifier the rule keeps. | substantive | `SKILL.md:826–827` | Align the item with the rule's test, excluding caller-observed behavior and public identifiers named once. |
| F3. Version bumps in three files and four README bullets have no sentence in the commit message. Earlier feat commits in this series also bumped versions, but the form still requires a claim. | substantive | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168`; `README.md:26–35` | Add a sentence claiming the 1.4.0 bump and the README rules, or move them to their own commit. |
| F4. The audit rule ends the symptom even where a report quotes an observed one. The changelog row has the same problem. | substantive | `SKILL.md:91–96`; `SKILL.md:475` | Add: where a report quotes an observed symptom, quote it with its condition. |
| F5. The description's Why slot carries the symptom, but the audit and derived-consequence rules are written only for the commit body. | substantive | `SKILL.md:195`, `:319` against `:91–101` | Put the rule in the Why slot, or point the Why slot at slot 2. |
| F6. The final open-question rule and the final What-slot example have no run. The commit says so. | substantive | `SKILL.md:458–466`, `:342–357`; commit message | Run both final wordings on the bad cases and name the result, or state in the commit that they are unmeasured. |
| F7. The "Skip when" cell carries a requirement, not a skip condition. | taste | `SKILL.md:81` | Move the requirement into the slot's content. Expect this to be declined. |
| F8. Positional references: "the first sentence" and "slot 2", where the sentence and the slot have content names. | taste | `SKILL.md:357`; `:475` | Name the sentence by its content and the slot by its name. Expect this to be declined. |

**Not checked:** the drift script (no code in the change); the `apm-authoring` text, which is not in the skills folder; the blind-draft measurements, which are not in the repo; and a prose pass for style alone, beyond the grep for em-dashes, "now", "will", and similar tells.
