I filled the final-review form for `d79c43d..HEAD`. It is one commit, 4f69810, `feat(change-description-authoring): stop drafts from inventing symptoms and translating hunks`.

There was no task statement, so the claimed cases come from the commit message alone. This change has no code: it touches a skill, its README, and three version manifests. So each item below reads the §2a stand-in for a change with no code, and the review applies `english-developer-style` and `apm-authoring` (the repository copy at `agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`). I ran the drift script anyway; it listed nothing, because it does not parse Markdown or YAML. There is no previous report.

In what follows, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
**Stand-in used:** every statement one changed file makes about another file, about its own other sections, or about its examples.

- **1a. The What-slot *After* example breaks its own rule (`SKILL.md:354-355`).** The rule at :342-344 says a sentence the reviewer can recover from one hunk is a translation, "even under a lead-in that states a reason". The *After* ends "…; with the pool open from startup it sends directly." That clause is a reason followed by the edit, which is the same shape as the *Before*'s "With the pool opened at startup, the lazy ensureOpen() calls are removed". A reader learns that putting a reason in front of an edit makes it acceptable. That may be why, as the commit message admits, translation still shows up in about one draft in two.
- **1b. The *After* still puts an outcome in prose (`SKILL.md:353`).** "A caller that runs before startup completes fails at once instead of opening the pool on demand" is the same outcome that :358-359 sends to "User-visible changes". Line :231 says "A fact stated in slot 3 is not restated in slot 2". This also makes the commit message's claim that the example "no longer puts an outcome in prose" false.
- **1c. The new identifier rule and §5 disagree on which identifiers to name (`SKILL.md:345-347` vs `:683-685`).** The new exception names only an identifier the change "adds, removes, or renames (a system property, a flag, an option)". §5 says to name "the public identifier the change touches: option, flag, class, method, configuration key", and a private helper where readers grep for it. A public method whose behavior changes is touched but not added, removed, or renamed. One rule tells the agent to name it, the other to cut it.
- **1d. "Reading the code" fires for nearly every fix (`SKILL.md:91-92`, `:81`, `:475`).** "Where reading the code or an audit found the defect" can also mean a reported failure whose cause the developer found by reading the code. Under that reading, slot 2 and changelog part 3 drop the reported diagnostic, which is the string R3 greps. The intended meaning (found with no report) is not stated.
- **1e. The open-question rule contradicts the decision test (`SKILL.md:463-465` vs `:299-302`).** "Leave a question out only when it does not bear on this change" keeps a question that bears on the change but affects no review decision. The decision test deletes exactly that paragraph.
- **1f. The README overstates the rule (`agent-packages/change-description-authoring/README.md:28-30`).** It says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code, if it is traced to what a caller sees and marked as derived.
- **1g. The new translation rule cuts sentences :289 asks for (`SKILL.md:342` vs `:289-290`).** Line :289 says the reader should be able to tell "where to look". The new rule cuts a sentence that points at the hunk carrying the decision. This is taste.
- **1h. Two other statements I checked hold.** "§7 points to this rule" holds at :762-764. "§2 asks for 'what changed that the diff does not show'" holds at :288.

## Item 2: claimed cases covered
**Stand-in used:** each case the commit message claims, against the section that handles it. I also read the claims the other way, hunk by hunk.

| Claimed case | Where it is handled |
| --- | --- |
| Slot 2: a defect found by an audit or code reading is named by what found it, and the sentence ends there | :90-94, :81, checklist :803-806 |
| Changelog: the condition alone | :475; the Changelog checklist line :842 does not reach it |
| Derived consequence: traced to what a caller sees and marked as derived | :98-101, :804 |
| "Say so" kept for a defect with no symptom by construction | :94-96, :81, :806 |
| What slot: translation even under a lead-in that states a reason | :342-344; the example contradicts it (1a) |
| Public identifier named once | :345-347 (1c) |
| §7 pointer; §2 "what the diff does not show" | :762-764; :288 |
| Rejected alternatives: the mechanism is a fact about the merged code; a removed obstacle is a step the change took | :370-373, :833-834 |
| Open questions: answered, kept in Scope, or dropped | :458-465, :199, :835-838 |
| New checklist items Discussion and Translation | :826-827, :835-838 |
| A *Before* and an *After* for slot 2 and for the What slot | :92-93, :349-359 |
| "This skill has no cases under research/" | True: `research/change-description-authoring/` has no `cases/`. Its `check-classifier-target-ref.sh` reads the §4 bash block, which this change does not touch. |

- **Commands:** the change adds no command line, so there is nothing to run.
- **Hunks no sentence claims:**
  - The README hunk (`README.md:26-32`).
  - The version bump from 1.3.0 to 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The previous commit, d79c43d, stated its bump ("Version 1.2.0 to 1.3.0.").

## Item 3: boundaries, partitions, and the negative control
**Partitions:** the change edits three artifacts: the commit body's slot 2, the PR description, and changelog part 3. The only trial reported is blind drafts of one PR description. The commit body and changelog rules have no evidence.
- The changelog's "the condition alone" changes what R3 can grep, which makes it the riskiest of the three.

**Pre-existing state:** an install of 1.3.0 is replaced by the newer text. Nothing persists between versions, so there is nothing to check.

