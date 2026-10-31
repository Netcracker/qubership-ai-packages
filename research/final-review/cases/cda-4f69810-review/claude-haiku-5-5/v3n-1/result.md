**Final review of `4f69810` (the only commit in `d79c43d..HEAD`)**

**Scope.** This change has no code, so the §2a analogues apply, and each section says which one it used. Files: `change-description-authoring` `SKILL.md`, `README.md`, `apm.yml`, the root `apm.yml`, and `.claude-plugin/marketplace.json`. No task statement was handed over, so item 2's claimed cases come from the commit message alone. No previous report exists. The drift script ran with exit 0 and no output; it parses no code members, so it does not apply here. Skills loaded from the given directory: `apm-authoring` and `english-developer-style`. `make check` (the offline marketplace gate) passed: version alignment OK, marketplace clean. The tree is unchanged.

**Item 1: comments consistent with the code and with each other (analogue: the skill's statements about rules, files, and examples).** Findings F1, F2, F3 and F7 below. The README bullets (26–35) match the skill. The versions agree across the three files and the gate passes.

**Item 2: claimed cases covered.**
- Predicted failure and absent symptom (Slot 2, 90–100): covered by the Symptom checklist item, 803–806.
- Hunk translation (What, 342–348): covered by the Translation item, 826–827, and §7 at 762–763. The checklist contradicts the rule (F2).
- Rejected alternative with a retold obstacle (369–376): covered by the Alternatives item, 832–834.
- Open question repeated as open (458–464, Scope row 199): covered by the Discussion item, 835–838.
- "Each fix has a checklist item": false for the changelog row (F4).
- Reverse direction, hunks no sentence claims: the version bumps (F5) and the README (F6).
- Commands: the change adds none.

**Item 3: boundaries, partitions, and the negative control.** Added instructions: 8. Rows, with the negative input for each:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A crash a user reported with its exception text, which a reviewer also traced in the code | "A code reading found this." The exception text is dropped | None in the text. Should be "only where no one has seen it fail" (F7) |
| `:475` changelog row 3, "for a defect an audit or a code reading found, the condition alone" | An audit-found defect that users hit, with a logged line the on-call engineer greps | The condition alone; the grep-able line is dropped | None in the text. Should be "only where no symptom has been reported" (F4) |

Not findings: `:98`, `:287`, `:344`, `:369`, `:464`. The identifier rule at 345–347 conflicts with the checklist and is filed under F2. Partitions and prior state: there are no tests, and the installed copy is replaced on install, so no earlier state is read.

**Item 3a: level, placement, environment.** The rules sit in the sections that own them (Slot 2, What, Alternatives, Scope, the changelog table, §8). `make check` passed offline. It checks version alignment and marketplace sync, not whether a bump is claimed.

**Item 4: names by content.** T1: line 357 says "the first sentence", and row 475 cites "slot 2". Both are ordinals where the parts have content names.

**Item 5: failure report.** The Symptom, Alternatives, and Discussion checklist items detect their rules. The Translation item detects a broader property than its rule (F2). The changelog rule has no detection (F4).

**Item 6: what the writer says it verified.** The commit states the measured blind drafts, which ran against 1.0.1, and says the final open-question rule and the What example were not re-run. Those are the writer's to state. The rewritten What example also fails the commit's own claim that it "no longer puts an outcome in prose" (F3). The form makes that a finding.

**Item 7: siblings.** The instruction file, `qubership-repo-essentials`, and `problem-report-authoring` restate no changed rule; they only trigger or cross-reference. The root `apm.yml` and `marketplace.json` agree at 1.4.0. The `apm.lock.yaml` has no version pin. Slot counts ("five slots", "six slots") are unchanged and still correct.

**Findings**

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | For an audit-found defect with no symptom by construction, line 91–93 says "end the sentence there" and line 94–96 says "say so". The two rules give opposite instructions. | Substantive | `SKILL.md:91-96` | State which applies first. For example: "for an audit-found defect with no symptom by construction, name the finder and say there is no symptom." |
| F2 | The Translation checklist deletes any What-slot sentence "where the diff still says it". That includes the public-identifier sentence the rule keeps at 345–347. | Substantive | `SKILL.md:826-827` vs `345-347` | Limit it to sentences "one hunk alone says", and carve out public identifiers. |
| F3 | The What example has a caveat after it (357–359), and its After states an outcome ("fails at once"). That contradicts the commit's claim and the rule that outcomes belong in User-visible changes. | Substantive | `SKILL.md:349-359` | Remove the outcome from the After. Put the omitted-parts explanation in the rule above the example, or cut the caveat. Re-apply the rule to the rewritten example. |
| F4 | Changelog row 3 has no checklist item. The changelog checklist at 842–843 is unchanged. The cell also points to "slot 2", which says something different: name the finder. | Substantive | `SKILL.md:475`, `842-843` | Add a changelog checklist item for the audit-found case. Fix the pointer. Add the "no symptom reported" clause from the table above. |
| F5 | The version bump 1.3.0→1.4.0 has no sentence in the commit message. | Substantive | `apm.yml:2`, `apm.yml:168`, `.claude-plugin/marketplace.json:291` | Name the bump in the message and say why. The apm-authoring rule supports it for a new required step. Otherwise drop it. |
| F6 | The README bullets (26–35) are not claimed by any commit sentence. | Substantive | `agent-packages/change-description-authoring/README.md:26-35` | Name the README update in the message, or move it to its own change. |
| F7 | The Slot 2 found-by-reading condition does not exclude defects that users also saw. A reviewer's code reading would then drop the observed exception text that the slot exists to carry. | Substantive | `SKILL.md:91-93` | Add "and no one has seen it fail" to the condition. |
| T1 | Ordinal references: "the first sentence" and "slot 2". | Taste | `SKILL.md:357`, `475` | Name the sentence by its opening words and the rule by its name. Expect this to be declined. |

**What this review did not check.** I did not re-run the blind-draft measurements, which cannot be checked from the repository. I did not run any drafts through the rules. The `research/` directory was not read beyond its file names. No wording pass was done beyond what changes a claim.
