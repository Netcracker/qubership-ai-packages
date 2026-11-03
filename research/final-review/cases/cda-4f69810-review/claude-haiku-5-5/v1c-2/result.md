## Final review of 4f69810

**Scope and inputs.** The range `d79c43d..HEAD` is one commit, `4f69810`, which changes only the `change-description-authoring` skill, its README, and the version in three manifests. Its commit message is the only claim source, since no task statement was handed over and the change has no tests. The change has no code, so §2a's analogues apply under every item. I loaded `english-developer-style` from the skills folder. For the authoring skill I used the repo copy at `agent-packages/apm-authoring/.apm/skills/apm-authoring/SKILL.md`, because it is not one of the three named copies. I read its rules 1 and 2 and its Versions section. The rule "Fix a bad output where the rule stops" is not in that copy, so the §2a table uses the wording of final-review. I did not load `test-authoring`, since no tests changed. I ran the drift script; it printed nothing because the change has no members. There is no previous report, so there is no §4 table.

### Item 1: comments consistent with the code and with each other
Analogue: the skill's statements about other files, sections, and its own commit claims. The cross-references resolve: §5 is the identifiers section, §7 holds the "same test" sentence, and "(§2, slot 2)" and "(§2, §3)" point where they say. The README bullets match the SKILL text. One statement is contradicted, the commit's claim that the What example "no longer puts an outcome in prose" (see F5). Result: one finding.

### Item 2: claimed cases covered
Analogue: each claimed rule against its detection in the §8 checklist.
- Slot 2, audit or reading found the defect: Symptom item, covered.
- Derived consequence traced and marked: Symptom item, covered.
- "Say so" for no symptom by construction: Symptom item, covered.
- What-slot translation rule: Translation item, but the public-identifier exception is missing (F1).
- Rejected alternative stated as a fact about the merged code: Alternatives item, covered.
- Open questions answered, kept in Scope, or dropped: Discussion item, covered.
- Changelog entry names the condition alone: no changelog item carries it; the existing changelog checklist still requires a symptom (F2).
- Hunks against claims: the version bump in three files and the README bullets are claimed by no sentence of the commit message (F4).
- Commands the change tells a reader to run: none in the changed hunks, so none.

### Item 3: boundaries, partitions, and the negative control
Partition: the defect kinds are "observed by a report", "found by audit or reading", and "no symptom by construction". The overlap of the first two, a defect a report shows and a reading also explains, is not covered (F3). Negative control: the table of added instructions:

| Instruction (quoted) | Input it does not serve | What the agent writes | Clause that ends it |
| --- | --- | --- | --- |
| "Where reading the code or an audit found the defect, name what found it and end the sentence there" (:91–92) | A defect a report shows and a code reading also explains | "A code reading of the retry path found this." The trigger the report gives is dropped. | "Where a report or log shows the symptom, quote it; this sentence serves a defect no report shows" (F3) |
| "for a defect an audit or a code reading found, the condition alone" (changelog row 3, :475) | Same input, in a changelog | The condition alone; the literal the on-call reader greps for is gone | Same clause (F3) |
| "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" (:826) | A new public flag | The sentence naming the flag is deleted, so the flag appears nowhere in the description | "unless a public identifier the change adds, removes, or renames, named once" (F1) |
| "symptom" in the changelog checklist (:842) | An audit-found defect | Requires a symptom the changelog rule no longer asks for | Same clause as F1 (F2) |
| "A consequence derived from the code earns a sentence only after it is traced…" (:98–101) | A derived consequence no caller sees | No sentence | Ended by its own condition; not a finding |

### Item 3a: level, placement, and the environment
The offline gate `make check-descriptions` passes: all 27 skill descriptions are within 1020 characters. The package-version gate, `apm pack --check-versions --check-clean`, needs `uvx` and the network, so I did not run it. By reading, the version is 1.4.0 in `agent-packages/change-description-authoring/apm.yml`, `apm.yml`, and `.claude-plugin/marketplace.json`. The rules sit in the right sections.

