# Final review: `d79c43d..4f69810` (one commit, change-description-authoring 1.4.0)

There was no separate task statement, so the claimed cases in item 2 come only from the commit message. The change has no code: it edits a skill (`SKILL.md`), the package README, and version fields. I filled the form through the §2a analogues and loaded `english-developer-style` and `apm-authoring` (the repository copy under `agent-packages/`). I did not run `comment-drift.py` because the change has no members for it to parse, only Markdown, YAML, and JSON.

## Item 1: comments consistent with the code and with each other
Analogue: what each changed file says about another file, and the worked examples.

- **README contradicts the skill** (`README.md:28-30`). The README says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` does allow a consequence derived from the code, once it is traced to what a caller sees and marked as derived. A reader of the README would think derived consequences are banned.
- **The What-slot *After* example keeps the clause its own rule bans** (`SKILL.md:354-355`). It ends with "with the pool open from startup it sends directly". That is the *Before*'s "With the pool opened at startup, … QueryExecutor.execute now uses sendDirect" again: a lead-in giving a reason, followed by the edit from one hunk. The rule at `:342-345` calls exactly that translation. An agent copying the example learns to keep the hunk behind a reason, which is the failure the commit message says still shows up in about one draft in two.
- **A rule conflicts with the skill's older example** (`SKILL.md:254`). The PR-description *After* says "The orphan sync is requeued with backoff on failure instead of being dropped". A reviewer recovers that from one hunk, so by `:342` and the checklist at `:826` it should be deleted. That would leave the What slot without the behavioral change the slot table (`:196`) says it carries.
- **The commit message overstates the example**: "the What-slot example … no longer puts an outcome in prose". The *After*'s first sentence still says the early caller "fails at once". This is taste: it can also be read as the behavioral boundary, which belongs in What.
- No sentence narrates the change (`now`, `no longer`) outside the examples, where "now" belongs to the example text.

## Item 2: claimed cases covered
The commit message claims these cases. Each is mapped to the section that handles it:

| Claimed case | Where the change handles it |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it | `:81` skip column, `:91-96`, checklist `:803-806` |
| Changelog entry names the condition alone | `:475` |
| Derived consequence must be traced and marked as derived | `:98-101`, checklist `:804` |
| "Say so" kept only for a defect with no symptom by construction | `:94-96`, `:81` |
| What slot: translation even under a lead-in; public identifier named once | `:342-347` |
| §7 points to this rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternatives: mechanism as a fact about the merged code | `:370-373`, checklist `:831-832` |
| Open questions: answer, keep in Scope, or drop | `:458-465`, Scope row `:197`, checklist `:835-838` |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-355` |

- **Commands:** the change adds no command lines, so there is nothing to map here.
- **Hunks no sentence claims:** the README hunk and the four version bumps (1.3.0 → 1.4.0 in `apm.yml`, the package `apm.yml`, and `marketplace.json`). The bumps follow the convention of the three earlier commits on this package, and `apm-authoring` asks for a bump when the contract changes, so both are taste. The request would be one sentence in the commit message claiming them.

## Item 3: boundaries, partitions, and the negative control

- **Genres without evidence** (substantive). The change claims three genres: commit body slot 2, PR description, and changelog part 3. The trial was "blind drafts of one pull request description", so the commit-body and changelog rules have no evidence.
- **Merge-model partition** (substantive). Under §4 rule 5 the description becomes the commit body, and reviewer-only content must stay out of it (`:267`, `:608-610`). The new rule `:461` says to keep a maintainer-only question "in the Scope slot". For a repository that squashes with "title and description", these two rules give opposite answers on the same input.
- **Earlier installed versions:** none. The package carries no persisted state; consumers get a new `SKILL.md`.

