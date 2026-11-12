I read the diff and the skill and found no bad version bump. I'm now writing the report. There is no task statement, so the claimed cases come from the commit message alone. This change has no code, so I filled the form through the no-code analogues in §2a. I did not run the drift script, because there are no members to parse. I loaded `english-developer-style` only to check that the prose reads correctly. The commit is `4f69810`, a single commit on top of `d79c43d`.

**Previous report:** none.

## Item 1: comments consistent with each other
Analogue used: statements the changed file makes about itself, about other sections, and about its siblings.

- **Section references:** `§5` (line 347, identifiers a reader greps), `§7` and `§2`, and `§4 rule 5` (lines 281, 823) all resolve to existing headings.
- **Version:** 1.4.0 appears in `agent-packages/change-description-authoring/apm.yml`, the root `apm.yml` and `.claude-plugin/marketplace.json:292`. The 1.3.0 left at `marketplace.json:57` belongs to a different package.
- **Same fact in two places:** the Symptom rule appears in the slot-2 table, in slot-2 prose, in the changelog row 3 and in the checklist. The open-question rule appears in the Scope table, the Scope prose, the checklist and the README. The wording agrees across all of them.
- **Finding A (substantive):** `SKILL.md:92-96` gives two rules that both fire on the same input.
  - Rule one: "Where reading the code or an audit found the defect… end the sentence there."
  - Rule two: "Where the defect has no symptom by construction (a leak on an error path with nothing logged), say so."
  - An audit that finds a leak on an error path satisfies both conditions, and the two rules ask for different things.
  - "Nothing logged" is also a statement about observation, which the text just said "is not known".
  - The request is a clause that decides the overlap. Either by-construction wins when the code shows the symptom cannot exist, or the example is replaced with one that is not an audit finding.
- **Narration:** `now` appears only inside the Before/After examples, where it is the thing being demonstrated. None found elsewhere.

## Item 2: claimed cases covered
The claims come from the commit message only. For each, the analogue is the section that handles it and the detection a reader can apply.

| Claim | Section | Detection |
| --- | --- | --- |
| Slot 2: audit or code-reading finding, derived consequence, "say so" kept | `SKILL.md:81`, `90-103` | Checklist Symptom |
| What slot: hunk translation, identifier named once, §7 pointer, §2 wording | `SKILL.md:285-360`, `763`, `288` | Checklist Translation (new) |
| Rejected alternatives: fact about merged code | `SKILL.md:368-372` | Checklist Alternatives |
| Open questions | `SKILL.md:458-465`, Scope row | Checklist Discussion (new) |
| Changelog row 3 | `SKILL.md:475` | None |

- **Commands:** the change tells the reader to run none.
- **Hunk coverage:** every hunk maps to a sentence of the commit message. This includes the README bullets, the Scope row, the three version bumps and the §7 "no paraphrase" line.
- **Finding B (taste):** changelog row 3 has no checklist line. Symptom covers it only indirectly.

## Item 3: boundaries, partitions, negative control
**Added instructions**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit or code-reading finding: name what found it | A defect users reported, which the audit then confirmed | "An audit found this", although a report exists | None. "Where reading the code or an audit found the defect" does not say whether a user report overrides it. |
| Derived consequence needs tracing and a "derived" mark | A defect with an observed symptom | Nothing extra | Ended by "predicted from one missing call" and "stated as derived, not observed". Not a finding. |
| Hunk translation test | A one-line fix whose What slot is a single reason | A deleted sentence, leaving nothing | Ended by "where the diff still says it". Not a finding. |
| Public identifier named once | The identifier is private | Names it anyway | Ended by "public identifier… (a system property, a flag, an option)". Not a finding. |
| Alternative: check the mechanism against post-change code | No alternative was proposed | A check with nothing to check | Ended by the existing "earns its sentence only where a reader would propose it". Not a finding. |
| Open question: answer, keep in Scope, or drop | A commit body, where §4 rule 5 makes the description the body and there is no Scope slot | A Scope-slot question with nowhere to go | None |

- **Finding C (taste):** the first row has no clause for a defect that has both an audit finding and a user report. This is the partition the Symptom rule most affects, and the change says nothing about it.
- **Finding D (taste):** the last row has no clause for the case where a commit body has no Scope slot. Line 281 only says the body "takes the body's shape".

