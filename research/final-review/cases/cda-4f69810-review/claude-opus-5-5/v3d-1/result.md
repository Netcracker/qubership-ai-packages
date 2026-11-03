# Final review: `d79c43d..4f69810`, change-description-authoring 1.4.0

**Inputs.** There was no task statement, so the claimed cases come from the commit message alone. The change touches no code: it edits `SKILL.md` and `README.md` of change-description-authoring and bumps the version in three files. I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring`. I did not run `comment-drift.py`, because there are no members for it to parse. There was no previous report.

In this report, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other
*Analogue used: statements one changed file makes about itself, another file, or the repository.*

- **A. The audit rule and the "say so" rule overlap, and the example sits in both** (`SKILL.md:91-96`).
  - The new rule says: where "reading the code or an audit found the defect, name what found it and end the sentence there".
  - The narrowed rule keeps "(a leak on an error path with nothing logged), say so" for "no symptom by construction".
  - A leak on an error path is the standard audit finding. It also has a symptom (resource exhaustion), just not a logged one, so it does not fit "by construction".
  - An agent with an audit-found leak gets two instructions: end at the audit, or state an absence. Stating the absence is the exact output the commit message says it banned.
- **B. The README contradicts the derived-consequence rule.**
  - `README.md:28-29` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen".
  - `SKILL.md:98-101` allows a consequence derived from the code, once it is traced and marked as derived.
  - Within `SKILL.md`, line 94 ("A predicted failure is not known") is followed by that permission with no "except" linking the two.
- **C. The Translation checklist item drops the public-identifier exception** (`SKILL.md:826-827`).
  - The item says: "where the diff still says it, leave it deleted".
  - The rule at `SKILL.md:345-347` says a new system property or flag is named once.
  - The diff shows the property name, so the checklist deletes it. The commit message says drafters check against §8, not §2, so this checklist item is the one they will follow.
- **D. The What-slot *After* keeps the edit its own rule removes** (`SKILL.md:353-355`).
  - "with the pool open from startup it sends directly" is the hunk the *Before* lists as translation ("execute now uses sendDirect instead of sendWithRetry").
  - The rule says to "state the reason for the decision, not the edit that carries it".
  - The *After*'s first sentence also states an outcome in prose ("fails at once"), although the commit message says the example "no longer puts an outcome in prose". I count that second part as taste, since a behavioral change does belong in the What slot.
- **Checked and consistent:**
  - §7 now points to the What rule (`:763-764`).
  - §2 asks for "what changed that the diff does not show" (`:288`).
  - The Scope table row matches the Scope paragraph.
  - The measured counts in the skill match the commit message.
  - No changed sentence narrates the change with "now", "no longer", or "used to".

## Item 2: claimed cases covered
*Analogue used: the sections that handle each claim, and each rule's detection.*

| Claim (from the commit message) | Section | Detection |
| --- | --- | --- |
| Slot 2: an audit-found defect is described by what found it | `:91-93`, table `:81` | Symptom checklist item `:803-806` |
| A changelog entry names the condition alone | `:475` | None in the Changelog checklist item `:842` (see Item 5) |
| A derived consequence is traced and marked as derived | `:98-101` | Symptom checklist item |
| "Say so" is kept for a defect with no symptom by construction | `:94-96` | Symptom checklist item |
| A sentence recovered from one hunk is translation; a public identifier is named once | `:342-357` | Translation checklist item (misses the exception, finding C) |
| §7 points to the What rule; §2 asks for what the diff does not show | `:763`, `:288` | — |
| A rejected alternative's mechanism is a fact about the merged code | `:369-374` | Alternatives checklist item `:831-833` |
| Open questions are answered, kept for a maintainer, or dropped | `:458-465`, Scope row `:199` | Discussion checklist item `:835-838` |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-357` | — |

- **Commands:** none of the changed hunks contains a command line.
- **Unclaimed hunks:** the version bump 1.3.0 → 1.4.0 in `apm.yml:168`, `.claude-plugin/marketplace.json:291`, and the package `apm.yml:2` has no sentence in the commit message. The three earlier commits on this package bump the same way without claiming it, and `apm-authoring` asks for a bump on a contract change. I label this taste.

## Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres and situations the change claims, and the table of added instructions.*

- **E. Two of the three genres have no trial evidence.** Every draft was a pull request description. The commit-body slot 2 rule and the changelog "condition alone" rule (`:475`) were never drafted under. This is substantive.
- **F. The rule does not cover a description that becomes the commit body.** Under §4 rule 5 (`:608-611`) the description takes the body's shape, and the body has no Scope slot. The open-question rule (`:458-463`) sends a maintainer question to "the Scope slot" and says nothing about this case. The question would then land in permanent history, or have nowhere to go.
- **Pre-existing state:** the change only edits skill text, so a package installed over 1.3.0 has nothing to migrate. None.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| Changelog part 3: "for a defect an audit or a code reading found, the condition alone" (`:475`) | An audit-found defect that a user has since reported, with a stack trace in the issue | An entry with no diagnostic, so R3's grep misses it. §3 (`:511-512`) says this costs R3 "the whole entry" | "…, unless a diagnostic has since been observed" (substantive) |
| Slot 2: name what found it and end the sentence there (`:91-93`) | The same defect, found by an audit and later observed | One sentence about the audit; the observed log line is cut | "where no one has observed it" (substantive) |
| Translation: delete What-slot sentences the diff recovers (`:342-347`, `:826`) | A one-hunk change, such as a timeout constant raised | An empty What slot, although the description's What slot has no skip condition (`:191`, "the last three are conditional") | A What slot left empty once its sentences are deleted is dropped, and the Why slot carries the description (substantive) |
| Open question kept in the Scope slot (`:460-463`) | A squash with "title and description" (§4 rule 5) | A maintainer question inside the commit body, or nowhere | Same as finding F; that row is filed there |