Added or widened instructions:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:475` changelog "for a defect an audit … found, the condition alone" | audit-found defect that the change's regression test reproduces with a literal error | condition only; the reproduced diagnostic R3 greps for is dropped | "unless a run reproduced it; then quote what it showed" |
| `:92` "name what found it and end the sentence there" | same reproduced defect | "A code reading found this."; slot 2 loses the observed failure | same clause, in slot 2 |
| `:342` "a sentence … recovered from one hunk is translation" | one-hunk behavioral fix (`:254` orphan-sync example) | What slot without the new behavior | "a sentence that states the new behavior at the caller's level stays" |
| `:458` "Where the code … answers it, give the answer and its evidence" | issue asks "does this cover the async path?"; the diff edits that path | "The async path is covered: AsyncExecutor is changed the same way" (translation, conflicts with `:342`) | "where the diff answers it on its face, leave it out" |
| `:461` "keep it in the Scope slot" | squash with "title and description" (§4 rule 5) | maintainer question frozen into `git log` | "; under §4 rule 5, in a pull request comment instead" |

Not findings:
- `:98` derived consequence: for a consequence no caller sees, the instruction is ended by `:94` "Where the defect has no symptom by construction … say so".
- `:370` alternative as a fact about the merged code: ended by "when a reviewer would propose it" (`:368`).
- `:288`: a narrowing, not an added instruction.

## Item 3a: level, placement, and the environment
None. Each rule sits in the slot section it governs, with a checklist line in §8, and the layout matches the siblings.
- `make check-descriptions` passed.
- `make check` failed once on `plugins[33]` (NiFi, an unrelated package; its values came back as `null`, apparently a fetch failure) and passed on a re-run at HEAD. It also passes at the base commit.
- The new prose lines stay within 120 characters.
- No sentence reads as a generic tutorial.

## Item 4: names by content, not by position
None. The references use the file's own numbered headings (`§2`, `§7`, "the What slot", "Slot 2") and checklist items by name. The `Leave` / `a question out` line break at `:463-464` only looks odd in the source and reads fine.

## Item 5: the failure report
Analogue: what the checklist tells the reader to look at, and whether that detects the rule.

- **Translation checklist is weaker than its rule** (`:826`, substantive). "Delete each sentence … where the diff still says it" keeps any sentence that has a reason in front of it, because the diff does not say the reason. The rule at `:343` says such a sentence is translation anyway. This is the failure that "persists in about one draft in two". The request: test clause by clause and keep the reason.
- **The same checklist drops the exception** (substantive). A sentence naming an added or renamed public identifier is in the diff, so the checklist deletes it, against the exception at `:345-347`.
- **None** for the remaining rules: Symptom, Alternatives, Discussion, and the Scope row each have a checklist line that detects them.

## Item 6: what the writer says it verified
- **Stated:** counts from about fifteen blind Opus drafts for the bad cases (symptom 2/2 → 5/10 → 0/2; retold obstacle 2/4 → 0/4; open question 3/3 → 0/4; translation reduced but still about 1 in 2).
- **Stated as not done:** the current open-question rule and the rewritten What-slot example were not re-run, and the drafts ran on 1.0.1.
- **Missing** (substantive):
  - No run of the final wording.
  - No input where an added item is noise, with a check that the output did not grow.
  - The drafts are not committed anywhere. `README.md:53` says the evidence "stays in the research directory", but `research/change-description-authoring/` has none of the new measurements.

## Item 7: siblings of the change
- **None for the listing surfaces:** README, `apm.yml`, `marketplace.json`, and the umbrella `qubership-repo-essentials` (relative dependency, no pin to bump). The description and trigger are unchanged, which is right because the scope did not widen.
- **None for `problem-report-authoring`:** it asks for an observed symptom for a different reader and has no rule on audit-found defects.
- **None for the set's old size:** no prose counts the checklist items.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Translation checklist keeps a hunk sentence that has a reason in front of it | Substantive | `SKILL.md:826` | Test clause by clause; keep the reason, delete the edit |
| Translation checklist deletes public identifiers that the rule exempts | Substantive | `SKILL.md:826` | Add the exception to the checklist line |
| What-slot *After* ends with a reason lead-in plus a hunk clause | Substantive | `SKILL.md:355` | End the sentence at the reason |
| Translation rule removes the behavioral change from a one-hunk fix (`:254` example) | Substantive | `SKILL.md:342` | Clause keeping caller-level behavior |
| Maintainer question in Scope conflicts with §4 rule 5 | Substantive | `SKILL.md:461` | "under §4 rule 5, in a PR comment instead" |
| Changelog and slot 2 drop a symptom that a regression test reproduced | Substantive | `SKILL.md:475`, `:92` | "unless a run reproduced it; quote what it showed" |
| Open-question answer duplicates what the diff shows | Substantive | `SKILL.md:458` | "where the diff answers it on its face, leave it out" |
| README bans derived consequences that the skill allows | Substantive | `README.md:29` | Mention the traced, derived-marked exception |
| Commit-body and changelog genres not exercised | Substantive | commit message | Run at least one draft of each |
| Final wording, noise control, and draft artifacts missing | Substantive | commit message; `README.md:53` | Re-run the final rules, add a noise input, and commit the drafts under `research/` |
| "No longer puts an outcome in prose" while the *After* says the caller "fails at once" | Taste | commit message; `SKILL.md:353` | Reword the claim or the sentence |
| Version bumps and README hunk not claimed by the message | Taste | `apm.yml`, `marketplace.json`, `README.md` | One sentence claiming them |

I did not check the wording for style alone, did not re-run any drafts or verify the trial counts, and did not fetch any cited source.
