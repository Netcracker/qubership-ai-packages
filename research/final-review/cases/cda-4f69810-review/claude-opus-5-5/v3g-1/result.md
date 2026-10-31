# Final review: change `d79c43d..4f69810` (one commit, `change-description-authoring` 1.3.0 to 1.4.0)

I had no task statement, so item 2 takes its claimed cases from the commit message alone. This change has no code: it touches a skill, its README, and version entries. Each item therefore uses the §2a analogue, which I name under that item. I did not run the drift script because it parses code members and this change has none. I loaded `english-developer-style` from the provided copy. `apm-authoring` is not among the three provided skills, so I read the repository's copy (`agent-packages/apm-authoring`); it has no rule called *Fix a bad output where the rule stops*. No previous report exists.

## Item 1: comments consistent with the code and with each other
**Analogue:** statements one changed file makes about another, or about another part of the same file.

- **README contradicts SKILL.md.** `README.md:29-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` does allow a derived consequence, once it has been traced to the caller and marked as derived.
- **Broken cross-reference in the changelog table.** Row 3 at `SKILL.md:475` says that for an audit-found defect you name "the condition alone (§2, slot 2)". Slot 2 (`SKILL.md:90-96`) never mentions the condition for that case. It says "name what found it and end the sentence there", and its *After* line (`An audit of the retry paths found this.`) names no condition. A reader who follows the reference can't find the rule, and can't tell whether the commit body keeps the trigger condition.
- **What-slot example contradicts its own rules and the commit message.** The commit message says the example "no longer puts an outcome in prose". The *After* at `SKILL.md:353-354` says "a caller that runs before startup completes fails at once". That is the same outcome the note at `:358-359` sends to "User-visible changes". It breaks "A fact stated in slot 3 is not restated in slot 2" (`:228`). Its second sentence also ends "it sends directly", which is the `sendDirect` hunk restated. That breaks the rule just above it: "state the reason for the decision, not the edit that carries it".
- **Checked and consistent:**
  - §7 now points to the What slot (`:762-764`), as the commit message claims.
  - §2 now says "what changed that the diff does not show" (`:288`).
  - The Scope row (`:199`) matches the Scope prose (`:458-465`) and the Discussion checklist item (`:835-838`).
  - The measured parentheticals match the commit message: "two of two" and "three of three".
  - The PR Why slot inherits the slot 2 rules through "Slots 1 and 2 are the commit body's slots 1 to 3" (`:206`).

## Item 2: claimed cases covered
**Analogue:** each claimed case against the section that handles it. The test for a rule is its detection (the checklist item that catches a breach).

| Claim (commit message) | Section | Detection |
| --- | --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:90-94` | Symptom, `:803-806` |
| Changelog names the condition alone | `:475` | Symptom item cites §3, but no check names "condition alone" |
| A derived consequence is traced to what the caller sees and marked as derived | `:98-101` | Symptom, `:804` |
| "Say so" kept only for no symptom by construction | `:94-96`, `:81` | Symptom, `:806` |
| What slot: translation even under a lead-in; public identifier named once | `:342-347` | Translation, `:826` |
| §7 points to the rule; §2 asks for "what changed that the diff does not show" | `:762`, `:288` | n/a |
| Rejected alternative stated as a fact about the merged code; a removed obstacle is a step | `:370-373` | Alternatives, `:832-833` |
| Open questions: answered, kept in Scope, or dropped | `:458-465`, `:199` | Discussion, `:835-838` |
| Slot 2 and What slot each carry a bad and a good example | `:92-93`, `:349-355` | n/a |

- **Commands:** none added.
- **Hunks no sentence claims:**
  - The version bump 1.3.0 → 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2` and `.claude-plugin/marketplace.json:291`. The three previous commits each state their bump ("Version 1.2.0 to 1.3.0.").
  - The `README.md` hunk.

## Item 3: boundaries, partitions, and the negative control
**Analogue:** the claimed genres and the trial arms.

**Partitions:**
- The trials drafted one pull request description only. The new slot 2 and changelog row 3 rules govern the commit body and the changelog, and neither has any trial evidence.
- All drafts came from one PR, so there is one input per rule.
- The commit message says plainly that the current open-question rule and the What-slot example were not re-run.

**Added instructions:**

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Audit-found defect: name what found it, end the sentence (`:91`), and the changelog gets the condition alone (`:475`) | Audit found it, then a test reproduced it and printed an exception | "An audit … found this.", dropping the literal R3 greps | "unless a run reproduced it; then quote what the run printed" |
| "Say so" for no symptom by construction (`:94`) | An audit finds a leak on an error path with nothing logged | Two rules collide: one says end at what found it, the other says state the absence | Define "by construction" and say which rule wins; the leak example does have a symptom (exhaustion) |
| Hunk-recoverable sentence is translation (`:342-345`) | A 30-hunk diff where one hunk carries the behavior | Cuts the pointer, against "where to look" at `:290` | "except one sentence naming where the behavior change sits" |
| Alternative stated as a fact about the merged code (`:371`) | An alternative ruled out by the supported Java version or a platform API | Recasts the reason as code, or drops it | "where the mechanism lies in the code" |
| Maintainer question kept in the Scope slot (`:461`) | §4 rule 5: the description becomes the commit body | The open question lands in permanent history, which has no Scope slot | "under §4 rule 5, in a review comment, not the description" |