**Added instructions:** 6, 1 row.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:475` "for a defect an audit … found, the condition alone" | An audit-found defect later seen in production, with a log line | A changelog entry without the literal R3 greps | "where no failure of it has been observed" |

Not findings: `:92`, `:98`, `:370`.

## Item 3a: level, placement, and the environment
**Stand-in used:** which file each rule lives in, the layout against sibling packages, and the repository's own gates.

- **Placement:** each rule sits in its slot's section and has a checklist entry. The layout matches the earlier commits on this package.
- **Version bump:** consistent across all three manifests.
- **Gates:**
  - `scripts/check-skill-descriptions.py` passed: "all 27 skill descriptions are within 1020 characters".
  - `make check` (`uvx … apm pack --check-versions`) needs the network and was not run.
- **Generic sentences:** none found that could appear unchanged in any tutorial.

## Item 4: names by content, not by position
These are taste only, because the skill already uses section numbers throughout.
- `SKILL.md:358` says "the first sentence says why". It could name the sentence by content, such as "the sentence on opening at startup".
- `SKILL.md:475` cites "(§2, slot 2)". It could cite "(§2, Impact and trigger)".

## Item 5: the failure report
**Stand-in used:** for a rule, the check that detects a violation.

- **5a. The Translation check (`SKILL.md:826-827`) is weaker than the rule it checks.** "Delete each sentence … where the diff still says it, leave it deleted" keeps any sentence that carries a reason the diff lacks. That is exactly the "reason; edit" shape that :342-344 bans, so the check passes the *After*'s second sentence from 1a.
- **5b. The Symptom check (`SKILL.md:805`) misses the evasion the commit message measured.** "Does the sentence end at what found it?" passes "An audit found this. It has not been seen to fail." written as two sentences. The commit message reports exactly this evasion: drafts stated the absence of a failure in four different wordings.
- **5c. The Changelog check line (`SKILL.md:842-843`) does not reach the audit case of part 3.**

## Item 6: what the writer says it verified
The writer states red/green counts over fifteen blind Opus drafts. They state frankly that the drafts ran against version 1.0.1, and that the current open-question rule and the What-slot example were not re-run.

What is missing:
- The bad case is not named. The examples deliberately avoid that PR, so the evidence cannot be reproduced.
- No run shows an input where the new items are noise, and none checks that output there did not grow. The decision test asks for that.
- Applying the rewritten translation rule to its own *After* fails (1a).

## Item 7: siblings of the change
- **Places that list the package:** the umbrella `qubership-repo-essentials` pins it by path, and its README description is unchanged. Neither `apm.yml` nor the marketplace description widened scope. Nothing is stale.
- **Commit body slot 3 (`SKILL.md:103-106`)** does not carry the new alternatives rule. Only the PR description section and the shared checklist do. This is taste, because the checklist covers it.
- **`problem-report-authoring`** says "Open with the user-facing symptom" (`agent-packages/problem-report-authoring/.apm/skills/problem-report-authoring/SKILL.md:90`). A report of an audit finding meets the same pressure to invent a symptom. It is neither fixed nor named as a follow-up.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| *After* keeps a "reason; edit" clause the rule bans | Substantive | SKILL.md:354-355 | End the sentence at the reason, e.g. "…used sendWithRetry only to reopen a closed pool, and after startup the pool is not closed." |
| *After* puts the outcome in prose; the commit message claims it does not | Substantive | SKILL.md:353 | Drop "so a caller … fails at once …" and leave it to the User-visible line, or correct the commit message |
| New identifier exception disagrees with §5 on class, method, and "touches" | Substantive | SKILL.md:345-347, :683-685 | Make the exception "a public identifier §5 names", or narrow §5 |
| "Reading the code" fires for reported failures too | Substantive | SKILL.md:91-92, :81, :475 | Add "with no report of a failure" |
| "Only when it does not bear" contradicts the decision test | Substantive | SKILL.md:463-465 | Use "only when its answer changes no review decision" |
| README says no predicted failure, but SKILL allows a derived one | Substantive | README.md:28-30 | Add "unless traced and marked as derived" |
| Changelog "condition alone" drops an observed diagnostic | Substantive | SKILL.md:475 | Item 3 table row |
| Commit body and changelog rules have no trial | Substantive | SKILL.md:81, :475 | One draft of each, or a sentence in the message saying they are untested |
| Translation check passes the banned shape | Substantive | SKILL.md:826-827 | Check clause by clause: remove the reason, and where the rest is in the diff, keep only the reason |
| Symptom check misses an absence stated in a separate sentence | Substantive | SKILL.md:805 | Add "and is no absence of a failure stated anywhere in the body?" |
| Changelog check line does not reach the audit case | Substantive | SKILL.md:842-843 | Add the audit clause to that line |
| Bad case not named; no noise-input control | Substantive | commit message | Name the PR or branch the drafts ran on, and report one draft on an input where the items are noise |
| README hunk and version bump not claimed by the message | Substantive | README.md:26-32; the three manifests | One sentence each, as d79c43d had |
| `problem-report-authoring` has the same symptom pressure | Substantive | problem-report-authoring SKILL.md:90 | Name it as a follow-up |
| New translation rule cuts the pointer :289 asks for | Taste | SKILL.md:289, :342 | Exempt a sentence that points to the hunk carrying the decision |
| Commit body slot 3 lacks the alternatives rule | Taste | SKILL.md:103-106 | Point to :370-373 |
| References by position ("the first sentence", "slot 2") | Taste | SKILL.md:358, :475 | Name them by content |

**Not checked:** I did not run `make check` (it needs the network) or markdownlint, did not re-run any drafts, and did not do a style-only pass over the prose.
