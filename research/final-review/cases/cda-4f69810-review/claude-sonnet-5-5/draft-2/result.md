## Final review of `d79c43d..HEAD` (commit 4f69810)

**Inputs.** There is no separate task statement. The claimed cases come from the commit message alone. The package has no `tests/` or `research/` cases for this skill, and the commit message says so.

This change has no code: it edits a skill, a README, and manifests. I filled each item through the §2a analogues.

I did not use the drift script. I ran it, and it printed nothing because it does not parse Markdown or YAML.

I loaded `apm-authoring` and `english-developer-style` from the given directory. I did not load `test-authoring` because there are no tests.

**Gates run.** `scripts/check-skill-descriptions.py` passes. No added line exceeds 120 characters except table rows, which match the existing table style.

### Item 1: comments consistent with the code and with each other

The analogue is statements the files make about each other.

- The commit's claims about its own text check out:
  - §7 points to the What-slot rule.
  - §2 now asks for "what changed that the diff does not show".
  - The Symptom and Alternatives checklist items are extended, and the Discussion and Translation items are new.
  - The README summary matches the new rules.
  - The versions agree across the package `apm.yml`, the root `apm.yml`, and `marketplace.json` (1.4.0).
- **Finding A (substantive, `SKILL.md`, the What-slot *After* paragraph, around line 355).**
  - The new *After* contradicts the rule above it and the commit message. It says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is an outcome, and the text two lines below says an outcome goes on its own line under "User-visible changes". Line 218 also says a fact in slot 3 is not restated in slot 2.
  - The *After* then says "with the pool open from startup it sends directly". That is `Y now calls Z`, which the same section calls translation.
  - The commit message says the example "no longer puts an outcome in prose". The text says otherwise. `apm-authoring` says a rewritten rule that fails the change's own worked example is a finding, and that an example followed by a caveat teaches what the caveat forbids.
  - The paragraph "The removed `ensureOpen()` calls are gone from the text…" is such a caveat.
  - Request: make the *After* a pure reason, for example "Opening the pool at startup makes the on-demand reopen path dead, so `sendWithRetry` has no remaining purpose". Move the early-caller outcome to its line under "User-visible changes".
- **Finding B (taste, `SKILL.md:93-100` against `:475`).**
  - For a defect found by an audit, the changelog row says "the condition alone". The slot 2 text allows a traced, derived consequence, in its separate paragraph.
  - The two read differently for an audit-found defect whose consequence was traced to a caller. My preference: say in the changelog row that the derived consequence is allowed when traced.
