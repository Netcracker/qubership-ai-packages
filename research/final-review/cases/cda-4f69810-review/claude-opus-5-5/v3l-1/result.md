# Final review: `d79c43d..4f69810`, change-description-authoring 1.4.0

There was no separate task statement, so I took the claimed cases from the commit message alone. There is no previous report to check against. This change has no code: it edits a skill (`SKILL.md`), its README, and three version fields. I filled the form using the §2a analogues, after loading `english-developer-style` from the given path and `apm-authoring` from `agent-packages/apm-authoring`. I ran the drift script on the range: it printed nothing and exited 0, because it has no Markdown members to parse.

Below, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

## Item 1: comments consistent with the code and with each other

*Analogue used:* every statement the changed files make about each other and about their own examples.

- **The new Translation rule removes a sentence the skill's own example needs.** The rule at `SKILL.md:342-347` cuts any sentence the reviewer could recover from one hunk. The existing PR *After* example at `SKILL.md:254` says "The orphan sync is requeued with backoff on failure instead of being dropped." One hunk shows that, so the rule cuts it. That leaves the What slot without "the behavioral change", which the slot table at `:196` requires. The rule never says where "the behavioral change" stops and "translation" begins. It also conflicts with `:290`, which says the reader should "tell … where to look".
- **The What *After* example still states an outcome in prose.** At `:353` it says "a caller that runs before startup completes fails at once". The note at `:358-359` says that outcome belongs under "User-visible changes", and `:231` says "A fact stated in slot 3 is not restated in slot 2". The commit message claims the example "no longer puts an outcome in prose", which is false.
- **The Symptom checklist contradicts the changelog row.** The checklist at `:804-805` asks whether "the sentence end[s] at what found it". The changelog row at `:475` says to write "the condition alone". An agent that checks a changelog entry against the checklist would add "An audit found this".
- **The no-symptom example does not fit the new wording.** `:94-95` says "no symptom by construction (a leak on an error path with nothing logged)". A leak does have a symptom: the leaked resource grows until it runs out. Read with `:94`, "neither is the absence of one" known, an agent with a leak an audit found gets two answers: say there is no symptom, or end at what found the defect.
- **The README contradicts the skill.** README `:29-30` says "with neither a predicted failure nor a claim that none was seen". The skill allows a traced consequence marked as derived (`:98-101`) and a stated absence by construction (`:94-96`).
- **Taste:** the identifier exception at `:345` covers only identifiers the change "adds, removes, or renames". §5 at `:683` names any public identifier "the change touches", and the *After* example itself names `QueryExecutor.execute`.

## Item 2: claimed cases covered

| Claim in the commit message | Where it is handled | Detection |
| --- | --- | --- |
| Name what found the defect and end the sentence there | `:81`, `:91-93` | Symptom checklist `:804` |
| Changelog entry gives the condition alone | `:475` | **none** (`:842` is silent, `:804` contradicts it) |
| Derived consequence must be traced and marked | `:98-101` | `:803-804` |
| "Say so" kept for no symptom by construction | `:94-96` | `:805` |
| Translation even under a reason lead-in | `:342-345` | `:826` |
| A public identifier is named once | `:345-347` | `:826` deletes it anyway (item 5) |
| §7 points to the rule | `:763-764` | n/a |
| §2 asks for "what changed that the diff does not show" | `:288` | n/a |
| Rejected alternative is a fact about the merged code | `:370-373` | `:833-834` |
| Open questions: answer, keep in Scope, or drop | `:199`, `:458-465` | `:835-838` |
| Slot 2 and What carry a bad and a good example | `:92-93`, `:349-355` | n/a |

- The claim "each fix … has a checklist item" does not hold for the changelog condition-alone rule.
- **Unclaimed hunks:**
  - The version bump from 1.3.0 to 1.4.0 in `apm.yml:168`, `agent-packages/change-description-authoring/apm.yml:2`, and `.claude-plugin/marketplace.json:291`. The two previous commits each stated "Version 1.x.0 to 1.y.0".
  - The README hunk (`README.md:26-32`).
- Commands: the changed text tells the reader to run none.

## Item 3: boundaries, partitions, and the negative control

*Analogue used:* the claimed artifacts and situations, the trial's arms, and the table of added instructions.

- **Partitions with no evidence.** The trial drafts were PR descriptions only. These claimed artifacts or branches have no draft at all:
  - the commit body (slot 2);
  - the changelog row;
  - the maintainer-only branch of the open-question rule.

  The commit message says itself that the current open-question rule and the new What example were not re-run. The final symptom wording rests on two drafts ("none of two").
- **Negative control.** No run on an input where the new items are noise (no audit-found defect, no open question, no rejected alternative) shows that the output did not grow.
- **Pre-existing state.** Consumers upgrade the package with `apm install`. The change reads no persisted state, so nothing to check.

Added or widened instructions: 6 (`:92`, `:98`, `:342`, `:370`, `:458`, `:475`), no rows. The inputs that fire them without serving a reader are conflicts or ambiguities, and those are filed under item 1.

