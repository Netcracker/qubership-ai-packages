# Final review: `d79c43d..4f69810`, one commit (change-description-authoring 1.4.0)

There was no task statement. The claimed cases come from the commit message alone. The change has no code: it edits a skill (`SKILL.md`), a package README, and three version entries. So this report uses the §2a analogues, and I loaded `apm-authoring` and `english-developer-style` in place of a doc-comment skill. The drift script ran and printed nothing, because it has no Markdown members to parse. No previous report exists.

`SKILL.md` below means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

Analogue used: every statement one file makes about another file or about the repository.

- **Substantive.** The checklist's Translation item (`SKILL.md:826`, "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted") contradicts the exception at `SKILL.md:345-347`. That exception says a public identifier the change adds, removes, or renames is named once, because readers search for it. The diff always shows a renamed flag, so an agent that checks against the checklist deletes the sentence §2 requires. The commit message says this is how drafting agents work: they check against §8. **Request:** add the exception to the item, for example "...leave it deleted, unless it names a public identifier the change adds, removes, or renames".
- **Substantive.** `README.md:28-30` says an audit-found defect is described "with neither a predicted failure nor a claim that none was seen". `SKILL.md:98-101` allows a consequence derived from the code, provided it is traced to what a caller sees and marked as derived. A reader of the README concludes no consequence may ever be stated. **Request:** add "unless traced to what a caller sees and marked as derived" to the README sentence.
- **Taste.** The commit message says the What-slot example "no longer puts an outcome in prose". But the *After* at `SKILL.md:353-354` says "a caller that runs before startup completes fails at once". That is the same caller-observable outcome that `SKILL.md:358-360` sends to "User-visible changes". The commit-body rule says "A fact in slot 4 is not also buried in slot 3's prose". It can also be read as the "new behavioral boundary" that the What slot carries (`SKILL.md:~318`). I prefer "...no longer opens the pool on demand" and leaving the failure to the outcome line.
- Other checks found nothing:
  - §7 now points to the What-slot rule (`:762`).
  - §2 asks for "what changed that the diff does not show" (`:288`).
  - The search claim at `:346-347` matches §5 (`:683-684`).
  - The table cell `:81` and the prose `:91-96` agree.
  - The rejected-alternative and open-question rules match their checklist items (`:830-838`).

## Item 2: claimed cases covered

Claimed cases come from the commit message alone. Each case, with the place that handles it and the place that detects it:

| Claimed case | Handled at | Detected at |
| --- | --- | --- |
| Audit or code-read defect: name what found it, end the sentence | `:81`, `:91-93` (Before/After) | checklist `:804-805` |
| Changelog entry: the condition alone | `:475` | none; see item 5 |
| Derived consequence traced and marked | `:98-101` | `:803-804` |
| "Say so" kept for a defect with no symptom by construction | `:94-96` | `:805-806` |
| What slot: one-hunk sentence is translation; public identifier named once | `:342-360` (Before/After) | `:826`, which conflicts with the identifier exception (item 1) |
| §7 points to the rule; §2 "does not show" | `:762`, `:288` | — |
| Rejected alternative: a fact about the merged code | `:370-373` | `:830-831` |
| Open questions: answered, kept in Scope, or dropped | `:199`, `:458-465` | `:835-838` |

The version bump to 1.4.0 in `apm.yml`, `agent-packages/change-description-authoring/apm.yml`, and `.claude-plugin/marketplace.json` is registration output. It follows the convention of the three earlier commits and needs no separate claim. No command lines were added. I found no unclaimed hunk.

## Item 3: boundaries, partitions, and the negative control

**Substantive: the trial covered one partition.** The commit says every trial draft was a description of one pull request about one audit-found defect. The change also claims these situations, none of which a draft exercised:
- a commit body;
- a changelog entry (the new "condition alone" rule at `:475`);
- a defect found by code reading rather than by audit;
- the control: a defect with an observed symptom, where the new slot 2 wording must not make the draft drop the diagnostic;
- a change whose discussion left no open question.

**Request:** a run on at least the observed-symptom control and on one changelog entry.

