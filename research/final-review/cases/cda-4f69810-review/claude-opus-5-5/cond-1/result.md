# Final review: commit 4f69810 (`d79c43d..HEAD`)

**Inputs.** I had no separate task statement, so the claimed cases come from the commit message alone. This change edits a skill and has no code, so I used the §2a analogues and loaded `apm-authoring` and `english-developer-style`. I did not run `comment-drift.py`, because the change has no members for it to parse. No previous report exists. All paths below are relative to `agent-packages/change-description-authoring/`, and `SKILL.md` means `.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: Comments consistent with the code and with each other (analogue: statements between files and between sections)

1. **The README and SKILL.md disagree on derived consequences.** `README.md:29-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code, as long as it is traced to the caller and marked as derived. `SKILL.md:94` sits between the two: "A predicted failure is not known". A reader can't tell whether an audit-found defect may carry a traced, marked consequence.
   - **Request:** state one rule in both files. For example, change the README to "…described by what found it; a consequence derived from the code only when traced to the caller and marked as derived".
2. **The changelog rule and the Symptom checklist item point opposite ways.** `SKILL.md:475` says a changelog entry for an audit-found defect carries "the condition alone". The Symptom item at `:803-806` cites §3, the changelog section, and asks "does the sentence end at what found it?". A reviewer who applies that item to a changelog entry would add "An audit found this" to the entry, which `:475` excludes. The Changelog item at `:842` doesn't mention the audit case at all.
   - **Request:** limit the Symptom item's audit question to the commit body and description, and add "for an audit-found defect, the condition alone" to the Changelog item.
3. **The Translation checklist item contradicts the identifier exception.** The checklist at `:826` says "where the diff still says it, leave it deleted". A sentence naming a public identifier that the change adds, removes, or renames is recovered from one hunk, so the checklist deletes it. The rule at `:345-348` says to keep that sentence and name the identifier once.
   - **Request:** add "except a public identifier the change adds, removes, or renames (§2)" to the item.
4. **The What-slot example states an outcome in prose.** The first sentence of the *After* example (`:353-354`) says the early caller "fails at once instead of opening the pool on demand". That is the caller-visible outcome. The commit message says this example "no longer puts an outcome in prose", and `:231` says a fact in the User-visible slot "is not restated in slot 2". The paragraph after the example (`:361-363`) sends only the exception class to that slot, so a reader who copies the example writes the outcome twice.
   - **Request:** make the first sentence state the reason without the caller's result, for example "Opening the pool at startup removes the lazy-open path, and the pool is open before any caller runs." Or have `:361-363` say that this sentence is the What slot's behavioral boundary and that the User-visible line carries the observable result.
5. **The open-question rule competes with the decision test (taste).** `:463-464` drops a question "only when it does not bear on this change". `:304-306` deletes any paragraph that makes no review decision harder. A question that bears on the change but affects no decision is kept by one rule and cut by the other. I'd prefer "…or when its answer changes no review decision".

## Item 2: Claimed cases covered (analogue: the section that handles each claim)

| Claimed case (commit message) | Where it is handled |
| --- | --- |
| Audit or code-reading defect: name what found it, end the sentence | `SKILL.md:81`, `:91-94`, before/after at `:92-93`, checklist `:803-806` |
| Changelog entry: the condition alone | `:475`. The checklist item doesn't reach it (finding 1.2) |
| Derived consequence: trace to the caller, mark as derived | `:98-101`, checklist `:804`. The detection is weaker than the rule (finding 6.1) |
| "Say so" kept for a defect with no symptom by construction | `:94-96`, `:81`, `:805-806` |
| What slot: one-hunk sentence is translation, even under a reason lead-in | `:342-345`, example `:350-359`, checklist `:826`. The detection is weaker than the rule (finding 6.2) |
| Public identifier named once | `:345-348`. The checklist contradicts it (finding 1.3) |
| §7 points to the translation rule | `:762-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternative: a fact about the merged code; a removed obstacle is a step | `:370-373`, checklist `:832-833` |
| Open questions: answer, keep in Scope with the decision needed, drop only if irrelevant | `:458-465`, Scope row `:199`, checklist `:835-837` |
| New Discussion and Translation checklist items | `:826`, `:835` |

- **Commands:** the change adds no command line.
- **Version bump:** the move from 1.3.0 to 1.4.0 in `apm.yml`, the root `apm.yml`, and `marketplace.json` is the package's own release step, and `make check` validates it. It is claimed with the change.
- **Unclaimed hunks:** none.

## Item 3: Boundaries, partitions, and the negative control

The change adds six instructions. One input breaks one of them:

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:91` "Where reading the code or an audit found the defect, name what found it and end the sentence there" (with `:81`, `:475`) | A code-reading find whose new regression test now fails with a literal exception | "Reading the code found this."; no diagnostic; changelog gets the condition alone | "only where no run, test, or report has shown the symptom" |

