## Change 1

**Sentences**

1. **Guarantee of a dependency**: "Where a rule or a reason depends on the guarantee and its source is not a decision record, such as a base image's README, state the guarantee in **Context** as a fact, with its source."
   - Class: a rule that rests on a dependency's promise, where that promise is documented outside any record.
   - Inputs: a record on outbound TLS that relies on a base image loading certificates from a directory; a record on log shipping that relies on a platform's documented promise that stdout reaches the collector.
   - Finding: general. The sentence narrows an existing instruction.
2. **Guarantee of a dependency**: "Where its source is a decision record, cite its rule by what it is about instead (**One home**)."
   - Class: a dependency's promise that another team's record decides.
   - Inputs: a payments-client record that relies on the platform repository's rule on idempotency keys; a cache record that relies on another record's rule on event ordering.
   - Finding: a fix. It gives sentence 1 its boundary, and it settles the conflict with **One home** in the same edit, as rule 7 asks.
3. **Template, Context**: "No requirement belongs here, and no rule of this record or another is restated (**One home**)."
   - Class: a Context section that repeats a rule.
   - Inputs: a record that restates its own retry limit while it describes the problem; a record that quotes another record's token lifetime in Context.
   - Finding: patch (see below).
4. **Numbers freeze**: "…and a rule of a record in another repository as `owner/repo ADR-NNNN Rn`."
   - Class: a citation of a rule in another repository.
   - Inputs: a service record that cites the organization's security repository; a library record that cites a platform repository's rule on log fields.
   - Finding: general.
5. **Numbers freeze**: "Every record the text cites appears under **Related ADRs**, except a retired number that Context maps to its replacement (**Record numbers**), which has no file to link."
   - Class: a cited record that is missing from the metadata.
   - Inputs: a Justification that cites a database-choice record; a Negative that cites a record on API versioning.
   - Finding: general. The rule has one exception, and **Record numbers** is its source.
6. **One home**: "A requirement is stated once, in one rule. Everywhere else, cite it by number (by section and a short quote where the record has no numbers)."
   - Class: a requirement stated in two places.
   - Inputs: a Confirmation entry that restates its rule; a rewrite that cites an old record without numbers.
   - Finding: general.
7. **One home**: "Where you cite a rule of another record, in any section, name what the rule is about, not what it decides: …"
   - Class: a citation across records that copies the cited value.
   - Inputs: a client record that cites a server record's timeout; a deployment record that cites a record on allowed regions.
   - Finding: general. "A restatement drifts." is the reason kept from the old text.
8. **One home**: "In the rule's own record, a section other than **Rules** and Context may say what the rule decides, with its number, as **Negative**, **Open points**, and **Confirmation** do."
   - Class: a record that summarizes its own rules.
   - Inputs: a Negative entry that names a changed default; an open point that names a placeholder in a rule.
   - Finding: a fix (a boundary). "A table that summarizes rules holds rule numbers." only shortens the old sentence.
9. **Cite only what the reader needs** (all five sentences):
   - Class: a citation that changes no check and gives no reason.
   - Inputs that fire: a message-queue record with a "see also" to the logging record; a token-validation rule that reminds the reader that the audit rule still applies.
   - Input that stays quiet: a Justification that cites the record whose cost motivated a rule.
   - Finding: general.
10. **Every requirement is a rule**: "Where such a section refers to a requirement, it cites the rule that states it (**One home**), not the record."
    - Finding: a rewording of the old reference sentence. It asks the same thing, so it needs no check.
11. **No pointer rules**: "A rule that only repeats a requirement of another rule, or only says that another rule applies, adds a number and no requirement."
    - Finding: patch in its first clause (see below).
    - "Leave it out; where an approver needs the link, give it in the Justification."
      - Class: a rule that only points.
      - Inputs: "R9. ADR-0031 R4 applies" in a client record; a rule in a migration record that only says another rule still applies.
      - Finding: general.
12. **Drafting**: the two rule names added to the list, and "Then read every sentence outside **Rules** that cites a rule, in Context, the Justification, and the Consequences too, against …"
    - Class: a citation outside **Rules**.
    - Inputs: a Justification that cites a sibling record; a Negative that cites a rule.
    - Finding: general. The names in the list are citations.

Verdict: contains patches

- "No requirement belongs here, and no rule of this record or another is restated (**One home**)."
  - Rule 7. **One home** already says that Context may not say what a rule decides, and that a rule of another record is cited by its subject. The template placeholder is a second copy of that condition.
- "A rule that only repeats a requirement of another rule, …"
  - Rule 7, for this clause. "A requirement is stated once, in one rule" (**One home**) already forbids a rule that repeats another rule's requirement.

## Change 2

**Sentences**

1. "…first give that part a condition that ends it: when the part is absent, and, where it is owed, what to state and where to stop."
   - Class: a part of an agent's output that is wrong or padded on some inputs.
   - Inputs that fire: a pull request description skill whose Migration section gets invented for changes with no migration; an `AGENTS.md` rule that makes the agent add a changelog line for internal refactors.
   - Input that stays quiet: a rule for a format that a parser requires (rule 4 says it needs no boundary).
   - Finding: general. The change turns the old "or" into "and".
