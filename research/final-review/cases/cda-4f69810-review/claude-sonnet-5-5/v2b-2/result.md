# Final review: `d79c43d..HEAD` (4f69810, one commit)

**Inputs.**
- There is no separate task statement. The claimed cases below come from the commit message alone.
- The commit has no previous report.
- This is a change with no code: a skill, its README, and version metadata (§2a). I did not run the drift script, because there are no members to parse. It did produce no output when I ran it on the range.
- I applied the analogues in §2a and cited `english-developer-style` for wording only where a sentence reads wrongly. I did not load `test-authoring`, because the change has no tests. I did not load `apm-authoring`, because it isn't among the three skills I was given.
- I read the new text against the commit's claims and against the existing sections.
- `make check` (`apm pack --check-versions --check-clean --dry-run`) exits 0 and leaves the tree clean.

Claimed cases, from the commit message:
1. A defect found by an audit or a code reading is described by what found it, and the sentence ends there.
2. A derived consequence is written only when traced to what a caller sees, and is marked as derived.
3. A sentence recoverable from one hunk is translation. A public identifier is named once.
4. A rejected alternative states a mechanism that holds in the merged code. An obstacle the change removes is a step, not a reason.
5. An open question is answered, or kept in Scope when only a maintainer can settle it, or dropped when it doesn't bear on the change.
6. The Symptom and Alternatives checklist items are tightened, and there are new Discussion and Translation items.
7. The slot 2 and What-slot rules carry a bad and a good example.

## Item 1: comments consistent with the code and with each other

Analogue used: statements the changed files make about each other and about the repository.

- **Finding (substantive), SKILL.md, the What-slot example (lines ~350–359).** The commit says the What-slot example "no longer puts an outcome in prose". The *After* text does put one there: "a caller that runs before startup completes fails at once instead of opening the pool on demand". The next paragraph then says the `IllegalStateException` for that caller "goes on its own line under 'User-visible changes'". Line ~229 says "A fact stated in slot 3 is not restated in slot 2", so the example restates an outcome in prose. A reader copying the example duplicates the outcome. The commit message is also wrong about the example.
- **Taste, same example.** *After* sentence 2 ends "with the pool open from startup it sends directly". That is a "Y now calls Z" sentence under a lead-in that states a reason, which the new rule calls translation. The part about `sendWithRetry` existing only to reopen a closed pool is not recoverable from the hunk, so the sentence is arguable. Cutting it to the reason alone would make the example obey its own rule.
- **Taste, slot 2.** The new text says "a predicted failure is not known" and also allows a derived consequence once traced. The two are reconciled only by the word "sentence" and by "marked as derived". One clause saying "a traced consequence is not a prediction" would remove the second reading.
- **Holds.**
  - Section cross-references resolve: §2, §3, §4 rule 5, §5, §7.
  - The README bullets match the new rules.
  - The slot 2 skip condition, the changelog part 3, and the Symptom checklist item all agree.
  - Nothing narrates the change with "now" or "no longer" outside the examples.

## Item 2: claimed cases covered

Analogue used: each claimed case against the section that handles it, and its detection.

| Case | Section | Detection |
| --- | --- | --- |
| 1 | slot 2 paragraph, Symptom item | Symptom item asks "does the sentence end at what found it". |
| 2 | new slot 2 paragraph | Symptom item asks "traced and marked as derived". |
| 3 | What slot, §6, Translation item | Translation item says delete each sentence in turn. |
| 4 | rejected-alternative paragraph, Alternatives item | Alternatives item asks "is the mechanism a fact about the merged code". |
| 5 | Scope slot row, new Scope paragraph, Discussion item | Discussion item. |
| 6 | §8 | Present. |
| 7 | slot 2 and What slot | Both examples are present. |

- Every hunk belongs to a sentence of the commit message. The version bumps to 1.4.0 appear in all four places and agree (`apm.yml` ×2, package `apm.yml`, `marketplace.json`).
- No command is added, so there are no command lines to match against runs.
- **Taste.** The Scope-row addition in the PR table and the Scope paragraph both carry the "decision it needs and evidence" clause. That is duplication, but it is the repo's usual table-plus-prose shape.

## Item 3: boundaries, partitions, and the negative control

Analogue used: the partitions the change claims, and the negative control.

