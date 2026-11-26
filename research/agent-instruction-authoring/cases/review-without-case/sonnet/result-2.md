## Change 1

Each added or changed sentence, with its class and two inputs from the skill's scope:

1. **Guarantee whose source is not a decision record goes in Context with its source.**
   - Class: where a dependency guarantee that a rule relies on is recorded.
   - Inputs: a base image README that promises trust-store handling, and a library's documented default timeout that a reason depends on.
2. **Guarantee whose source is a decision record is cited by what its rule is about.**
   - Class: the same guarantee, when another record's rule is the source.
   - Inputs: a platform record's retry limit that a rule relies on, and a logging-format record that a reason relies on.
3. **Template Context: no rule of this record or another is restated.**
   - Class: what Context may contain.
   - Inputs: Context of a token-expiry record that mentions an earlier record's limit, and Context of a rewrite that carries the old record's facts.
4. **A rule of a record in another repository is cited as `owner/repo ADR-NNNN Rn`.**
   - Class: cross-repository citation form.
   - Inputs: a Justification that cites an org-wide record, and a Related ADRs line that links one.
5. **Every cited record appears under Related ADRs, except a retired number mapped in Context.**
   - Class: completeness of the Related ADRs list.
   - Inputs: Rules that cite `ADR-0091 R7`, and Context that maps a retired number to its successor.
6. **One home: stated once, cited by number, or by section and quote where there are no numbers.**
   - Class: how a requirement is referred to outside its rule.
   - Inputs: a Confirmation entry for a rule of the same record, and a new record that cites an old record with no numbered rules.
7. **A rule of another record is cited by what it is about, not what it decides.**
   - Class: cross-record citation wording.
   - Inputs: a Consequences line about another record's retry limit, and an Alternatives entry about another record's storage rule.
8. **In its own record, sections other than Rules and Context may say what a rule decides, with its number.**
   - Class: where a decision may be restated.
   - Inputs: a Negative entry that names an accepted cost, and an open point that lists the rules it affects.
9. **Cite only what the reader needs.** This is the new rule, and each of its four sentences has the same class: pruning citations.
   - Inputs: a Justification "see also" for a neighboring record, and a rule that adds "R4 still applies".
   - The sentence "A rule in force applies to every change whether or not it is cited" has the same two inputs.
   - So does the sentence that says to rewrite the citing rule instead of adding a citation.
10. **Every requirement is a rule: a referring section cites the rule, not the record.**
    - Class: how Confirmation and Implementation notes point at requirements.
    - Inputs: a Confirmation entry for a limit set by another record, and an Implementation note about a migration order.
11. **No pointer rules: also a rule that only repeats a requirement.**
    - Class: rules that add a number and no requirement.
    - Inputs: an R6 that copies R2's timeout, and an R5 that says "R3 applies to uploads".
    - The sentence that sends the link to the Justification has the same two inputs.
12. **Drafting: the pre-publication read adds No pointer rules and Cite only what the reader needs, plus a second pass over every citing sentence.**
    - Class: the review before publishing a record.
    - Inputs: a new record on a dependency choice, and a rewrite of an accepted record.

No sentence is a patch. Sentences 6, 10 and 11 sharpen rules that already exist (rule 3 of the authoring skill), and 1, 2, 3 and 8 give a rule its boundary (rule 4).

Verdict: general change

## Change 2

Each changed sentence:

1. **The fix order is now: when the part is absent first, then, where it is owed, what to state and where to stop.**
   - Class: how to fix a bad output in a part of an instruction.
   - Inputs: a commit body that guesses at a cause, and a PR description whose Testing section is padded on a docs-only change.
2. **"A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise."**
   - Class: why the absence condition comes first.
   - Inputs: a review with "none found because…" on a clean diff, and a changelog "Breaking" section on a patch release.

The remaining lines are re-wrapped with no change of meaning.

Verdict: general change

## Change 3

**Sentences that pass.** Each is a boundary (rule 4) or a sharpening of an existing rule, with a class and two inputs.

