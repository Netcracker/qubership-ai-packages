Status: I've read the diff and the touched skill text and run the drift script. The change has no code, so it printed nothing. The report follows. I changed no files and did not commit.

# Final review of `d79c43d..HEAD` (4f69810)

**Inputs.**
- No task statement was handed over, so the claimed cases come from the commit message alone.
- No previous report exists.
- This is a no-code change (§2a). The drift script was run and listed no members, because it parses code and the change is a skill, a README and version metadata.
- Loaded: `english-developer-style` (the copy under the given skills directory). `apm-authoring` is not among the three skills I was told to use, so I did not load it. Its rules are not applied, and I cite none.

## Item 1: Comments consistent (analogue: statements one file makes about another)
- Versions: `apm.yml`, the package `apm.yml` and `marketplace.json` all read 1.4.0. No other file I found pins the old 1.3.0.
- Section references resolve: `§5` is Identifiers, `§2` the slots, `§7` "When to write nothing", `§8` the checklist. Slot 2 in the changelog row points to the commit-body slot 2.
- The measured counts ("two of two", "three of three") match the commit message.
- **Finding A (substantive), `SKILL.md`, What-slot *After* example (about line 355).**
  - Its first sentence says the early caller "fails at once instead of opening the pool on demand". That is an outcome stated in prose.
  - The sentence after the example says the same outcome goes on its own line under "User-visible changes". The skill's own rule says "A fact stated in slot 3 is not restated in slot 2".
  - The commit message says the example "no longer puts an outcome in prose". The example contradicts that, and a drafting agent copies the example.
- The *After* second sentence ("with the pool open from startup it sends directly") restates the `sendWithRetry` → `sendDirect` hunk. Only its reason clause is new. That is **taste**: end the sentence after the reason.

## Item 2: Claimed cases covered
No commands to run in the changed files. Claimed cases and where each is handled:

| Claim | Where handled |
| --- | --- |
| Slot 2 audit-found defects | Slot 2 table row and text, changelog row 3, Symptom checklist item |
| Derived consequence traced and marked | Slot 2 paragraph, Symptom checklist item |
| Hunk translation | What-slot rule with example, §7 pointer, Translation checklist item |
| Rejected alternative as a fact about merged code | Alternatives rule, Alternatives checklist item |
| Open questions | Scope rule, Scope table row, Discussion checklist item |
| "§2 asks for 'what changed that the diff does not show'" | Done |

- The "bad and good example" claim holds for slot 2 and the What slot.
- Hunks no sentence of the commit message claims:
  - The 1.3.0 → 1.4.0 bumps in three files.
  - The README paragraph.
- **Finding B (taste):** add one sentence to the message saying the minor bump and the README summary carry the change.

## Item 3: Boundaries, partitions, negative control
This item reads the table of added instructions.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "for a defect an audit or a code reading found, the body names what found it" (slot 2, changelog row 3: "the condition alone") | An audit-found defect that a user has since reproduced, with a log line | `An audit found this`, with the observed diagnostic dropped, which R3 greps for | None. It needs "only where no one has observed the symptom". |
| "A consequence derived from the code earns a sentence only after it is traced…" | A one-line fix with no consequence | Nothing | It ends itself ("earns a sentence only after"). |
| "a sentence whose content the reviewer recovers from one hunk is translation" | A hunk that is the decision's value, such as a raised timeout | The value is kept | "Keep a specific value where the decision depends on that value" quotes it. Not a finding. |
| Translation checklist: "delete each sentence of the What slot…; where the diff still says it, leave it deleted" | A sentence naming a renamed public property | The sentence is deleted, because the diff shows it | None in the checklist. Prose has "name it once (§5)", but the checklist lacks the exception. |
| "answer from verified evidence; keep a maintainer-only question in Scope" | A commit message, or a description whose Scope slot is skipped | Rule sits only under the description's Scope | The slot is conditional, so it applies where Scope is written. Not a finding. |

- **Finding C (substantive):** audit-found plus observed. Request: add "and no one has observed the symptom" to the slot 2 skip cell and to changelog row 3.
- **Finding D (substantive):** Translation checklist item. Request: add "except a public identifier named once (§5)".

## Item 3a: Level, placement, environment
- Each rule sits in the section its siblings use. The checklist gained items beside the existing ones.
- The repository's registration gate was not run (see the end).
- **None** otherwise.

## Item 4: Names by content
**None.** Headings and cross-references use `§` numbers. The skill itself says a number changes with insertions, but that sentence concerns descriptions that cite other repositories' documents. Section references inside one skill are the existing convention.

## Item 5: Failure report (detection per rule)
- Each new rule has a checklist question that detects it.
- Alternatives and Discussion detect the rule they are attached to.
- The Translation check is weaker than its rule (Finding D).

## Item 6: Writer's verified evidence
- The commit message reports blind-draft counts: bad-case rates before and after.
- It states that the open-question rule and the What-slot example were not re-run.
- No "input where the added item is noise" check is stated. The audit-found and Translation rows above are such inputs.
- Finding A shows the example failed its own rule, which a re-run would likely have caught.

## Item 7: Siblings
- Every place that lists or routes to the skill (marketplace entry, umbrella `apm.yml`, README, the cross-references in `english-developer-style` and `docs-page-authoring`) still describes the skill accurately.
- No sentence counts a set of slots or checklist items with the old size.
- §7a/7b: line 794 lists "symptom dropped" as a finding name. That is fine alongside the new rule.
- **None**.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| A | What-slot *After* example puts an outcome in prose and restates it in the next paragraph, contrary to "A fact stated in slot 3 is not restated" and to the commit message | Substantive | `SKILL.md` ~l.355 | Cut "fails at once…" from the *After*; leave the outcome to the `User-visible` line |
| C | Audit-found rule drops an observed symptom | Substantive | `SKILL.md` slot 2 row (l.81), changelog row 3 (l.475) | Add "and no one has observed the symptom" |
| D | Translation checklist item deletes a public identifier the prose says to name once | Substantive | `SKILL.md` ~l.826 | Add "except a public identifier named once (§5)" |
| B | Version bumps and README paragraph are claimed by no sentence | Taste | `apm.yml`, `marketplace.json`, `README.md` | One sentence in the message |
| — | Second *After* sentence restates a hunk | Taste | `SKILL.md` ~l.356 | End after the reason |

Not checked: the repository's registration gate, markdown lint, link checks, and the blind-draft numbers were not run, and I did not review prose for style.