Table of added instructions, one input per instruction:

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it | Label |
| --- | --- | --- | --- | --- |
| Slot 2: name what found the defect | A defect users reported, so the symptom is observed | "An audit found this" is not written. Observed symptoms still apply. | "Where reading the code or an audit found the defect…" | Not a finding; the condition ends it. |
| Derived consequence earns a sentence only after tracing | A one-line fix with a single call site | A "traced through every mechanism" sentence about a path that has none | None | **Taste**: "only where more than one mechanism lies on the path". |
| Translation rule (cut a sentence recoverable from one hunk) | A one-hunk change whose What slot is the only sentence and gives the reason | It deletes the slot, as the Translation checklist item says to ("leave it deleted") | The rule keeps "state the reason for the decision". | Not a finding. |
| Name a public identifier once | An identifier already named in a trailer or a `User-visible:` line | It names the identifier a second time in What | None | **Taste**: "unless a `User-visible:` line already names it". |
| Rejected-alternative mechanism must hold in the merged code | A description with no rejected alternative | It invents one | "earns its sentence only where a reader would propose it" | Not a finding. |
| Open question rule | An issue with no open questions | Nothing | "Leave a question out only when it does not bear on this change" | Not a finding. |

- Other partitions: the commit body, the PR description, and the changelog entry each get a matching rule or a checklist item. The changelog row (line 475) and the PR Scope row are covered.
- No prior state was left behind. This is a documentation package, and the install-over-earlier-version partition has no state beyond the version number.

## Item 3a: level, placement, and the environment

Analogue used: file placement, registration entries, and the repository gate.

- None. The rules sit in the existing SKILL.md sections.
- The README gets a matching bullet.
- Registration entries are in sync, and `make check` passes.
- No sentence is generic enough to appear unchanged in any tutorial.

## Item 4: names by content, not by position

None. The new text refers to slots by name and section number, which are stable headings. The "slot 3" and "slot 2" references are the skill's own slot numbering, which the existing text already uses.

## Item 5: the failure report

Analogue used: every new rule is reached by the checklist and detects what it names.

- None as findings. Symptom, Alternatives, Translation, and Discussion are in §8.
- **Taste.** The Translation item ("delete each sentence in turn; where the diff still says it, leave it deleted") catches a hunk-recoverable sentence. It does not catch the outcome-in-prose case in the example, because that sentence isn't recoverable from a hunk. It is caught only by the Caller item. This ties to the Item 1 finding.

## Item 6: what the writer says it verified

- The commit states fifteen blind drafts with counts: both drafts predicted a failure; five of ten stated that none was seen; none of two did under the final wording. It also states the retold obstacle (two of four down to none of four) and the open question (three of three down to none of four).
- It states that hunk translation "persists in about one draft in two".
- It states that the current open-question rule and the What-slot example were **not re-run**.
- The bad-case evidence exists for most rules. The one gap the commit admits is the one the Item 1 finding hits: the *After* example was not re-run.
- It does not state an input where an added rule is noise, and a check that the output did not grow there.
- I did not run any drafts.

## Item 7: siblings of the change

Analogue used: places that enumerate or route to the artifact.

- The marketplace entries and the version-bearing files are all updated, and no `1.3.0` for this package remains. The other `1.3.0` hits belong to other packages.
- The umbrella and other-package references (`docs-page-authoring`, the `english-*-developer-style` skills) name the package, not its rules, so none need an update.
- **Taste.** The "no paraphrase of the diff" rule in §7 now points to the What slot. The commit-body section has a similar "paraphrase" ban, so the Translation checklist item says "What slot" and does not say it also governs commit bodies. The reader can tell from the §7 pointer, so I'm not requesting a change.
- No count sentence ("both", "the three") still applies to a set the change enlarged.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The *After* example puts an outcome in prose ("fails at once…"), against the slot 3 rule and the commit's own claim about the example | **Substantive** | `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` ~353–355 | Rewrite *After* sentence 1 as the reason only, with no outcome. Re-run drafts against the final example, or state in the description that it was not re-run (the commit does say this). |
| *After* sentence 2 ("it sends directly") is a hunk translation under a reason lead-in | Taste | same, ~355–357 | Keep only "`sendWithRetry` existed only to reopen a closed pool". |
| "Predicted failure is not known" and "derived consequence earns a sentence" read as opposed | Taste | same, ~93–100 | Add "a traced consequence is not a prediction". |
| Derived-consequence tracing is owed on a one-line, single-path fix | Taste | same, ~97–100 | Add "only where more than one mechanism lies on the path". |
| A public identifier is named again in What although a `User-visible:` line has it | Taste | same, ~343–347 | Add "unless a `User-visible:` line already names it". |

The review did not run the skill against any draft, did not run the drift script (no parsable members), and did no style-only pass over the prose.