### Item 4: names by content, not by position
One finding (T2): the new changelog cross-reference "(§2, slot 2)" is positional, while the slot has a name.

### Item 5: the failure report
Analogue: each rule's detection must detect that rule. The Translation detection flags the exception-covered public identifier (F1), and the changelog detection requires a symptom where the rule does not (F2). No others.

### Item 6: what the writer says it verified
The commit states its evidence: fifteen blind drafts, with per-rule counts. It also discloses that the open-question rule and the What example were not re-run on the final text. Applying the rewritten What rule to its own worked example fails it (F5). The open-question rule has no run on the final text (F6).

### Item 7: siblings of the change
- The README is the one sibling that restates the rules; it is updated.
- `change-description-authoring.instructions.md` only triggers the skill and states no rule.
- `references/merge-model.md` asks for a symptom in the commit body. The new "say so" rule still allows a stated absence, so this is consistent.
- The `docs-page-authoring`, `problem-report-authoring`, `test-authoring`, and `qubership-repo-essentials` packages cite only the package's ownership.
- No copies of the skill exist under `.claude/` or `.agents/`.
- No count of checklist items appears in prose.

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The Translation checklist has no public-identifier exception. A reader following it deletes the sentence naming a new flag, which the What rule says to keep once. | substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:826`; exception at :342–346 | Add "except a public identifier the change adds, removes, or renames, named once (§2, What)." |
| F2 | The changelog checklist requires a symptom, while changelog row 3 now asks for "the condition alone" for audit- or reading-found defects. | substantive | `SKILL.md:842`; `SKILL.md:475` | Add the same exception to the checklist line. |
| F3 | The slot-2 trigger has no case for a defect a report shows and a code reading also explains. "Name what found it and end the sentence there" drops the observed symptom that R3 greps for. The changelog row has the same problem. | substantive | `SKILL.md:90–93`; `SKILL.md:475` | Scope the rule to defects no report or log shows. Where a report shows the symptom, quote it and add the reading after it. |
| F4 | Two hunks are claimed by no sentence of the commit message: the version bump 1.3.0→1.4.0 in three files, and the README bullets. The three prior commits bumped the same files, so the bump follows the repo's practice. `apm-authoring`'s Versions rule says to bump only on a contract change, so the sentence should say why this change is one. | substantive | `.claude-plugin/marketplace.json:291`; `agent-packages/change-description-authoring/apm.yml:2`; `apm.yml:168`; `agent-packages/change-description-authoring/README.md:26–31` | Add a sentence to the commit message that claims the bump and the README summary, or move them to their own commit. |
| F5 | The What-slot worked example fails its own rule. "with the pool open from startup it sends directly" restates the hunk, the `Y now calls Z` shape the rule names. "fails at once" puts an outcome in prose, which contradicts the commit message's "no longer puts an outcome in prose." | substantive | `SKILL.md:353–355` | Cut the "sends directly" clause. Move "fails at once" to the User-visible line, or correct the commit message. |
| F6 | The open-question rule and the What example were not run on the final text, which the commit discloses. §2a requires the rewritten rules to be applied again. | substantive | commit message; `SKILL.md:335–355`, `:458–466` | Run the final text against blind drafts, and state the result. |
| T1 | The "Skip when" cell of the slot-2 row now holds a rule for audit-found defects. Read as a skip condition, it reads as an exception. | taste | `SKILL.md:81` | Move the sentence into the slot text at :90–93. |
| T2 | The changelog row cites "(§2, slot 2)", a positional reference where the slot has a name. | taste | `SKILL.md:475` | Cite "(§2, the impact and trigger slot)". |

**Not checked:** `apm pack --check-versions --check-clean` needs the network, so the version gate did not run. No drafts were re-run, so F6 stands as a request. The "Fix a bad output where the rule stops" rule that final-review cites is not in the repo copy of `apm-authoring`. No file was changed and nothing was committed.