**Not findings:**
- The derived-consequence rule, ended by "A consequence derived from the code earns a sentence only after it is traced…".
- The rejected-alternative mechanism rule, ended by "where a reader would propose it" (`:351`).
- The open-question rule for a change with no discussion, ended by "A question the issue or the review left open".

## Item 3a: level, placement, and the environment
None. The rules sit in the slot sections they govern, with checklist lines in §8, matching the earlier commits. `UV_OFFLINE=1 make check` exited 0, and the working tree stayed clean. No new sentence reads as generic tutorial text.

## Item 4: names by content, not by position
- **Taste:** `SKILL.md:357`, "the first sentence says why they are no longer needed", points to a sentence of the *After* by its ordinal. "The startup sentence" would name it by content.
- "Slot 2" and "§2, slot 2" are numbered in a table the skill defines, so they stand.

## Item 5: the failure report
*Analogue used: whether the checklist reaches each rule, and whether each check detects that rule.*

- **G. The changelog's "condition alone" rule has no check of its own.** The Changelog checklist item (`:842`) does not mention it. The Symptom item (`:804-805`) asks "does the sentence end at what found it?", so applied to a changelog entry it asks the entry to name the audit, which is the opposite of "the condition alone". This is substantive.
- **C again:** the Translation check is stricter than its rule (see Item 1).
- Every other new rule is reached by a checklist line that tests the rule itself.

## Item 6: what the writer says it verified
The commit message gives baselines and results: symptom predicted 2/2 → 0/2, retold obstacle 2/4 → 0/4, open question repeated 3/3 → 0/4, translation in about 1 draft in 2. Three gaps remain:

- **H. The current text was never re-run.** The commit message says itself that the final open-question rule and the rewritten What example were not re-run.
- **H. The drafts ran against an older skill.** All of them used version 1.0.1, before the outcome slot and the length rules this text now sits beside.
- **H. There is no noise control.** No run checked that output did not grow on an input where the new items are noise: a fix with an observed diagnostic, or a change with no open question.

The final symptom wording rests on n=2.

## Item 7: siblings of the change
- `README.md` was updated.
- The frontmatter `description` and the marketplace description are unchanged, and the scope was not widened, so that is correct.
- The umbrella `qubership-repo-essentials` resolves the package from the same commit, and the earlier bumps also left it alone.
- I grepped `agent-packages` for "no symptom", "has not been seen", "paraphrase of the diff", and "open question". Only unrelated hits came back (meeting-analysis, troubleshooting-skill-creator).
- `english-developer-style` routes commit and PR content to this skill and repeats none of these rules.
- None.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| A. The audit rule and "say so" overlap; the leak example fits both | Substantive | `SKILL.md:91-96` | Say which rule wins for an audit-found defect, and use an example with no symptom by construction |
| B. The README bans predicted failures; the skill allows traced, derived ones | Substantive | `README.md:28-29`, `SKILL.md:94-101` | Have the README name the traced-and-marked exception, and link line 94 to the exception |
| C. The Translation checklist deletes public identifiers that the rule keeps | Substantive | `SKILL.md:826-827` | Add the exception to the checklist item |
| D. The What *After* keeps "it sends directly", the edit its own rule cuts | Substantive | `SKILL.md:353-355` | End the *After* at the reason, and re-apply the rule to the example |
| E. No trial covered the commit-body or changelog genres | Substantive | `SKILL.md:91-101`, `:475` | Draft at least one commit body and one changelog entry, or say these rules are untested |
| F. A maintainer question has no place under §4 rule 5 | Substantive | `SKILL.md:458-463` | Add a clause for a description that becomes the commit body |
| Row: the changelog "condition alone" rule drops a diagnostic observed later | Substantive | `SKILL.md:475` | Add "unless a diagnostic has since been observed" |
| Row: slot 2 "end the sentence there" cuts a symptom observed later | Substantive | `SKILL.md:91-93` | Add "where no one has observed it" |
| Row: the Translation rule can empty a required What slot | Substantive | `SKILL.md:342`, `:191` | State what happens to an emptied What slot |
| G. The changelog rule's check is missing, and the Symptom check asks the opposite | Substantive | `SKILL.md:804-805`, `:842` | Add the condition-alone check to the Changelog checklist item |
| H. The final wording was not re-run, and there is no noise control | Substantive | commit message | Re-run the current text, including an input where the new items are noise |
| Version bump not claimed by the commit message | Taste | `apm.yml:168` and two other files | One clause in the commit message |
| *After* states an outcome in prose | Taste | `SKILL.md:353` | Optional rewording |
| "the first sentence" refers to a sentence by ordinal | Taste | `SKILL.md:357` | Name the sentence by its content |

I did not check the wording for style, re-run any drafts, fetch the cited pull request, or run `make test` or `make verify-docs`, which needs a pushed revision and network access. The comment-drift script was not run because the change has no code.
