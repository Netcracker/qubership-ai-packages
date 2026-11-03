# Final review: `d79c43d..4f69810`, "stop drafts from inventing symptoms and translating hunks"

This change edits a skill, so the form is filled through the §2a analogues; each section names the analogue it used. No task statement was handed over, so the claimed cases come only from the commit message. I did not run `comment-drift.py`, because the change has no code members for it to parse: it touches one SKILL.md, one README, two `apm.yml` files, and `marketplace.json`. I loaded `english-developer-style`, `test-authoring`, and the repository's `apm-authoring`. There is no previous report.

`S` below is `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

Analogue: what each changed file says about the others, and the worked examples.

- **The What-slot example puts an outcome in prose. (`S:353`)** The *After* sentence "a caller that runs before startup completes fails at once instead of opening the pool on demand" is an outcome: it says what the caller observes and under which condition. The paragraph after the example sends the same fact, as `IllegalStateException`, to "User-visible changes". That breaks `S:231`, "A fact stated in slot 3 is not restated in slot 2". It also contradicts the commit message, which says the example "no longer puts an outcome in prose".
- **The README forbids what SKILL.md allows. (`README.md:28-30`)** The README says a defect an audit found gets "neither a predicted failure nor a claim that none was seen". `S:98` allows a consequence derived from the code once it is traced to the caller and marked as derived. Someone who reads only the README will drop a sentence the skill allows.
- **The changelog row and slot 2 agree.** Row 3 at `S:475` and slot 2 at `S:92` say the same thing. §3 (`S:503-512`) does not contradict either. §7 at `S:762` does point to the What slot, as the commit says.

## Item 2: claimed cases covered

Analogue: the section that handles each claim, and whether each hunk is claimed.

| Claim in the commit message | Where it is handled |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there; bad and good example | `S:91-96` |
| A changelog entry for such a defect names the condition alone | `S:475` |
| A derived consequence is written only when traced and marked as derived | `S:98-101` |
| "Say so" is kept for a defect with no symptom by construction | `S:83`, `S:96` |
| What slot: translation from one hunk, even under a lead-in that states a reason; bad and good example | `S:342-359` |
| A public identifier is named once | `S:345-347` |
| §7 points to the What-slot rule | `S:762-763` |
| §2 asks for "what changed that the diff does not show" | `S:288` |
| Rejected alternatives: the mechanism is a fact about the merged code | `S:370-373` (PR description only; see item 7) |
| Open questions are answered, kept in Scope, or dropped | `S:458-465`, Scope row `S:199` |
| Checklist: Symptom and Alternatives extended; Discussion and Translation added | `S:803-806`, `S:826`, `S:832-838` |

There are no commands in the changed text to list.

Two kinds of hunk are not claimed by any sentence of the commit message:
- **The README hunk** (`README.md:26-32`).
- **The version bump from 1.3.0 to 1.4.0** in `apm.yml`, the package's `apm.yml`, and `marketplace.json`. The previous commit, d79c43d, stated its own bump ("Version 1.2.0 to 1.3.0") and its README update; this one states neither.

## Item 3: boundaries, partitions, and the negative control

Analogue: the genres the change claims, and a negative control for each added instruction.

**Missing partitions.** The change claims three genres: the commit body (slot 2 and its skip condition), the pull request description, and the changelog entry (row 3). The trials drafted only pull request descriptions ("Blind drafts of one pull request description"), so the commit body and the changelog have no evidence.

The commit also says the final open-question rule and the revised What-slot example were not re-run. That is stated honestly, but it leaves the newest wording of two rules with no evidence.

There is no earlier state to meet: the change ships content only, and the version pins agree.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Name what found an audit-found defect, end the sentence there, and give the changelog entry "the condition alone" (`S:92`, `S:475`, `S:804-805`) | An audit found the defect, and a user later reported it with a log line | Only "An audit found this", and a changelog entry without the literal the on-call reader (R3) greps | "where nobody has observed it fail; an observed diagnostic is quoted as for any other defect" |
| A sentence the reviewer recovers from one hunk is translation and is cut (`S:342-345`, `S:826`) | A 40-file change where the reviewer needs to know which hunk holds the decision | No pointer to that hunk, even though `S:289` asks that the reader can tell "where to look" | "except a sentence that names where in a large diff the decision sits" |
| Answer a question the code settles, with its evidence (`S:458-460`) | An open question from the issue ("is null handled?") that the diff answers with one added check | "Null is handled: the change adds a check in X", which is the translation `S:342` forbids | "where the diff does not show the answer in one hunk" |
| The mechanism against an alternative is a fact about the merged code; an obstacle the change removes is not a reason (`S:370-373`) | The alternative needs the same obstacle removed in 30 call sites, while this change removes it in one | The cost comparison is dropped as an "obstacle the change removes" | Taste: the text does not address a cost argument. "unless the alternative pays a larger cost to remove it" |

Not findings:
- The derived-consequence rule on a defect with an observed, quoted symptom. It is ended by "A consequence derived from the code" (`S:98`).
- The no-symptom-by-construction clause on an ordinary fix. It is ended by "by construction" (`S:96`).
- The public identifier named again in a User-visible line. It is ended by "name it once" (`S:347`).
- An open question already resolved in the thread. It is ended by "left open" (`S:458`).

## Item 3a: level, placement, and the environment

Analogue: which file each rule lives in, and the repository's own gates.

- **Placement:** the rules sit in the slots they govern, and the checklist items are in §8. The layout matches the sibling packages.
- **Gates, all run offline:**
  - `make check-descriptions`: ok, all 27 descriptions within 1020 characters.
  - `apm pack --check-versions --check-clean --dry-run`: no error.
  - `research/change-description-authoring/check-classifier-target-ref.sh`: all cases ok, control included.
- **Line length:** no new line is over 120 characters outside the tables.
- **Generic tutorial text:** no new sentence reads like one; each rule is tied to a measured failure.
- **Taste:** `S:463` is a stray short line, "wanted. Leave". It does not change how the sentence reads.

## Item 4: names by content, not by position

Analogue: the change's own headings, cross-references, and case names.

none. The cross-references use the skill's existing scheme of section numbers and named slots ("§2, slot 2", "§2, the What slot"). The example's own explanation says "the first sentence", which refers inside a two-sentence quote and cannot go stale.

## Item 5: the failure report

Analogue: each rule's detection in the §8 checklist.

- **The Translation item detects a weaker property than the rule. (`S:826`)** "Delete each sentence… where the diff still says it, leave it deleted" works one whole sentence at a time. The rule at `S:343-345` targets a sentence that pairs a hunk with a reason: cut the edit, keep the reason. The checklist keeps that whole sentence, because the diff does not say the reason. This matches the commit's own report that translation "persists in about one draft in two".
- **The same item contradicts the identifier exception.** The diff still says a new system property's name, so the Translation item deletes the sentence that `S:345-347` says to keep.
- The Symptom, Alternatives, and Discussion items reach every rule they are attached to.

## Item 6: what the writer says it verified

Analogue: the evidence that the rules can fail.

**What is stated.** The commit gives before-and-after counts over fifteen blind Opus drafts:
- symptom: 2/2 predicted a failure, then 5/10 stated none was seen, then 0/2;
- retold obstacle: from 2/4 to 0/4;
- open question: from 3/3 to 0/4;
- hunk translation: partly fixed, still about one draft in two.

**What is missing:**
- The drafts ran against 1.0.1, an older version of the skill. The final open-question wording and the revised What-slot example were not re-run, as the commit says.
- No input is named where an added item is noise, with a check that the output did not grow. Keeping maintainer-only questions in Scope and naming public identifiers both add text.
- No bad case is named for the commit-body and changelog genres.
- The revised What-slot example fails the skill's own rule at `S:231` (item 1).

## Item 7: siblings of the change

Analogue: the places that list or route to the artifact.

- **The commit-body slot 3 rule lacks the new clause. (`S:103-106`)** The "fact about the merged code" and "obstacle the change removes" clause went only into the pull request What slot (`S:370-373`). The commit-body slot 3 rule on rejected alternatives did not get it, although the commit message states the rule without restricting it to descriptions. A writer of a commit body reads slot 3, not the description section.
- **Version pins agree.** `apm.yml`, the package's `apm.yml`, and `marketplace.json` all say 1.4.0. The umbrella `qubership-repo-essentials` pins by relative path, so it needs no change.
- **No other copies or restatements.** No deployed copy of this skill is under `.claude/skills` or `.agents/skills`. No other package restates the old "say so" rule: I grepped for "no observable symptom" and "absence stated" and found only historical research notes.
- **README** is updated (but see item 1).

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The What-slot *After* example states the caller-visible outcome in prose and also sends it to User-visible changes, against `S:231`; the commit message says it no longer does | Substantive | `S:353-354` | Make the first sentence the reason only (for example, "The pool opens at startup, so no call site needs to open it on demand"), and leave the early-caller failure to the User-visible line |
| The Translation checklist item deletes a sentence naming a public identifier, which `S:345-347` says to keep, and it keeps a whole hunk-plus-reason sentence, which the rule says to cut down to its reason | Substantive | `S:826` | Make it work clause by clause ("cut the clause the diff still says, keep the reason") and add "except a public identifier the change adds, removes, or renames" |
| The audit-found rule and changelog row 3 drop the observed diagnostic when an audit-found defect was later observed | Substantive | `S:92`, `S:475`, `S:804-805` | Add "where nobody has observed it fail" to the rule, the changelog row, and the checklist item |
| The translation rule removes a pointer to where the decision sits in a large diff, which `S:289` asks for | Substantive | `S:342-345` | Add a clause exempting a sentence that tells the reviewer where to look in a large diff |
| The open-question rule asks for an answer that, when the diff shows it in one hunk, is translation | Substantive | `S:458-460` | Add "where the diff does not show the answer in one hunk" |
| The README forbids any predicted failure, but SKILL.md allows a traced consequence marked as derived | Substantive | `README.md:28-30` | Add "unless it is traced to the caller and marked as derived" |
| The commit-body slot 3 lacks the "fact about the merged code / obstacle the change removes" clause given to the PR What slot | Substantive | `S:103-106` | Add the same clause to slot 3, or say in the commit message that it applies to descriptions only |
| The README hunk and the 1.3.0 → 1.4.0 bump in three files are not claimed by any sentence of the commit message | Substantive | `README.md:26-32`, `apm.yml:168`, the package's `apm.yml:2`, `marketplace.json:291` | Add a sentence to the commit message claiming both, as d79c43d did |
| The commit-body and changelog genres, the final open-question wording, and the revised example have no trial; no noise input checks that output did not grow | Substantive | commit message | Run the final wording on one commit-body draft and one changelog draft, plus one input where the added items are noise, or say in the commit message that these were not run |
| A cost comparison where the alternative removes the same obstacle at greater cost is dropped | Taste | `S:371-372` | "unless the alternative pays a larger cost to remove the same obstacle" |
| Stray short line "wanted. Leave" | Taste | `S:463` | Re-wrap the paragraph |

I did not run any drafting trial, did not run `make test` or the install smoke test, and did not do a pass over the wording for style alone.
