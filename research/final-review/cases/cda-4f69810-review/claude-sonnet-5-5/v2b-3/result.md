# Final review: `d79c43d..4f69810` (change-description-authoring 1.4.0)

**Inputs.**
- There is no task statement. The claimed cases are taken from the commit message alone.
- There is no previous report.
- This is a change with no code (§2a): it touches a skill, its README, and the registration entries. I did not run the drift script, because it lists members and this change has none. I did run it as a check, and it printed nothing.
- I read the `english-developer-style` copy under the given skills directory for wording. I did not load `apm-authoring` or `docs-page-authoring`, because they are outside the three allowed copies. Under item 3a I could not check the `apm-authoring` layout rules for that reason.

**Claims taken from the commit message.**
- C1: A defect found by an audit or a code reading is described by what found it, and the sentence ends there.
- C2: A changelog entry for such a defect names the condition alone.
- C3: A derived consequence is written only when traced to what a caller sees, and is marked as derived.
- C4: "Say so" stays for a defect with no symptom by construction.
- C5: In the What slot, a sentence recoverable from one hunk is translation, even under a lead-in that states a reason.
- C6: A public identifier is named once.
- C7: The What slot asks for "what changed that the diff does not show".
- C8: §7 points to the translation rule.
- C9: The rejected-alternative mechanism is stated as a fact about the merged code, and an obstacle the change removes is a step it took.
- C10: A question that code or verified evidence answers gets its answer.
- C11: A question only a maintainer can settle stays in the Scope slot.
- C12: A question is dropped only when it does not bear on the change.
- C13: The checklist gets Symptom and Alternatives updates and new Discussion and Translation items.
- C14: Slot 2 and the What slot each carry a bad and a good example.
- C15: The What-slot example "no longer puts an outcome in prose".
- C16: The examples avoid the original pull request.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement the changed files make about one another. I checked them as follows.
- **Versions.** The version reads 1.4.0 in `apm.yml:168`, `marketplace.json:291`, and the package `apm.yml`.
- **Section references.** `(§2, slot 2)` in the changelog row resolves. `(§5)` for public identifiers resolves, because §5 is "Trailers and the identifiers a reader greps". `(§2, the What slot)` in §7 resolves.
- **README.** Its two new bullets match the new rules.
- **Other "symptom" mentions.** The sentences near lines 123, 136, 195, 319, and 332 do not contradict the new rule.

Findings:
- **Finding A.** `SKILL.md`, the What-slot *After* example (about lines 351–355). It says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome stated in prose. The paragraph under the example says the early caller's exception "is an outcome, and it goes on its own line under 'User-visible changes'". C15 says the example no longer puts an outcome in prose. The example therefore contradicts the paragraph beneath it, and a drafting agent copying it will repeat the outcome in the What slot. Substantive.
- **Finding B.** `SKILL.md:94–96`. The rule for a defect with no symptom by construction says "say so", and it cites "a leak on an error path with nothing logged". The preceding sentences, however, tell the writer to name what found it and end the sentence there. A leak found by an audit meets both conditions and gets opposite instructions. The ban on stating an absence is also worded broadly ("neither is the absence of one"). Taste: one clause saying which rule wins would settle it. Two readings are defensible.
- **Finding C.** `SKILL.md:458–464`. The sentence break "wanted. Leave\na question" leaves a one-word line. This is churn, so I do not request it.

## Item 2: claimed cases covered

Analogue: the section that handles each case, plus the detection a reader can apply.

| Claim | Handled by |
| --- | --- |
| C1 | §2 Slot 2 prose and table row, Symptom checklist item |
| C2 | Changelog row 3, Symptom checklist item |
| C3 | The new §2 paragraph, Symptom checklist item |
| C4 | Slot 2 prose; the Symptom checklist's last question |
| C5 | The §2 What-slot paragraph, Translation checklist item, §7 sentence |
| C6 | The same paragraph's exception, with the pointer to §5 |
| C7 | "A reviewer decides" paragraph |
| C8 | §7 final bullet |
| C9 | Rejected-alternatives paragraph, Alternatives checklist item |
| C10–C12 | The new Scope-slot paragraph, Discussion checklist item, Scope table row |
| C13 | Present: Symptom and Alternatives were extended, Discussion and Translation are new |
| C14 | Both examples are present; the Slot 2 pair and the What-slot pair |
| C15 | Not met (Finding A) |
| C16 | Examples use `Pool`/`QueryExecutor` and "retry paths". I cannot check the original pull request from here. |

- Commands the change tells anyone to run: none.
- Hunk-to-claim check: every hunk belongs to a sentence of the commit message. This includes the README and the four version bumps, which the 1.3.0 → 1.4.0 release implies.
- The wording of the claim "fifteen blind Opus drafts" does not reconcile with the per-rule numbers. The counts are 2 + 10 + 2, then 4, then 3 and 4, which total more than fifteen unless the runs overlap. This is unverifiable here and mostly harmless, so I mention it only as a note.

