# Final review: `d79c43d..4f69810` (change-description-authoring 1.4.0)

**Inputs.** The change has no code, so I used the §2a analogues under every item. There was no task statement, so item 2 is answered from the commit message alone. There is no previous report. I loaded `apm-authoring` and `english-developer-style` from the given skills directory. I did not run the drift script, because the change touches only a skill, a README and manifests. I ran the repository's description gate, `scripts/check-skill-descriptions.py`, which passed (27 descriptions within 1020 characters).

## Item 1: comments consistent with the code and with each other

Analogue: statements one file makes about another, counts, repeated descriptions, and the skill's own rules against each other.

- **Version and registration, none.** 1.3.0 became 1.4.0 in `apm.yml` of the package, the root `apm.yml` and `marketplace.json`, which all agree. The skill's own description is unchanged and still covers the widened scope. No sentence counts the set as before.
- **Cross-references, none.** The `§2`, `§3`, `§5` and `§7` pointers resolve, and the new checklist items exist (lines 826 and 835-838).
- **Substantive: the checklist item is stricter than the rule it checks.** Line 826 says "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted", with no identifier exception. The rule at `SKILL.md:345-347` says a public identifier the change adds, removes or renames is named once. The commit message says drafts check against §8 and not against §2. An agent following the checklist deletes the sentence that names the flag or property, which is the sentence the rule keeps.
- **Substantive: the What-slot example contradicts its own commit-message claim.** The commit says the example "no longer puts an outcome in prose". The *After* at `SKILL.md:357-358` still puts it there ("a caller that runs before startup completes fails at once instead of opening the pool on demand"). The paragraph after it (359-360) says that outcome belongs on its own `User-visible changes` line.
- **Substantive: the *After*'s second sentence fails the new Translation check.** "with the pool open from startup it sends directly" is the `sendDirect` hunk restated. The *After* therefore fails the rule it illustrates.
- **Taste: conflicting rationale.** Line 346 justifies the identifier exception with "readers search for the change by that string". Line 363 says "Being searchable does not make a value necessary". The two cover different things (identifiers versus values), but the reasons read as opposed. I would drop the searchability rationale from 346 and cite §5.
- **Taste: slot 2 sentence order.** "neither is the absence of one" (94) sits directly before "a stated absence does not [look like an omission]" (96). The by-construction distinction does resolve it, but the two read close together.
- **Churn, not reported:** the ragged line wrap at `SKILL.md:463-464` ("wanted. Leave / a question out").

## Item 2: claimed cases covered

The claims come from the commit message only.

| Claim | Where it lands |
| --- | --- |
| Slot 2 audit rule, with a bad and a good example | `SKILL.md:91-96` |
| Derived consequence traced to a caller and marked as derived | `SKILL.md:98-101` |
| Changelog entry names the condition alone for an audit-found defect | row 3 |
| What-slot translation rule, identifier exception, bad and good example | `SKILL.md:343-360` |
| Rejected alternative is a fact about the merged code | `SKILL.md:369-372` |
| Open-question rule | `SKILL.md:458-465` and the Scope row |
| §7 points to the translation rule | `SKILL.md:763` |
| §2 asks for "what changed that the diff does not show" | `SKILL.md:285` |
| Checklist: Symptom, Alternatives, Discussion, Translation | `SKILL.md:803-806, 826, 835-838` |

- **Commands the change tells someone to run:** none.
- **Hunks no sentence claims:** none. The README hunk and the version bumps belong to the "stop drafts from…" claims.
- **Measured claims:** the figures in the commit ("over fifteen drafts", "two of two", "three of three", "none of four") have no case under `research/change-description-authoring/`, and the commit says so. I could not check them. The commit's arithmetic for the symptom rule adds to 14 drafts, not "over fifteen"; the others may overlap.

## Item 3: boundaries, partitions, and the negative control

**Added instructions: 5.**
- Slot 2 audit rule, with the changelog row.
- Derived-consequence rule.
- Translation rule, with the "what the diff does not show" wording.
- Rejected-alternative-as-fact rule.
- Open-question rule, with its Scope row.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:91` "name what found it and end the sentence there" | defect an audit found and a user then reproduced, with a log line | "An audit found this." and no diagnostic; the changelog row 475 drops it too, so the on-call reader has nothing to grep | "only where no failure has been observed" |
| `:461` "keep it in the Scope slot as a question" | a commit body, where `:823` says the Scope slot is absent | a Scope heading in a body that has none, or the question dropped | "in a commit body, put it as a closing sentence of the body" |

Not findings: `:98`, `:343` (the exception is a stated condition and the checklist gap is filed under item 1), `:369` (its condition is "where a reviewer would propose it").

**Partitions.** Both audit-found defects with an observed symptom and without one are partitions the change claims. Only the unobserved one has evidence, and that evidence is the drafts it describes. Pre-existing state: the skill ships as an update, and nothing on the target needs migrating.

## Item 3a: level, placement, and the environment

- The rules sit in the skill and the checklist, which is where siblings keep them.
- No instruction file changed.
- The gate passed (see Inputs).

## Item 4: names by content, not by position

None. The new headings and cross-references use `§2`, `§5` and slot names. This repository numbers its sections, so that is not an ordinal-position problem.

## Item 5: the failure report

- **Substantive: the Translation check's failure report is weaker than its rule.** The check ("where the diff still says it, leave it deleted") has no way to detect the identifier exception. The *Before* and *After* are the rule's only detection. The *After* fails it, as filed under item 1.
- **Other checks:** the Symptom, Alternatives and Discussion checklist items detect what their rules state.

## Item 6: what the writer says it verified

The commit states what was and was not run. Drafts ran against 1.0.1, before the outcome slot and length rules. The current open-question rule and the What-slot example were not re-run. Translation still occurs in about one draft in two, so the rule is not shown to work. There is no exemplar-pass and bad-case-fail pair for the new rules. Applying the Translation rule to the change's own worked example, the *After* fails it (item 1). No input was run where the added items are noise, such as a non-audit fix or a change with no discussion, to check that the output did not grow.

## Item 7: siblings of the change

- **Places that list the package:** root `apm.yml`, `marketplace.json`, the README, the umbrella `qubership-repo-essentials` (it uses a relative path, so no pin), and the pointer lists in the `english-developer-style` copies. All need no change.
- **Other mentions of the old rule:** the "symptom dropped" finding at `SKILL.md:794` and the Why-slot description (195) still describe a symptom without the audit exception. The changelog row got the exception and these two did not. Taste.
- **Count sentences:** none still count the set as before.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Translation checklist lacks the identifier exception | Substantive | `SKILL.md:826` | Add "except a public identifier the change adds, removes or renames" |
| *After* puts an outcome in prose and restates the `sendDirect` hunk | Substantive | `SKILL.md:357-358` | Drop "fails at once…" and "it sends directly"; keep the reason; align the commit-message claim |
| Audit rule drops the diagnostic when a symptom was observed | Substantive | `SKILL.md:91`, `475` | Add "where no failure has been observed" |
| Maintainer-question rule has no home in a commit body | Substantive | `SKILL.md:461`, `823` | Say where it goes when the Scope slot is absent |
| Searchability rationale vs line 363 | Taste | `SKILL.md:346` | Cite §5 instead of "readers search" |
| Audit exception missing from the Why-slot row and from line 794 | Taste | `SKILL.md:195`, `794` | Add one clause to each |

I did not run the suite or the research cases. I did not check the draft-count figures, and I did not do a style pass over the prose.
