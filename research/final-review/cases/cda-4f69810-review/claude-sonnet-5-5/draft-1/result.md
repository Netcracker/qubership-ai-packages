# Final review: `d79c43d..HEAD` (4f69810)

**Inputs.**
- **Task statement:** none was handed over, so I took the claimed cases from the commit message, as the skill allows. The report relies on that message alone.
- **Previous report:** none.
- **Change type:** all five files are skill, README, or manifest text. This is the §2a "no code" form.
- **Drift script:** not run, because there are no members to parse.
- **Skills loaded:** `apm-authoring` and `english-developer-style`, from the given directory.
- **Gate:** `check-skill-descriptions.py` passes. `marketplace.json`, `apm.yml`, and the package `apm.yml` all say 1.4.0. I did not run `apm pack --check` because it needs `uvx`.

**Claims in the commit message**
- Slot 2 audit and code-reading rule, with a bad and a good example.
- Derived consequences traced to the caller and marked as derived.
- "Say so" kept for a defect with no symptom by construction.
- A changelog entry for such a defect names the condition alone.
- What slot: translation rule with an example, the identifier exception, a §7 pointer, and the "what changed that the diff does not show" wording.
- Rejected alternatives stated as facts about the merged code.
- Open-question rule.
- New checklist items Discussion and Translation, and extended Symptom and Alternatives items.

## Item 1: Comments consistent with the code and with each other

*Analogue used: every statement the changed files make about each other.*

Checked and holding:
- The §7 pointer "(§2, the What slot)" resolves.
- The checklist's "(§2, §3)" and "(§2, slot 2)" references resolve.
- The "§5" identifier cross-reference is supported by `SKILL.md:523` and `:683`.
- The version is 1.4.0 in all three manifests.
- Every other "no symptom" mention in the repo is unrelated.

**Finding 1.1 (substantive): the Translation checklist item contradicts the identifier exception.**
- `SKILL.md:826` says "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted".
- `SKILL.md:345` says a public identifier the change adds, removes, or renames is named once, "because readers search for the change by that string".
- A sentence naming a renamed system property is recoverable from the diff. The checklist, which the drafting agents said they check against, deletes it, and the rule asks for it.
- Request: add "except a public identifier the change adds, removes, or renames (§5)" to the checklist line.

**Finding 1.2 (substantive): the translation worked example fails its own rule and the commit's claim.**
- The *After* at `SKILL.md:353` ends "with the pool open from startup it sends directly". `QueryExecutor.execute now uses sendDirect` is the very hunk-recoverable sentence the rule calls translation. Run the Translation check on this example and it does not pass.
- Its first sentence puts an outcome in prose: "a caller that runs before startup completes fails at once instead of opening the pool on demand". The paragraph at `:357` then says that outcome belongs on its own line under "User-visible changes".
- The commit message says the example "no longer puts an outcome in prose".
- Request: cut the clause "it sends directly", and either remove the outcome from the prose or drop the claim.
- Related, taste: the paragraph at `:357` that explains what was cut is an example followed by a caveat (`apm-authoring` rule 2). The example should stand alone.

## Item 2: Claimed cases covered

*Analogue used: claimed case → section that handles it, plus the detection a reader has.*

| Claim | Section |
| --- | --- |
| Audit or code-reading defect | `:81`, `:92`, `:475`, checklist Symptom |
| Derived consequence | `:99`, checklist Symptom |
| No symptom by construction | `:94` |
| Translation | `:341`, checklist `:826` |
| Alternatives as facts about merged code | `:368`, checklist Alternatives |
| Open questions | `:458`, `:197`, checklist Discussion |

- Every claim has a rule and a checklist item.
- No command line is added.
- Unclaimed hunks: none. The README bullet and the version bumps are claimed by the message.
- Claims in the README: "its reason stays" and "A sentence ... is cut even when it carries a decision" match `:341`. Neither mentions the identifier exception. That is the same omission as 1.1, in a prose summary, so I did not refile it.

## Item 3: Boundaries, partitions, and the negative control

