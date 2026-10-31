No previous report exists for this change, so the report has no table of earlier findings. The change is one commit, `4f69810` (`d79c43d..HEAD`). It touches a skill and its package files (`SKILL.md`, `README.md`, `apm.yml`, the root `apm.yml`, `marketplace.json`) and has no code. I filled the form through the §2a analogues, with `apm-authoring` and `english-developer-style` loaded. There was no task statement, so I took the claimed cases from the commit message alone. I did not run the drift script because there is no code for it to parse.

In this report, `SKILL.md` means `agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md`.

### Item 1: comments consistent with the code and with each other
*Analogue used: statements one file makes about another, and worked examples treated as statements.*

- **F1 (substantive).** The What-slot *After* example at `SKILL.md:356-358` says "a caller that runs before startup completes fails at once instead of opening the pool on demand". That is a caller-visible outcome written in What-slot prose. The paragraph after it (`:362-363`) puts the same outcome, the `IllegalStateException` from `Pool.acquire()`, on a "User-visible changes" line. `:227` says "A fact stated in slot 3 is not restated in slot 2", so the example breaks that rule, and agents copy examples. It also makes the commit message wrong where it says the example "no longer puts an outcome in prose". **Request:** keep only the reason in the first sentence, for example "The pool opens at startup, so the on-demand open path is no longer needed", and leave the early-caller outcome to its User-visible line.
- **F2 (substantive).** The Translation checklist item (`:826-827`) says "where the diff still says it, leave it deleted" and has no exception. The rule at `:345-347` keeps a sentence that names a public identifier the change adds, removes, or renames. A sentence like "Adds the system property `x.y`" is fully in the diff, so the checklist deletes what the rule keeps. The commit message itself reports that drafters check against the §8 checklist and not §2. **Request:** add the clause "except the one sentence that names a public identifier the change adds, removes, or renames (§2)".
- **F3 (substantive).** "name what found it and end the sentence there" (`:92`) can be read in two ways: the sentence ends there, or the slot ends there. Under the first reading, "An audit of the retry paths found this. It has not been seen to fail." passes the rule and also passes the checklist question at `:804-805` ("does the sentence end at what found it?"). That brings back the claim of absence the change set out to remove, now split into two sentences instead of joined by a semicolon. `README.md:28-30` states the stronger reading ("with neither a predicted failure nor a claim that none was seen"), so the two files disagree. **Request:** at `:92` and `:805`, say that the slot carries nothing more about a failure, seen or unseen, except a consequence traced as in `:98-101`.
- **F4 (substantive).** The open-question rule (`:461`) says a question only a maintainer can settle is kept "in the Scope slot". Under §4 rule 5 (`:608-610`) the description becomes the commit body and keeps reviewer-only content out, and the body's slots (`:76-83`) have no Scope slot. Under a squash, the instruction therefore either writes a maintainer question into permanent history or drops a question that bears on the change, which `:463` forbids. **Request:** add the clause "under §4 rule 5, in a review comment instead of the description".
- **F5 (taste).** The second sentence of the *After* example (`:358-359`) ends with "it sends directly", which is the edit. `:344` says "state the reason for the decision, not the edit that carries it". The sentence-by-sentence checklist test passes it because the first clause is a reason, so both readings hold up. I would drop the closing clause.
- **F6 (taste).** In a small fix, the behavioral change the What slot asks for (`:196`) can often be read from one hunk (`n < 0` → `n <= 0`). The translation rule at `:342-344` could then be read as deleting the slot's required content. Its examples (`X is removed`, `Y now calls Z`) are edits, not behavior, so the intended reading is probably that behavior stays. Saying so in one clause would settle it.

No other statement drifted. The README bullets, the §7 cross-reference (`:763-764`), the narrowed §2 wording (`:288`), and the Scope table cell (`:199`) match the body. `marketplace.json`, `apm.yml`, and the root `apm.yml` all say 1.4.0.

### Item 2: claimed cases covered
*Analogue used: the sections that handle each claim. These claims come from the commit message alone.*

| Claim | Section |
| --- | --- |
| Slot 2: an audit-found defect is described by what found it, and the sentence ends there | `:91-93`, table `:81` |
| A changelog entry for it names the condition alone | `:475` |
| A derived consequence is traced to what a caller sees and marked as derived | `:98-101` |
| "Say so" is kept for a defect with no symptom by construction | `:94-96`, `:81` |
| What slot: a sentence recovered from one hunk is translation; a public identifier is named once | `:342-347` |
| §7 points to that rule | `:763-764` |
| §2 asks for "what changed that the diff does not show" | `:288` |
| A rejected alternative's mechanism is a fact about the merged code | `:371-373` |
| An open question is answered, kept in Scope, or dropped | `:458-464`, `:199` |
| Checklist: Symptom, Alternatives, Discussion, Translation | `:803-806`, `:832-833`, `:834-837`, `:826` |
| Bad and good examples for slot 2 and the What slot | `:92-93`, `:349-359` |

