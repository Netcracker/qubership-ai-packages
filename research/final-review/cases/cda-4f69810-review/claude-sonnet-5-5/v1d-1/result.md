# Final review: `d79c43d..HEAD` (4f69810)

This change is a skill, a README, and version metadata, so I filled the form through the §2a analogues. The drift script was not run because there are no code members. The task statement was not supplied, so claimed cases come from the commit message alone. I loaded `english-developer-style` for wording. `apm-authoring` is not among the three permitted skills, so I did not load it.

## Item 1: comments consistent with each other
Analogue: statements the changed file makes about itself and other files.
- Checked: the §2 section references, the slot 2 skip condition against the body text, the changelog row 3 against slot 2, the checklist against §2, §7's pointer, and the version in `apm.yml`, the package `apm.yml`, and `marketplace.json`. The three versions agree at 1.4.0. §7's pointer ("§2, the What slot") resolves.
- **Finding A (substantive):** the new worked example breaks the rule it illustrates. SKILL.md:352-358 gives the *After* as "QueryExecutor.execute used sendWithRetry only to reopen a closed pool; with the pool open from startup it sends directly." The clause "it sends directly" is a sentence recoverable from one hunk. That is the translation case the rule defines and the new Translation checklist item deletes. The example fails its own checklist.
- **Finding B (taste):** SKILL.md:90-102 allows two things for one defect. For an audit-found defect, "end the sentence there". It then allows a derived consequence that is "stated as derived". A writer can't tell whether the second paragraph applies to an audit-found defect. I'd add "for a defect found otherwise than by audit" or similar. Expect this to be declined.
- **Finding C (taste):** SKILL.md:~462 has a one-word orphan line ("wanted. Leave") from a bad reflow.
- No narrating `now`/`no longer` language was added outside example text.

## Item 2: claimed cases covered
Analogue: each claim in the commit message against the section that handles it.
- Slot 2 audit/code-reading rule: SKILL.md:81, 90-96. Covered, with a checklist item.
- Derived consequence traced to a caller: SKILL.md:98-101. Covered by the Symptom item.
- Changelog row 3 "condition alone": SKILL.md:475.
- What slot, hunk translation: SKILL.md:342-358, §7 pointer, Translation item. Covered, but see Finding A.
- Identifier named once: SKILL.md:344-347. This has no checklist item. A rule with no detection is a claimed case with no test (**taste**: the Translation item could mention it).
- Rejected alternative as a fact about merged code: SKILL.md:369-372, Alternatives item.
- Open questions: SKILL.md:458-464, the Scope table row, and the Discussion item. The Scope checklist item (SKILL.md:~840) still says only "every gap named as intentional" and does not mention open questions.
- README bullets match the SKILL.md rules.
- No command lines are told to run.
- **Finding D (substantive, small):** the hunks bumping 1.3.0 to 1.4.0 in four files have no sentence in the commit message. Earlier commits bumped the version the same way, so this is probably intended. The commit needs one clause that claims it.

## Item 3: boundaries, partitions, negative control
Analogue: the genres and situations claimed, and the table of added instructions.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "name what found it and end the sentence there" | A defect found by an audit that also has an observed symptom in a report | It drops the reported symptom and writes only "An audit found this" | The rule's own condition is "the audit or code reading found the defect". It does not cover a symptom also observed, so add "and no one observed a symptom". **Substantive.** |
| "A consequence derived from the code earns a sentence only after it is traced…" | A trivial change where the consequence is obvious | An extra "derived" sentence | "only where a reviewer would otherwise not infer it" (**taste**) |
| "a sentence recoverable from one hunk is translation" | A change with a semantic effect no hunk shows, such as a rename that changes behavior | The agent may delete the sentence that carries the effect | The Translation item says "where the diff still says it". That condition is the clause, so there is no finding. |
| "a question only a maintainer can settle stays in Scope" | A trivial question, such as a naming preference | A Scope entry for a non-decision | The same sentence says "or left out when it does not bear on this change". No finding. |
| "name a public identifier once" | An identifier that appears in a user-visible line already | A duplicate mention | Covered by "once". No finding. |

- Negative control: the *Before*/*After* pairs serve as controls for slot 2 and the What slot. The open-question rule has no example, bad or good.
- The package had no prior-state concern (a pure text package).

## Item 3a: level and placement
Analogue: which file holds each rule and whether the registration entries match.
- The rules sit in the sections the sibling rules use, and the checklist entries are in §8. `marketplace.json`, root `apm.yml`, and package `apm.yml` are consistent. I did not run the repository's gate.
- Not checked beyond the grep: `.agents/` copies of other skills. The package has no copy of its own to update.

## Item 4: names by content
Analogue: headings and cross-references.
- None. Cross-references are by section number plus a named slot or rule, and each resolves.

## Item 5: failure report
Analogue: whether a rule's detection detects the rule.
- Symptom item: it checks "traced and marked as derived" and "sentence ends at what found it". Both detect their rules.
- Translation item: "delete each sentence in turn; where the diff still says it, leave it deleted". This detects the rule, but the skill's own *After* example fails it (Finding A).
- Alternatives item: "an obstacle the change itself removes" is checked.

## Item 6: what the writer says it verified
Analogue: an exemplar that passes and a bad case that fails.
- The message states the blind-draft counts: the 15 Opus drafts, the symptom rule, and the retold obstacle (two of four, then none of four). It also says that the current open-question rule and the What-slot example were not re-run, and that the skill has no `research/` cases.
- So the open-question rule and the final What example have no evidence at all, and the example fails its own checklist. State this plainly as **Finding E (substantive)**: re-run both, or mark them unverified in the message.
- The "measured" figures embedded in SKILL.md (two of two; three of three) were taken on earlier wording of those rules.

## Item 7: siblings
Analogue: places that enumerate or route to the package.
- The README, marketplace entry, root `apm.yml`, and package `apm.yml` carry the same description and version.
- No sentence counts the slots or the checklist items in digits or words that this change alters. I grepped for "six", "five slots", and "four". The Commit body "Five slots" and the PR "Six slots" are unchanged.
- The twin copies under `.agents/` and `english-uk-developer-style` refer to this package by name only.
- The Scope checklist item was not updated (see Item 2).

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| A: the What *After* example's second sentence is hunk translation | Substantive | SKILL.md:352-358 | Cut "with the pool open from startup it sends directly", or replace the example, then re-run the Translation item on it |
| D: version bump in four files is unclaimed by the message | Substantive | marketplace.json:291, apm.yml:168, package apm.yml:3 | Add a sentence to the commit message |
| E: open-question rule and What example not re-run | Substantive | commit message, SKILL.md:458-464 | Re-run, or label the rule unverified |
| Table row 1: an audit-found defect that also has an observed symptom loses the symptom | Substantive | SKILL.md:81, 90-93 | Add "and no symptom was observed" |
| B: audit "end the sentence there" versus derived consequence | Taste | SKILL.md:90-101 | Say which applies to an audit-found defect |
| Identifier-once rule and the Scope checklist item have no detection | Taste | §8 | Add the identifier to the Translation item and open questions to Scope |
| C: orphan line "wanted. Leave" | Taste | SKILL.md:~462 | Reflow |

I did not run the suite or the repository's gate, and I did not do a style-only pass over the prose. No previous report existed.