## Item 3: boundaries, partitions, and the negative control

Added instructions, one row each:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Audit-found defect: "name what found it and end the sentence there" | An audit found the defect, and users have since reported the exact error text | "An audit of the retry paths found this." The reported diagnostic is dropped, though slot 2 and the changelog row exist to carry it for R3. | "…unless a symptom was observed, in which case quote it" | Substantive (Finding D) |
| Derived consequence needs a traced chain, marked as derived | A trivial defect with an obvious one-step consequence | A short derived sentence. The rule does not grow the output. | None needed | Not a finding; the text says "earns a sentence only after traced" |
| Translation: a one-hunk sentence is cut | A one-line config toggle whose only content is the hunk | The What slot is emptied, but the Why and Outcome slots survive | The Slot 3 skip condition already covers it ("approach obvious") | Not a finding |
| Public identifier named once | A renamed internal-only constant | Nothing; "public" limits it | The word "public" in the text | Not a finding |
| Rejected-alternative mechanism must hold in merged code | A change with no plausible alternative | No sentence | The existing "earns its sentence only where a reader would propose it" | Not a finding |
| Open question answered or kept | A question that doesn't bear on the change | Dropped | "dropped only when it does not bear" | Not a finding |

- **Finding D.** `SKILL.md:90–93`, plus the same condition in the table row at line 81 and in changelog row 3 at line 475. The condition is "found by reading the code or an audit". It does not require that no one has observed the failure. An agent following the rule on an audited defect with a reported symptom writes only the finder. The Symptom checklist then asks for observed symptoms in the same breath, so the rules conflict. The request is a clause, for example "and no observation of it exists; where one does, quote the diagnostic as usual". Substantive.
- **Pre-existing state:** none. A skill update meets no state an earlier version left behind.
- **Other limits and faults on the same work:** none apply.

## Item 3a: level, placement, and the environment

- No new file was added, and the package layout is unchanged.
- The registration entries (`apm.yml`, `marketplace.json`, the package `apm.yml`) agree with each other. I did not run the repository's gate: it needs the apm tooling, which I did not check.
- The new tutorial-like sentence check: "A predicted failure is not known" is specific to the failure mode this change targets. None.
- Finding: none.

## Item 4: names by content, not by position

none. The new headings, cross-references, and the `*Before:*`/`*After:*` labels are named by content. One new reference, "Slot 2", is a position in a numbered table. It is the skill's existing convention, and the table row is titled "Impact and trigger" next to it.

## Item 5: the failure report

- Every new rule that carries a detection is reached by the checklist: Symptom, Translation, Alternatives, and Discussion.
- The Symptom item does not catch an audit-found defect with a reported symptom, because it asks both questions at once (Finding D).
- The Translation item says "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted". It detects the rule it is attached to, not a weaker property.
- Finding: none beyond D.

## Item 6: what the writer says it verified

The commit message states its evidence, which I read as the writer's own account and did not re-run:
- Blind-draft runs for each rule, with the counts quoted above.
- Hunk translation "persists in about one draft in two", which is stated openly.
- The final open-question rule and the What-slot example were not re-run.
- No case under `research/` was re-run.

The "not re-run" example is the one Finding A concerns. A run would likely have shown the outcome-in-prose copy.

## Item 7: siblings of the change

- **Places that list the package:** `apm.yml`, `marketplace.json`, the package `apm.yml`, and the package `README.md`. All four are updated. The mentions in `docs-page-authoring` and `english-developer-style` name the package only and carry no version, so they need nothing.
- **Slot 2 skip rule.** The same fact appears in the table row (line 81), the prose (lines 90–96), the changelog row (line 475), and the checklist (lines 803–806). All four now agree with each other, apart from Finding D.
- **Old size of any set.** The change adds two checklist items. No sentence counts the checklist, so no stale count.
- **The commit-body and PR-title sections.** They do not repeat the symptom or open-question rules, so they need nothing.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A: the What-slot *After* example puts the early caller's failure in prose, which the paragraph below sends to a "User-visible changes" line and C15 says it no longer does | Substantive | `SKILL.md` What-slot example, about lines 351–355 | Drop the "fails at once" outcome from the *After* sentence, or move it out of the example, so that the example follows its own rule |
| D: the audit-found rule ends the sentence at the finder even when a symptom was observed, so R3's diagnostic is dropped | Substantive | `SKILL.md:81`, `90–93`, `475` | Add the clause "and no observation of it exists; where one does, quote the diagnostic as usual" |
| B: "name what found it" and "no symptom by construction, say so" both fit an audited leak | Taste | `SKILL.md:90–96` | State which wins when both apply; I would prefer finder first. Expect this to be declined. |

Finding C, the one-word line wrap, is churn and not requested.

## Not checked

I did not run the repository's gate, the drafting trials the commit message reports, or the `apm-authoring` and `docs-page-authoring` rules, and I did not review the prose for style alone.
