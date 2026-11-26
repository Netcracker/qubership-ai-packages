## Change 1

1. **Guarantee of a dependency, split by source.** The class is where a dependency's guarantee gets recorded. Input A is a base image README that promises certificate loading, which goes into Context as a fact with its source. Input B is a rule from another ADR that this record's rule depends on, which gets cited by topic. General.
2. **Template Context comment ("no rule of this record or another is restated").** The class is Context restating a requirement. Input A is Context repeating the timeout of its own R2. Input B is Context quoting the retry limit of another record's rule. General, and it cites One home without restating it.
3. **Numbers freeze: cross-repository form and "every cited record appears under Related ADRs", with the retired-number exception.** The class is citation traceability. Input A is a Justification that cites a rule of a record in another repository. Input B is a Consequences entry that cites a record missing from Related ADRs. The retired-number exception is a first exception tied to Record numbers. General.
4. **One home, rewritten.** The class is where a requirement may reappear. Input A is a Justification citing R4. Input B is Context naming another record's rule by what it is about. The own-record clause (Negative, Open points, Confirmation) gives a boundary, not a third exception. General.
5. **Cite only what the reader needs.** The class is decorative citations. Input A is a "see also ADR-0031" in the Justification. Input B is a Confirmation line saying "ADR-0044 R2 still applies". General.
6. **Every requirement is a rule ("cites the rule that states it, not the record").** The class is how Confirmation and Implementation notes refer to requirements. Input A is an Implementation note saying "as ADR-0091 states". Input B is a Confirmation entry for a rule of another record. General.
7. **No pointer rules ("or only repeats a requirement", "give it in the Justification").** The class is a rule that adds a number and no requirement. Input A is a rule reading "R5 also applies to the batch endpoint". Input B is a rule copying R2's limit under another layer tag. General.
8. **Pre-publication read, extended to No pointer rules, Cite only what the reader needs, and sentences outside Rules.** The class is the final review of a record. Input A is a record whose Consequences cite a rule. Input B is a record whose Context cites a retired record. General.

Verdict: general change

## Change 2

1. **"when the part is absent, and, where it is owed, what to state and where to stop".** The class is a bad output that fills or leaves empty a part of an output. Input A is a pull request description whose "Testing" section is filled for a docs-only change. Input B is a review skill whose "Findings" section is padded with "none found because…". General. It sharpens the existing rule 4 and adds no rule.
2. **"A clause on where to stop bounds the part … only the condition on when it is absent keeps it off the inputs where it is noise".** The class is why the absence condition comes first. Input A is an `AGENTS.md` rule "summarize risks" that fires on a typo fix. Input B is a skill step "list assumptions" that fires on a task with none. General.

The other changed lines only rewrap and need no class.

Verdict: general change

## Change 3

### General sentences

- **Goal bullet (§3), with its test and the §11 Goal item's "where a reader could know another way".** The class is a missing boundary for "state the goal". Input A is a forum question asking how to do something. Input B is a request whose workaround step is the blocker. A crash or a red build is the quiet input. This is a fix under rule 4. The Goal item's clause restates this condition, so it is a patch (see below).
- **Isolation bullet (§4), "where more than one could … no isolation is owed".** The class is a defect that sits in the target project's own files. Input A is a dead link in a docs page. Input B is a crash whose trace stops in the project's code. Fix.
- **Nearest hit definition.** The class is what to cite when the search finds no exact duplicate. Input A is a tracker hit with another symptom. Input B is a list-archive thread. General.
- **Search that found nothing goes in a search slot or the hand-over note.** The class is where a null result goes. Input A is a GitHub form with no search field. Input B is a request form with a required "searched" field. Fix.
- **Count: dependencies only where several reports or a known relative exist.** Input A is a split across two repositories. Input B is a single report. Fix.
- **Question 4: "the observation is the grounding".** Input A is a crash. Input B is a link that returns 404. Fix. The example swap in the weak-grounding sentence changes no requirement.
- **§6 source labels needed only where one kind could be mistaken for another.** Input A is a report that mixes the reporter's log with your own run. Input B is a solo report. Fix.
- **§6 redaction sentence: say nothing where nothing changed.** Input A is a vendor ticket with substituted hostnames. Input B is a report about public code with no substitutions. Fix.
- **§6 version bullet, "whose behavior the symptom could depend on".** Input A is a library defect that surfaces through a build tool. Input B is a documentation defect. Fix.
- **§8 default layout, each part tied to a condition.** Input A is a library defect with a reproducer. Input B is a one-line documentation defect. Fix.
- **§11 intro (item applies only where its rule applies).** Input A is a question owing no Expected behavior item. Input B is a colleague message. General.
- **Request genre: opening paragraph (the search result goes to the prior-proposals slot).** Input A is a request with prior art. Input B is one with none. General.
- **Request genre: slot conditions for who is blocked, out of scope, prior proposals, and alternatives.** Input A is a request that adds a dependency. Input B is a request that changes a default. Fix.
- **Request genre: grounding sentence ("with who else has it where you know").** The class is a boundary for "who else has it". Input A is a new need with known co-sufferers. Input B is a new need with none. General.
- **Colleague message: Failing output row ("paste the lines that carry the claim and say nothing about the trim").** Input A is a failing test with a CI run link. Input B is a deploy log with a build-scan link. General. The colleague table is the right place for the override of §7.
- **Project conventions (acceptance criterion only; ownership, duplicates, and disclosure "need no line in it").** Input A is a bug filed in your own repository to fix yourself. Input B is a small request in a team backlog. General.
- **Worked cases header and Case 7.** The class is a report that is only its core. Input A is a misspelled name in a document. Input B is a dead link or stale claim in a document. General as a worked case. Case 7 has two flaws:
  - It says "every part past the core failed its condition in §8", but the commit and the search have no §8 condition. They fail §7 and §4.
  - The misspelled-name input recurs in rules 4, 6, and 8 and in Case 7, which leans toward rule 6.

### Patches

- **Request genre: "and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."** Rule 7 makes it a patch. §7 and §9 already say each section adds a fact, and the Alternatives slot and §3 already carry the negative-result setting, in the next bullet. The sentence is also a single instance of a class that already has a rule, so it fails rule 9's two-input test.
- **§8: "a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."** Rule 7 makes it a patch. The request-genre intro states the same condition and no-headings rule ("a request that fits in a few paragraphs carries no headings"). The text should cite one home and not carry two copies.
- **§11 items that restate the condition of their rule, now that the intro says each rule states when it applies.** Rule 7 makes each a patch, because a checklist item cites a rule and does not repeat its condition. The clauses are:
  - "where a reader could know another way to what you were doing"
  - "where more than one project could own the defect"
  - "where the search found something"
  - "where there are several reports or a related one is known"
  - "where the core does not show the expectation"
  - "where a reader could take one kind of evidence for another"
  - "whose version could change the outcome"
  - "where anything was changed"
  - "carry only the parts of §8 whose condition holds"
  - "each other slot of `references/request-genre.md` where that slot's condition holds"
- **Colleague table, Goal row: "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none."** Rule 7 makes it a patch. It copies the §3 boundary, and the table could say "Holds".
- **Colleague table, Reproducer row: "The versions of your tools only where the failure could depend on them; a failure CI shows too does not."** The first half restates §6 (rule 7). The second half names a single input kind and has no second input (rule 9).

Verdict: contains patches
