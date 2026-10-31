I found six substantive findings and three taste findings. The main problem is that the change's own examples and checklist don't obey its new rules.

**Scope and inputs.** I reviewed `d79c43d..4f69810`, one commit that changes the `change-description-authoring` package (SKILL.md, README, three version fields). There was no task statement, so item 2's claimed cases come from the commit message alone. The change has no code, so I filled the form through the §2a analogues and did not run the drift script, which parses code members. I loaded `english-developer-style` and `apm-authoring`, the authoring skill for a skill package. There is no previous report. Line numbers below are in `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md` unless another file is named.

### Item 1: comments consistent with the code and with each other
*Analogue used: statements one file makes about another, counts, cross-references, and worked examples.*

- **Cross-references hold.** The skill and the commit message both say:
  - §5 holds the searchable-identifier rule (`:684`).
  - §7's paraphrase bullet now points to the What slot (`:763-764`).
  - §2 asks for "what changed that the diff does not show" (`:288`).
  - The changelog's symptom row cites "§2, slot 2" (`:475`).
  - "Six slots" and "Five slots" are unchanged and still correct.
- **The new What-slot *After* example (`:353-355`) breaks the rule it illustrates.**
  - Its second sentence, "with the pool open from startup it sends directly", is the `sendDirect` hunk, which the *Before* lists as "now uses sendDirect instead of sendWithRetry". The reason in front of it doesn't excuse it: the rule at `:342-344` says a sentence is "translation, even under a lead-in that states a reason… state the reason for the decision, not the edit that carries it."
  - Its first sentence, "a caller that runs before startup completes fails at once", is the caller-visible outcome. The paragraph after the example (`:357-359`) sends that outcome to "User-visible changes". `:231` says "A fact stated in slot 3 is not restated in slot 2." The commit message claims the example "no longer puts an outcome in prose", but it still does.
  - A reader who copies the exemplar keeps both forms the rule bans.
- **The existing description *After* example (`:254`), "The orphan sync is requeued with backoff on failure instead of being dropped", is the kind of sentence the new rule calls translation.** It is one hunk's content, yet the What slot table (`:196`) asks for "The behavioral change". See the instruction row on `:342` below.
- **README (lines 28-32) vs. SKILL.** The README says an audit-found defect gets "neither a predicted failure nor a claim that none was seen". SKILL `:96-99` allows a consequence derived from the code if it is traced and marked as derived. Someone deciding whether to install from the README gets a stricter rule than the one the skill ships (taste: "predicted" can be read as "untraced").
- **No narrating words.** Outside quoted examples, the added text has no "now", "no longer", or "used to".

### Item 2: claimed cases covered
*Analogue used: each claim the commit message makes, against the section that handles it. The claims come from the commit message alone.*

| Claim | Section |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:91-94`; table row `:81` |
| Changelog: the condition alone | `:475` |
| Derived consequence: traced to what a caller sees and marked as derived | `:96-99` |
| "Say so" kept for a defect with no symptom by construction | `:94-96` |
| What slot: a sentence recovered from one hunk is translation, even under a reason | `:342-344` |
| A public identifier the change adds, removes, or renames is named once | `:345-347` |
| §7 points to the rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| Rejected alternative: stated as a fact about the merged code; an obstacle the change removes is a step it took | `:371-373` |
| Open questions: answered, or kept in Scope with the decision and evidence, or dropped | `:458-464`; Scope row `:199` |
| Checklist: Symptom, Alternatives, Discussion, Translation | `:803-806`, `:826-838` |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-355` |
| "The examples avoid the pull request the drafts were written for" | Can't be checked: the commit message doesn't name that pull request |

- **Commands:** the change adds no command line.
- **Hunks no sentence claims:**
  - the version bump 1.3.0 → 1.4.0 in `.claude-plugin/marketplace.json`, `apm.yml`, and the package `apm.yml`;
  - the two README bullets.

  The three previous commits on this package each stated their bump ("Version 1.2.0 to 1.3.0."). This one doesn't.

### Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres the change claims, and the table of added instructions.*

**Partitions without evidence.** The commit claims rules for three genres:
- the commit body (slot 2),
- the pull request description,
- the changelog entry (row 3).

All fifteen trial drafts were pull request descriptions. The commit-body and changelog rules have no draft behind them. Also, by the writer's own account, the final open-question rule and the rewritten What-slot example were not re-run.

**Pre-existing state.** Consumers on 1.3.0 get the new rules through the version bump; nothing persistent is migrated. None.