**Not findings:**
- Derived consequence, ended by "earns a sentence only after it is traced".
- Public identifier, ended by "name it once".
- A question already settled in the discussion, ended by "left open".

## Item 3a: level, placement, and the environment
None. Each rule sits in the section of its slot, with a checklist line. The README is updated, and the three version entries agree. Offline, `make check` reported `change-description-authoring 1.4.0 [matches]` and exited 0. `make check-descriptions` printed "all 27 skill descriptions are within 1020 characters". No sentence reads as generic tutorial text.

## Item 4: names by content, not by position
`SKILL.md:357`, "the first sentence says why they are no longer needed", refers to a sentence by its position. The other positional references are slot numbers or pre-existing text. Taste.

## Item 5: the failure report
**Analogue:** whether each rule's detection catches the rule it is attached to.

The Translation detection at `:826` ("delete each sentence … where the diff still says it") is sentence-level. A sentence that pairs a reason with a hunk restatement survives it. That is the "lead-in that states a reason" case the rule targets, and the *After* example's "it sends directly" shows it passing. Changelog row 3's "condition alone" has no detection. Every other new rule is reached by the checklist.

## Item 6: what the writer says it verified
Stated:
- Before/after counts over the blind drafts.
- That the current open-question rule and the What-slot example were not re-run.
- That there are no `research/` cases (true: `research/change-description-authoring/` has phases, not cases).

Not stated: a control input where the added items are noise, with a check that the output did not grow there. The symptom counts (2 + 10 + 2 = 14) also don't reconcile with "fifteen blind Opus drafts". This may be overlap between arms, but the message doesn't say.

## Item 7: siblings of the change
- No sentence anywhere still counts the slots or the checklist as before.
- The umbrella `qubership-repo-essentials` pins by path, not version.
- There is no installed copy under `.claude/skills` or `.agents/skills`.
- No other file carries 1.3.0 for this package.
- `problem-report-authoring` (`SKILL.md:63`, "What every report has to carry is an observation") may meet the same audit-found case in an issue. It is not in this change's scope, so it is at most a follow-up. Taste.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| README says no predicted failure; SKILL allows a traced, marked derived consequence | Substantive | `README.md:29-30` | Make the README match `SKILL.md:98-101` |
| Changelog row 3 cites slot 2 for "the condition alone"; slot 2 says nothing about the condition | Substantive | `SKILL.md:475`, `:90-94` | State in slot 2 whether the trigger condition stays for an audit-found defect |
| What-slot *After* restates the outcome bound for "User-visible changes" and keeps a hunk clause ("sends directly"); the commit message says it puts no outcome in prose | Substantive | `SKILL.md:353-355` | Rewrite the *After* so it carries only the reasons, and re-check it with the Translation item |
| Audit rule and "say so" rule collide on an audit-found leak; the leak example has a symptom | Substantive | `SKILL.md:91-96`, `:81` | Define "by construction" and state which rule wins, or replace the example |
| Audit rule drops a symptom that a reproduction actually observed | Substantive | `SKILL.md:91`, `:475` | Add "unless a run reproduced it; then quote what it printed" |
| Under §4 rule 5 the open maintainer question lands in permanent history | Substantive | `SKILL.md:461` | Add the rule 5 clause: the question goes in a review comment |
| Translation rule cuts a navigation pointer that `:290` asks for | Substantive | `SKILL.md:342` | Add an exception for one pointer to the hunk that carries the behavior |
| Alternative must be a fact about the merged code, even when the reason is outside the code | Substantive | `SKILL.md:371` | Limit it with "where the mechanism lies in the code" |
| Translation detection is sentence-level and misses reason-plus-edit sentences | Substantive | `SKILL.md:826` | Make it clause-level: "delete each clause the diff still shows" |
| Version bump and README hunks are claimed by no sentence of the commit message | Substantive | `apm.yml:168`, package `apm.yml:2`, `marketplace.json:291`, `README.md:26-32` | Add "Version 1.3.0 to 1.4.0." and a sentence on the README, as earlier commits do |
| No noise-input control; the draft counts don't sum to fifteen | Substantive | commit message | State a control run with no output growth, and reconcile the counts |
| "the first sentence" refers by position | Taste | `SKILL.md:357` | "the sentence on startup" |
| `problem-report-authoring` may need the same audit-found rule | Taste | `problem-report-authoring/.../SKILL.md:63` | Name it as a follow-up |

I did not re-run any drafting trial, I did not check the measured counts against the draft transcripts (they aren't in the repository), and I did not do a style pass over the prose for wording alone.
