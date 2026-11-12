## Final review: `d79c43d..HEAD` (commit 4f69810)

**Scope.** The change edits a skill, its README, and three manifests. It has no code, so the drift script parses nothing here. Its empty output is not evidence. The claimed cases come from the commit message only; no task statement was handed over. No previous report exists.

**Skills.** `final-review` was read in full. `english-developer-style` was loaded from the given skills folder. `test-authoring` was not loaded because no test changed. The authoring skill for the package is `apm-authoring`, which has no copy in the given folder. I read only its rule headings and its versioning paragraph (`.claude/skills/apm-authoring/SKILL.md`), not the whole file.

**Gates, run offline.** `make check` exits 0 and `make check-descriptions` exits 0. The tree is still clean.

## Item 1: comments consistent with the code and with each other

Finding F1 and F6 below. The rest is consistent: the new slot 2 rule, the derived-consequence paragraph, the rejected-alternative paragraph, the Symptom, Alternatives, and Discussion checklist items, and the commit's own counts all agree with each other.

## Item 2: claimed cases covered

Each claim in the commit message has its sentence in the diff. The checklist items for Symptom, Alternatives, Discussion, and Translation exist. §7 has the sentence-by-sentence pointer (line 762), and §2 has the "what changed that the diff does not show" wording (line 287).

Hunks no sentence claims: the version bump, 1.3.0 to 1.4.0, in `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168`, and `.claude-plugin/marketplace.json:291`. The index gate may require the three edits together, but the body says nothing about it (F3).

Commands the change tells a reader to run: none.

## Item 3: boundaries, partitions, and the negative control

For a skill the control is the table below. Its boundary is the case of a defect that is both found by audit and observed (F1).

**§2a table, one row per instruction the change adds or widens:**

| Instruction | Input it fires on | What the agent writes | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Slot 2: audit or code reading found it (line 90) | An audit finds a defect that a user report also shows, with a logged diagnostic | `An audit of the retry paths found this.`, dropping the diagnostic | "end the sentence there" | Substantive, F1 |
| Slot 2: derived consequence (line 98) | A missing `close()` on an error path that only surfaces after retries | A derived failure, if traced through the retry; otherwise no sentence | "only after it is traced" | One line, ended by its own condition |
| What slot: translation (line 342) | A removed `flush()` with a stated reason | The reason only: `The buffer drains at close, so the explicit flush is redundant.` | "not the edit that carries it" | Served; the worked example fails it (F2) |
| What slot: public identifier (line 345) | A new system property that readers grep | The property, named once | "named once" | Served; the checklist does not check it (F4) |
| Rejected alternative (paragraph near line 369) | An alternative rejected because of a lock the change removes | No obstacle sentence; a mechanism of the merged code, or nothing | Slot 3: a rejected alternative "earns its sentence only where…" | One line, ended by slot 3 |
| Open question (line 458) | A question the code answers, and a maintainer-only question | The answer with evidence; or the question in Scope with its decision | "give the answer and its evidence"; "keep it in the Scope slot" | Served; no exemplar (F5) |

## Item 3a: level, placement, and the environment

The rules sit in the package's `SKILL.md`, with the README and manifests in step. The repository gate passes (see Gates above). No new file or layout is introduced.

## Item 4: names by content, not by position

Finding F6 (taste). The new changelog cell refers to `(§2, slot 2)` by ordinal.

## Item 5: the failure report

Every rule with a detection is reached by the checklist except the public-identifier exception. The Translation item's deletion test is also a weaker property than the rule states (F4).

## Item 6: what the writer says it verified

The writer states the evidence and says that the current open-question rule and the What-slot example were not re-run. Applying the What-slot rule to its own example fails it, which is F2. The open-question rule has no exemplar (F5).

## Item 7: siblings of the change

`git grep` finds no other copy of these rules in tracked files. The English-style changelog rule (`english-developer-style` §7) and the new changelog row agree except where a defect is both observed and found by audit, which is F1. The package README was updated with the rules.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | "Found by audit or code reading" ends the impact sentence and drops the observed diagnostic. A defect both observed and audited loses the string R3 greps. The Skip-when cell mixes a fill rule into a skip column. | Substantive | `SKILL.md:81`, `:90–92`, `:475` | Condition on "found, with no symptom observed". Move the fill rule out of the Skip-when cell. |
| F2 | The What-slot "After" example fails its own rule. "with the pool open from startup it sends directly" is the edit, recovered from the `sendDirect` hunk. | Substantive | `SKILL.md:352–355` | Delete that clause, keep the reason, and re-test the example against the rule. |
| F3 | The version bump is not claimed by any sentence. The index gate may require the three edits together, but the body does not say so. The repo's `apm-authoring` says to bump only on a contract change, not a prose edit. | Substantive | `agent-packages/change-description-authoring/apm.yml:2`, `apm.yml:168`, `.claude-plugin/marketplace.json:291` | Add a sentence to the body that claims the bump and says why it is a contract change, or drop the bump. |
| F4 | The Translation checklist item deletes every sentence the diff still says. It omits the public-identifier exception at `:345–347`, and it deletes whole reason-bearing sentences instead of the edit clause. | Substantive | `SKILL.md:826–827` | Add the exception. Say the edit clause goes, not the sentence. |
| F5 | The open-question rule has no bad-and-good pair. The writer says it was not re-run. | Substantive | `SKILL.md:458–466` | Add one bad case and one good case, as the slot 2 and What rules have. |
| F6 | The ordinal `slot 2` in the changelog row. | Taste (expect it declined) | `SKILL.md:475` | Name it "Impact and trigger". |

**Not checked:** the full `apm-authoring` skill; the test suite (`make test`); a red or mutation run of the rules; the English wording beyond what makes a sentence read wrongly, so no style pass was done.