Not findings: "hunk translation test", ended by "where the diff still says it"; "derived consequence", ended by "stated as derived, not observed".

- **Negative control for the Translation rule:** the Before/After pair fires it. No input is given where the rule is noise. The commit says the example was not re-run (Item 6).
- **Pre-existing state:** the version rises from 1.3.0 to 1.4.0 and installed copies are unaffected. No migration is owed.

## Item 3a: level, placement, environment
- The rules sit in the same sections as their siblings. The checklist items sit in §8 beside the existing ones.
- The registration entries are the version in three places, and the three agree.
- I did not run a repository gate. I found no offline one for marketplace consistency.
- Finding E (taste): `SKILL.md` is now about 10.6k words, and this change adds about 90 lines to it. The Translation rule is long for a rule the commit says "persists in about one draft in two", but the claim is only for ending that persistence.

## Item 4: names by content, not by position
None. The new text refers to slots by name. The checklist items are named Translation and Discussion. The `§` references are to numbered headings the skill itself fixes.

## Item 5: failure report
- **Analogue:** every new rule has a checklist line, and each line detects the rule it is attached to.
- **Finding F (substantive):** the "Translation" line says "delete each sentence of the What slot… where the diff still says it, leave it deleted". The Before/After example breaks this test.
  - The After's second sentence, "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly", ends in a clause the diff states. That clause is "it sends directly".
  - The After therefore fails the rule it is shown to satisfy, or the rule needs a narrower reading of "state the reason, not the edit".
  - The request is to cut "it sends directly", or to say that a clause which finishes a reason is kept.

## Item 6: what the writer says it verified
- **Evidence given:** the commit reports about 15 blind drafts against 1.0.1.
- **Stated as not re-run:** the final open-question rule and the What-slot example. The commit says so itself.
- **Not stated:** how the draft count splits per rule, and any run of the changelog row-3 change. The "5 of 10" and "none of 2" figures cover Symptom only.
- **Not stated:** any run that shows the new Translation example passes the new Translation checklist. This ties to Finding F.
- **Finding G (substantive):** the evidence does not show that the rewritten rules fail the skill's own worked example. The Translation example is the open case. The request is to apply the rule to the After text (Finding F) and report the result.

## Item 7: siblings of the change
- **Version listings:** `git grep` for 1.3.0 and the package name finds the three places that were bumped. The other hits are cross-references that carry no version.
- **Other skills that cite the rules:** `english-developer-style` (`.agents`, `.claude/rules`, `.cursor/rules`) and `docs-page-authoring` cite the package by name only.
- **Counts:** I searched for the old counts ("five slots", "six slots") and found none stale.
- **README:** the added bullets match the skill.
- **Finding H (taste):** the `description` fields in `apm.yml` and `marketplace.json` do not mention the new rules. They describe the package in general, so I think that is fine.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| A: audit-finding rule and "no symptom by construction" rule both fire on a leak found by audit | Substantive | `SKILL.md:92-96`, `81` | Say which wins when both apply, or use an example that is not an audit finding. Drop "nothing logged" or mark it as derived. |
| F: the Translation After example's last clause is recoverable from the diff | Substantive | `SKILL.md:354-358`, `826` | Cut "it sends directly", or state that a reason-completing clause is kept. |
| G: no evidence that the rewritten rule passes the skill's own example; the commit says the example was not re-run | Substantive | commit message | Apply the rule to the After text and state the result. |
| B: changelog row 3 has no checklist line | Taste | `SKILL.md:475`, `§8` | Add a half-clause to the Symptom line. |
| C: no clause for a defect that is both audit-found and user-reported | Taste | `SKILL.md:92` | Add "unless a report exists". |
| D: the open-question rule has no clause for a commit body without a Scope slot | Taste | `SKILL.md:458` | Say where the question goes in a commit body. |
| E: the skill keeps growing | Taste | `SKILL.md` | None requested. |
| H: the package description does not mention the new rules | Taste | `apm.yml`, `marketplace.json` | None requested. |

I did not run the drift script, any repository gate or any draft, and I did no style-only pass over the prose.