*Analogue used: the table of added instructions. The package installed over an earlier version needs no state migration, because it is text.*

**Added instructions: 6.** These are the slot 2 audit rule, the derived-consequence rule, the translation rule with the identifier exception, the alternatives-mechanism rule, the open-question rule, and the checklist items that restate them.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:81`, `:475` "for a defect an audit or a code reading found, the body names what found it" / "the condition alone" | A defect found by reading code after a user's report, with a quoted exception | The changelog entry drops the exception text R3 greps; the commit body says only that a code reading found it | "only where no symptom has been observed" |

Not findings: `:99`, `:341` (a one-hunk change leaves a reason-only What slot, which the rule asks for), `:368` (its own clause checks the mechanism against the code after the change), `:458` (the Scope slot is already absent from a description that becomes a commit body, `:823`).

**Finding 3.1 (substantive): the audit rule has no condition for an observed symptom.**
- A code reading triggers it, and reading code after a bug report is the common case.
- The row above shows the result: the changelog's symptom part is dropped even where a diagnostic was observed.
- Request: add the ending condition to `:81` and `:475` ("only where no symptom has been observed").

**Partitions without evidence.**
- Two partitions have no trial, and the commit says so. They are the maintainer-only open question and the What-slot example as it now reads. Those two rules are untested.
- The README and the skill both cite the "measured" counts, but no trial files exist under `research/` to check them against.

## Item 3a: Level, placement, and the environment

*Analogue used: file placement and registration.*
- The rules sit in the existing sections. The README bullets and the manifest entries follow their siblings.
- The description gate passes.
- `SKILL.md:462-463` has a stray line break that leaves "Leave" alone on a line. This is cosmetic and I filed no finding.

## Item 4: Names by content, not by position

*Analogue used: the change's own headings and cross-references.*
- Cross-references are by section number and slot name, not by ordinal.
- The "slot 2" and "slot 3" references follow the existing convention in this file.
- None.

## Item 5: The failure report

*Analogue used: detections reached by the checklist.*
- Each new rule has a checklist item. Symptom, Alternatives, Discussion, and Translation cover them all.
- Detection mismatch: the Translation item (`:826`) detects the translation rule without its exception. That is the weaker property, and it is Finding 1.1.
- The audit rule's detection ("does the sentence end at what found it?") cannot tell the observed-symptom case from the audit-only case. That is Finding 3.1.

## Item 6: What the writer says it verified

*Analogue used: exemplar passes and bad case fails.*
- The commit states blind-draft counts over about fifteen Opus drafts, with the version tested (1.0.1).
- The final What-slot example and open-question wording were not re-run, and the message says so.
- The rewrite check applies. The new worked example fails the new Translation rule (Finding 1.2).
- No drafts are stored in the repo.

## Item 7: Siblings of the change

*Analogue used: places that enumerate or route to the artifact.*
- Version sets: the package `apm.yml`, root `apm.yml`, and `marketplace.json` all moved.
- `AGENTS.md` and `CLAUDE.md` are not in this repo for this package.
- The trigger instruction file did not need to change.
- Sibling package READMEs only link to the skill.
- Prose that still counts the old set: none found.
- The PR Why slot (`:197`) does not point to the new slot 2 audit rule. Slot 1 and 2 of the description are defined as the commit body's slots 1 to 3, so it inherits the rule. This is taste, and I do not request it.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The Translation checklist deletes the identifier sentence the rule says to keep | Substantive | `SKILL.md:826` (rule at `:345`) | 1 |
| The translation example's *After* still contains a hunk-recoverable clause and an outcome in prose, against the commit's claim | Substantive | `SKILL.md:353` | 1 |
| The audit and code-reading rule has no condition for an observed symptom, so the changelog drops the diagnostic | Substantive | `SKILL.md:81`, `:475` | 3 |
| The explanatory paragraph after the translation example is a caveat after an example | Taste | `SKILL.md:357` | 1 |

No check was skipped. The drift script did not apply, and I could not run `apm pack --check` offline.
