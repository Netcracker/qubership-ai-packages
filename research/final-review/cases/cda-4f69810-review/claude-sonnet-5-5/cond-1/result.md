I'm reviewing the commit as a no-code change, meaning a skill package. I read the diff, the `final-review` form, `apm-authoring` and `english-developer-style`, and searched the package for stale text. I changed no file and made no commit.

## Final review: `d79c43d..4f69810` (change-description-authoring 1.4.0)

**Inputs.**
- There is no separate task statement, so the claimed cases come from the commit message alone.
- There is no previous report for this change.
- This change has no code, so I used the §2a analogues under every item and did not run the drift script.
- I did not run `make check`, the repository's gate, because it needs `uvx` and the network. I compared the versions by hand instead.
- I did not run any command, so none of the items below rests on a run.

### Item 1: Comments consistent with the code and with each other

Analogue: every statement the changed files make about each other or about the repository.

- **Finding 1 (substantive).** `SKILL.md:~354-358` is the *After* example for the What slot. It contradicts the rule printed above it and the commit message.
  - Its first sentence states an outcome in prose: "a caller that runs before startup completes fails at once". The paragraph after the example says the early caller's `IllegalStateException` is an outcome that belongs on its own "User-visible changes" line.
  - The commit message says the example "no longer puts an outcome in prose". It still does.
  - Its second sentence, "with the pool open from startup it sends directly", is what the rule calls translation. The reviewer recovers it from the `sendWithRetry` to `sendDirect` hunk, and the rule says a lead-in stating a reason does not exempt it.
  - Request: make the *After* a reason only (for example, "The pool opens at startup, so no caller has to open it on demand"). Move the failure to the `User-visible` line the paragraph already points to. Cut or reduce the `sendDirect` sentence.
- **Finding 2 (taste).** `SKILL.md:81`, `:92-94`, and `:475` give the audit-found rule two forms.
  - The commit-body slot says only "names what found it", while the changelog row says "the condition alone".
  - I prefer one sentence saying whether the commit body also carries the trigger condition. A reader could take either reading.
- No narration of the change (`now`, `no longer`) appears outside the *Before/After* labels.
- The README addition matches the SKILL text.

### Item 2: Claimed cases covered

Analogue: each rule the commit message claims, matched to the section that holds it.

| Claim | Where it lives |
| --- | --- |
| Slot 2: audit or code-reading rule, with a bad and a good example | `:88-96` |
| Slot 2: derived consequence traced to what a caller sees and marked as derived | `:98-101` |
| Slot 2: "no symptom by construction" | `:81`, `:94` |
| Changelog entry names the condition alone | `:475` |
| What slot: hunk translation, with an example | `:339-359` |
| What slot: a public identifier is named once | `:344-347` |
| `§2` asks for "what changed that the diff does not show" | `:288` |
| `§7` points to the translation rule | `:763` (§7 is the "When to write nothing" section, which starts at `:754`) |
| Rejected alternative: mechanism stated as a fact about the merged code | `:368-` |
| Open questions: answer, keep in Scope, or drop | the Scope paragraph, plus the Scope cell of the table |
| Checklist: Symptom, Alternatives, Discussion, Translation | the checklist at `:800-840` |

- Every claimed hunk exists.
- No command line is added or edited.
- The version bump to 1.4.0 appears in `marketplace.json`, `agent-packages/change-description-authoring/apm.yml`, and the root `apm.yml`. The commit message does not mention it. It matches the pattern of `51b35c9` and the earlier commits, so I do not file it.
- `apm.lock.yaml` has no entry for this package.
- The README hunk is claimed through the rules it summarises.

### Item 3: Boundaries, partitions, and the negative control

Analogue: the claimed situations, and the table of added instructions.

- **Partitions:**
  - Defect with an observed symptom, found by audit, or with no symptom by construction.
  - Question answered by the code, only a maintainer can settle it, or does not bear on the change.
  - Each has a rule. Three have no worked input in the repository. These are the maintainer-only question, the changelog row, and the derived-consequence rule, which carries its own measurement but no example.
- **Pre-existing state:** this is a package update, and a consumer is already on 1.3.0. The rules contain no persisted state.

Added instructions: 7.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:~339` "sentence recoverable from one hunk is translation" and the *Translation* checklist item ("delete each sentence of the What slot in turn") | a one-hunk fix where Why already gives the reason | an empty What slot, or a What sentence repeating Why | "only where the diff has more than one hunk the reviewer must connect" |

Not findings: `:88-96`, `:98-101`, `:344-347`, `:368-`, and the open-question paragraph. Each states its own condition: the defect was found by an audit, the consequence is derived, the identifier is public, an alternative a reviewer would propose, the question was left open.

### Item 3a: Level, placement, and the environment

- All rules sit in the existing `SKILL.md`, the README and the three version fields, which matches the layout of earlier commits.
- The three versions agree by hand check, but I did not run the gate.
- No sentence is tutorial boilerplate.
- The example carries a trailing commentary paragraph. It explains what the *After* leaves out rather than telling the reader not to copy it, so it does not break the "example followed by a caveat" rule.

### Item 4: Names by content, not by position

None. The checklist cross-references name sections (`§2, the What slot`), and the examples use named identifiers.

### Item 5: The failure report

Analogue: what each rule's checklist detection looks at.

- **Finding 3 (substantive).** The *Translation* checklist item (`SKILL.md:~826`) says to delete each What-slot sentence "where the diff still says it". The rule above it exempts a public identifier the change adds, removes or renames. The checklist has no exemption, so following it deletes the sentence that names the new flag. Request: add "except a public identifier, named once (§2)" to the item.
- Every other new rule is reached by a checklist item: Symptom, Alternatives, Discussion and Translation. The changelog row is covered by Symptom.

### Item 6: What the writer says it verified

- The commit message reports counts from blind drafts: 2 of 2, 5 of 10, none of 2, 2 of 4 to none of 4, and 3 of 3 to none of 4.
- None of the drafts is in the repository, and the message says the skill has no cases under `research/`.
- It states that the current open-question rule and the What-slot example were not re-run. That example is where finding 1 sits, so the unverified part carries a defect.
- There is no exemplar and bad-case pair for the changelog row or for the derived-consequence rule.

### Item 7: Siblings of the change

- Surfaces that list the package: `marketplace.json`, `apm.yml`, the package `apm.yml` and the README. All were updated and agree.
- No sentence counts the slots differently. "Five slots" and "Six slots" are unchanged and still correct.
- I searched the package for the old symptom wording. I found no stale "observable symptom" text.
- The README summary matches the SKILL rules.
- Two other packages mention `change-description-authoring`: `docs-page-authoring` and `problem-report-authoring`. They refer to it only by name, so they are unaffected.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The *After* example states an outcome in prose and a `sendDirect` hunk translation, against its own rule and the commit message | Substantive | `SKILL.md:354-358` | 1 |
| Audit-found rule: the commit body names what found it, the changelog row names the condition alone | Taste | `SKILL.md:81`, `:475` | 1 |
| The *Translation* checklist item has no exemption for a public identifier | Substantive | `SKILL.md:~826` | 5 |
| What slot with Translation deleted has no skip condition on a one-hunk fix | Substantive (table row) | `SKILL.md:~339`, `:~826` | 3 |

Not done: the drift script (no code), `make check` (needs the network), and a re-run of the blind drafts.