- **Finding C (taste, `SKILL.md` near line 463).** The Discussion rule has a stray wrap, "Leave" alone on a line. It is harmless, and the rule can be reflowed.
- No change narrates itself (`now`, `no longer`) outside a *Before*/*After* label.

### Item 2: claimed cases covered

The analogue is the section or detection that handles each claim.

| Claim from the commit message | Where it is handled |
| --- | --- |
| Slot 2, audit or code-reading finding: name what found it | `:81`, `:91-96`, `:475`, checklist `:803-806` |
| Changelog names the condition alone | `:475` |
| Derived consequence traced to the caller and marked as derived | `:98-101`, checklist |
| "Say so" kept for a defect with no symptom by construction | `:94-96` |
| What slot: hunk translation, plus the identifier exception | `:342-359`, new Translation checklist item, `:763` |
| Rejected alternative stated as a fact about the merged code | `:369-373`, Alternatives item |
| Open question answered, or kept in Scope with its evidence | Scope table row, `:458-465`, Discussion item |
| Bad and good examples for the slot 2 and What rules | Both present (see Finding A for the What example) |

- **Finding D (substantive, no file line).**
  - The "measured" figures are in the skill text: "two of two drafts", "three of three drafts". They cannot be checked from the repository because the drafts are not stored. The commit message also says the final open-question rule and the What-slot example were not re-run.
  - The commit's totals do not reconcile. The symptom counts add to 14 drafts (2 + 10 + 2), not "over fifteen".
  - Request: state in the commit or the description which drafts support each figure. Alternatively, cite the figures as measured against the earlier rule wording, as the commit message does.
- **Version bump.** The 1.3.0 to 1.4.0 bump is not claimed in the message. The previous commit bumped the same files the same way, and `marketplace.json` carries it. I treated it as the change's own output and did not file it.
- No command line is added or edited.

### Item 3: boundaries, partitions, and the negative control

The analogues are the partitions the change claims and the table of added instructions.

- **Partitions claimed.**
  - Audit-found defect with no symptom, with the commit's trial evidence: two drafts, final wording.
  - Retold obstacle: four drafts.
  - Open question the code answered: four drafts, run against the earlier rule.
  - The open question only a maintainer can settle was never run, and the commit says so.
  - The changelog partition and the commit-body partition were not run. The drafts were pull request descriptions.
- **Added instructions: 6.** The six are the audit-found rule, the derived-consequence rule, the translation rule, the rejected-alternative rule, the open-question rule, and the checklist lines that restate them.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:91` "Where reading the code or an audit found the defect, name what found it and end the sentence there" | A defect a user reported with a stack trace, and a maintainer also found the cause by reading the code | Names the code reading and omits the reported exception text, though slot 2 says to quote the diagnostic | "only where no one observed the failure" |
| `:342` translation rule, with the checklist "delete each sentence of the What slot in turn" | A one-hunk fix whose What slot is two sentences | Deletes both sentences, since each is recoverable from the hunk, and leaves no What slot, which has no skip condition | "only where the sentence gives no reason for the behavior" |

Not findings: `:98`, `:369`, `:458`.

- **Upgrade state (pre-existing).** Consumers who have a 1.3.0 copy installed meet the same files, so there is no new state to test.

### Item 3a: level, placement, and the environment

The analogue is where each rule lives and the registration entries.

- The rules sit in the sections that own them.
- The registrations are consistent: the package `apm.yml`, the root `apm.yml`, and `marketplace.json` all say 1.4.0, and the description strings are unchanged.
- The offline gate `scripts/check-skill-descriptions.py` passes.
- I did not run the marketplace validation workflow, because it needs `apm` through `uvx`.
- Nothing here has no level (no tutorial-grade sentences).

### Item 4: names by content, not by position

None. The new text refers to rules by section number and by slot name. A slot is also a named heading, such as "the What slot".

### Item 5: the failure report

The analogue is the detection each rule gives the reader.

- Each new rule has a checklist item that detects the rule, not a weaker property:
  - **Translation:** "delete each sentence in turn" detects exactly the rule.
  - **Symptom:** now checks the observed-or-traced property.
  - **Discussion:** checks the answer-or-keep-open property.
- None found.

### Item 6: what the writer says it verified

- The commit message gives the red-and-green evidence: drafts without the rule predicted a failure, and drafts with the final wording did not.
- It also admits two unverified pieces: the current open-question rule and the What-slot example.
- Finding A shows that the unverified *After* is the part that fails its own rule.
- See Finding D for the figures.

### Item 7: siblings of the change

- **Same-named slot in the commit body.** The PR-description Why slot (`:195`, "the problem, the symptom, the condition") has no audit-found carve-out. It inherits it through `:218`, "slots 1 and 2 are the commit body's slots 1 to 3". This is taste and I did not file it as a finding.
- **Set size.** No member was added to a set, so no count in the prose is stale.
- **Other surfaces that mention the changed rule.**
  - The instruction file and `references/merge-model.md` do not mention the changed rules (grep for symptom, say so, and open question found nothing).
  - The README is updated.
  - `research/change-description-authoring/` has no case for the new rules, which the commit states.

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The What-slot *After* states an outcome in prose and a `now calls Z` sentence, against the rule above it and the commit message | Substantive | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md:~355` | 1 |
| The "measured" figures cannot be checked, and the commit's draft totals do not reconcile | Substantive | `SKILL.md:100`, `:464`, commit message | 2 |
| The slot 2 rule fires on a defect that was also observed and reported | Substantive | `SKILL.md:91` | 3 |
| The translation checklist deletes the whole What slot of a one-hunk fix | Substantive | `SKILL.md:~828` | 3 |
| The changelog row says "condition alone" while slot 2 allows a traced consequence | Taste | `SKILL.md:475` | 1 |
| Stray line wrap ("Leave" alone on a line) | Taste | `SKILL.md:~463` | 1 |

Every check could be done. I did not run the marketplace workflow, which needs `uvx` and the network.