2. "A clause on where to stop bounds the part on the inputs that need it; only the condition on when it is absent keeps it off the inputs where it is noise."
   - Class: the same as sentence 1. This is the reason both conditions are required.
   - Inputs: the same two as sentence 1.
   - Finding: general.

The rest of the paragraph only moved to new line breaks.

Verdict: general change

## Change 3

**Sentences in `SKILL.md`**

1. **§3, goal**: the new heading, "A maintainer who knows another way…", "A crash, a red build, a typo, or a broken page is its own goal…", and the new test.
   - Class: a report that asks about a step when the step may not be the only way to the goal.
   - Inputs that fire: a question about pinning a transitive dependency in a build tool; a request for a cleanup hook in a test runner.
   - Input that stays quiet: a segfault in an image decoder.
   - Finding: general (a boundary).
2. **§4, ownership**: "where more than one could", and "Where the symptom sits in the project's own files, … no isolation is owed."
   - Class: whether isolation is owed.
   - Inputs that fire: a TLS error seen through an HTTP client and a proxy; a layout bug seen through a browser and a UI library.
   - Inputs that stay quiet: a dead link in the project's docs; an exception whose trace stops in the library's parser.
   - Finding: general.
3. **§4, search**: "The nearest hit is the closest item the search returned, one with another symptom included: …"
   - Class: a search that finds related reports that are not duplicates.
   - Inputs: a date-parsing defect where the search finds a closed time-zone issue; a request for a CLI flag where the search finds a discussion of a config key.
   - Finding: general.
4. **§4, search**: "Where the search found nothing, the report says so only in a slot … with no such slot, the query goes to the hand-over note."
   - Class: a search that found nothing.
   - Inputs: a GitHub form with a field for what you searched; a mailing-list report with no such field.
   - Finding: general.
5. **§4, count**: "Where the count produced several reports, or a related report is known, each report says what it depends on…"
   - Class: reports that depend on each other.
   - Inputs: a defect split between an ORM and a database driver; a protocol change that needs both the client and the server.
   - Finding: general.
   - "A single report with no known relative says nothing about dependencies."
     - Finding: not a patch. It repeats the boundary of the sentence before it, and rule 1 would cut it.
6. **§5, Q4**: "Where the observation shows the expectation by itself, … needs no sentence of its own."
   - Class: an observation that is its own grounding.
   - Inputs: a link in an API reference that returns 404; a crash in a CLI.
   - Finding: general. The replaced example sentence ("nothing in the documentation promises this…") is general too.
7. **§6, attribution**: "…wherever a reader could take one for another; a report whose evidence is all your own pasted output needs no label."
   - Finding: general (a boundary).
   - Inputs: a report that mixes a user's log with your own run; a report that holds only your own transcript (quiet).
8. **§6, redaction**: "Where you changed or removed anything, … and where nothing changed, say nothing."
   - Finding: general (a boundary).
   - Inputs: a vendor ticket with a renamed internal service; a report on an open-source library with nothing private (quiet).
9. **§6, versions**: the new heading and the new test ("whose version could change the outcome").
   - Finding: general (a boundary).
   - Inputs: a serialization defect that depends on the JDK version; a CSS defect that depends on the browser.
   - "A misspelled name in a README fails under any version of the tool that reads it, and the report gives the page and its commit, not the tool's version (§4)."
     - Finding: patch in its second clause (see below).
10. **§8, no form**: "…a defect report opens with the core (§7): …"
    - Class: a report with no form and no guide.
    - Finding: general. The list cites §7 and keeps close to its words.
    - "the reproducer, where reproducing takes more than opening the place the report names or running the command it pastes"
      - Class: a reproducer that is needed.
      - Inputs that fire: a race in a connection pool; a crash under one specific load.
      - Input that stays quiet: a dead link.
      - Finding: general.
    - "the workaround, where one exists; the analysis, marked, where you have one"
      - Finding: general.
    - "A report whose parts fit in a few sentences carries no headings: …"
      - Class: a short report.
      - Inputs: a CLI that returns the wrong exit code; a dead link in docs.
      - Finding: general.
    - The conditions on the grounding part and on the version part, and the sentence on requests and questions.
      - Finding: patches (see below).
11. **§11, preamble**: "An item applies only where the rule it asks about applies…", "An item that applies is answered…", and "…they go in the review or the hand-over note…"
    - Class: a checklist item answered with "none".
    - Inputs: a review of a dead-link report; a review of a vendor support ticket.
    - Finding: general.
    - The sentence on an issue you file to fix yourself: patch (see below).
12. **§11, items**: the conditions added to Goal, Ownership, Duplicates, Count, Grounding, Attribution, Reproducer, Redaction, Form, and Request.
    - Finding: patches (see below). The Form and Request items otherwise cite §8 and the request reference, which is fine.

**Sentences in `references/colleague-message.md`**

