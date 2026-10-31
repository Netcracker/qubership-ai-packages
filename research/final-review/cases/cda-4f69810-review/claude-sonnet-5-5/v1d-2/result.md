# Final review: `d79c43d..HEAD` (commit 4f69810)

**Inputs.** There was no separate task statement, so the claimed cases come from the commit message alone. The change is a skill (`SKILL.md`), a README, two version manifests and a marketplace entry, so I used the no-code form (§2a). I did not run `comment-drift.py` on it: it parses members, and it returned nothing, as expected for Markdown. I loaded `final-review` and `english-developer-style`. I did not load `apm-authoring`, because the task limited me to the three skills provided. Rule citations to it are therefore missing.

## Item 1: comments consistent with the code and with each other
Analogue: each statement the changed files make about each other or about the repository.

- **Version.** `none`. The bump 1.3.0 to 1.4.0 appears in `agent-packages/change-description-authoring/apm.yml`, `apm.yml:168` and `.claude-plugin/marketplace.json:291`. The other 1.3.0 hits belong to other packages.
- **Cross-references.** `none`. `(§5)` for public identifiers resolves, `§3 argues the order` still resolves, and `(§2, the What slot)` from the §7 checklist resolves.
- **Finding 1 (substantive).** The new "What" example's *After* says "a caller that runs before startup completes fails at once instead of opening the pool on demand" (SKILL.md, PR "What" example, around line 355). That is a caller-visible outcome in prose. The same paragraph then sends the `IllegalStateException` to "User-visible changes", and slot 3 says "A fact stated in slot 3 is not restated in slot 2". The commit message says the example "no longer puts an outcome in prose", which is false.
- **Finding 2 (substantive).** The *After* ends "`QueryExecutor.execute` used `sendWithRetry` only to reopen a closed pool; with the pool open from startup it sends directly." Its second half is the `Y now calls Z` shape the new rule calls translation. The new Translation checklist item ("delete each sentence … where the diff still says it, leave it deleted") would delete it, so the exemplar fails its own rule. Only the reason clause is the part the diff doesn't show.
- **Finding 3 (substantive).** The changelog row says "(§2, slot 2)". In §2, "slot 2" is the commit body's Impact slot, but the pull request description table in the same section also has a slot 2 ("What"), so the reference is ambiguous. Say "commit body, slot 2".
- **Finding 4 (taste).** The Scope rule wraps to a stub line (`wanted. Leave` / `a question out…`), which looks like a reflow miss.
- **Narration.** `none`. No "now", "no longer" or "used to" sits outside example text.

## Item 2: claimed cases covered
Claims taken from the commit message only. Detection means a reader can tell whether a text obeys the rule.

| Claim | Section that handles it | Detection |
| --- | --- | --- |
| Audit or code-reading defect: name what found it and stop | Slot 2 text, Slot 2 table row, changelog row 3 | Checklist "Symptom" |
| No predicted failure unless traced, marked as derived | Paragraph after slot 2 | Checklist "Symptom" |
| No symptom by construction: say so | Slot 2 text | Checklist "Symptom" |
| Hunk translation cut, public identifier named once | PR description, What slot | Checklist "Translation" |
| Rejected alternative is a fact about the merged code, not an obstacle the change removes | Rejected-alternatives paragraph | Checklist "Alternatives" |
| Open question: answered, kept in Scope, or dropped | Scope paragraph | Checklist "Discussion" |

- **Finding 5 (substantive).** The Translation checklist item has no exception for a public identifier the change adds, removes or renames, although §2 requires it to be named once. An agent following only the checklist, which the commit message says is how drafts are checked, deletes that sentence. Add "except a public identifier (§5)".
- **Commands.** `none`. The change tells nobody to run a command.
- **Hunks claimed.** Every hunk belongs to a sentence of the commit message, including the version bumps and the README bullets.

## Item 3: boundaries, partitions, and the negative control
Analogue: the partitions are the genres and situations the change claims, plus the table of added instructions.