| Instruction | Input it does not serve | What the agent writes there | Clause that ends it |
| --- | --- | --- | --- |
| `:92` "name what found it and end the sentence there", with `:475` "the condition alone" | An audit-found defect that a user has since hit, with a logged exception | "An audit of X found this."; the changelog drops the grep-able diagnostic | "where no failure has been observed" |
| `:342` "a sentence whose content the reviewer recovers from one hunk… is translation" | A one-hunk fix whose behavior change is that hunk | A What slot with the reason but no statement of the new behavior, against `:196` "The behavioral change" | "a sentence stating the behavior a caller or reviewer must judge stays, even where one hunk carries it" |
| `:826` "delete each sentence of the What slot in turn; where the diff still says it, leave it deleted" | A change that adds a system property | The sentence naming the property is deleted, which `:345` says to keep | "except a sentence naming a public identifier the change adds, removes, or renames" |

Not findings:
- `:96`, ended by "A consequence derived from the code".
- `:371`, ended by "The What slot names the alternative a reviewer would raise".
- `:458`, ended by "Where the code, a test, or another source you verified answers it".
- `:199`, ended by "a question from the discussion that only a maintainer can settle".

### Item 3a: level, placement, and the environment
The rules sit where their siblings are: the slot table and slot prose, "What each paragraph must earn", `#### Scope`, the changelog table, and the §8 checklist.

Both gates that work offline pass:
- `make check` (`apm pack --check-versions --check-clean --dry-run`) exits 0 and writes nothing. The three version fields agree on 1.4.0.
- `scripts/check-skill-descriptions.py` reports "ok: all 27 skill descriptions are within 1020 characters".

No added sentence is generic tutorial material. None.

### Item 4: names by content, not by position
`:357-358` says "the first sentence says why they are no longer needed"; "the sentence about opening at startup" would survive an edit (taste). Separately, `:463` breaks the line after "wanted. Leave". It renders correctly, so this isn't reported.

### Item 5: the failure report
*Analogue used: each rule reached by the checklist, and each detection checking its own rule.*

Every new rule has a checklist item: Symptom, Translation, Alternatives, and Discussion. One detection checks a different property than its rule: the Translation item (`:826`) deletes the identifier sentence that `:345` keeps. That is the third row of the table above.

### Item 6: what the writer says it verified
The commit message reports counts over fifteen blind Opus drafts, but:
- the drafts, prompts, and inputs are not committed. The commit says this skill has no cases under `research/`, which is true: `research/change-description-authoring/` holds only phase documents, while sibling skills keep a `cases/` directory;
- the drafts ran against 1.0.1, three versions before this one;
- the final open-question wording and the rewritten What example were not re-run, so no exemplar passes the rules as they now read;
- no input is reported where an added rule is noise, together with a check that the output there did not grow.

Hunk translation "persists in about one draft in two" is stated openly. The exemplar problem in item 1 may be one reason.

### Item 7: siblings of the change
- The README bullet list is updated.
- The frontmatter `description:` and the marketplace descriptions didn't need to change, because the skill's scope didn't widen.
- The two checklist items join an unnumbered list, and no prose counts them.
- `git grep` finds no other package with a rule on audit-found defects or hunk paraphrase. The `english-developer-style` copies only mention "audit the changelog" as a trigger verb.

None.

### Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| The What *After* example keeps a hunk under a reason ("it sends directly") and puts the outcome in prose ("fails at once"), against `:342-344` and `:231`; the commit message says it doesn't | Substantive | SKILL.md:353-355 | Rewrite the *After* so it states only the reason and the behavior the reviewer judges, then re-run a draft against it |
| The translation rule has no clause for a behavior change that is itself one hunk; it conflicts with `:196` and the `:254` example | Substantive | SKILL.md:342, :254 | Add a clause keeping the sentence that states the behavior a caller or reviewer must judge |
| An audit-found defect with an observed symptom loses its diagnostic in slot 2 and in the changelog | Substantive | SKILL.md:92, :475 | Limit both to "where no failure has been observed" |
| The Translation checklist item deletes the public-identifier sentence the rule keeps | Substantive | SKILL.md:826 | Add "except a sentence naming a public identifier the change adds, removes, or renames" |
| Only pull request descriptions were trialed; the commit-body and changelog rules, the final open-question rule, and the new example have no run; no noise-input check | Substantive | Commit message; SKILL.md:81, :458, :475 | One commit-body and one changelog draft under 1.4.0, plus an input where the rules are noise, with output length compared |
| Unclaimed hunks: version bump 1.3.0 → 1.4.0 and the README bullets | Substantive | apm.yml:168, marketplace.json:291, package apm.yml:2, README.md:26-32 | Add "Version 1.3.0 to 1.4.0." and a sentence for the README |
| The README says "neither a predicted failure", while SKILL allows a traced, marked derived consequence | Taste | README.md:28-30 | Add "unless traced to what a caller sees and marked as derived" |
| The audit case sits in the "Skip when" column of slot 2, while the prose puts a sentence in slot 2 | Taste | SKILL.md:81 | Move the audit clause to the "Answers" column |
| "the first sentence" refers by position | Taste | SKILL.md:357 | Name the sentence by its content |

I did not run the trials again or `make test`. `make verify-docs` and `install-smoke` need the network, and I did not do a style pass over the added prose.