13. **Goal row**: "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none."
    - Finding: patch (see below).
14. **Failing output row**: "Where a run link holds the rest, paste the lines that carry the claim and say nothing about the trim."
    - Class: a chat message backed by a CI run.
    - Inputs that fire: a red Java build on main; a failed deploy pipeline.
    - Input that stays quiet: a local run with no link.
    - Finding: general.
15. **Reproducer row**: "The versions of your tools only where the failure could depend on them; a failure CI shows too does not."
    - Class: a chat about a failure that may depend on a version.
    - Inputs: a test that fails only on a colleague's local Node version; a lint error that main CI shows.
    - Finding: general.

**Sentences in `references/project-conventions.md`**

16. "…for a request, the acceptance criterion, the slot a backlog item most often lacks."
    - Finding: general. It follows the slot change in the request reference.
17. "…ownership, duplicates, and disclosure need no line in it."
    - Finding: patch (see below).

**Sentences in `references/request-genre.md`**

18. "…what it found goes in the prior-proposals slot below."
    - Finding: general (a boundary).
19. **The slots**: "Every request carries the first two." and "Each other slot appears only where its condition holds…"
    - Class: a short request.
    - Inputs: a request for a log-format option; a request to change a default retry count.
    - Finding: general.
    - "A slot is what the request says, not a heading: …"
      - Finding: patch (see below).
20. **Slot boundaries**: who else is blocked ("where you know or the change is costly"), out of scope, prior proposals, and alternatives.
    - Class: optional slots of a request.
    - Inputs that fire: a request to change a default timeout in an HTTP client (costly); a request that a maintainer could read as also asking for async support.
    - Input that stays quiet: a request for one new config key.
    - Finding: general. The prior-proposals clause "as §4 of the skill says" is a citation and matches §4.
21. **Grounding**: "…the grounding is then the task and what it costs today, stated as such, with who else has it where you know."
    - Finding: general.
22. **Backlog**: "…the acceptance criterion is the one a backlog item most often lacks."
    - Finding: general.

**Sentences in `references/worked-cases.md`**

23. **Intro**: "that serves", and "Case 7 is constructed…"
    - Finding: general.
24. **Case 7**
    - Class: a documentation defect with nothing past the core.
    - Inputs: a wrong flag name on a CLI help page; a dead link in an API reference.
    - Finding: general as a rule-9 case.
    - Under rule 2: this change makes a misspelled name or a typo the example in §3, §4, Q4, §6, §8, and case 7. After this round, re-read those sections as rule 9 asks, and draw the examples from other inputs.

Verdict: contains patches

- "A misspelled name in a README fails under any version of the tool that reads it, and the report gives the page and its commit, not the tool's version (§4)."
  - Rule 7 for the second clause. §4 already sets the identifier of a documentation defect as "the page URL and the version it shows", and this copy already says something different.
- From §8: "what the expectation rests on, where the core does not show it (§5, question 4); the version of every layer, where the symptom could depend on more than the project's files at the commit the report names (§6)"
  - Rule 7. Each part cites its rule and also restates that rule's condition in new words. The version condition no longer matches §6's "whose behavior the symptom could depend on".
- "A request and a question take the slots their references name, in that order, under the same rule: a slot whose condition does not hold is left out, and one that fits in a few paragraphs carries no headings."
  - Rule 7. The request reference now states the same rule, and the two copies differ: "a few sentences" for a report, "a few paragraphs" for a request.
- "A slot is what the request says, not a heading: a request that fits in a few paragraphs carries no headings, and each fact appears once, so a setting that does not serve you is stated beside the problem and not again under alternatives."
  - Rule 7. The first part is the second copy of the §8 sentence above. The last clause restates §3's rule on negative results and the "One kind moves" sentence of the Alternatives slot in the same file.
- "…and its Ownership, Duplicates, and Disclosure answers go in the hand-over note where they name anything, not in the issue." (§11), together with "…ownership, duplicates, and disclosure need no line in it." (`project-conventions.md`)
  - Rule 7. One rule now has two homes, and they already disagree. One copy sends the answers to the hand-over note, and the other only says that the issue carries no line for them.
- "Holds where you ask how to do something and the step may not be the only way; a red build, a failing test, or a broken service needs none" (colleague-message Goal row)
  - Rule 7. "Holds" now carries §3's new boundary on its own. This row restates that boundary with a narrower condition ("where you ask how to do something") and its own list of examples.
- The conditions added to the §11 items:
  - Goal: "where a reader could know another way to what you were doing"
  - Ownership: "where more than one project could own the defect"
  - Duplicates: "where the search found something"
  - Count: "where there are several reports or a related one is known"
  - Grounding: "where the core does not show the expectation"
  - Attribution: "where a reader could take one kind of evidence for another"
  - Reproducer: "whose version could change the outcome"
  - Redaction: "where anything was changed"
  - Rule 7. The new preamble already says that an item applies only where its rule applies. Each condition is a second copy of its rule's condition, and the Grounding copy already uses different words from Q4.