Not findings: `:98`, `:342`, `:370`, `:458`.

The trials cover only the failing corner. No draft was run on a change where a symptom was observed, or where the issue had no open question, to check that the new rules add nothing there (see Item 6).

## Item 3a: Level, placement, and the environment (analogue: file placement and the repository gate)

None. Each rule sits in its own section, with its checklist item in §8. `make check` exits 0. `make check-descriptions` reports `ok: all 27 skill descriptions are within 1020 characters`. `research/change-description-authoring/check-classifier-target-ref.sh` passes, including its control case. The `description:` field is unchanged, which fits: the change doesn't widen the skill's scope.

## Item 4: Names by content, not by position

None. The cross-references use section and slot names (`§2, slot 2`, "the What slot"). The example's "the first sentence" refers to a sentence two lines above it, inside the same example.

## Item 5: The failure report (analogue: checklist reach and detection strength)

Two detections test a weaker property than their rules (findings 6.1 and 6.2), and two rules have no checklist reach or a contradicting one (findings 1.2 and 1.3).

- **6.1. The derived-consequence check is weaker than its rule.** The checklist at `:804` asks only whether a symptom is "traced in the code and marked as derived". The rule at `:98-99` asks for a trace "to the point where a caller sees it, through every mechanism on the way". The measured defect was a trace that stopped one step short, and the checklist would pass exactly that.
  - **Request:** use "traced to where the caller sees it, through every lazy initialization, retry, or fallback" in the item.
- **6.2. The Translation check doesn't catch a reason lead-in.** "Where the diff still says it" (`:826`) keeps the *Before* sentence at `:350-352`, because the diff doesn't contain its lead-in "With the pool opened at startup". The rule at `:343-345` says the lead-in doesn't exempt the sentence. The commit message says agents check against §8 and that translation persists in about one draft in two.
  - **Request:** add "a lead-in that states a reason does not keep the rest; keep the reason alone" to the item.

## Item 6: What the writer says it verified

The commit states trials over fifteen blind Opus drafts:
- **Symptom:** under a ban on the word, five of ten drafts stated that none was seen; with the final wording, none of two did.
- **Retold obstacle:** from two of four drafts to none of four.
- **Open question:** from three of three drafts to none of four, under an earlier wording.
- **Translation:** persists in about one draft in two.

It also states what was not re-run: the current open-question rule and the What-slot example. Two gaps remain:
- No run covers the changelog "condition alone" row or the identifier exception.
- §2a asks for a bad case where each added item is noise (a defect with an observed symptom, an issue with no open question), with a check that the output did not grow there. The commit states none.

The final symptom wording rests on two drafts.

**Request:** one run on a change with an observed symptom and no open questions, reporting whether the slot 2 and Scope output changed. Or state in the commit message that this was not checked.

## Item 7: Siblings of the change (analogue: index, marketplace, umbrella)

None. The README "What it covers" list is updated. The versions in `apm.yml`, the root `apm.yml` marketplace entry, and `.claude-plugin/marketplace.json` agree. The umbrella `qubership-repo-essentials` pins the package by relative path, with no version to bump. The description text is identical in all three places. The `english-*-developer-style` packages, `docs-page-authoring`, and `problem-report-authoring` only route to this skill by name and don't restate the slot 2 skip condition or the §8 items.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| README rules out a predicted failure that SKILL.md allows when traced and marked | Substantive | `README.md:29`, `SKILL.md:98` | 1 |
| Symptom checklist asks a changelog entry to name what found the defect; Changelog item misses the audit rule | Substantive | `SKILL.md:803`, `:842`, `:475` | 1 |
| Translation checklist deletes the public-identifier sentence the rule keeps | Substantive | `SKILL.md:826`, `:345` | 1 |
| What-slot *After* example states the caller's outcome in prose | Substantive | `SKILL.md:353` | 1 |
| Open-question "drop only when irrelevant" competes with the decision test | Taste | `SKILL.md:463`, `:304` | 1 |
| Audit rule fires on a code-reading find that a test has reproduced | Substantive | Table row in Item 3 | 3 |
| Derived-consequence checklist checks "traced in the code", not traced to the caller | Substantive | `SKILL.md:804` | 5 |
| Translation checklist keeps a hunk sentence behind a reason lead-in | Substantive | `SKILL.md:826` | 5 |
| No noise-input control run; changelog row and identifier exception not run | Substantive | commit message | 6 |

I did not run the drift script, because the change has no code for it to parse.