- **Finding 6 (substantive).** The commit message reports measured results that no file in the repository records. Those are the fifteen drafts, "five of ten", "none of two" and "two of four to none of four". It also says the skill has no cases under `research/`, although `research/change-description-authoring/` exists. The "(measured: two of two drafts …)" claim now sits in the skill itself, where nobody can check it. Either add the drafts to `research/` or drop the figure from the skill text.
- **Partitions.** The pull request (PR) description's Why slot still says "the symptom" and does not carry the audit rule, which lives only in the commit body's slot 2. The checklist covers both, so I'm not raising a finding.
- **State left by the earlier version.** `none`. This is a prose package, and there is no persisted state.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A defect with a user-reported symptom that was also confirmed by an audit | Possibly drops the reported symptom and the quoted diagnostic, leaving only "An audit found this" | The text says "found" and "end there", which could be read as the whole of slot 2. Add "and the symptom, where one was reported, still goes first". |
| "A consequence derived from the code earns a sentence only after it is traced to … a caller" | A trivial change (a rename) with no consequence | Nothing, because the rule is conditional on a consequence being written | The condition "only after it is traced" ends it. Not a finding. |
| "A sentence … recovered from one hunk is translation" | A one-line fix whose description is a single sentence | May delete the only sentence | "Delete each sentence in turn" on a one-sentence What slot empties it. Add "only where the What slot has other content". |
| "A question … is answered, kept open, or left out" | A discussion with no open question | Possibly invents a "Questions" paragraph | No condition. The rule opens with "A question the issue or the review left open", so it only fires when one exists. Not a finding. |

- **Finding 7 (substantive).** Two rows above are noise cases with no ending clause: the audit-plus-reported-symptom row, and the Translation item on a one-sentence description. The requested clauses are given in the table.

## Item 3a: level, placement, and the environment
`none`. The files sit beside the sibling packages. `scripts/check-skill-descriptions.py` passes (27 descriptions within the limit), and `marketplace.json` parses. I did not run `apm pack --check`, because it needs the `apm` tool.

## Item 4: names by content, not by position
`none`. I found no ordinal names in the added text, apart from "slot 2" and "slot 3", which are fixed table indices.

## Item 5: the failure report
`none`. There are no assertions. Each added checklist item states what to look at.

## Item 6: what the writer says it verified
The commit message states blind-draft counts for the symptom, obstacle and question rules. It says outright that the current open-question rule and the What-slot example were not re-run. The example is the part Findings 1 and 2 show failing its own rule. No bad case is named for the changelog row. The commit message states no check that the instructions leave output unchanged where they don't apply (the noise inputs in the table above).

## Item 7: siblings of the change
- The set "slots" and "checklist items" gained members (Translation and Discussion). `git grep -n "checklist"` shows no count of items.
- The README bullet text matches the skill.
- Siblings of the audit rule: the PR Why slot (row 1) and the §7b comparison text do not mention it. This is a taste-level gap, not a request.
- The `marketplace.json` and `apm.yml` entries carry the same description, which is unchanged. Does the description frontmatter need to mention the new rules? No, it lists areas, not rules.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The example's *After* puts an outcome in prose, contradicting slot 3 and the commit message | Substantive | `SKILL.md`, PR What example (around line 355) | Remove "fails at once instead of opening the pool on demand", or move it to the outcome line only |
| 2 | The example's last sentence ("it sends directly") is hunk translation, so the exemplar fails its own rule | Substantive | same | Keep only the reason clause, or pick a sentence the diff doesn't show |
| 3 | "(§2, slot 2)" is ambiguous with the PR description's slot 2 | Substantive | `SKILL.md:475` | Write "commit body, slot 2" |
| 4 | The wrapped stub line ("wanted. Leave") | Taste | `SKILL.md`, Scope paragraph | Reflow |
| 5 | The Translation checklist item lacks the public-identifier exception | Substantive | `SKILL.md`, §8 | Add "except a public identifier (§5)" |
| 6 | The measured claims have no recorded evidence; the commit message's "no cases under `research/`" is doubtful | Substantive | commit message, `SKILL.md` ("measured: two of two") | Record the drafts under `research/`, or remove the figures |
| 7 | Two instructions have no ending clause for their noise input | Substantive | `SKILL.md`, slot 2 and §8 Translation | Add the clauses from the table |

This review did not run `apm pack --check`. It did not re-run the blind drafts, and it did not pass over the prose for style alone. I did not load `apm-authoring`, and I did not check the commit message's draft counts against anything, since no record of them exists.