| Sentence | Class | Two inputs |
| --- | --- | --- |
| §3 Goal: stated where another route may exist; "a crash, a red build, a typo, or a broken page is its own goal" | when the goal needs its own sentence | a "how do I export X" question with other routes, and a crash report |
| §4 Isolate: "where more than one could"; no isolation owed where the place the report names is the evidence | when ownership isolation is owed | a dead link in a project's docs, and a crash whose trace stays in the project |
| §4 Duplicates: the nearest hit is the closest item returned, even with another symptom | which hit gets cited | a closed issue with a similar symptom, and a rejected proposal for a request |
| §4 Duplicates: a null search is reported only in a slot made for it, otherwise the query goes to the note | where a null result goes | a form with "searched existing issues", and a mailing list |
| §4 Count: dependencies are stated where there are several reports or a known relative | when a dependency statement is owed | a client/server pair, and a single typo report |
| §5 Q4: the observation is the grounding where it shows the expectation | when a grounding sentence is owed | a 404 link, and a crash |
| §5 Q4: the example "nothing in the documentation promises this; it rests on our own setup" | example of plain wording for a weak grounding | a preference-grounded request, and reliance on undocumented behavior |
| §6 Source: labels where a reader could confuse kinds; none for all-own output | when attribution labels are owed | a report with only your own transcript, and one that mixes in a reporter's log |
| §6 Redaction: one sentence only where something changed | when the redaction note is owed | a log with a token removed, and a reproducer with nothing private |
| §6 Version: layers "whose behavior the symptom could depend on", with the README example, and the changed test | which layers need a version | a doc typo, and a hosted-service failure |
| §8 Defect order: core first, then parts "each only where its condition holds" | which parts a form-less report carries | a doc typo, and a build-tool crash |
| §11 intro: items apply only where their rule applies; answers go in the review or the note; own-backlog wording | checklist use | a redaction item with nothing to redact, and a request |
| `colleague-message.md` Failing output: where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim | the trim note in a chat message | a red CI link, and a build-pipeline link |
| `project-conventions.md`: the acceptance criterion is the slot a backlog item most often lacks | which slot a backlog request lacks | a backlog feature request, and a backlog refactoring request |
| `request-genre.md`: "Every request carries the first two"; the conditions on Who else, Out of scope, Proposed before and Alternatives; the grounding paragraph; the opening rewording | which request slots are owed | a two-paragraph request, and a costly API addition |
| `worked-cases.md`: the intro rewording and Case 7 | an example of a report that is only its core | a misspelled name, and a dead link in a docs page |

**Patches:**

1. `request-genre.md`: "each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."
   - Rule 7 makes this a patch. The negative-result rule in §3 and the Alternatives bullet right below this sentence already say it. The same-fact repetition is also covered by §7 and by §9, "The same fact in four sections".

2. The no-headings condition, stated in three places:
   - `request-genre.md`: "A slot is what the request says, not a heading: a request that fits in a few paragraphs carries no headings".
   - §8: "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."
   - §8, defect case: "A report whose parts fit in a few sentences carries no headings".
   - Rule 7 makes these patches. The condition has three copies and no single home. The §8 sentence also restates the slot conditions that the request reference owns. Keep the condition in §8 and let the request reference cite it.

3. `colleague-message.md`, two table rows:
   - The Goal row: "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none".
   - The Reproducer row: "The versions of your tools only where the failure could depend on them; a failure CI shows too does not".
   - Rule 7 makes these patches. Both copy the boundaries that §3 and §6 now carry. The old "Holds" cited the rule, and the table's own text says a rule it lists as holding holds whole.

4. §11, restated conditions:
   - The condition clauses added to the Goal, Ownership, Duplicates, Count, Grounding, Attribution, Reproducer, Redaction, Form and Request items.
   - The sentence "its Ownership, Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the issue".
   - Rule 7 makes these patches. The new intro says "each rule above says when that is", so these items only copy each rule's boundary a second time. The self-filed-issue sentence also repeats the paragraph in `project-conventions.md`. Make the items cite their rules and keep one home for each condition.

Verdict: contains patches