Added instructions: 6.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:92` "name what found it and end the sentence there" | code-read defect a regression test then reproduced, with an exception text | "A code reading found this."; the reproduced exception R3 greps is dropped | "unless a test or run reproduced it; then quote what it showed" |
| `:475` "the condition alone" for an audit-found defect | same reproduced defect, in the changelog | entry without the diagnostic literal the row's own R3 question asks for | "where no test or run reproduced it" |
| `:458` "Where the code … answers it, give the answer" | an answered question from the issue that does not bear on this change | an answer with evidence to an off-topic question | "Of a question that bears on this change, …" |

Not findings: `:98`, `:345`, `:370`.

## Item 3a: level, placement, and the environment

None. I checked these:
- Each rule sits in the section it governs: slot 2 prose, What-slot rules, Scope, the changelog table, and the checklist.
- The layout matches the sibling packages.
- `scripts/check-skill-descriptions.py` passed ("all 27 skill descriptions are within 1020 characters").
- The version is 1.4.0 in all three registration files.
- No new sentence reads as generic tutorial advice; each one carries a measured case.

## Item 4: names by content, not by position

**Taste.** `SKILL.md:357-358` says "the first sentence says why they are no longer needed". This points to the first sentence of the *After*; "the startup sentence" would name it by content. The two-sentence example sits right above it, so the risk is low.

## Item 5: the failure report

Analogue used: whether the checklist reaches each rule, and whether each detection checks the rule it is attached to.

- **Substantive.** No checklist item reaches the changelog rule at `:475`. The Changelog item (`:845-846`) checks only the order of the parts. The Symptom item (`:805`) asks whether "the sentence end[s] at what found it", which is the commit-body form. Applied to a changelog entry, it asks for the audit to be named, which `:475` excludes. **Request:** add a clause to the Changelog item, for example "for a defect found by an audit or a code reading, the condition alone (§2)".
- The Translation detection at `:826` deletes more than the rule allows. It is filed under item 1.
- The Translation detection says "where the diff still says it". The rule (`:342`) says "recovers from one hunk". This is close enough that I did not file it.

## Item 6: what the writer says it verified

The commit message gives counts from fifteen blind drafts. These covered:
- the symptom rule: 2 of 2 drafts predicted a failure, then 5 of 10 stated that none was seen, then 0 of 2;
- the retold obstacle: 2 of 4, then 0 of 4;
- the open question: 3 of 3, then 0 of 4;
- hunk translation: persists in about one draft in two.

It also says the current open-question rule and the What-slot example were not re-run. The drafts are not in the repository.

- **Substantive.** The commit message says "This skill has no cases under research/, so none were re-run". That is false. `research/change-description-authoring/phase3_result.md:402` ("## 11. Test of the rule set") holds six real public changes used to check that the slot tests discriminate. Its conclusion is about exactly the rule this change rewrites: "an absent symptom on a defect that has none, which the skill should let the author state". **Request:** re-run the slot 2 and changelog rules on those six samples, or correct the claim in the pull request description.
- **Substantive.** The commit adds instructions after bad outputs, but no run used an input where the added items are noise, with a check that the output did not grow. For example: a fix with an observed symptom, or a pull request with no open question and no rejected alternative. Hunk translation "persists in about one draft in two", so the What-slot rule has an exemplar it fails, and the commit says so. **Request:** one noise-input run, with its word count against 1.3.0.

## Item 7: siblings of the change

None. I checked these:
- The package README was updated.
- The marketplace and `apm.yml` descriptions are unchanged, and the scope did not widen.
- The umbrella `qubership-repo-essentials/apm.yml:10` pins the package by relative path, so no version needs updating there.
- `apm.lock.yaml` does not list the package.
- Packages that point to this one say only that it owns commit messages, PR descriptions, and changelogs: `english-*-developer-style`, `docs-page-authoring`, `problem-report-authoring`, `test-authoring`. They restate none of the changed rules.
- `english-*-developer-style` `:468` ("Verify the symptom… against the source") agrees with the new slot 2 rule.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Translation checklist deletes the public-identifier sentence §2 requires | Substantive | `SKILL.md:826` | 1 |
| README forbids any predicted failure; the skill allows a traced, derived one | Substantive | `README.md:28` | 1 |
| Trial covered one PR description; commit body, changelog, and observed-symptom control untested | Substantive | `SKILL.md:91` | 3 |
| Reproduced code-read defect loses its diagnostic | Substantive | `SKILL.md:92` (row) | 3 |
| Changelog "condition alone" drops a reproduced diagnostic | Substantive | `SKILL.md:475` (row) | 3 |
| Off-topic question answered | Substantive | `SKILL.md:458` (row) | 3 |
| No checklist item reaches the changelog audit rule; the Symptom item asks the opposite | Substantive | `SKILL.md:845` | 5 |
| "No cases under research/" is false; phase 3 §11 has six | Substantive | `research/change-description-authoring/phase3_result.md:402` | 6 |
| No noise-input run for the added instructions | Substantive | commit message | 6 |
| *After* still states the caller outcome in What prose | Taste | `SKILL.md:353` | 1 |
| "the first sentence" names the sentence by position | Taste | `SKILL.md:357` | 4 |

Two checks could not be done. The repository's gate `make check` (`apm pack --check-versions --check-clean`) needs `uvx` with network access, so it was not run; I checked by hand that the three version entries match. The drift script does not parse Markdown, so item 1 was done by reading.
