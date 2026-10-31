I read the skill and the one-commit diff, and I ran the sibling greps. The drift script reports nothing here, because this change has no code. Without a separate task statement, the claimed cases below come from the commit message alone. I applied the no-code analogues of §2a, loading `english-developer-style` only. I did not load `apm-authoring`, which is not among the three skills I was given, so I cited no sections from it.

## Item 1: Comments consistent with the code and with each other
Analogue used: statements the changed files make about each other and about the repository.

- **Commit message vs. example (substantive):** `SKILL.md`, the What-slot *After* (~l.355). The commit message says the example "no longer puts an outcome in prose". Its first sentence still does: "a caller that runs before startup completes fails at once". The paragraph after it says that outcome belongs on its own line under "User-visible changes", so the example does what its own text forbids.
- **Checklist vs. exception (substantive):** the new Translation checklist item (~l.826) says to delete each What sentence the diff still says and "leave it deleted". The rule it checks has an exception: a public identifier the change adds, removes, or renames is named once. Following the checklist literally deletes that sentence. The commit message says agents check against the checklist, so the exception needs to be there.
- **Slot 2 skip cell (taste):** the "Skip when" cell (l.81) now also holds an instruction, "the body names what found it", which is not a skip condition. I'd put that in the slot 2 prose and keep the cell to skip conditions.
- **Section references:** the "§7 points to this rule" claim holds (§7 now says "§2, the What slot"). The §2, §3 and §5 references I checked resolve.
- **Narration:** the new text uses `Before:` and `After:` examples, and its only "now" is inside an example.
- **Other counts and quotes:** "Five slots" and "Six slots" are unchanged and still true. The README bullet matches the SKILL rules.

## Item 2: Claimed cases covered
Analogue used: the claimed cases are the four defects the commit message names, plus the checklist items. A rule's test is its detection.

| Claim | Section that handles it | Detection |
| --- | --- | --- |
| Slot 2: a defect found by an audit | slot 2 prose, row 3 of the changelog table | Symptom checklist item |
| Derived consequence traced to the caller | slot 2 paragraph | Symptom checklist item |
| Translation of hunks | What-slot paragraph, with before/after | new Translation item |
| Retold obstacle | rejected-alternatives paragraph | Alternatives item |
| Open question | Scope paragraph | new Discussion item |

- **Commands:** the change tells no one to run a command.
- **Hunks vs. claims:** every hunk maps to a claim. The version bump to 1.4.0 appears in three places that agree: `marketplace.json`, `apm.yml`, and the package `apm.yml`. The commit message does not mention the bump, which is a minor omission and not a finding.
- **Unclaimed hunk (none):** I found no hunk without a claim.

## Item 3: Boundaries, partitions, and the negative control
Analogue used: the partitions are the four defects. The commit message supplies the control arm as the measured blind drafts (fifteen Opus drafts, with counts).

The message states what was not re-run: the current open-question rule and the What-slot example. It also states that no `research/` cases exist. That is an honest gap, not a hidden one, and I don't count it as a finding.

Added instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found the defect and end the sentence | A defect with a real observed symptom, such as a user report with a stack trace | Could drop the symptom. | Already ended: the rule applies only to "reading the code or an audit found the defect", and slot 2 still asks for the quoted diagnostic. Not a finding. |
| Trace a derived consequence to the caller | A one-line fix with an obvious symptom | A "derived" paragraph nobody needs. | Already ended by "earns a sentence only after". Not a finding. |
| Delete any What sentence the diff shows | A change whose diff is hard to read, such as a generated or large rename | Drops the only orienting sentence. | None, but the reviewer decision test ("what changes that decision") already governs the What slot. Taste. |
| Rejected-alternative mechanism is a fact about the merged code | A change with no proposed alternative | Nothing. | Already ended: "earns its sentence only where a reader would propose it". Not a finding. |
| Answer, keep open, or leave out each open question | A discussion with no questions | Nothing. | Already ended by "left out only when it does not bear on this change". Not a finding. |

## Item 3a: Level, placement, and the environment
None. All the rules sit in the same `SKILL.md` as their siblings. The README and the manifest entries are the registration surfaces, and I did not run the repository's own gate.

## Item 4: Names by content, not by position
None. The new checklist items are named by content: Translation, Discussion, Symptom, and Alternatives.

## Item 5: The failure report
Analogue used: what each new rule tells the reader to look at.

- **Checklist coverage:** each new rule has a checklist item, and the Translation exception gap is under Item 1.
- **Detection strength:** the Symptom item asks "does the sentence end at what found it", which detects the rule it belongs to, not a weaker property.
- **Line wrap (taste):** `SKILL.md` ~l.460 has an odd wrap, "Leave" alone on a line. It is cosmetic.

## Item 6: What the writer says it verified
The commit message states the evidence: blind-draft counts per rule, and which versions of the skill the drafts ran against. It also states what was not re-run (above). Evidence for the *After* example not putting an outcome in prose is missing, and the example currently does (Item 1).

## Item 7: Siblings of the change
- **Version:** `1.3.0` no longer appears for this package, and the three `1.4.0` entries agree.
- **Slot 2 skip cell:** I found no other place that restates it. The matching changelog row 3 was updated.
- **Checklist "Symptom" item:** it is changed, and its description in the README matches.
- **Set sizes:** no member was added to a set. The checklist grows by two items, and I found no prose that counts the checklist.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The What-slot *After* states an outcome in prose, against the commit message and the example's own explanation. | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` ~355 | Reword the first sentence to give the reason only (the pool opens at startup, so the lazy open is gone). Leave the early-caller failure to the "User-visible changes" line. |
| The Translation checklist item deletes the sentence naming a public identifier, which the rule exempts. | Substantive | same file, ~826 | Add "except a public identifier the change adds, removes, or renames (§2)". |
| Slot 2 "Skip when" cell carries a non-skip instruction. | Taste | same file, 81 | Move "names what found it" to the prose. Expect it to be declined. |
| Stray line wrap in the open-question paragraph. | Taste | same file, ~460 | Reflow. |

This review did not run the repository's gate, did not re-run any blind drafts, and did not do a style pass over the prose beyond where a sentence reads wrongly.
