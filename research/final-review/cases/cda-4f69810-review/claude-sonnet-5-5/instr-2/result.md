Status: I've read the diff, both skills the review needs, and the surrounding sections of the skill file, so I'm writing the report now. I did not change or commit any file.

# Final review: `d79c43d..HEAD` (4f69810)

**Task statement:** none was handed over, so item 2 uses the commit message alone.

**Kind of change:** a skill package (SKILL.md, README, version manifests). The §2a analogues apply under every item. I did not run the drift script. I did run it, and it printed nothing for these files because it doesn't parse Markdown or YAML. Loaded `apm-authoring` and `english-developer-style`; no style pass was done.

**Claimed cases (from the commit message):**
- Slot 2: audit or code-reading rule.
- Slot 2: derived-consequence rule.
- Changelog row 3.
- What-slot translation rule, with the identifier exception.
- §7 pointer.
- §2 "what changed that the diff does not show".
- Rejected-alternatives rule.
- Open-question rule.
- Checklist items: Symptom, Alternatives, Discussion, Translation.
- Bad/good examples in slot 2 and the What slot.

## Item 1: comments consistent with each other

Two findings, both substantive.

- **Overlapping conditions (`SKILL.md:81`, `:92-96`).**
  - "Reading the code … found the defect" is told to name what found it and end the sentence.
  - "No symptom by construction" is told to "say so".
  - The skill's own example for the second, a leak on an error path with nothing logged, is a defect a code reading would typically find. An agent can follow either rule.
  - The commit message says "say so" is kept for the no-symptom case. The text doesn't say which rule wins when both hold.
- **The "After" example breaks the rules it illustrates (`SKILL.md:~354-356`).**
  - The commit says the What-slot example "no longer puts an outcome in prose". The After's first sentence still does: "a caller that runs before startup completes fails at once instead of opening the pool on demand".
  - The text under the example sends that outcome to a `User-visible changes` line, and a fact in slot 3 is not restated in slot 2.
  - "With the pool open from startup it sends directly" restates the `sendDirect` hunk. That is the "Y now calls Z" sentence the new rule calls translation.
  - Under the new Translation checklist item ("delete each sentence … where the diff still says it, leave it deleted") that clause is deleted. A rewrite that fails its own worked example is a finding.

Checked and fine: the table cell at `:81` matches the prose at `:92`. Changelog row 3 (`:475`) matches slot 2. The `(§5)` reference for identifiers resolves to the "Identifiers" bullet in §5. No `now` / `no longer` narration was added. The README additions match the rules.

## Item 2: claimed cases covered

Every claim above has its section (`:92`, `:98`, `:475`, `:339-346`, `:760`, `:285`, `:368`, `:455`, and the checklist at `:804-838`).

- **Unclaimed hunks (substantive).** The version bump 1.3.0 to 1.4.0 appears in four places: `marketplace.json`, root `apm.yml`, package `apm.yml`, and nothing in the README. No sentence of the commit message claims it. Add one, or move it out.
- No commands in the changed files.

## Item 3: boundaries, partitions, negative control

No instruction table. Added instructions: 5, 1 row.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:455` open questions "kept in the Scope slot" | A description that §4 rule 5 makes a commit body, where Scope is absent (`:823`) | A Scope slot, or nowhere to put the maintainer question | "in the Scope slot, or in a closing sentence where the description is the commit body" |

Not findings: `:92` (ends at "end the sentence there"), `:98` (conditioned on a consequence being derived), `:339` (the identifier exception ends it), `:368` (conditioned on "where a reviewer would propose it").

The row is substantive: the Scope slot is the only home the rule names, and the checklist forbids that slot in a commit-body-shaped description.

Negative controls: the audit rule has no example where the rule is noise, such as a defect with an observed symptom. The commit admits the new open-question rule and the What example were not re-run, and that no cases exist under `research/`. I don't file this separately; it is item 6.

## Item 3a: level, placement, environment

None. The rules sit in the existing sections, the checklist lines are in §8, and the manifest versions agree across `marketplace.json`, root `apm.yml` and the package `apm.yml`. I did not run the repository's own gate.

## Item 4: names by content

None. The new text refers to things by content (`slot 2`, `the What slot`, `§5`).

## Item 5: failure report

None. Rules carry detections: Symptom and Alternatives were extended, and Discussion and Translation are new. The Translation check ("delete each sentence … where the diff still says it") detects the rule it is attached to. The new Before/After pair for the audit case is detectable by wording.

## Item 6: what the writer verified

The commit states the evidence. For the symptom rule, both unruled drafts predicted a failure and the final wording produced no "none seen" statements. The retold-obstacle and open-question rules also have counts.

It also states what was not verified: the current open-question rule and the What example were not re-run, and translation persists in about one draft in two. That last number weakens the claim that the rule fixes translation.

I did not check these numbers against any drafts; none are in the repository.

## Item 7: siblings

- **Set-size counts:** none. The change added no member to a set.
- **Sibling surfaces (`:81`):** the slot-2 rule has a commit-body table row and a changelog row, and both were updated.
- **Missed sibling (taste):** the commit-body "Change and approach" slot (`:83`) has no translation rule, but the new Translation checklist item names only the PR "What" slot. A commit-body reader gets the translation test only through the one-line pointer at `:760`. Taste.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Audit rule and no-symptom "say so" overlap with no precedence | Substantive | `SKILL.md:81`, `:92-96` | State which wins when a defect found by code reading also has no symptom, e.g. "name what found it; add that nothing is logged only where the leak is the finding" |
| What-slot After states an outcome in prose, and "it sends directly" restates the hunk | Substantive | `SKILL.md:~354-356` | Cut the outcome and the "sends directly" clause so the example passes the Translation check |
| Version bump to 1.4.0 not claimed by any sentence | Substantive | `marketplace.json:291`, `apm.yml:168`, package `apm.yml:2` | Add a sentence claiming it, or move it out |
| Open-question rule names only the Scope slot, which is absent in commit-body form | Substantive | `SKILL.md:455`, `:823` | Add the clause in the table row above |
| Commit-body "Change and approach" slot has no translation rule | Taste | `SKILL.md:83`, checklist | Add the slot to the Translation checklist line; expect it may be declined |

I did not run the suite or the repository's gate, and did no style pass on the prose.