Every claimed case has a section. The commit message's statement that the What-slot example "no longer puts an outcome in prose" is false; see F1. The change adds or edits no commands. The version bumps (1.3.0 → 1.4.0 in three files) are not mentioned in the message, but they are this package's own release bump and follow the repository's practice: `d79c43d`, `51b35c9`, and `985bf80` all do the same. They are not a finding.

### Item 3: boundaries, partitions, and the negative control
*Analogue used: the genres the change claims (commit body slot 2, pull request description, changelog part 3), and the table of added instructions.*

- **F7 (substantive).** Every trial in the commit message is a blind draft of one pull request description. The audit-defect rule also covers the commit body's slot 2 (`:81`, `:91-96`) and the changelog's part 3 (`:475`), and neither of those genres has any evidence. The message does say which rule versions were not re-run, but not that these two genres were never drafted. **Request:** either draft a commit body and a changelog entry for an audit-found defect, or add a sentence to the message saying these two genres have no evidence.

| Instruction | Input it does not serve | What the agent writes there | Condition that ends it |
| --- | --- | --- | --- |
| `:91-92` "name what found it and end the sentence there" (with `:475` "the condition alone") | an audit-found defect whose regression test (`:397`) then reproduced an exception | "An audit found this."; the exception text R3 greps for is dropped | "unless a run or a report has since shown the failure; then quote it" |

Not findings: `:98`, `:288`, `:371`.

The conflicts in the translation rule (`:342`) and the open-question rule (`:458`) are filed as F2, F4, and F6 under item 1.

### Item 3a: level, placement, and the environment
*Analogue used: where each rule lives, and the repository's own gates.*

none. Each rule sits in the section it governs, and the README summary is updated beside the body. I ran the offline gates: `make check` exited 0, `make check-descriptions` reported "ok: all 27 skill descriptions are within 1020 characters", and `research/change-description-authoring/check-classifier-target-ref.sh` passed all its cases. None of the new sentences reads as generic tutorial material.

### Item 4: names by content, not by position
*Analogue used: the change's own headings and cross-references.*

none. The new cross-references (`(§2, the What slot)`, `(§2, slot 2)`) use the skill's existing numbered slots and sections. No new text uses "above", "below", or an ordinal.

### Item 5: the failure report
*Analogue used: whether the §8 checklist reaches each rule, and whether each detection checks the rule it is attached to.*

- **F8 (substantive).** The changelog's "condition alone" rule (`:475`) has no checklist item. The Changelog item (`:842`) asks only for "symptom" in order. Worse, the Symptom item (`:803-806`) cites §3 and asks of an audit-found defect "does the sentence end at what found it?", which applied to a changelog entry asks for the opposite of `:475`. **Request:** add to the Changelog item "for an audit-found defect, the condition alone, with no word on what found it".

The other new rules are each reached by a checklist item. The Translation detection's gap is F2, and the sentence-versus-slot gap in the Symptom detection is F3.

### Item 6: what the writer says it verified
*Analogue used: an exemplar the rules pass and a bad case they fail.*

The commit message gives draft counts for the symptom, retold-obstacle, and open-question rules, and it says plainly which wordings were not re-run (the current open-question rule and the What-slot example) and that `research/` has no cases for this skill. Both slot 2 and the What slot have a bad and a good example. Applied to its own *After* example, the rewritten What-slot rule fails; see F1.

### Item 7: siblings of the change
*Analogue used: the places that list the package or point to it.*

none. I read every file outside the package that names `change-description-authoring` (`git grep`; the hits are the English style skills and rules, `docs-page-authoring`, `problem-report-authoring`, `test-authoring`, `qubership-repo-essentials`, and `research/`):
- None of them repeats the slot-2 or changelog wording.
- `qubership-repo-essentials` depends on the package by relative path, so there is no version to bump.
- The marketplace entry and both `apm.yml` versions agree, and `make check` confirms it.
- `references/merge-model.md` lists "problem, symptom, approach" for commit bodies and defers to §2, so it inherits the new rule.
- No counted set changed: the body still has five slots, the description six, and the changelog five parts.

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| F1: the What-slot *After* states the outcome that goes on a User-visible line; the commit message says it does not | Substantive | `SKILL.md:356` | 1 |
| F2: the Translation checklist item deletes the public-identifier sentence the rule keeps | Substantive | `SKILL.md:826` | 1 |
| F3: "end the sentence there" allows a second sentence claiming no failure; the README says otherwise | Substantive | `SKILL.md:92`, `README.md:28` | 1 |
| F4: a maintainer question kept "in the Scope slot" has no place under §4 rule 5 | Substantive | `SKILL.md:461` | 1 |
| F5: the *After* example ends with the edit ("it sends directly") | Taste | `SKILL.md:358` | 1 |
| F6: translation rule against the What slot's required behavioral change | Taste | `SKILL.md:342` | 1 |
| F7: commit-body and changelog genres of the audit rule have no draft evidence | Substantive | `SKILL.md:81`, `:475` | 3 |
| Table row: an audit-found defect that was later reproduced loses its diagnostic | Substantive | `SKILL.md:91` | 3 |
| F8: the changelog "condition alone" rule has no checklist item, and the Symptom item contradicts it | Substantive | `SKILL.md:842`, `:805` | 5 |

The comment-drift script was not run because the change contains no code for it to parse.