Not findings:
- `:458`: a Scope-slot question in a description that becomes the commit body is ended by `:608-610` ("keep reviewer-only content out of it").
- `:92`: on a changelog entry it is ended by `:475`.
- `:98`: ended by its own "only after it is traced".

## Item 3a: level, placement, and the environment

*Analogue used:* where each rule lives and which repository gates check it.

- Each rule sits in the slot section it governs and has its own checklist line, which matches the skill's existing layout.
- `scripts/check-skill-descriptions.py` passes: "all 27 skill descriptions are within 1020 characters".
- The version is 1.4.0 in all three places.
- I could not run `apm pack --check-versions --check-clean` offline.
- No added sentence reads as generic tutorial material.
- Taste: in the source, `:463` "wanted. Leave" is a stray short line. It renders fine.

## Item 4: names by content, not by position

- **Ambiguous pointer.** `:475` cites "(§2, slot 2)", but §2 has two slot 2s: the commit body's *Impact and trigger* and the PR description's *What*. The new `:763` already does it right with "(§2, the What slot)".
- No other changed heading or cross-reference uses an ordinal.

## Item 5: the failure report

*Analogue used:* whether each checklist line detects the rule it is attached to.

- **Translation detection is broader than the rule.** `:826` says "where the diff still says it, leave it deleted". That also deletes the public-identifier sentence the rule keeps at `:345`.
- **Symptom detection contradicts the changelog rule.** `:804` conflicts with `:475` (item 1). The Changelog checklist line `:842` does not check condition-alone at all.
- The Discussion and Alternatives checklist lines match their rules.

## Item 6: what the writer says it verified

- The commit message gives measured bad cases for three of the four defects: symptom, retold obstacle, and open question. For hunk translation it says only that the defect persists in about one draft in two.
- It says the current open-question rule and the new What example were not re-run.
- When I apply the rewritten Translation rule to the skill's own PR exemplar, the exemplar fails it (item 1).
- No noise input is named.

## Item 7: siblings of the change

- The README was updated. The marketplace description and frontmatter are unchanged, and the scope did not widen, so they did not need to change.
- The umbrella `qubership-repo-essentials` pins the package by relative path and needs no bump.
- The PR Why slot inherits the slot 2 rules through `:206`. The changelog got its own row.
- I grepped for "observable symptom" and "no symptom" across `agent-packages/` and found no other skill that restates the old slot 2 wording.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| The Translation rule cuts the behavioral-change sentence of the skill's own PR *After* example. | Substantive | `SKILL.md:342`, `:254` | Add a clause that keeps one statement of the behavioral change in the caller's terms, and limits translation to sentences that narrate code edits. |
| The Translation checklist deletes the public-identifier sentence the rule keeps. | Substantive | `SKILL.md:826` | Append "unless it names a public identifier the change adds, removes, or renames". |
| The Symptom checklist contradicts the changelog's "condition alone", and no checklist line checks that rule. | Substantive | `SKILL.md:804`, `:475`, `:842` | Scope `:804` to the commit body and description, and add condition-alone to the Changelog line. |
| The What *After* example restates in prose an outcome assigned to "User-visible changes". The commit message says otherwise. | Substantive | `SKILL.md:353`, `:358`, `:231` | Drop "fails at once …" from the *After* sentence, or reconcile it with `:231` and correct the commit message. |
| The README says the skill forbids any predicted failure. The skill allows a derived consequence marked as such. | Substantive | `README.md:29` | Add "except a consequence traced in the code and marked as derived". |
| The leak example has a symptom, so it does not illustrate "by construction". | Substantive | `SKILL.md:95` | Replace it with an example whose absence of symptom is structural, such as a wrong value written to a field nothing reads. |
| The version bump and README hunks are unclaimed. | Substantive | `apm.yml:168`, `…/apm.yml:2`, `marketplace.json:291`, `README.md:26` | Add "Version 1.3.0 to 1.4.0" and a sentence on the README. |
| "(§2, slot 2)" is ambiguous between two slot 2s. | Substantive | `SKILL.md:475` | Name it by content: "(§2, Impact and trigger)". |
| The commit body, changelog row, maintainer-question branch, and final What example were never drafted against. No noise-input control. | Substantive | commit message | Run the final wording on a commit body and a changelog entry, and on an input where the new items do not apply; report whether the output grew. |
| The identifier exception is narrower than §5's "the public identifier the change touches". | Taste | `SKILL.md:345`, `:683` | Align the two lists. |
| "This skill has no cases under research/", but `research/change-description-authoring/` exists. | Taste | commit message | Say "no draft cases". |
| Stray short source line "wanted. Leave". | Taste | `SKILL.md:463` | Reflow the paragraph. |

I did not run `make test`, `apm pack`, super-linter, or markdownlint, because they need `uv`/`uvx` and the network. The drift script parses no Markdown, and I did not do a style-only pass over the prose.
